from dataclasses import asdict
import json
from typing import List, Tuple

from backend.probes.models import ProbeResult, ProbeScorecard
from backend.probes.config import ENHANCED_PERSONAS
from backend.models.llm import LLMClient
from backend.probes.harness import AgentTestHarness

def calculate_grade(total_score: int, penalty_applied: bool) -> str:
    """Convert total score to letter grade."""
    if penalty_applied:
        total_score -= 5  # Uncanny valley penalty already applied

    if total_score >= 45:
        return "A"
    elif total_score >= 38:
        return "B"
    elif total_score >= 30:
        return "C"
    elif total_score >= 20:
        return "D"
    else:
        return "F"
