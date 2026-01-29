"""
Tests for llm.
"""
from backend.models.llm import MockLLM, OpenAIClient

def test_mock_llm() -> None:
    """Test the Mock LLM client."""
    client = MockLLM()
    response = client.complete("Hello")
    assert isinstance(response, str)
    assert len(response) > 0

def test_mock_llm_json() -> None:
    """Test the Mock LLM client JSON generation."""
    client = MockLLM()
    response = client.complete_structured("Generate JSON", schema={"type": "object"})
    assert isinstance(response, dict)

# We skip OpenAI tests if no key is present, or mock it
def test_openai_llm_init() -> None:
    """Test OpenAI LLM initialization."""
    client = OpenAIClient(api_key="fake-key")
    assert client.client is not None
