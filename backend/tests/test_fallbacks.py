"""
Tests for fallbacks.
"""
from unittest.mock import MagicMock, patch
from backend.research.agent import ResearchAgent
from backend.challenges.generator import ChallengeGenerator
from backend.config import config
from backend.models.core import ChallengerPersona

def test_research_fallback_config() -> None:
    """Test research disabled by config."""
    # We need to patch config.ENABLE_RESEARCH
    with patch("backend.config.config.ENABLE_RESEARCH", False):
        agent = ResearchAgent()
        dossier = agent.run("s1", "Deck", ["tag"])
        assert dossier.competitor_insights == ["Research disabled."]

def test_research_fallback_exception() -> None:
    """Test research fallback on exception."""
    mock_llm = MagicMock()
    mock_search = MagicMock()
    mock_search.search.side_effect = Exception("Search failed")
    
    # We need to patch generate_queries to return something so search is called
    with patch("backend.research.agent.generate_queries", return_value=["q1"]):
        agent = ResearchAgent(llm_client=mock_llm, search_client=mock_search)
        dossier = agent.run("s1", "Deck", ["tag"])
        assert dossier.competitor_insights == []

def test_challenge_fallback_exception() -> None:
    """Test challenge fallback on exception."""
    mock_llm = MagicMock()
    mock_llm.complete_structured.side_effect = Exception("LLM failed")
    
    mock_retriever = MagicMock()
    mock_fact_store = MagicMock()
    
    generator = ChallengeGenerator(llm_client=mock_llm, deck_retriever=mock_retriever, fact_store=mock_fact_store)
    persona = ChallengerPersona(id="p1", name="P1", role="Role", style="Style", focus_areas=["tag"], domain_tags=["tag"])
    
    # Mock slide with tag matching persona
    mock_slide = MagicMock()
    mock_slide.index = 0
    mock_slide.tags = ["tag"]
    mock_slide.title = "Title"
    mock_slide.text = "Text"
    
    challenges = generator.generate_challenges(
        session_id="s1",
        persona=persona,
        deck_context="Context",
        dossier=MagicMock(),
        slides=[mock_slide]
    )
    
    # Since we catch exceptions in implementations.py and log error, we might get 0 challenges if it fails.
    # But wait, implementations.py catches exception and logs error, returns empty list?
    # Yes: except Exception as e: logger.error...
    # So we expect 0 challenges if LLM fails, unless there's a fallback mechanism in generator?
    # generator.py calls agent.precompute_challenges.
    # implementations.py catches exception inside loop.
    
    assert len(challenges) == 0
