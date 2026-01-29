"""
Search client abstractions and implementations.
"""
from abc import ABC, abstractmethod
from typing import List
from dataclasses import dataclass
import requests # type: ignore
from tenacity import retry, stop_after_attempt, wait_exponential

@dataclass
class SearchResult:
    """
    Represents a single search result.
    """
    title: str
    url: str
    snippet: str
    source: str

class SearchClient(ABC):
    """
    Abstract base class for search clients.
    """
    @abstractmethod
    def search(self, query: str, limit: int = 5) -> List[SearchResult]:
        """Execute a search query."""

class MockSearchClient(SearchClient):
    """
    Mock search client for testing.
    """
    def search(self, query: str, limit: int = 5) -> List[SearchResult]:
        """Return mock search results."""
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
    """
    Brave Search API client implementation.
    """
    def __init__(self, api_key: str):
        """
        Initialize the BraveSearchClient.

        Args:
            api_key: Brave Search API key.
        """
        self.api_key = api_key
        self.base_url = "https://api.search.brave.com/res/v1/web/search"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def search(self, query: str, limit: int = 5) -> List[SearchResult]:
        """Execute a search query using Brave Search."""
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
            response = requests.get(self.base_url, headers=headers, params=params, timeout=10)
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
            
        except requests.exceptions.HTTPError as e:
            # Don't retry 4xx errors except 429
            if e.response.status_code == 429:
                raise e
            if 400 <= e.response.status_code < 500:
                print(f"Brave search failed (client error): {e}")
                return []
            raise e
        except Exception as e:
            # Retry other errors
            print(f"Brave search failed: {e}")
            raise e
