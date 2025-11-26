from dataclasses import dataclass
from typing import List, Dict, Any
from backend.models.session import SessionStore

@dataclass
class PersonaScore:
    persona_id: str
    average_score: int
    total_challenges: int

@dataclass
class SessionReport:
    overall_score: int
    persona_breakdown: List[PersonaScore]
    total_challenges: int
    strengths: List[str]
    weaknesses: List[str]

class ReportingEngine:
    def __init__(self, session_store: SessionStore):
        self.session_store = session_store

    def generate_report(self, session_id: str) -> SessionReport:
        history = self.session_store.get_history(session_id)
        
        if not history:
            return SessionReport(
                overall_score=0,
                persona_breakdown=[],
                total_challenges=0,
                strengths=[],
                weaknesses=[]
            )

        total_score = 0
        persona_scores: Dict[str, List[int]] = {}
        
        for interaction in history:
            score = interaction.get("score", 0)
            persona_id = interaction.get("persona_id", "unknown")
            
            total_score += score
            if persona_id not in persona_scores:
                persona_scores[persona_id] = []
            persona_scores[persona_id].append(score)

        overall_score = int(total_score / len(history))
        
        breakdown = []
        for pid, scores in persona_scores.items():
            avg = int(sum(scores) / len(scores))
            breakdown.append(PersonaScore(
                persona_id=pid,
                average_score=avg,
                total_challenges=len(scores)
            ))

        # Mock strengths/weaknesses for MVP based on score
        strengths = []
        weaknesses = []
        if overall_score >= 80:
            strengths.append("Strong command of content")
            strengths.append("Clear communication")
        elif overall_score >= 60:
            strengths.append("Good basic understanding")
            weaknesses.append("Missed some nuances")
        else:
            weaknesses.append("Needs deeper research")
            weaknesses.append("Review objection handling")

        return SessionReport(
            overall_score=overall_score,
            persona_breakdown=breakdown,
            total_challenges=len(history),
            strengths=strengths,
            weaknesses=weaknesses
        )
