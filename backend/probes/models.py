from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class InteractionResult:
    """Result from a single agent interaction."""
    response_text: str
    latency_ms: float
    turn_number: int
    prompt: str

@dataclass
class ConversationContext:
    """Maintains conversation history for multi-turn tests."""
    history: List[Dict[str, str]] = field(default_factory=list)

    def add_turn(self, role: str, content: str):
        self.history.append({"role": role, "content": content})

    def get_messages(self) -> List[Dict[str, str]]:
        return self.history.copy()

@dataclass
class ProbeResult:
    """Result from a single probe."""
    probe_name: str
    score: int  # 1-10
    rationale: str
    key_observations: List[str]
    transcript: List[InteractionResult]

@dataclass
class ProbeScorecard:
    """Final scorecard for an agent."""
    target_agent_persona: str
    test_script_summary: str
    scores: Dict[str, int]
    total_score: int
    human_likeness_grade: str
    telemetry_data: Dict[str, Any]
    critical_failures: List[str]
    human_wins: List[str]
    coaching_tip: str
