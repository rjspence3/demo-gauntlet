"""
Tests for session.
"""
import os
import shutil
from backend.models.session import SessionStore
from backend.models.core import ResearchDossier

def test_session_store() -> None:
    """Test saving and loading session data."""
    # test_dir cleanup removed as SessionStore uses DB
        
    store = SessionStore()
    session_id = "test_session"
    
    # Test Dossier
    dossier = ResearchDossier(session_id=session_id, competitor_insights=["Comp1"])
    store.save_dossier(session_id, dossier)
    
    loaded_dossier = store.get_dossier(session_id)
    assert loaded_dossier is not None
    assert loaded_dossier.session_id == session_id
    assert loaded_dossier.competitor_insights == ["Comp1"]
    
    # Test Deck Summary
    store.save_deck_summary(session_id, "Summary")
    summary = store.get_deck_summary(session_id)
    assert summary == "Summary"
    
    # Cleanup
    # Cleanup handled by in-memory DB teardown
