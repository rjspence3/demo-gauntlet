"""
Module for generating research queries using LLM.
"""
from typing import List, Any, Optional
from backend.models.llm import LLMClient

def generate_queries(deck_title: str, tags: list[str], llm_client: LLMClient, slides: Optional[list[Any]] = None) -> list[str]:
    """
    Generates research queries based on deck context using LLM.

    Args:
        deck_title: Title of the deck.
        tags: List of tags associated with the deck.
        llm_client: LLM client instance.
        slides: Optional list of Slide objects.

    Returns:
        List of search queries.
    """
    context_str = ""
    if slides:
        # Extract text from first few slides or all if small
        # For now, let's take the first 5 slides' text
        preview = slides[:5]
        context_str = "\n".join([f"Slide {s.index}: {s.title}\n{s.text}" for s in preview])
    
    prompt = f"""
    You are a research assistant. Generate 3-5 specific search queries to research the following topic for a sales demo gauntlet.
    Focus on: Competitors, Cost/Pricing, Security/Compliance, and Implementation Risks.

    Deck Title: {deck_title}
    Tags: {', '.join(tags)}
    
    Deck Content Preview:
    {context_str}

    Output JSON format:
    {{
        "queries": ["query 1", "query 2", ...]
    }}
    """

    response = llm_client.complete_structured(prompt)
    return list(response.get("queries", []))
