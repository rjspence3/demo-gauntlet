"""
Tests for upload_flow.
"""
from typing import Any
import os
import shutil
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

@patch("backend.services.blob_storage.get_blob_storage")
def test_upload_deck(mock_get_blob: Any) -> None:
    """Test the upload deck endpoint."""
    # Mock Blob Storage
    mock_blob = MagicMock()
    mock_blob.save_upload.return_value = "test_deck.pdf"
    mock_get_blob.return_value = mock_blob

    # Mock Arq Pool
    mock_pool = MagicMock()
    mock_pool.enqueue_job = MagicMock()
    # Make it awaitable
    async def async_enqueue(*args, **kwargs):
        return
    mock_pool.enqueue_job.side_effect = async_enqueue
    app.state.arq_pool = mock_pool

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
        assert data["status"] == "processing"
        assert "session_id" in data

        # Verify enqueue called
        mock_pool.enqueue_job.assert_called_once()
        
    finally:
        if os.path.exists(filename):
            os.remove(filename)
        # Cleanup created data dir
        if os.path.exists("data/decks"):
            shutil.rmtree("data/decks")
