"""
API router for evaluation-related endpoints.
"""
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from backend.evaluation.engine import EvaluationEngine
from backend.models.session import SessionStore
from backend.evaluation.reporting import ReportingEngine
from backend.limiter import limiter
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
    # ideal_answer intentionally excluded: server looks it up from stored challenge

class ScoreResponse(BaseModel):
    """
    Response model for scoring result.
    """
    score: int
    feedback: str

@router.post("/score", response_model=ScoreResponse)
@limiter.limit("10/minute")
async def score_answer(request: Request, score_request: ScoreRequest) -> ScoreResponse:
    """Score a user's answer to a challenge."""
    try:
        store = SessionStore()

        # P1-8: Always look up ideal_answer server-side; never trust client-supplied value
        challenge = store.get_challenge(score_request.session_id, score_request.challenge_id)
        if not challenge:
            raise HTTPException(status_code=404, detail="Challenge not found")

        result = engine.evaluate(score_request.user_answer, challenge.ideal_answer)
        
        # Save interaction
        store.save_interaction(score_request.session_id, {
            "challenge_id": score_request.challenge_id,
            "persona_id": score_request.persona_id,
            "slide_index": challenge.slide_index,
            "user_answer": score_request.user_answer,
            "ideal_answer": challenge.ideal_answer,
            "score": result.score,
            "feedback": result.feedback,
            "breakdown": result.breakdown,
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
