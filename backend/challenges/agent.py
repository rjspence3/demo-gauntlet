"""
Protocol definition for challenger agents.
"""
from typing import Protocol, List, Optional
from backend.models.core import Slide, Challenge, ChallengerPersona, ResearchDossier, Chunk, Fact, EvaluationResult
from backend.models.store import DeckRetriever
from backend.models.fact_store import FactStore
from backend.models.llm import LLMClient

class ChallengerAgent(Protocol):
    """
    Protocol defining the interface for a challenger agent.
    """
    id: str
    name: str
    role: str
    domain_tags: List[str]
    persona: ChallengerPersona

    def precompute_challenges(
        self,
        session_id: str,
        deck_context: str,
        slides: List[Slide],
        deck_retriever: DeckRetriever,
        fact_store: FactStore,
        dossier: ResearchDossier,
        llm_client: LLMClient
    ) -> List[Challenge]:
        """
        Offline reasoning step:
        - Retrieve slide-relevant deck chunks
        - Retrieve relevant research facts
        - Generate grounded questions
        """
        ...

    def decide_questions_for_slide(
        self,
        slide_index: int,
        challenges: List[Challenge]
    ) -> List[Challenge]:
        """
        Online reasoning step:
        - Decides whether to speak on a slide
        """
        ...

    def evaluate_response(
        self,
        question: Challenge,
        user_answer: str,
        llm_client: LLMClient
    ) -> EvaluationResult:
        """
        Online reasoning step:
        - Evaluates the user's answer
        """
        ...
