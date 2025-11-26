from backend.models.core import Slide
from backend.ingestion.tagger import tag_slide

def test_tag_slide_keywords() -> None:
    """Test tagging based on keywords."""
    text = "This architecture is scalable and secure."
    slide = Slide(index=0, title="Arch", text=text)

    tags = tag_slide(slide)

    assert "architecture" in tags
    assert "security" in tags
    assert "cost" not in tags

def test_tag_slide_title() -> None:
    """Test tagging based on title."""
    slide = Slide(index=1, title="Cost Analysis", text="Numbers here.")

    tags = tag_slide(slide)

    assert "cost" in tags
