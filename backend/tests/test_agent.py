"""
Tests for agent.
"""
from typing import Any
from unittest.mock import MagicMock, patch
from backend.research.agent import ResearchAgent
from backend.models.core import ResearchDossier

@patch("backend.research.agent.generate_queries")
@patch("backend.research.agent.summarize_research")
def test_research_agent_run(mock_summarize: Any, mock_gen_queries: Any) -> None:
    """Test the full research agent flow."""
    # Mock dependencies
    mock_gen_queries.return_value = ["query 1"]
    mock_summarize.return_value = ResearchDossier(session_id="123")

    mock_llm = MagicMock()
    mock_search = MagicMock()
    mock_search.search.return_value = []

    agent = ResearchAgent(llm_client=mock_llm, search_client=mock_search)
    dossier = agent.run("123", "Title", ["tag"])

    assert dossier.session_id == "123"
    mock_gen_queries.assert_called_once()
    mock_search.search.assert_called_once()
    mock_summarize.assert_called_once()
