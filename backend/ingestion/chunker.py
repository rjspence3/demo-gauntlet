"""
Module for chunking slides into smaller text units.
"""
import re
import uuid
from typing import List, Dict, Any
from backend.models.core import Slide, Chunk

def chunk_slide(slide: Slide) -> List[Chunk]:
    """
    Splits a slide into smaller chunks based on bullets and sentences.

    Args:
        slide: The slide to chunk.

    Returns:
        List of Chunk objects.
    """
    text = slide.text
    raw_chunks = []

    # Split by newlines first (often bullets or paragraphs)
    lines = text.split('\n')

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Check for bullet points
        if line.startswith('•') or line.startswith('- '):
            clean_line = line.lstrip('•- ').strip()
            if clean_line:
                raw_chunks.append(clean_line)
        else:
            # Split by sentence boundaries if it's a long paragraph
            # Simple regex for sentence splitting
            sentences = re.split(r'(?<=[.!?])\s+', line)
            for sentence in sentences:
                if sentence.strip():
                    raw_chunks.append(sentence.strip())

    # Also chunk notes if present
    if slide.notes:
        notes_sentences = re.split(r'(?<=[.!?])\s+', slide.notes)
        for sentence in notes_sentences:
            if sentence.strip():
                # Prefix notes so we can distinguish them, but for span finding this is tricky.
                # Notes are separate from slide.text.
                # We will store notes chunks but they won't have spans in slide.text.
                raw_chunks.append(f"Note: {sentence.strip()}")

    MAX_CHUNK_SIZE = 1000 # Characters
    
    final_chunks = []
    for content in raw_chunks:
        if len(content) > MAX_CHUNK_SIZE:
            # Split large chunks
            for i in range(0, len(content), MAX_CHUNK_SIZE):
                final_chunks.append(content[i:i + MAX_CHUNK_SIZE])
        else:
            final_chunks.append(content)

    chunks = []
    
    # Track search position to handle duplicate phrases correctly
    search_start_index = 0
    
    for content in final_chunks:
        metadata: Dict[str, Any] = {"title": slide.title}
        
        # Try to find span in slide.text
        # Note: This is imperfect if content was modified (e.g. bullets removed).
        # But we stripped bullets from content, so we search for content in text.
        
        # If it's a note, skip span finding in slide.text
        if content.startswith("Note: "):
             # Could add span in notes if we wanted, but for now just skip
             # Could add span in notes if we wanted, but for now just skip
             # logger.debug(f"Skipping span finding for note chunk: {content[:20]}...")
             pass
        else:
            start_index = text.find(content, search_start_index)
            if start_index != -1:
                end_index = start_index + len(content)
                metadata["start_index"] = start_index
                metadata["end_index"] = end_index
                # Update search start so next search is after this one
                # But be careful if chunks are out of order? 
                # Our chunking order preserves text order, so this is safe.
                search_start_index = end_index
        
        chunks.append(Chunk(
            id=str(uuid.uuid4()),
            slide_index=slide.index,
            text=content,
            metadata=metadata
        ))

    return chunks
