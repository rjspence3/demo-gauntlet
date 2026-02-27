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
        self.llm_client = llm_client
        self.deck_retriever = deck_retriever
        self.fact_store = fact_store

        self.agent_map: Dict[str, Type[BaseChallenger]] = {
            "skeptic": CTOAgent,
            "cto": CTOAgent,
            "budget_hawk": CFOAgent,
            "cfo": CFOAgent,
            "compliance": ComplianceAgent,
            "executive": BaseChallenger,
        }

        self._dspy_agent = self._load_dspy_agent()

    def _load_dspy_agent(self):
        """Load the compiled DSPy agent if DSPY_PROGRAM_PATH is configured."""
        from backend.config import config
        if not config.DSPY_PROGRAM_PATH:
            return None
        try:
            import dspy
            from backend.dspy_optimization.gauntlet_agent import GauntletAgent
            lm = dspy.LM("openai/gpt-4o", api_key=config.OPENAI_API_KEY)
            dspy.configure(lm=lm)
            agent = GauntletAgent.from_file(config.DSPY_PROGRAM_PATH)
            logger.info(f"Loaded DSPy agent from {config.DSPY_PROGRAM_PATH}")
            return agent
        except Exception as e:
            logger.warning(f"DSPy agent load failed, falling back to standard pipeline: {e}")
            return None

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
        Generates challenges using the specific agent implementation,
        then optionally enriches ideal answers using a compiled DSPy agent.
        """
        agent = self.get_agent_for_persona(persona)
        logger.info(f"Generating challenges for {persona.name} using {type(agent).__name__}")

        challenges = agent.precompute_challenges(
            session_id=session_id,
            deck_context=deck_context,
            slides=slides,
            deck_retriever=self.deck_retriever,
            fact_store=self.fact_store,
            dossier=dossier,
            llm_client=self.llm_client
        )

        if self._dspy_agent and challenges:
            challenges = self._enrich_with_dspy(persona, challenges)

        return challenges

    def _enrich_with_dspy(
        self,
        persona: ChallengerPersona,
        challenges: List[Challenge]
    ) -> List[Challenge]:
        """
        Replace ideal_answer text on each challenge using the compiled DSPy agent.
        Falls back to the original ideal_answer if DSPy fails for any individual challenge.
        """
        persona_context = (
            f"{persona.role}: {persona.style}\n"
            f"Focus areas: {', '.join(persona.focus_areas)}"
        )
        for challenge in challenges:
            try:
                evidence_text = "\n".join(challenge.evidence.get("chunks", []))
                pred = self._dspy_agent(
                    persona_context=persona_context,
                    challenge_question=challenge.question,
                    deck_evidence=evidence_text,
                )
                challenge.ideal_answer = pred.response
            except Exception as e:
                logger.warning(f"DSPy enrichment failed for challenge {challenge.id}: {e}")
        return challenges
