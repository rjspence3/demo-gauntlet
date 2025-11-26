from typing import List
from backend.models.llm import LLMClient

def generate_queries(deck_title: str, tags: List[str], llm_client: LLMClient) -> List[str]:
    """
    Generates research queries based on deck context using LLM.

    Args:
        deck_title: Title of the deck.
        tags: List of tags associated with the deck.
        llm_client: LLM client instance.

    Returns:
        List of search queries.
    """
    prompt = f"""
    You are a research assistant. Generate 3-5 specific search queries to research the following topic for a sales demo gauntlet.
    Focus on: Competitors, Cost/Pricing, Security/Compliance, and Implementation Risks.

    Deck Title: {deck_title}
    Tags: {', '.join(tags)}

    Output JSON format:
    {{
        "queries": ["query 1", "query 2", ...]
    }}
    """

    response = llm_client.generate_json(prompt)
    return list(response.get("queries", []))
