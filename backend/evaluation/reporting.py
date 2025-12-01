from dataclasses import dataclass
from typing import List, Dict, Any
from backend.models.session import SessionStore

@dataclass
class PersonaScore:
    persona_id: str
    average_score: int
    total_challenges: int
    breakdown: Dict[str, int]

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
        persona_stats: Dict[str, Dict[str, Any]] = {}
        
        for interaction in history:
            score = interaction.get("score", 0)
            breakdown = interaction.get("breakdown", {})
            persona_id = interaction.get("persona_id", "unknown")
            
            total_score += score
            
            if persona_id not in persona_stats:
                persona_stats[persona_id] = {
                    "scores": [],
                    "breakdowns": {"accuracy": [], "completeness": [], "clarity": [], "truth_alignment": []}
                }
            
            persona_stats[persona_id]["scores"].append(score)
            for k, v in breakdown.items():
                if k in persona_stats[persona_id]["breakdowns"]:
                    persona_stats[persona_id]["breakdowns"][k].append(v)

        overall_score = int(total_score / len(history))
        
        breakdown_list = []
        for pid, stats in persona_stats.items():
            scores = stats["scores"]
            avg = int(sum(scores) / len(scores))
            
            # Average breakdown per persona
            avg_breakdown = {}
            for k, v_list in stats["breakdowns"].items():
                avg_breakdown[k] = int(sum(v_list) / len(v_list)) if v_list else 0

            breakdown_list.append(PersonaScore(
                persona_id=pid,
                average_score=avg,
                total_challenges=len(scores),
                breakdown=avg_breakdown
            ))

        # Determine strengths/weaknesses based on aggregate breakdown
        agg_breakdown = {"accuracy": [], "completeness": [], "clarity": [], "truth_alignment": []}
        for interaction in history:
            bd = interaction.get("breakdown", {})
            for k, v in bd.items():
                if k in agg_breakdown:
                    agg_breakdown[k].append(v)
        
        avg_metrics = {k: (sum(v)/len(v) if v else 0) for k, v in agg_breakdown.items()}
        
        strengths = [k.replace("_", " ").title() for k, v in avg_metrics.items() if v >= 80]
        weaknesses = [k.replace("_", " ").title() for k, v in avg_metrics.items() if v < 60]

        return SessionReport(
            overall_score=overall_score,
            persona_breakdown=breakdown_list,
            total_challenges=len(history),
            strengths=strengths,
            weaknesses=weaknesses
        )
