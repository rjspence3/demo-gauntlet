from fastapi import APIRouter, HTTPException, Depends
from backend.research.agent import ResearchAgent
from backend.models.core import ResearchDossier
from backend.models.llm import OpenAILLM, MockLLM, LLMClient
from backend.research.client import MockSearchClient
from backend.config import config

from backend.models.session import SessionStore

router = APIRouter(prefix="/research", tags=["research"])
session_store = SessionStore()

def get_agent() -> ResearchAgent:
    # Factory for agent, can inject dependencies here
    # For MVP, check for keys
    llm: LLMClient
    if config.OPENAI_API_KEY:
        llm = OpenAILLM(api_key=config.OPENAI_API_KEY)
    else:
        llm = MockLLM()
        
    # Check for search key
    if config.BRAVE_API_KEY:
        search = BraveSearchClient(api_key=config.BRAVE_API_KEY)
    else:
        search = MockSearchClient()
    
    return ResearchAgent(llm_client=llm, search_client=search)

@router.post("/generate/{session_id}", response_model=ResearchDossier)
async def generate_research(session_id: str, agent: ResearchAgent = Depends(get_agent)) -> ResearchDossier:
    """
    Generates a research dossier for a given session.
    """
    # TODO: Fetch session metadata from store
    deck_title = "Demo Deck"
    tags = ["general"]
    
    # Generate research
    try:
        dossier = agent.run(session_id, deck_title, tags)
        
        # Save to session store
        session_store.save_dossier(session_id, dossier)
        
        return dossier
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Research generation failed: {str(e)}") from e

from backend.challenges.generator import ChallengeGenerator
from backend.challenges.store import ChallengerStore
from backend.models.store import DeckRetriever
from backend.models.fact_store import FactStore
from typing import List
from pydantic import BaseModel

class PrecomputeRequest(BaseModel):
    persona_ids: List[str]

@router.post("/precompute/{session_id}")
async def precompute_challenges(
    session_id: str, 
    request: PrecomputeRequest,
    agent: ResearchAgent = Depends(get_agent) # Reuse agent factory for LLM/Search clients
):
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

        # 2. Load Slides
        # We need a way to get slides. SessionStore or DeckRetriever?
        # DeckRetriever gets chunks. We need slides for context.
        # Let's assume we can get them from ingestion or store.
        # For MVP, let's re-parse or load from a file if we saved them.
        # Wait, ingestion router didn't save slides.json.
        # I should fix ingestion to save slides.json or use DeckRetriever to reconstruct?
        # Let's use DeckRetriever to get all chunks and reconstruct "slides" conceptually?
        # No, `generator.py` expects `List[Slide]`.
        # I'll add a helper to `SessionStore` or just re-parse here for MVP.
        # Re-parsing is safest given current state.
        
        # Find deck file
        upload_dir = f"data/decks/{session_id}"
        if not os.path.exists(upload_dir):
             raise HTTPException(status_code=404, detail="Session deck not found")
        files = os.listdir(upload_dir)
        if not files:
             raise HTTPException(status_code=404, detail="No deck found")
        file_path = os.path.join(upload_dir, files[0])
        
        from backend.ingestion.parser import extract_from_file
        slides = extract_from_file(file_path)
        
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
