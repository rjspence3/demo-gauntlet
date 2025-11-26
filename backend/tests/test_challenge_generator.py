from typing import Any
from unittest.mock import MagicMock
from backend.challenges.generator import ChallengeGenerator
from backend.models.core import ChallengerPersona, ResearchDossier, Challenge

def test_generate_challenges() -> None:
    """Test generating challenges."""
    mock_llm = MagicMock()
    mock_llm.generate_json.return_value = {
        "challenges": [
            {
                "question": "Q1",
                "context_source": "Slide 1",
                "difficulty": "hard"
            }
        ]
    }
    
    persona = ChallengerPersona(
        id="p1", name="P1", role="R1", style="S1", focus_areas=["F1"]
    )
    dossier = ResearchDossier(session_id="s1")
    
    generator = ChallengeGenerator(mock_llm)
    challenges = generator.generate_challenges(
        session_id="s1",
        persona=persona,
        deck_context="Deck Context",
        dossier=dossier
    )
    
    assert len(challenges) == 1
    assert challenges[0].question == "Q1"
    assert challenges[0].persona_id == "p1"
    mock_llm.generate_json.assert_called_once()
