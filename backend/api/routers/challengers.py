"""
API router for managing challenger personas.
"""
from typing import List, Dict, Any, Annotated
from fastapi import APIRouter, HTTPException, Body, Depends, Request
from backend.models.core import ChallengerPersona
from backend.challenges.store import ChallengerStore
from backend.limiter import limiter
from backend.api.deps import get_current_user
from backend.models.db_models import User

def get_challenger_store() -> ChallengerStore:
    """Dependency provider for ChallengerStore."""
    return ChallengerStore()

router = APIRouter(prefix="/challengers", tags=["challengers"])

@router.get("/", response_model=List[ChallengerPersona])
@limiter.limit("20/minute")
async def list_challengers(request: Request, store: ChallengerStore = Depends(get_challenger_store)) -> List[ChallengerPersona]:
    """List all available challenger personas."""
    return store.list_personas()

@router.post("/", response_model=ChallengerPersona)
@limiter.limit("5/minute")
async def create_challenger(
    request: Request,
    persona: ChallengerPersona,
    current_user: Annotated[User, Depends(get_current_user)],
    store: ChallengerStore = Depends(get_challenger_store)
) -> ChallengerPersona:
    """Create a new challenger persona."""
    try:
        store.add_persona(persona)
        return persona
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{persona_id}", response_model=ChallengerPersona)
@limiter.limit("5/minute")
async def update_challenger(
    request: Request,
    persona_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    updates: Dict[str, Any] = Body(...),
    store: ChallengerStore = Depends(get_challenger_store)
) -> ChallengerPersona:
    """Update an existing challenger persona."""
    updated = store.update_persona(persona_id, updates)
    if not updated:
        raise HTTPException(status_code=404, detail="Challenger not found")
    return updated
