import re
import uuid
from typing import List
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
                raw_chunks.append(f"Note: {sentence.strip()}")

    chunks = []
    for content in raw_chunks:
        chunks.append(Chunk(
            id=str(uuid.uuid4()),
            slide_index=slide.index,
            text=content,
            metadata={"title": slide.title}
        ))

    return chunks
