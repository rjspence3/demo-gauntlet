"""
API router for research-related endpoints.
"""
import asyncio
import os
from fastapi import APIRouter, HTTPException, Depends
from backend.logger import get_logger
from backend.research.agent import ResearchAgent
from backend.models.core import ResearchDossier
from backend.models.llm import create_llm_client, MockLLM, LLMClient
from backend.research.client import MockSearchClient, BraveSearchClient, SearchClient
from backend.config import config

from backend.models.session import SessionStore

router = APIRouter(prefix="/research", tags=["research"])
session_store = SessionStore()
logger = get_logger(__name__)

def get_agent() -> ResearchAgent:
    """Dependency provider for ResearchAgent. Prefers Anthropic; falls back to OpenAI."""
    try:
        llm: LLMClient = create_llm_client(
            anthropic_api_key=config.ANTHROPIC_API_KEY,
            openai_api_key=config.OPENAI_API_KEY,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=500,
            detail="No LLM API key configured. Set ANTHROPIC_API_KEY (preferred) or OPENAI_API_KEY."
        ) from exc

    search: SearchClient
    if config.BRAVE_API_KEY:
        search = BraveSearchClient(api_key=config.BRAVE_API_KEY)
    else:
        logger.warning("BRAVE_API_KEY not set, using mock search client")
        search = MockSearchClient()

    return ResearchAgent(llm_client=llm, search_client=search)

@router.post("/generate/{session_id}", response_model=ResearchDossier)
async def generate_research(session_id: str, agent: ResearchAgent = Depends(get_agent)) -> ResearchDossier:
    """
    Generates a research dossier for a given session.
    """
    try:
        # Load slides from session store (already parsed during ingestion)
        slides = session_store.get_slides(session_id)

        if slides:
            deck_title = slides[0].title if slides[0].title else "Demo Deck"
            all_tags: set = set()
            for s in slides:
                all_tags.update(s.tags)
            tags = list(all_tags) if all_tags else ["general"]
        else:
            logger.warning(f"No slides found for session {session_id}, using defaults")
            deck_title = "Demo Deck"
            tags = ["general"]
            slides = []

        dossier = await asyncio.to_thread(agent.run, session_id, deck_title, tags, slides)
        session_store.save_dossier(session_id, dossier)
        return dossier
    except Exception as e:
        logger.error(f"Research generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Research generation failed: {str(e)}") from e

from backend.challenges.generator import ChallengeGenerator
from backend.challenges.personas import ChallengerRegistry
from backend.models.store import DeckRetriever
from backend.models.fact_store import FactStore
from typing import List, Dict, Any
from pydantic import BaseModel

class PrecomputeRequest(BaseModel):
    """
    Request model for precomputing challenges.
    """
    persona_ids: List[str]

@router.post("/precompute/{session_id}")
async def precompute_challenges(
    session_id: str,
    request: PrecomputeRequest,
    agent: ResearchAgent = Depends(get_agent)
) -> Dict[str, Any]:
    """
    Precomputes challenges for the selected personas based on the deck and research.
    """
    try:
        dossier = session_store.get_dossier(session_id)
        if not dossier:
            dossier = ResearchDossier(session_id=session_id)

        slides = session_store.get_slides(session_id)
        if not slides:
            raise HTTPException(status_code=404, detail="Slides not found for session. Please ensure deck ingestion is complete.")

        registry = ChallengerRegistry()
        deck_retriever = DeckRetriever()
        fact_store = FactStore()

        generator = ChallengeGenerator(
            llm_client=agent.llm_client,
            deck_retriever=deck_retriever,
            fact_store=fact_store
        )

        all_challenges = []
        for p_id in request.persona_ids:
            persona = registry.get_persona(p_id)
            if not persona:
                logger.warning(f"Persona {p_id} not found in registry, skipping")
                continue

            challenges = await asyncio.to_thread(
                generator.generate_challenges,
                session_id=session_id,
                persona=persona,
                deck_context="",
                dossier=dossier,
                slides=slides
            )
            all_challenges.extend(challenges)

        session_store.save_challenges(session_id, all_challenges)
        return {"status": "completed", "count": len(all_challenges)}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Precompute failed: {str(e)}") from e
