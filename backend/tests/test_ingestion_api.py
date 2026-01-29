"""
Tests for ingestion_api.
"""
from typing import Any
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from backend.main import app
from backend.models.core import Slide

client = TestClient(app)

@patch("backend.ingestion.router.SessionStore")
def test_get_slides(mock_store_cls: Any) -> None:
    """Test retrieving slides."""
    mock_store = mock_store_cls.return_value
    mock_store.get_slides.return_value = [
        Slide(index=0, title="S1", text="T1", notes="N1", tags=[])
    ]
    
    response = client.get("/ingestion/session/test_session/slides")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "S1"

@patch("backend.ingestion.router.SessionStore")
def test_get_slides_processing(mock_store_cls: Any) -> None:
    """Test retrieving slides when processing."""
    mock_store = mock_store_cls.return_value
    mock_store.get_slides.return_value = []
    mock_store.get_session_status.return_value = "processing"
    
    response = client.get("/ingestion/session/test_session/slides")
    assert response.status_code == 200
    assert response.json() == []

@patch("backend.ingestion.router.SessionStore")
def test_get_slides_no_session(mock_store_cls: Any) -> None:
    """Test retrieving slides for invalid session."""
    mock_store = mock_store_cls.return_value
    mock_store.get_slides.return_value = []
    mock_store.get_session_status.return_value = "unknown"
    
    response = client.get("/ingestion/session/invalid/slides")
    assert response.status_code == 404
