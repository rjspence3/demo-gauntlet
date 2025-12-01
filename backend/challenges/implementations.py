import uuid
import random
from typing import List
from backend.challenges.agent import ChallengerAgent
from backend.models.core import Slide, Challenge, ChallengerPersona, ResearchDossier
from backend.models.store import DeckRetriever
from backend.models.fact_store import FactStore
from backend.models.llm import LLMClient
from backend.logger import get_logger

logger = get_logger(__name__)

class BaseChallenger(ChallengerAgent):
    def __init__(self, persona: ChallengerPersona):
        self.persona = persona
        self.id = persona.id
        self.name = persona.name
        self.role = persona.role
        self.domain_tags = persona.domain_tags

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
        challenges = []
        
        logger.info(f"Precomputing challenges for {self.name} across {len(slides)} slides.")
        
        # For MVP, we'll iterate through slides and generate challenges if relevant
        # In a real system, we might look at the deck holistically first
        
        for slide in slides:
            # Check relevance based on tags
            slide_tags = set(slide.tags)
            persona_tags = set(self.domain_tags)
            
            # Simple intersection check
            if not slide_tags.intersection(persona_tags):
                # Low probability of challenging if no tag overlap, but maybe check text?
                # For MVP, skip if no tag match to save LLM calls, unless it's a key slide (like architecture for CTO)
                continue

            # Retrieve Evidence
            # 1. Deck Chunks
            chunks = deck_retriever.get_chunks_for_slide(slide.index)
            chunk_texts = [c.text for c in chunks]
            
            # 2. Research Facts (by tags)
            facts = []
            for tag in slide_tags:
                facts.extend(fact_store.get_facts_by_topic(tag, limit=2))
            
            fact_texts = [f.text for f in facts]

            # Generate Challenge
            prompt = f"""
            You are roleplaying as {self.name}, a {self.role}.
            Your style is: {self.persona.style}
            Your focus areas are: {', '.join(self.persona.focus_areas)}
            
            Context:
            Slide Title: {slide.title}
            Slide Content: {slide.text}
            
            Evidence from Deck:
            {chr(10).join([f"- {c}" for c in chunk_texts])}
            
            Research Facts:
            {chr(10).join([f"- {f}" for f in fact_texts])}
            
            Generate 1 challenging question/objection based on the deck and research.
            The question MUST be grounded in the provided evidence.
            
            Output JSON format:
            {{
                "question": "The question text",
                "ideal_answer": "The ideal response...",
                "key_points": ["point 1", "point 2", "point 3"],
                "tone": "professional",
                "difficulty": "medium",
                "evidence_used": {{
                    "chunks": ["indices of used chunks..."],
                    "facts": ["indices of used facts..."]
                }}
            }}
            """
            
            try:
                response = llm_client.generate_json(prompt)
                
                # Map back evidence indices to IDs (simplified for MVP)
                used_chunk_ids = [c.id for c in chunks] # In reality, LLM should pick specific ones
                used_fact_ids = [f.id for f in facts]

                challenges.append(Challenge(
                    id=str(uuid.uuid4()),
                    session_id=session_id,
                    persona_id=self.id,
                    question=response.get("question", ""),
                    ideal_answer=response.get("ideal_answer", ""),
                    key_points=response.get("key_points", []),
                    tone=response.get("tone", "professional"),
                    difficulty=response.get("difficulty", "medium"),
                    slide_index=slide.index,
                    evidence={
                        "chunks": used_chunk_ids,
                        "facts": used_fact_ids
                    }
                ))
            except Exception as e:
                logger.error(f"Failed to generate challenge for {self.name} on slide {slide.index}: {e}")

        logger.info(f"Generated {len(challenges)} challenges for {self.name}.")
        return challenges

    def decide_questions_for_slide(
        self,
        slide_index: int,
        challenges: List[Challenge]
    ) -> List[Challenge]:
        # Filter challenges for this slide
        slide_challenges = [c for c in challenges if c.slide_index == slide_index]
        
        if not slide_challenges:
            return []
            
        # Simple probabilistic trigger for MVP
        # In a real system, this would be more complex (e.g., based on conversation history)
        if random.random() < 0.7: # 70% chance to speak if there's a challenge
            return slide_challenges[:1] # Return top challenge
            
        return []

class CTOAgent(BaseChallenger):
    pass

class CFOAgent(BaseChallenger):
    pass

class ComplianceAgent(BaseChallenger):
    pass
