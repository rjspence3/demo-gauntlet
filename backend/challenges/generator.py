import uuid
from typing import List, Any, Optional
from backend.models.core import Challenge, ChallengerPersona, ResearchDossier
from backend.models.llm import LLMClient
from backend.logger import get_logger

logger = get_logger(__name__)

class ChallengeGenerator:
    def __init__(self, llm_client: LLMClient) -> None:
        self.llm_client = llm_client
        
    def generate_challenges(
        self, 
        session_id: str, 
        persona: ChallengerPersona, 
        deck_context: str, 
        dossier: ResearchDossier,
        slide_content: Optional[str] = None,
        slide_index: Optional[int] = None
    ) -> List[Challenge]:
        """
        Generates challenges based on persona, deck, and research.
        """
        
        prompt = f"""
        You are roleplaying as {persona.name}, a {persona.role}.
        Your style is: {persona.style}
        Your focus areas are: {', '.join(persona.focus_areas)}
        
        Context:
        Deck Summary: {deck_context}
        {f"Current Slide Content: {slide_content}" if slide_content else ""}
        
        Research Insights:
        - Competitors: {', '.join(dossier.competitor_insights)}
        - Costs: {', '.join(dossier.cost_benchmarks)}
        - Risks: {', '.join(dossier.implementation_risks)}
        
        Generate 3 challenging questions/objections based on the deck and research.
        
        Output JSON format:
        {{
            "challenges": [
                {{
                    "question": "The question text",
                    "ideal_answer": "The ideal response to this question based on the research and deck",
                    "context_source": "Reference to slide or research",
                    "difficulty": "easy/medium/hard"
                }}
            ]
        }}
        """
        
        try:
            response = self.llm_client.generate_json(prompt)
            raw_challenges = response.get("challenges", [])
            
            challenges = []
            for rc in raw_challenges:
                challenges.append(Challenge(
                    id=str(uuid.uuid4()),
                    session_id=session_id,
                    persona_id=persona.id,
                    question=rc.get("question", ""),
                    ideal_answer=rc.get("ideal_answer", ""),
                    context_source=rc.get("context_source", ""),
                    difficulty=rc.get("difficulty", "medium"),
                    slide_index=slide_index
                ))
            
            return challenges
        except Exception as e:
            logger.error(f"Challenge generation failed: {e}")
            # Fallback challenges
            return [
                Challenge(
                    id="fallback_1",
                    session_id=session_id,
                    persona_id="cto", # Using a generic persona_id for fallback
                    question="Can you explain the technical architecture in more detail?",
                    ideal_answer="The architecture should be scalable, secure, and easy to integrate.",
                    context_source="Fallback due to generation error.",
                    difficulty="medium",
                    slide_index=slide_index
                ),
                Challenge(
                    id="fallback_2",
                    session_id=session_id,
                    persona_id="cfo", # Using a generic persona_id for fallback
                    question="What is the ROI of this solution?",
                    ideal_answer="The ROI is positive due to cost savings and efficiency gains.",
                    context_source="Fallback due to generation error.",
                    difficulty="medium",
                    slide_index=slide_index
                )
            ]
