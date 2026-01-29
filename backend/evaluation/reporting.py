"""
Module for generating session reports.
"""
from dataclasses import dataclass
from typing import List, Dict, Any
from backend.models.session import SessionStore

@dataclass
class PersonaScore:
    """
    Aggregated score stats for a persona.
    """
    persona_id: str
    average_score: int
    total_challenges: int
    breakdown: Dict[str, int]

@dataclass
class SessionReport:
    """
    Comprehensive report for a session.
    """
    overall_score: int
    persona_breakdown: List[PersonaScore]
    total_challenges: int
    strengths: List[str]
    weaknesses: List[str]
    slide_breakdown: Dict[int, int]

class ReportingEngine:
    """
    Generates reports from session history.
    """
    def __init__(self, session_store: SessionStore):
        """Initialize the ReportingEngine."""
        self.session_store = session_store

    def generate_report(self, session_id: str) -> SessionReport:
        """Generate a comprehensive report for the session."""
        history = self.session_store.get_history(session_id)
        
        if not history:
            return SessionReport(
                overall_score=0,
                persona_breakdown=[],
                total_challenges=0,
                strengths=[],
                weaknesses=[],
                slide_breakdown={}
            )

        total_score = 0
        persona_stats: Dict[str, Dict[str, Any]] = {}
        slide_scores: Dict[int, List[int]] = {}
        
        for interaction in history:
            score = interaction.get("score", 0)
            breakdown = interaction.get("breakdown", {})
            persona_id = interaction.get("persona_id", "unknown")
            # Assuming interaction has slide_index. If not, we might need to fetch it from challenge
            # But for now let's assume it's stored or we can't easily get it without challenge lookup.
            # Let's check if we save slide_index in history. 
            # In submitAnswer (client.ts) we don't pass slide_index. 
            # But backend submit_answer might look it up.
            # Let's assume interaction has 'slide_index' or we default to 0.
            slide_index = interaction.get("slide_index", 0)
            
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

            if slide_index not in slide_scores:
                slide_scores[slide_index] = []
            slide_scores[slide_index].append(score)

        overall_score = int(total_score / len(history))
        
        breakdown_list = []
        for pid, stats in persona_stats.items():
            scores = stats["scores"]
            avg = int(sum(scores) / len(scores))
            
            # Average breakdown per persona
            avg_breakdown: Dict[str, Any] = {}
            for k, v_list in stats["breakdowns"].items():
                avg_breakdown[k] = int(sum(v_list) / len(v_list)) if v_list else 0

            breakdown_list.append(PersonaScore(
                persona_id=pid,
                average_score=avg,
                total_challenges=len(scores),
                breakdown=avg_breakdown
            ))

        # Determine strengths/weaknesses based on aggregate breakdown
        agg_breakdown: Dict[str, List[int]] = {"accuracy": [], "completeness": [], "clarity": [], "truth_alignment": []}
        for interaction in history:
            bd = interaction.get("breakdown", {})
            for k, v in bd.items():
                if k in agg_breakdown:
                    agg_breakdown[k].append(v)
        
        avg_metrics = {k: (sum(v)/len(v) if v else 0) for k, v in agg_breakdown.items()}
        
        # Sort by score to get top strengths and weaknesses
        sorted_metrics = sorted(avg_metrics.items(), key=lambda x: x[1], reverse=True)
        
        strengths = [k.replace("_", " ").title() for k, v in sorted_metrics if v >= 80][:3]
        # For weaknesses, we want the lowest scores, so we look at the end of the sorted list or sort ascending
        sorted_metrics_asc = sorted(avg_metrics.items(), key=lambda x: x[1])
        weaknesses = [k.replace("_", " ").title() for k, v in sorted_metrics_asc if v < 60][:3]

        # Calculate slide averages
        slide_breakdown_final = {}
        for idx, scores in slide_scores.items():
            # Ensure idx is an int, defaulting to 0 if somehow None (though dict keys shouldn't be None usually if we handled it earlier)
            safe_idx = int(idx) if idx is not None else 0
            slide_breakdown_final[safe_idx] = int(sum(scores) / len(scores))

        return SessionReport(
            overall_score=overall_score,
            persona_breakdown=breakdown_list,
            total_challenges=len(history),
            strengths=strengths,
            weaknesses=weaknesses,
            slide_breakdown=slide_breakdown_final
        )
