"""
API router for evaluation-related endpoints.
"""
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from backend.evaluation.engine import EvaluationEngine, EvaluationResult
from backend.models.core import Challenge
from backend.models.session import SessionStore
from backend.evaluation.reporting import ReportingEngine
from dataclasses import asdict

router = APIRouter(prefix="/evaluation", tags=["evaluation"])

# Singleton engine
engine = EvaluationEngine()

class ScoreRequest(BaseModel):
    """
    Request model for scoring an answer.
    """
    session_id: str
    persona_id: str
    challenge_id: str
    user_answer: str
    ideal_answer: Optional[str] = None # Optional now, we look it up

class ScoreResponse(BaseModel):
    """
    Response model for scoring result.
    """
    score: int
    feedback: str

@router.post("/score", response_model=ScoreResponse)
async def score_answer(request: ScoreRequest) -> ScoreResponse:
    """Score a user's answer to a challenge."""
    try:
        store = SessionStore()
        
        # Look up challenge for ideal answer
        challenge = store.get_challenge(request.session_id, request.challenge_id)
        ideal_answer = request.ideal_answer
        
        if challenge:
            ideal_answer = challenge.ideal_answer
        elif not ideal_answer:
            # If not found and not provided, we can't score accurately.
            # For backward compatibility or testing, we might allow it, but ideally error.
            # For now, if missing, use a generic fallback or error.
            raise HTTPException(status_code=404, detail="Challenge not found and no ideal answer provided")

        result = engine.evaluate(request.user_answer, ideal_answer)
        
        # Save interaction
        store.save_interaction(request.session_id, {
            "challenge_id": request.challenge_id,
            "persona_id": request.persona_id,
            "slide_index": challenge.slide_index if challenge else None,
            "user_answer": request.user_answer,
            "ideal_answer": ideal_answer,
            "score": result.score,
            "feedback": result.feedback
        })
        
        return ScoreResponse(score=result.score, feedback=result.feedback)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}") from e

@router.get("/report/{session_id}")
async def get_report(session_id: str) -> Dict[str, Any]:
    """Generate a report for the session."""
    store = SessionStore()
    reporting_engine = ReportingEngine(store)
    report = reporting_engine.generate_report(session_id)
    return asdict(report)
