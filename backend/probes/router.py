"""
API router for synthetic personhood probe endpoints.
"""
import asyncio
from dataclasses import asdict
from fastapi import APIRouter, HTTPException
from backend.models.llm import create_llm_client
from backend.config import config
from backend.probes.runner import run_full_probe_suite
from backend.probes.config import ENHANCED_PERSONAS

router = APIRouter(prefix="/probes", tags=["probes"])

@router.get("/agents")
async def list_probeable_agents() -> list:
    """List agent IDs that can be probed."""
    return list(ENHANCED_PERSONAS.keys())

@router.post("/run/{agent_id}")
async def run_probes(agent_id: str) -> dict:
    """
    Run the full synthetic personhood probe suite against a challenger agent.

    Returns a scorecard with scores across five dimensions:
    cognitive latency, episodic memory, linguistic imperfection,
    emotional coherence, and task friction.
    """
    if agent_id not in ENHANCED_PERSONAS:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown agent '{agent_id}'. Available: {list(ENHANCED_PERSONAS.keys())}"
        )

    if not config.ANTHROPIC_API_KEY and not config.OPENAI_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="No LLM API key configured. Set ANTHROPIC_API_KEY (preferred) or OPENAI_API_KEY."
        )

    try:
        llm = create_llm_client(
            anthropic_api_key=config.ANTHROPIC_API_KEY,
            openai_api_key=config.OPENAI_API_KEY,
        )
        scorecard = await asyncio.to_thread(run_full_probe_suite, agent_id, llm)
        return asdict(scorecard)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Probe run failed: {str(e)}") from e
