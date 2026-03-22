import logging
import os
from typing import Any, Dict
from backend.ingestion.parser import extract_from_file
from backend.ingestion.chunker import chunk_slide
from backend.ingestion.tagger import tag_slide
from backend.models.store import VectorStore
from backend.models.session import SessionStore
from backend.models.core import Slide

logger = logging.getLogger(__name__)

import asyncio
from concurrent.futures import ThreadPoolExecutor

async def process_deck_upload_task(ctx: Dict[str, Any], file_path: str, session_id: str) -> None:
    """
    Arq task to process an uploaded deck.
    """
    logger.info(f"Starting processing for session {session_id} with file ref {file_path}")
    
    local_path = None
    try:
        # Initialize stores
        vector_store = VectorStore()
        session_store = SessionStore()
        
        # Get local file path from blob storage
        from backend.services.blob_storage import get_blob_storage
        blob_storage = get_blob_storage()
        local_path = blob_storage.get_file_path(file_path)
        
        # Run heavy extraction in thread pool
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor() as pool:
            slides, metadata = await loop.run_in_executor(pool, extract_from_file, local_path)
            logger.info(f"Extracted {len(slides)} slides for session {session_id}")
            
            all_chunks = []
            processed_slides = []
            
            for slide in slides:
                # Tag
                tags = await loop.run_in_executor(pool, tag_slide, slide)
                slide.tags = tags
                
                # Chunk
                chunks = await loop.run_in_executor(pool, chunk_slide, slide)
                
                # Add tags to chunk metadata
                for chunk in chunks:
                    chunk.metadata["tags"] = ", ".join(tags)
                    
                all_chunks.extend(chunks)
                processed_slides.append(slide)
            
            # Store Chunks (VectorStore might be sync or async, assuming sync for now so run in executor)
            # If VectorStore uses HTTP client it might be better to use async, but Chroma client is sync by default?
            # The DeckRetriever uses chromadb.HttpClient which is sync.
            await loop.run_in_executor(pool, vector_store.add_chunks, all_chunks, session_id)
            
            # Store Slides
            await loop.run_in_executor(pool, session_store.save_slides, session_id, processed_slides)
            
            # Update Status
            await loop.run_in_executor(pool, session_store.update_session_status, session_id, "completed")
        
        logger.info(f"Completed processing for session {session_id}")
        
    except Exception as e:
        logger.error(f"Error processing deck for session {session_id}: {str(e)}", exc_info=True)
        try:
            session_store = SessionStore()
            # We can run this directly as it's just a DB update, but consistent to use executor if sync
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, session_store.update_session_status, session_id, "failed")
        except Exception as update_error:
            logger.error(f"Failed to update session status to failed for {session_id}: {update_error}")
    finally:
        if local_path and os.path.exists(local_path) and local_path != file_path:
            try:
                os.unlink(local_path)
            except Exception as e:
                logger.warning(f"Failed to cleanup temp file {local_path}: {e}")
