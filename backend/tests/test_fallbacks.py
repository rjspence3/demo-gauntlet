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
    mock_llm.generate_json.side_effect = Exception("LLM failed")
    
    generator = ChallengeGenerator(llm_client=mock_llm)
    persona = ChallengerPersona(id="p1", name="P1", role="Role", style="Style", focus_areas=["tag"])
    
    challenges = generator.generate_challenges(
        session_id="s1",
        persona=persona,
        deck_context="Context",
        dossier=MagicMock(),
        slide_content="Slide",
        slide_index=0
    )
    
    assert len(challenges) == 2
    assert challenges[0].id == "fallback_1"
    assert "fallback" in challenges[0].context_source.lower()
