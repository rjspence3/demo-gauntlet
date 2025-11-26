from typing import List, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from backend.models.core import Challenge, ChallengerPersona, ResearchDossier
from backend.challenges.personas import ChallengerRegistry
from backend.challenges.generator import ChallengeGenerator
from backend.models.llm import OpenAILLM, MockLLM, LLMClient
from backend.config import config

from backend.models.session import SessionStore
from backend.ingestion.router import store as vector_store

router = APIRouter(prefix="/challenges", tags=["challenges"])
registry = ChallengerRegistry()
session_store = SessionStore()

class GenerateRequest(BaseModel):
    session_id: str
    persona_id: str
    slide_index: Optional[int] = None
    slide_content: Optional[str] = None

def get_generator() -> ChallengeGenerator:
    llm: LLMClient
    if config.OPENAI_API_KEY:
        llm = OpenAILLM(api_key=config.OPENAI_API_KEY)
    else:
        llm = MockLLM()
    return ChallengeGenerator(llm_client=llm)

@router.get("/personas", response_model=List[ChallengerPersona])
async def list_personas() -> List[ChallengerPersona]:
    """List available challenger personas."""
    return registry.list_personas()

@router.post("/generate", response_model=List[Challenge])
async def generate_challenges(
    request: GenerateRequest,
    generator: ChallengeGenerator = Depends(get_generator)
) -> List[Challenge]:
    """Generate challenges for a specific persona."""
    persona = registry.get_persona(request.persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
        
    # Fetch Research Dossier
    dossier = session_store.get_dossier(request.session_id)
    if not dossier:
        # Fallback if no research done yet
        dossier = ResearchDossier(session_id=request.session_id)
        
    # Fetch Deck Context (Naive approach: get first few chunks or search for summary)
    # For MVP, we'll try to get a summary if we stored one, or just query generic terms
    deck_context = session_store.get_deck_summary(request.session_id)
    if not deck_context:
        # Fallback: Query vector store for "summary" or "overview"
        chunks = vector_store.query_similar("executive summary overview", n=3)
        deck_context = "\n".join([c.text for c in chunks])
    
    challenges = generator.generate_challenges(
        session_id=request.session_id,
        persona=persona,
        deck_context=deck_context,
        dossier=dossier,
        slide_content=request.slide_content,
        slide_index=request.slide_index
    )
    
    # Save challenges for scoring integrity
    session_store.save_challenges(request.session_id, challenges)
    
    return challenges
