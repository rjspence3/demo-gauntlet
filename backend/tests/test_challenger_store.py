"""
Tests for challenger_store.
"""
import pytest
from typing import Any
from unittest.mock import patch
from sqlmodel import create_engine, SQLModel, Session
from backend.challenges.store import ChallengerStore
from backend.models.core import ChallengerPersona
from backend.models.db_models import DBChallengerPersona

@pytest.fixture(name="engine")
def fixture_engine():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    return engine

def test_challenger_store_crud(engine: Any) -> None:
    """Test CRUD operations for ChallengerStore."""
    
    # Patch the engine used by ChallengerStore
    with patch("backend.database.engine", engine):
        store = ChallengerStore()
        
        # 1. List (Empty)
        assert store.list_personas() == []
        
        # 2. Add
        persona = ChallengerPersona(
            id="p1", name="Test Persona", role="Tester", style="Strict", focus_areas=["Testing"]
        )
        store.add_persona(persona)
        
        personas = store.list_personas()
        assert len(personas) == 1
        assert personas[0].id == "p1"
        
        # 3. Get
        fetched = store.get_persona("p1")
        assert fetched is not None
        assert fetched.name == "Test Persona"
        
        # 4. Update
        store.update_persona("p1", {"name": "Updated Persona"})
        updated = store.get_persona("p1")
        assert updated is not None
        assert updated.name == "Updated Persona"
        
        # 5. Duplicate ID check
        with pytest.raises(ValueError):
            store.add_persona(persona)
