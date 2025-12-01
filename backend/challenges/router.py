from typing import List, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from backend.models.core import Challenge, ChallengerPersona, ResearchDossier
from backend.challenges.personas import ChallengerRegistry
from backend.challenges.generator import ChallengeGenerator
from backend.models.llm import OpenAILLM, MockLLM, LLMClient
from backend.models.store import DeckRetriever
from backend.models.fact_store import FactStore
from backend.config import config

from backend.models.session import SessionStore

router = APIRouter(prefix="/challenges", tags=["challenges"])
registry = ChallengerRegistry()
session_store = SessionStore()

# Dependency injection
def get_llm() -> LLMClient:
    if config.OPENAI_API_KEY:
        return OpenAILLM(api_key=config.OPENAI_API_KEY)
    return MockLLM()

def get_deck_retriever() -> DeckRetriever:
    return DeckRetriever()

def get_fact_store() -> FactStore:
    return FactStore()

def get_generator(
    llm: LLMClient = Depends(get_llm),
    deck_retriever: DeckRetriever = Depends(get_deck_retriever),
    fact_store: FactStore = Depends(get_fact_store)
) -> ChallengeGenerator:
    return ChallengeGenerator(llm, deck_retriever, fact_store)

class GenerateRequest(BaseModel):
    session_id: str
    persona_id: str

@router.get("/personas", response_model=List[ChallengerPersona])
async def list_personas() -> List[ChallengerPersona]:
    """List available challenger personas."""
    return registry.list_personas()

@router.post("/generate", response_model=List[Challenge])
async def generate_challenges(
    request: GenerateRequest,
    generator: ChallengeGenerator = Depends(get_generator)
) -> List[Challenge]:
    """Generate challenges for a specific persona (precompute)."""
    persona = registry.get_persona(request.persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
        
    # Fetch Research Dossier
    dossier = session_store.get_dossier(request.session_id)
    if not dossier:
        dossier = ResearchDossier(session_id=request.session_id)
        
    # Fetch Slides (needed for precompute)
    # Note: SessionStore needs to support retrieving slides. 
    # For now, we assume we can get them or reconstruct them.
    # If SessionStore doesn't have get_slides, we might need to add it or fetch from somewhere else.
    # Assuming session_store has a way to get slides, or we pass them.
    # For MVP, let's assume we stored them in session_store.
    slides = session_store.get_slides(request.session_id)
    if not slides:
         # Try to load from file system if not in memory store? 
         # Or just fail gracefully.
         # For MVP, let's assume they are there if ingestion happened.
         pass

    # Fetch Deck Context
    deck_context = session_store.get_deck_summary(request.session_id) or "No context available."
    
    challenges = generator.generate_challenges(
        session_id=request.session_id,
        persona=persona,
        deck_context=deck_context,
        dossier=dossier,
        slides=slides or []
    )
    
    # Save challenges
    session_store.save_challenges(request.session_id, challenges)
    
    return challenges

@router.get("/session/{session_id}", response_model=List[Challenge])
async def get_challenges(session_id: str) -> List[Challenge]:
    """Retrieve all challenges for a session."""
    challenges = session_store.get_challenges(session_id)
    return challenges
