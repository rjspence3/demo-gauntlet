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
        self.base_url = "https://api.search.brave.com/res/v1/web/search"

    def search(self, query: str, limit: int = 5) -> List[SearchResult]:
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.api_key
        }
        params = {
            "q": query,
            "count": limit
        }
        
        try:
            import requests
            response = requests.get(self.base_url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            results = []
            if "web" in data and "results" in data["web"]:
                for item in data["web"]["results"]:
                    results.append(SearchResult(
                        title=item.get("title", ""),
                        url=item.get("url", ""),
                        snippet=item.get("description", ""),
                        source="brave"
                    ))
            return results
            
        except Exception as e:
            print(f"Brave search failed: {e}")
            return []
