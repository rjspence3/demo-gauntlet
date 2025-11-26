from typing import Any
from unittest.mock import MagicMock, patch, ANY
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

from backend.challenges.router import get_generator

@patch("backend.challenges.router.registry")
def test_generate_challenges_endpoint(mock_registry: Any) -> None:
    """Test the challenge generation endpoint."""
    # Mock Registry
    mock_persona = MagicMock()
    mock_persona.id = "p1"
    mock_registry.get_persona.return_value = mock_persona
    
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
            context_source="src", 
            difficulty="medium"
        )
    ]
    
    # Override dependency
    app.dependency_overrides[get_generator] = lambda: mock_generator
    
    try:
        # Test with slide index
        response = client.post(
            "/challenges/generate",
            json={
                "session_id": "s1", 
                "persona_id": "p1",
                "slide_index": 0,
                "slide_content": "Slide content"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["question"] == "Q1"
        
        # Verify generator was called with slide info
        mock_generator.generate_challenges.assert_called_with(
            session_id="s1",
            persona=mock_persona,
            deck_context=ANY, 
            dossier=ANY,
            slide_content="Slide content",
            slide_index=0
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
