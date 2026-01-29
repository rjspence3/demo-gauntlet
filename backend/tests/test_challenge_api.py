"""
Tests for challenge_api.
"""
from typing import Any
from unittest.mock import MagicMock, patch, ANY
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

from backend.challenges.router import get_generator

@patch("backend.challenges.router.registry")
@patch("backend.challenges.router.session_store")
def test_generate_challenges_endpoint(mock_session_store: Any, mock_registry: Any) -> None:
    """Test the challenge generation endpoint."""
    # Mock Registry
    mock_persona = MagicMock()
    mock_persona.id = "p1"
    mock_registry.get_persona.return_value = mock_persona
    
    # Mock Session Store
    mock_session_store.get_dossier.return_value = MagicMock()
    mock_session_store.get_slides.return_value = [MagicMock()]
    
    # Mock Generator
    mock_generator = MagicMock()
    from backend.models.core import Challenge
    mock_generator.generate_challenges.return_value = [
        Challenge(
            id="c1", 
            session_id="s1", 
            persona_id="p1", 
            question="Q1", 
            ideal_answer="A1",
            difficulty="medium"
        )
    ]
    
    # Override dependency
    app.dependency_overrides[get_generator] = lambda: mock_generator
    
    try:
        # Test with correct request body
        response = client.post(
            "/challenges/generate",
            json={
                "session_id": "s1", 
                "persona_id": "p1"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["question"] == "Q1"
        
        # Verify generator was called with correct args
        mock_generator.generate_challenges.assert_called_with(
            session_id="s1",
            persona=mock_persona,
            deck_context=ANY, 
            dossier=ANY,
            slides=ANY
        )
    finally:
        app.dependency_overrides = {}

def test_list_personas_endpoint() -> None:
    """Test listing personas."""
    response = client.get("/challenges/personas")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert "id" in data[0]
    assert "name" in data[0]
