"""
Agent for conducting research on deck topics.
"""
from typing import List, Optional, Any
from backend.models.core import ResearchDossier
from backend.models.llm import LLMClient, MockLLM
from backend.models.fact_store import FactStore
from backend.research.client import SearchClient, MockSearchClient
from backend.research.query_builder import generate_queries
from backend.research.summarizer import summarize_research
from backend.config import config
from backend.logger import get_logger

logger = get_logger(__name__)

class ResearchAgent:
    """
    Orchestrates the research process: query generation, search, summarization, and fact storage.
    """
    def __init__(self, llm_client: Optional[LLMClient] = None,
                 search_client: Optional[SearchClient] = None,
                 fact_store: Optional[FactStore] = None):
        """
        Initialize the ResearchAgent.

        Args:
            llm_client: Client for LLM operations.
            search_client: Client for web search.
            fact_store: Store for saving researched facts.
        """
        self.llm_client = llm_client or MockLLM()
        self.search_client = search_client or MockSearchClient()
        self.fact_store = fact_store or FactStore()

    def run(self, session_id: str, deck_title: str, tags: list[str], slides: Optional[list[Any]] = None) -> ResearchDossier:
        """
        Executes the full research workflow:
        1. Generate queries (LLM)
        2. Execute search (SearchClient)
        3. Summarize results (LLM)
        4. Store facts (FactStore)
        """
        if not config.ENABLE_RESEARCH:
            logger.info("Research disabled by config. Returning empty dossier.")
            return ResearchDossier(
                session_id=session_id,
                competitor_insights=["Research disabled."],
                cost_benchmarks=["Research disabled."],
                compliance_notes=["Research disabled."],
                implementation_risks=["Research disabled."]
            )

        try:
            logger.info("Starting research...")
            # 1. Generate Queries
            queries = generate_queries(deck_title, tags, self.llm_client, slides)
            logger.info(f"Generated queries: {queries}")
            
            # 2. Execute Search (aggregate results)
            all_results = []
            for query in queries:
                try:
                    results = self.search_client.search(query, limit=3)
                    all_results.extend(results)
                except Exception as e:
                    logger.error(f"Search failed for query '{query}': {e}")
            
            logger.info(f"Found {len(all_results)} search results.")
            
            # Deduplicate results by URL
            unique_results = {r.url: r for r in all_results}.values()

            # 3. Summarize
            dossier = summarize_research(session_id, list(unique_results), self.llm_client)
            
            # 4. Store Facts
            if dossier.facts:
                self.fact_store.add_facts(dossier.facts)
                logger.info(f"Stored {len(dossier.facts)} facts in FactStore.")

            logger.info("Research complete.")
            return dossier
        except Exception as e:
            logger.error(f"Research failed: {e}")
            return ResearchDossier(
                session_id=session_id,
                competitor_insights=["Research failed."],
                cost_benchmarks=["Research failed."],
                compliance_notes=["Research failed."],
                implementation_risks=["Research failed."]
            )
