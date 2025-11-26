from typing import Any
import os
import shutil
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

@patch("backend.ingestion.router.store")
@patch("backend.ingestion.router.extract_from_file")
def test_upload_deck(mock_extract: Any, mock_store: Any) -> None:
    """Test the upload deck endpoint."""
    # Mock extraction
    mock_slide = MagicMock()
    mock_slide.index = 0
    mock_slide.title = "Test Slide"
    mock_slide.text = "Test content."
    mock_slide.notes = ""
    mock_slide.tags = []

    mock_extract.return_value = [mock_slide]

    # Create a dummy file
    filename = "test_deck.pdf"
    with open(filename, "wb") as f:
        f.write(b"dummy content")

    try:
        with open(filename, "rb") as f:
            response = client.post(
                "/ingestion/upload",
                files={"file": (filename, f, "application/pdf")}
            )

        assert response.status_code == 200
        data = response.json()
        assert data["filename"] == filename
        assert data["slide_count"] == 1
        assert "session_id" in data

        # Verify store called
        mock_store.add_chunks.assert_called_once()

    finally:
        if os.path.exists(filename):
            os.remove(filename)
        # Cleanup created data dir
        if os.path.exists("data/decks"):
            shutil.rmtree("data/decks")
