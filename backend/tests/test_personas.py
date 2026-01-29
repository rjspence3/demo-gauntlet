"""
Tests for personas.
"""
from typing import Any
from backend.challenges.personas import ChallengerRegistry
from backend.models.core import ChallengerPersona

def test_registry_defaults() -> None:
    """Test that default personas are loaded."""
    registry = ChallengerRegistry()
    personas = registry.list_personas()
    assert len(personas) > 0
    
    ids = [p.id for p in personas]
    assert "skeptic" in ids
    assert "budget_hawk" in ids

def test_get_persona() -> None:
    """Test retrieving a specific persona."""
    registry = ChallengerRegistry()
    persona = registry.get_persona("skeptic")
    assert persona is not None
    assert persona.name == "The Skeptic"

def test_get_invalid_persona() -> None:
    """Test retrieving a non-existent persona."""
    registry = ChallengerRegistry()
    persona = registry.get_persona("invalid")
    assert persona is None
