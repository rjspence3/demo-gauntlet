"""
Tests for query_builder.
"""
from unittest.mock import MagicMock
from backend.research.query_builder import generate_queries

def test_generate_queries() -> None:
    """Test generating queries from deck context."""
    mock_llm = MagicMock()
    # Mock JSON response
    mock_llm.complete_structured.return_value = {
        "queries": [
            "competitor analysis for X",
            "cost of X",
            "security compliance for X"
        ]
    }

    queries = generate_queries("Deck Title", ["tag1", "tag2"], mock_llm)

    assert len(queries) == 3
    assert "cost of X" in queries
    mock_llm.complete_structured.assert_called_once()
