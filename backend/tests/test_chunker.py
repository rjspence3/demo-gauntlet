from backend.models.core import Slide
from backend.ingestion.chunker import chunk_slide

def test_chunk_slide_bullets() -> None:
    """Test chunking a slide with bullet points."""
    text = "• Point 1\n• Point 2\n• Point 3"
    slide = Slide(index=0, title="Bullets", text=text)

    chunks = chunk_slide(slide)

    assert len(chunks) == 3
    assert chunks[0].text == "Point 1"
    assert chunks[1].text == "Point 2"
    assert chunks[2].text == "Point 3"

def test_chunk_slide_sentences() -> None:
    """Test chunking a slide with sentences."""
    text = "This is sentence 1. This is sentence 2. This is sentence 3."
    slide = Slide(index=1, title="Sentences", text=text)

    chunks = chunk_slide(slide)

    assert len(chunks) == 3
    assert "This is sentence 1." in chunks[0].text
    assert "This is sentence 2." in chunks[1].text

def test_chunk_slide_mixed() -> None:
    """Test chunking mixed content."""
    text = "Intro text.\n• Bullet 1\n• Bullet 2"
    slide = Slide(index=2, title="Mixed", text=text)

    chunks = chunk_slide(slide)

    assert len(chunks) == 3
    assert chunks[0].text == "Intro text."
    assert chunks[1].text == "Bullet 1"
