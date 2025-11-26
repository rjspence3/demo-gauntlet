from backend.research.client import MockSearchClient, SearchResult

def test_mock_search_client() -> None:
    """Test the Mock Search client."""
    client = MockSearchClient()
    results = client.search("test query")

    assert len(results) == 1
    assert isinstance(results[0], SearchResult)
    assert "test query" in results[0].title
