"""
Tests for evaluation_api.
"""
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from backend.main import app
from backend.models.core import Challenge

client = TestClient(app)

def _make_challenge(ideal_answer: str) -> Challenge:
    return Challenge(
        id="c1", session_id="s1", persona_id="p1",
        question="How do you handle encryption?",
        ideal_answer=ideal_answer,
        difficulty="medium",
    )

def test_score_answer() -> None:
    """Test scoring endpoint."""
    with patch("backend.evaluation.router.SessionStore") as MockStore:
        mock_store = MockStore.return_value
        mock_store.get_challenge.return_value = _make_challenge("We use AES-256 encryption.")
        mock_store.save_interaction.return_value = None

        response = client.post(
            "/evaluation/score",
            json={
                "session_id": "s1",
                "persona_id": "p1",
                "challenge_id": "c1",
                "user_answer": "We use AES-256 encryption.",
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["score"] > 90
        assert "Excellent" in data["feedback"] or "Good" in data["feedback"]

def test_score_answer_weak() -> None:
    """Test scoring endpoint with weak answer."""
    with patch("backend.evaluation.router.SessionStore") as MockStore:
        mock_store = MockStore.return_value
        mock_store.get_challenge.return_value = _make_challenge("We use AES-256 encryption.")
        mock_store.save_interaction.return_value = None

        response = client.post(
            "/evaluation/score",
            json={
                "session_id": "s1",
                "persona_id": "p1",
                "challenge_id": "c1",
                "user_answer": "I don't know.",
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["score"] < 50
