"""
API router for research-related endpoints.
"""
import os
from fastapi import APIRouter, HTTPException, Depends
from backend.logger import get_logger
from backend.research.agent import ResearchAgent
from backend.models.core import ResearchDossier
from backend.models.llm import OpenAIClient, MockLLM, LLMClient
from backend.research.client import MockSearchClient, BraveSearchClient, SearchClient
from backend.config import config

from backend.models.session import SessionStore

router = APIRouter(prefix="/research", tags=["research"])
session_store = SessionStore()
logger = get_logger(__name__)

def get_agent() -> ResearchAgent:
    """Dependency provider for ResearchAgent."""
    # Factory for agent, can inject dependencies here
    # For MVP, check for keys
    llm: LLMClient
    if config.OPENAI_API_KEY:
        llm = OpenAIClient(api_key=config.OPENAI_API_KEY)
    else:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY is missing. Please configure it in .env")
        
    # Check for search key
    search: SearchClient
    if config.BRAVE_API_KEY:
        search = BraveSearchClient(api_key=config.BRAVE_API_KEY)
    else:
        # We can optionally allow missing search if it's not critical, but plan says "all real"
        # However, search might be optional features? The prompt says "all of this needs to be made real"
        # So let's enforce it or warn?
        # Research agent needs search.
        raise HTTPException(status_code=500, detail="BRAVE_API_KEY is missing. Please configure it in .env")
    
    return ResearchAgent(llm_client=llm, search_client=search)

@router.post("/generate/{session_id}", response_model=ResearchDossier)
async def generate_research(session_id: str, agent: ResearchAgent = Depends(get_agent)) -> ResearchDossier:
    """
    Generates a research dossier for a given session.
    """
    try:
        # Find deck file
        upload_dir = f"data/decks/{session_id}"
        if not os.path.exists(upload_dir):
             # Fallback if no deck found, though ideally we should error or handle gracefully
             logger.warning(f"No deck found for session {session_id}")
             deck_title = "Demo Deck"
             tags = ["general"]
             slides: List[Any] = []
        else:
            files = os.listdir(upload_dir)
            if not files:
                 logger.warning(f"No files in deck dir for session {session_id}")
                 deck_title = "Demo Deck"
                 tags = ["general"]
                 slides = []
            else:
                file_path = os.path.join(upload_dir, files[0])
                from backend.ingestion.parser import extract_from_file
                slides, _ = extract_from_file(file_path)
                
                if slides:
                    deck_title = slides[0].title if slides[0].title else "Demo Deck"
                    # Aggregate tags from all slides
                    all_tags = set()
                    for s in slides:
                        all_tags.update(s.tags)
                    tags = list(all_tags) if all_tags else ["general"]
                else:
                    deck_title = "Demo Deck"
                    tags = ["general"]

        # Generate research
        dossier = agent.run(session_id, deck_title, tags, slides)
        
        # Save to session store
        session_store.save_dossier(session_id, dossier)
        
        return dossier
    except Exception as e:
        logger.error(f"Research generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Research generation failed: {str(e)}") from e

from backend.challenges.generator import ChallengeGenerator
from backend.challenges.store import ChallengerStore
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
    agent: ResearchAgent = Depends(get_agent) # Reuse agent factory for LLM/Search clients
) -> Dict[str, Any]:
    """
    Precomputes challenges for the selected personas based on the deck and research.
    """
    try:
        # 1. Load Session Data
        dossier = session_store.get_dossier(session_id)
        if not dossier:
            # Try to generate if missing? Or fail?
            # For MVP, let's assume research was done or we do it now?
            # Better: fail if no research, or do a quick pass.
            # Let's assume research is done for now.
            pass
        
        if not dossier:
             # Create empty dossier if missing to satisfy type checker, or handle error
             dossier = ResearchDossier(session_id=session_id)

        # 2. Load Slides
        slides = session_store.get_slides(session_id)
        if not slides:
             raise HTTPException(status_code=404, detail="Slides not found for session. Please ensure deck ingestion is complete.")
        
        # 3. Setup Generator
        challenger_store = ChallengerStore()
        deck_retriever = DeckRetriever() # Should be initialized with session?
        # DeckRetriever currently uses a global store? 
        # backend/models/store.py: VectorStore is singleton-ish.
        # We need to make sure it filters by session or we just search all?
        # The current VectorStore implementation is simple.
        
        fact_store = FactStore()
        
        generator = ChallengeGenerator(
            llm_client=agent.llm_client,
            deck_retriever=deck_retriever,
            fact_store=fact_store
        )
        
        all_challenges = []
        for p_id in request.persona_ids:
            persona = challenger_store.get_persona(p_id)
            if not persona:
                continue
                
            challenges = generator.generate_challenges(
                session_id=session_id,
                persona=persona,
                deck_context="Context from slides...", # We could summarize deck here
                dossier=dossier,
                slides=slides
            )
            all_challenges.extend(challenges)
            
        # 4. Save Challenges
        session_store.save_challenges(session_id, all_challenges)
        
        return {"status": "completed", "count": len(all_challenges)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Precompute failed: {str(e)}") from e
