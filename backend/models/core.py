from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class Slide:
    index: int
    title: str
    text: str
    notes: str = ""
    tags: List[str] = field(default_factory=list)

@dataclass
class Chunk:
    id: str
    slide_index: int
    text: str
    embedding: List[float] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Fact:
    id: str
    topic: str
    text: str
    source_url: str
    source_title: str
    domain: str
    snippet: str

@dataclass
class ResearchDossier:
    session_id: str
    competitor_insights: List[str] = field(default_factory=list)
    cost_benchmarks: List[str] = field(default_factory=list)
    compliance_notes: List[str] = field(default_factory=list)
    implementation_risks: List[str] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)
    facts: List[Fact] = field(default_factory=list)

@dataclass
class ChallengerPersona:
    id: str
    name: str
    role: str
    style: str
    focus_areas: List[str]
    avatar_paths: Dict[str, str] = field(default_factory=dict)
    domain_tags: List[str] = field(default_factory=list)

@dataclass
class Challenge:
    id: str
    session_id: str
    persona_id: str
    question: str
    ideal_answer: str
    difficulty: str
    slide_index: Optional[int] = None
    evidence: Dict[str, List[str]] = field(default_factory=lambda: {"chunks": [], "facts": []})
    key_points: List[str] = field(default_factory=list)
    tone: str = "professional"
    metadata: Dict[str, Any] = field(default_factory=dict)
