from abc import ABC, abstractmethod
from typing import List
from dataclasses import dataclass

@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str
    source: str

class SearchClient(ABC):
    @abstractmethod
    def search(self, query: str, limit: int = 5) -> List[SearchResult]:
        """Execute a search query."""

class MockSearchClient(SearchClient):
    def search(self, query: str, limit: int = 5) -> List[SearchResult]:
        return [
            SearchResult(
                title=f"Result for {query}",
                url="http://example.com",
                snippet=f"This is a snippet for {query}.",
                source="mock"
            )
        ]

# Placeholder for real clients (Brave/SerpAPI)
class BraveSearchClient(SearchClient):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def search(self, query: str, limit: int = 5) -> List[SearchResult]:
        # Implementation would go here
        return []
