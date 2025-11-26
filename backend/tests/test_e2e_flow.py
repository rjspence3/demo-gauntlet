import os
import shutil
from typing import Any
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from backend.main import app
from backend.models.session import SessionStore

client = TestClient(app)

# Use a separate test directory for session store to avoid polluting real data
TEST_SESSION_DIR = "./data/test_e2e_sessions"

@patch("backend.ingestion.router.store")
@patch("backend.ingestion.router.extract_from_file")
@patch("backend.ingestion.router.chunk_slide")
@patch("backend.ingestion.router.tag_slide")
@patch("backend.research.router.session_store")
@patch("backend.challenges.router.session_store")
@patch("backend.challenges.router.vector_store")
def test_e2e_flow(
    mock_vector_store: Any,
    mock_challenges_session_store: Any,
    mock_research_session_store: Any,
    mock_tag: Any,
    mock_chunk: Any,
    mock_extract: Any,
    mock_ingestion_store: Any
) -> None:
    """
    Test the full flow:
    1. Upload Deck (Ingestion)
    2. Generate Research (Research)
    3. Generate Challenges (Challenges)
    """
    session_id = "e2e_session"
    
    # --- Step 1: Ingestion ---
    mock_slide = MagicMock()
    mock_slide.text = "This is a slide about AI."
    mock_slide.title = "AI Slide"
    mock_extract.return_value = [mock_slide]
    
    mock_tag.return_value = ["ai"]
    
    mock_chunk_obj = MagicMock()
    mock_chunk_obj.text = "Chunk text"
    mock_chunk_obj.metadata = {}
    mock_chunk.return_value = [mock_chunk_obj]
    
    # Mock file upload
    with open("test.pdf", "wb") as f:
        f.write(b"dummy pdf content")
        
    try:
        with open("test.pdf", "rb") as f:
            response = client.post(
                "/ingestion/upload",
                files={"file": ("test.pdf", f, "application/pdf")}
            )
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        # In a real scenario, we'd capture the session_id here. 
        # For this test, we'll force our known session_id or just verify the flow.
        
        # --- Step 2: Research ---
        # Mock session store for research
        real_store = SessionStore(base_path=TEST_SESSION_DIR)
        mock_research_session_store.save_dossier.side_effect = real_store.save_dossier
        
        response = client.post(f"/research/generate/{session_id}")
        assert response.status_code == 200
        dossier_data = response.json()
        assert dossier_data["session_id"] == session_id
        
        # Verify it was saved
        saved_dossier = real_store.get_dossier(session_id)
        assert saved_dossier is not None
        
        # --- Step 3: Challenges ---
        # Mock session store for challenges (read from the same real store)
        mock_challenges_session_store.get_dossier.side_effect = real_store.get_dossier
        mock_challenges_session_store.get_deck_summary.return_value = "Deck Summary"
        
        # Mock vector store query
        mock_chunk = MagicMock()
        mock_chunk.text = "Vector store context"
        mock_vector_store.query_similar.return_value = [mock_chunk]
        
        # Mock generator via dependency override
        from backend.challenges.router import get_generator
        from backend.models.core import Challenge
        
        mock_generator = MagicMock()
        mock_generator.generate_challenges.return_value = [
            Challenge(
            id="c1", 
            session_id="s1", 
            persona_id="skeptic", 
            question="Q1", 
            ideal_answer="A1",
            context_source="src", 
            difficulty="medium"
        )
        ]
        app.dependency_overrides[get_generator] = lambda: mock_generator
        
        try:
            response = client.post(
                "/challenges/generate",
                json={"session_id": session_id, "persona_id": "skeptic"}
            )
            assert response.status_code == 200
            challenges = response.json()
            assert len(challenges) > 0
            assert challenges[0]["persona_id"] == "skeptic"
        finally:
            app.dependency_overrides = {}
        
    finally:
        if os.path.exists("test.pdf"):
            os.remove("test.pdf")
        if os.path.exists(TEST_SESSION_DIR):
            shutil.rmtree(TEST_SESSION_DIR)
