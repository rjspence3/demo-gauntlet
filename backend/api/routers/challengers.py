"""
API router for managing challenger personas.
"""
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Body, Depends, Request
from backend.models.core import ChallengerPersona
from backend.challenges.store import ChallengerStore
from backend.limiter import limiter

# Assuming get_challenger_store is defined elsewhere or needs to be added
# For the purpose of making the provided snippet syntactically correct,
# we'll add a placeholder for get_challenger_store and get_db if they are new.
# If these functions already exist, this placeholder should be removed.
def get_challenger_store() -> ChallengerStore:
    """Dependency provider for ChallengerStore."""
    return ChallengerStore()

def get_db() -> Any:
    """Placeholder for database dependency."""
    pass

router = APIRouter(prefix="/challengers", tags=["challengers"])
# The original 'store = ChallengerStore()' is likely replaced by dependency injection.
# Keeping it commented out for context, but the new structure implies it's not directly used globally.
# store = ChallengerStore()

@router.get("/", response_model=List[ChallengerPersona])
@limiter.limit("20/minute")
async def list_challengers(request: Request, store: ChallengerStore = Depends(get_challenger_store)) -> List[ChallengerPersona]:
    """List all available challenger personas."""
    # The original snippet had -> Dict[str, Any], but response_model is List[ChallengerPersona].
    # To maintain consistency and syntactic correctness with the response_model,
    # the return type hint is adjusted to List[ChallengerPersona].
    return store.list_personas()

@router.post("/", response_model=ChallengerPersona)
@limiter.limit("5/minute")
async def create_challenger(request: Request, persona: ChallengerPersona, store: ChallengerStore = Depends(get_challenger_store)) -> ChallengerPersona:
    """Create a new challenger persona."""
    try:
        store.add_persona(persona)
        return persona
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{persona_id}", response_model=ChallengerPersona)
@limiter.limit("5/minute")
async def update_challenger(request: Request, persona_id: str, updates: Dict[str, Any] = Body(...), store: ChallengerStore = Depends(get_challenger_store)) -> ChallengerPersona:
    """Update an existing challenger persona."""
    updated = store.update_persona(persona_id, updates)
    if not updated:
        raise HTTPException(status_code=404, detail="Challenger not found")
    return updated
