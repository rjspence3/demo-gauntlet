from typing import List, Optional, Dict
from backend.models.core import ChallengerPersona

class ChallengerRegistry:
    def __init__(self) -> None:
        self._personas: Dict[str, ChallengerPersona] = {}
        self._load_defaults()
        
    def _load_defaults(self) -> None:
        defaults = [
            ChallengerPersona(
                id="skeptic",
                name="The Skeptic",
                role="Senior Engineer / Architect",
                style="Critical, technical, detail-oriented. Questions feasibility.",
                focus_areas=["Technical Feasibility", "Scalability", "Legacy Integration"]
            ),
            ChallengerPersona(
                id="budget_hawk",
                name="The Budget Hawk",
                role="CFO / Finance Director",
                style="Conservative, ROI-focused. Questions value and hidden costs.",
                focus_areas=["ROI", "TCO", "Licensing", "Implementation Costs"]
            ),
            ChallengerPersona(
                id="compliance",
                name="The Compliance Officer",
                role="CISO / Legal",
                style="Risk-averse, strict. Focuses on data safety and regulations.",
                focus_areas=["GDPR/CCPA", "Data Residency", "Security Certifications"]
            ),
            ChallengerPersona(
                id="executive",
                name="The Executive",
                role="VP / C-Level",
                style="Big-picture, impatient. Focuses on business outcomes.",
                focus_areas=["Time to Value", "Strategic Alignment", "Competitive Advantage"]
            )
        ]
        for p in defaults:
            self._personas[p.id] = p
            
    def list_personas(self) -> List[ChallengerPersona]:
        """List all available personas."""
        return list(self._personas.values())
        
    def get_persona(self, persona_id: str) -> Optional[ChallengerPersona]:
        """Get a persona by ID."""
        return self._personas.get(persona_id)
