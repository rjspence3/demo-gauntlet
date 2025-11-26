from typing import List
from backend.models.core import Slide

# Simple keyword mapping
KEYWORD_MAP = {
    "architecture": ["architecture", "system", "component", "design", "scale", "performance"],
    "cost": ["cost", "price", "budget", "roi", "value", "expensive", "cheap"],
    "security": ["security", "secure", "compliance", "risk", "auth", "encryption", "gdpr", "soc2"],
    "integration": ["integration", "api", "connect", "middleware", "webhook"],
    "workflow": ["workflow", "process", "step", "automation"],
}

def tag_slide(slide: Slide) -> List[str]:
    """
    Tags a slide based on keywords in title and text.

    Args:
        slide: The slide to tag.

    Returns:
        List of tags.
    """
    tags = set()
    content = (slide.title + " " + slide.text + " " + slide.notes).lower()

    for tag, keywords in KEYWORD_MAP.items():
        for keyword in keywords:
            if keyword in content:
                tags.add(tag)
                break

    return list(tags)
