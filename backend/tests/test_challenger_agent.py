"""
Tests for challenger_agent.
"""
from typing import Any
from unittest.mock import MagicMock
from backend.challenges.implementations import BaseChallenger
from backend.models.core import ChallengerPersona, Challenge, EvaluationResult

def test_evaluate_response() -> None:
    """Test the evaluate_response method."""
    persona = ChallengerPersona(
        id="p1", name="P1", role="R1", style="S1", focus_areas=["F1"], agent_prompt="Prompt"
    )
    agent = BaseChallenger(persona)
    
    mock_llm = MagicMock()
    mock_llm.complete_structured.return_value = {
        "score": 85,
        "feedback": "Good job",
        "accuracy_assessment": "Accurate",
        "completeness_assessment": "Complete",
        "tone_assessment": "Professional"
    }
    
    challenge = Challenge(
        id="c1", session_id="s1", persona_id="p1", 
        question="Q1", ideal_answer="A1", difficulty="medium"
    )
    
    evaluation = agent.evaluate_response(challenge, "User Answer", mock_llm)
    
    assert isinstance(evaluation, EvaluationResult)
    assert evaluation.score == 85
    assert evaluation.feedback == "Good job"
    mock_llm.complete_structured.assert_called_once()
