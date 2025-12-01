import uuid
from typing import List
from backend.models.core import ResearchDossier, Fact
from backend.models.llm import LLMClient
from backend.research.client import SearchResult

def summarize_research(session_id: str, results: List[SearchResult],
                       llm_client: LLMClient) -> ResearchDossier:
    """
    Synthesizes search results into a structured dossier using LLM.
    """
    if not results:
        return ResearchDossier(session_id=session_id)

    context = "\n\n".join(
        [f"Source: {r.url}\nTitle: {r.title}\nSnippet: {r.snippet}" for r in results]
    )

    prompt = f"""
    You are a research analyst. Synthesize the following search results into a structured dossier for a sales demo gauntlet.
    
    Extract specific, grounded facts from the search results. Each fact must be directly supported by a source.
    
    Search Results:
    {context}

    Output JSON format:
    {{
        "competitor_insights": ["insight 1", ...],
        "cost_benchmarks": ["benchmark 1", ...],
        "compliance_notes": ["note 1", ...],
        "implementation_risks": ["risk 1", ...],
        "facts": [
            {{
                "topic": "pricing/integration/security/competitor",
                "text": "The specific fact text...",
                "source_url": "url from results",
                "source_title": "title from results",
                "domain": "domain from results",
                "snippet": "relevant snippet..."
            }}
        ]
    }}
    """

    response = llm_client.generate_json(prompt)
    
    facts = []
    raw_facts = response.get("facts", [])
    for rf in raw_facts:
        facts.append(Fact(
            id=str(uuid.uuid4()),
            topic=rf.get("topic", "general"),
            text=rf.get("text", ""),
            source_url=rf.get("source_url", ""),
            source_title=rf.get("source_title", ""),
            domain=rf.get("domain", ""),
            snippet=rf.get("snippet", "")
        ))

    return ResearchDossier(
        session_id=session_id,
        competitor_insights=response.get("competitor_insights", []),
        cost_benchmarks=response.get("cost_benchmarks", []),
        compliance_notes=response.get("compliance_notes", []),
        implementation_risks=response.get("implementation_risks", []),
        sources=[r.url for r in results],
        facts=facts
    )
