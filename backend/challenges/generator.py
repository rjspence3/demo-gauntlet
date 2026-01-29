"""
Module for generating challenges using LLMs and agents.
"""
from typing import List, Optional, Dict, Type
from backend.models.core import Challenge, ChallengerPersona, ResearchDossier, Slide
from backend.models.llm import LLMClient
from backend.models.store import DeckRetriever
from backend.models.fact_store import FactStore
from backend.challenges.agent import ChallengerAgent
from backend.challenges.implementations import CTOAgent, CFOAgent, ComplianceAgent, BaseChallenger
from backend.logger import get_logger

logger = get_logger(__name__)

class ChallengeGenerator:
    """
    Orchestrates the generation of challenges for a session.
    """
    def __init__(self, llm_client: LLMClient, deck_retriever: DeckRetriever, fact_store: FactStore) -> None:
        """
        Initialize the ChallengeGenerator.
        """
        self.llm_client = llm_client
        self.deck_retriever = deck_retriever
        self.fact_store = fact_store
        
        # Registry of agent implementations
        self.agent_map: Dict[str, Type[BaseChallenger]] = {
            "skeptic": CTOAgent, # Mapping 'skeptic' to CTO for MVP, or we should align IDs
            "cto": CTOAgent,
            "budget_hawk": CFOAgent,
            "cfo": CFOAgent,
            "compliance": ComplianceAgent,
            "executive": BaseChallenger # Fallback
        }
        
    def get_agent_for_persona(self, persona: ChallengerPersona) -> ChallengerAgent:
        """Factory method to get the appropriate agent implementation for a persona."""
        agent_class = self.agent_map.get(persona.id, BaseChallenger)
        return agent_class(persona)

    def generate_challenges(
        self, 
        session_id: str, 
        persona: ChallengerPersona, 
        deck_context: str, 
        dossier: ResearchDossier,
        slides: List[Slide]
    ) -> List[Challenge]:
        """
        Generates challenges using the specific agent implementation.
        """
        agent = self.get_agent_for_persona(persona)
        
        logger.info(f"Generating challenges for {persona.name} using {type(agent).__name__}")
        
        return agent.precompute_challenges(
            session_id=session_id,
            deck_context=deck_context,
            slides=slides,
            deck_retriever=self.deck_retriever,
            fact_store=self.fact_store,
            dossier=dossier,
            llm_client=self.llm_client
        )
