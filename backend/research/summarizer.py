from typing import List
from backend.models.core import ResearchDossier
from backend.models.llm import LLMClient
from backend.research.client import SearchResult

def summarize_research(session_id: str, results: List[SearchResult],
                       llm_client: LLMClient) -> ResearchDossier:
    """
    Synthesizes search results into a structured dossier using LLM.

    Args:
        session_id: The session ID.
        results: List of search results.
        llm_client: LLM client instance.

    Returns:
        ResearchDossier object.
    """
    if not results:
        return ResearchDossier(session_id=session_id)

    context = "\n\n".join(
        [f"Source: {r.url}\nTitle: {r.title}\nSnippet: {r.snippet}" for r in results]
    )

    prompt = f"""
    You are a research analyst. Synthesize the following search results into a structured dossier for a sales demo gauntlet.

    Search Results:
    {context}

    Output JSON format:
    {{
        "competitor_insights": ["insight 1", ...],
        "cost_benchmarks": ["benchmark 1", ...],
        "compliance_notes": ["note 1", ...],
        "implementation_risks": ["risk 1", ...]
    }}
    """

    response = llm_client.generate_json(prompt)

    return ResearchDossier(
        session_id=session_id,
        competitor_insights=response.get("competitor_insights", []),
        cost_benchmarks=response.get("cost_benchmarks", []),
        compliance_notes=response.get("compliance_notes", []),
        implementation_risks=response.get("implementation_risks", []),
        sources=[r.url for r in results]
    )
