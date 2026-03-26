"""
Tests for e2e_flow.
"""
import os
import shutil
import uuid
from typing import Any
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from backend.main import app
from backend.models.core import Challenge, Slide, ResearchDossier

client = TestClient(app)

@patch("backend.ingestion.router.uuid.uuid4")
@patch("backend.ingestion.processor.extract_from_file")
@patch("backend.ingestion.processor.chunk_slide")
@patch("backend.ingestion.processor.tag_slide")
@patch("backend.research.router.ChallengerRegistry")
@patch("backend.research.router.session_store")
@patch("backend.research.router.ChallengeGenerator")
@patch("backend.research.router.FactStore")
@patch("backend.research.router.DeckRetriever")
@patch("backend.research.agent.FactStore")
@patch("backend.ingestion.parser.extract_from_file")
def test_e2e_flow(
    mock_parser_extract: Any,
    mock_agent_fact_store: Any,
    mock_router_deck_retriever: Any,
    mock_router_fact_store: Any,
    mock_challenge_generator_cls: Any,
    mock_session_store: Any,
    mock_challenger_store_cls: Any,
    mock_tag: Any,
    mock_chunk: Any,
    mock_processor_extract: Any,
    mock_uuid: Any
) -> None:
    """
    Test the full flow:
    1. Upload Deck (Ingestion)
    2. Generate Research (Research)
    3. Generate Challenges (Challenges)
    """
    # Fix session ID
    session_id = "e2e_session"
    mock_uuid.return_value = MagicMock()
    mock_uuid.return_value.__str__.return_value = session_id
    
    # --- Step 1: Ingestion ---
    # Mock extraction for ingestion (processor uses extract_from_file)
    mock_slide = Slide(index=0, title="AI Slide", text="This is a slide about AI.", notes="", tags=[])
    mock_processor_extract.return_value = ([mock_slide], {})
    
    mock_tag.return_value = ["ai"]
    
    mock_chunk_obj = MagicMock()
    mock_chunk_obj.id = "chunk1"
    mock_chunk_obj.slide_index = 0  # Fix: Ensure this is an int, not a MagicMock
    mock_chunk_obj.text = "Chunk text"
    mock_chunk_obj.embedding = [0.1, 0.2, 0.3]
    mock_chunk_obj.metadata = {}
    mock_chunk.return_value = [mock_chunk_obj]
    
    # Create dummy file
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
        assert data["session_id"] == session_id
        
        # --- Step 2: Research ---
        # Mock extraction for research (it uses backend.ingestion.parser.extract_from_file)
        # This corresponds to mock_parser_extract
        mock_parser_extract.return_value = ([mock_slide], {})
        
        # Mock ResearchAgent
        with patch("backend.research.router.get_agent") as mock_get_agent:
            mock_agent = MagicMock()
            mock_agent.run.return_value = ResearchDossier(
                session_id=session_id,
                competitor_insights=["Insight 1"]
            )
            mock_get_agent.return_value = mock_agent
            
            response = client.post(f"/research/generate/{session_id}")
            assert response.status_code == 200
            dossier_data = response.json()
            assert dossier_data["session_id"] == session_id
        
        # Configure session store mock for precompute
        mock_session_store.get_dossier.return_value = ResearchDossier(
            session_id=session_id,
            competitor_insights=["Insight 1"]
        )
        
        # Configure challenger store mock
        mock_challenger_store = mock_challenger_store_cls.return_value
        mock_challenger_store.get_persona.return_value = MagicMock(id="skeptic")

        # --- Step 3: Challenges ---
        # Mock generator class instantiation
        mock_generator_instance = MagicMock()
        mock_generator_instance.generate_challenges.return_value = [
            Challenge(
                id="c1", 
                session_id=session_id, 
                persona_id="skeptic", 
                question="Q1", 
                ideal_answer="A1",
                difficulty="medium",
                evidence={"chunks": [], "facts": []},
                key_points=["K1"],
                tone="professional"
            )
        ]
        mock_challenge_generator_cls.return_value = mock_generator_instance
        
        response = client.post(
            f"/research/precompute/{session_id}",
            json={"persona_ids": ["skeptic"]}
        )
        if response.status_code != 200:
            print(f"Precompute failed: {response.text}")
        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "completed"
        
    finally:
        if os.path.exists("test.pdf"):
            os.remove("test.pdf")
        if os.path.exists(f"data/decks/{session_id}"):
            shutil.rmtree(f"data/decks/{session_id}")
