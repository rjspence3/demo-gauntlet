import os
import shutil
import uuid
from typing import Any
from dataclasses import asdict
from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.ingestion.parser import extract_from_file
from backend.ingestion.chunker import chunk_slide
from backend.ingestion.tagger import tag_slide
from backend.models.store import VectorStore

router = APIRouter(prefix="/ingestion", tags=["ingestion"])

# Initialize store (singleton-ish for now)
store = VectorStore()

@router.post("/upload")
async def upload_deck(file: UploadFile = File(...)) -> dict[str, Any]:
    """
    Uploads a deck, parses it, and ingests it into the vector store.
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

    session_id = str(uuid.uuid4())
    upload_dir = f"data/decks/{session_id}"
    os.makedirs(upload_dir, exist_ok=True)

    # Sanitize filename by using a UUID, keep extension
    safe_filename = f"{uuid.uuid4()}{ext}"
    file_path = f"{upload_dir}/{safe_filename}"

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}") from e

    # Process synchronously for MVP (can be background task later)
    try:
        slides = extract_from_file(file_path)

        all_chunks = []
        for slide in slides:
            # Tag
            tags = tag_slide(slide)
            slide.tags = tags

            # Chunk
            chunks = chunk_slide(slide)

            # Add tags to chunk metadata
            for chunk in chunks:
                chunk.metadata["tags"] = tags

            all_chunks.extend(chunks)

        # Store
        store.add_chunks(all_chunks)

        return {
            "session_id": session_id,
            "filename": file.filename,
            "slide_count": len(slides),
            "status": "processed"
        }

    except Exception as e:
        # Cleanup on failure?
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}") from e

@router.get("/session/{session_id}/slides")
async def get_slides(session_id: str) -> list[dict[str, Any]]:
    """
    Retrieves the slides for a given session.
    """
    # For MVP, we'll re-parse the file or store slides in a JSON file.
    # Re-parsing is inefficient but easiest for now since we didn't store raw slides, only chunks.
    # Better approach: Store slides.json in the session directory.
    
    upload_dir = f"data/decks/{session_id}"
    if not os.path.exists(upload_dir):
        raise HTTPException(status_code=404, detail="Session not found")
        
    # Find the file
    files = os.listdir(upload_dir)
    if not files:
        raise HTTPException(status_code=404, detail="No deck found for session")
        
    file_path = os.path.join(upload_dir, files[0])
    
    try:
        slides = extract_from_file(file_path)
        return [asdict(s) for s in slides]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve slides: {str(e)}") from e
