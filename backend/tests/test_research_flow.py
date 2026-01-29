"""
Tests for research_flow.
"""
from backend.research.agent import ResearchAgent
from backend.models.llm import MockLLM
from backend.research.client import MockSearchClient

def test_research_flow_integration() -> None:
    """Test the research flow with mock components."""
    # Setup mocks to return predictable data
    mock_llm = MockLLM()
    # We can patch the generate_json method on the instance if needed,
    # but MockLLM already returns valid JSON.

    mock_search = MockSearchClient()

    agent = ResearchAgent(llm_client=mock_llm, search_client=mock_search)

    dossier = agent.run(
        session_id="test-session",
        deck_title="Enterprise Cloud Migration",
        tags=["cloud", "migration"]
    )

    assert dossier.session_id == "test-session"
    # MockLLM returns empty lists by default for the specific keys in summarizer,
    # so we check if the object is created correctly.
    # To test content, we'd need to mock the LLM responses more specifically.
    assert isinstance(dossier.competitor_insights, list)
