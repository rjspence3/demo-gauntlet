"""
API router for ingestion-related endpoints.
"""
import os
import uuid
from typing import Any
from dataclasses import asdict
from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from backend.ingestion.parser import extract_from_file
from backend.ingestion.chunker import chunk_slide
from backend.ingestion.tagger import tag_slide
from backend.models.session import SessionStore
from backend.limiter import limiter

router = APIRouter(prefix="/ingestion", tags=["ingestion"])

# NOTE: the web does NOT construct a VectorStore — that loads the embedding model
# (~80MB SentenceTransformer) at import and dominated the web cold start. Only the
# worker (backend/ingestion/processor.py) embeds, and it builds its own store.

@router.post("/upload")
@limiter.limit("5/minute")
async def upload_deck(
    request: Request,
    file: UploadFile = File(...)
) -> dict[str, Any]:
    """
    Uploads a deck, parses it, and ingests it into the vector store.
    Open access (demo mode), but rate-limited and size-capped: this endpoint
    enqueues a billable worker Job, so it must not be spammable anonymously.
    """
    if not file.filename:
         raise HTTPException(status_code=400, detail="Filename is missing")

    allowed_extensions = {".pdf", ".pptx"}
    ext = os.path.splitext(file.filename)[1].lower()

    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {allowed_extensions}"
        )

    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    # Fast-path reject on the declared size, then enforce the real limit by
    # streaming — Content-Length (file.size) is client-controlled and spoofable.
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 50MB.")
    total = 0
    while chunk := await file.read(1024 * 1024):
        total += len(chunk)
        if total > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="File too large. Maximum size is 50MB.")
    await file.seek(0)  # rewind so save_upload can re-read the stream

    session_id = str(uuid.uuid4())
    # Use BlobStorage to save the file
    from backend.services.blob_storage import get_blob_storage
    blob_storage = get_blob_storage()

    try:
        file_path = blob_storage.save_upload(file, session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}") from e

    # Offload processing to background task (Arq) — durable in Redis.
    await request.app.state.arq_pool.enqueue_job(
        "process_deck_upload_task", file_path, session_id,
        _queue_name=request.app.state.arq_queue_name
    )

    # Spin up the worker Cloud Run Job to drain the queue (no-op locally).
    from backend.services.worker_trigger import trigger_worker_job
    await trigger_worker_job()

    return {
        "session_id": session_id,
        "filename": file.filename,
        "slide_count": 0, # Unknown yet
        "metadata": {},   # Unknown yet
        "status": "processing"
    }

@router.get("/session/{session_id}/status")
async def get_session_status(session_id: str) -> dict[str, str]:
    """
    Retrieves the processing status of a session.
    """
    session_store = SessionStore()
    status = session_store.get_session_status(session_id)
    return {"status": status}

@router.get("/session/{session_id}/slides")
async def get_slides(session_id: str) -> list[dict[str, Any]]:
    """
    Retrieves the slides for a given session.
    """
    session_store = SessionStore()

    slides = session_store.get_slides(session_id)
    if not slides:
        # Check if session exists or is still processing
        status = session_store.get_session_status(session_id)
        if status == "processing":
             return [] # Return empty list while processing
        elif status == "unknown":
             raise HTTPException(status_code=404, detail="Session not found")

    return [asdict(s) for s in slides]
