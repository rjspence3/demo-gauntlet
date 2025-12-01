from typing import List
from fastapi import APIRouter, HTTPException, Body
from backend.models.core import ChallengerPersona
from backend.challenges.store import ChallengerStore

router = APIRouter(prefix="/challengers", tags=["challengers"])
store = ChallengerStore()

@router.get("/", response_model=List[ChallengerPersona])
async def list_challengers():
    return store.list_personas()

@router.post("/", response_model=ChallengerPersona)
async def create_challenger(persona: ChallengerPersona):
    try:
        store.add_persona(persona)
        return persona
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{persona_id}", response_model=ChallengerPersona)
async def update_challenger(persona_id: str, updates: dict = Body(...)):
    updated = store.update_persona(persona_id, updates)
    if not updated:
        raise HTTPException(status_code=404, detail="Challenger not found")
    return updated
