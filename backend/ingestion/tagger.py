from typing import List
from backend.models.core import Slide

# Simple keyword mapping
KEYWORD_MAP = {
    "architecture": ["architecture", "system", "component", "design", "scale", "performance", "microservices", "cloud", "on-prem", "hybrid"],
    "cost": ["cost", "price", "budget", "roi", "value", "expensive", "cheap", "license", "tco", "opex", "capex"],
    "security": ["security", "secure", "compliance", "risk", "auth", "encryption", "gdpr", "soc2", "hipaa", "iso", "penetration", "vulnerability"],
    "integration": ["integration", "api", "connect", "middleware", "webhook", "rest", "soap", "graphql", "legacy", "erp", "crm"],
    "workflow": ["workflow", "process", "step", "automation", "efficiency", "manual", "bottleneck"],
    "ai": ["ai", "ml", "artificial intelligence", "machine learning", "genai", "llm", "model", "training"],
    "data": ["data", "analytics", "reporting", "dashboard", "insight", "warehouse", "lake", "pipeline"],
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
