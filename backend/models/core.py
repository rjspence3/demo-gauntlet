"""
Core data models for the application.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional


class ClaimType(str, Enum):
    """Types of claims that can be extracted from slides."""
    FACTUAL = "factual"
    FORECAST = "forecast"
    ASSUMPTION = "assumption"
    RECOMMENDATION = "recommendation"
    METRIC = "metric"


class ClaimImportance(str, Enum):
    """Importance level of a claim."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class SourceOrigin(str, Enum):
    """Origin of the source span within the slide."""
    SLIDE_BODY = "slide_body"
    SPEAKER_NOTES = "speaker_notes"
    TITLE = "title"


class EvidenceRelevance(str, Enum):
    """Relevance level of evidence to claims."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class EvidenceStance(str, Enum):
    """Stance of evidence relative to a claim."""
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    NEUTRAL_OR_UNCLEAR = "neutral_or_unclear"


class EvidenceSource(str, Enum):
    """Source type of evidence."""
    DECK = "deck"
    RESEARCH = "research"


class TensionCategory(str, Enum):
    """Categories of tensions identified during analysis."""
    CONTRADICTION = "contradiction"        # claim vs evidence or claim vs claim
    MISSING_EVIDENCE = "missing_evidence"  # claim lacks supporting evidence
    RISK_EXPOSURE = "risk_exposure"        # unaddressed risks or vulnerabilities
    COMPETITIVE_GAP = "competitive_gap"    # gaps vs competitors or alternatives
    AMBIGUITY = "ambiguity"                # vague or unclear claims


class TensionSeverity(str, Enum):
    """Severity level of a tension."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class Slide:
    """
    Represents a single slide in a presentation.
    """
    index: int
    title: str
    text: str
    notes: str = ""
    tags: List[str] = field(default_factory=list)

@dataclass
class Chunk:
    """
    Represents a text chunk for embedding and retrieval.
    """
    id: str
    slide_index: int
    text: str
    embedding: List[float] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Fact:
    """
    Represents a researched fact.
    """
    id: str
    topic: str
    text: str
    source_url: str
    source_title: str
    domain: str
    snippet: str

@dataclass
class ResearchDossier:
    """
    Represents the collected research for a presentation.
    """
    session_id: str
    competitor_insights: List[str] = field(default_factory=list)
    cost_benchmarks: List[str] = field(default_factory=list)
    compliance_notes: List[str] = field(default_factory=list)
    implementation_risks: List[str] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)
    facts: List[Fact] = field(default_factory=list)

@dataclass
class ChallengerPersona:
    """
    Represents a challenger persona configuration.
    """
    id: str
    name: str
    role: str
    style: str
    focus_areas: List[str]
    avatar_paths: Dict[str, str] = field(default_factory=dict)
    domain_tags: List[str] = field(default_factory=list)
    agent_prompt: str = ""

@dataclass
class Challenge:
    """
    Represents a generated challenge question.
    """
    id: str
    session_id: str
    persona_id: str
    question: str
    ideal_answer: str
    difficulty: str
    slide_index: Optional[int] = None
    evidence: Dict[str, List[Any]] = field(default_factory=lambda: {"chunks": [], "facts": []})
    key_points: List[str] = field(default_factory=list)
    tone: str = "professional"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EvaluationResult:
    """
    Represents the evaluation of a user's answer.
    """
    score: int  # 0-100
    feedback: str
    accuracy_assessment: str
    completeness_assessment: str
    tone_assessment: str


@dataclass
class SourceSpan:
    """
    Represents a span in the source text where a claim originated.
    """
    start: int  # Character offset start
    end: int    # Character offset end
    origin: SourceOrigin  # Which part of the slide


@dataclass
class Claim:
    """
    Represents an extracted claim from a slide.
    """
    id: str  # e.g., "C1", "C2"
    text: str  # The claim statement
    claim_type: ClaimType
    importance: ClaimImportance
    confidence: float  # 0.0 to 1.0
    tags: List[str] = field(default_factory=list)
    source_spans: List[SourceSpan] = field(default_factory=list)


@dataclass
class ClaimExtractionMeta:
    """
    Metadata about the claim extraction process.
    """
    slide_index: int
    used_speaker_notes: bool
    notes: str = ""  # Any notes for downstream agents


@dataclass
class ClaimExtractionResult:
    """
    Result of claim extraction from a single slide.
    """
    claims: List[Claim]
    meta: ClaimExtractionMeta


@dataclass
class CandidateEvidence:
    """
    Raw candidate evidence retrieved from vector DB before LLM filtering.
    """
    id: str
    text: str
    source: EvidenceSource  # "deck" or "research"
    collection: str  # underlying collection name (e.g. "deck_chunks")
    base_score: float  # raw similarity score from vector DB
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EvidenceItem:
    """
    Filtered and enriched evidence item after LLM analysis.
    """
    id: str
    text: str
    source: EvidenceSource  # "deck" or "research"
    collection: str
    relevance: EvidenceRelevance  # "high" | "medium" | "low"
    stance: EvidenceStance  # "supports" | "contradicts" | "neutral_or_unclear"
    related_claim_ids: List[str]  # which claims this evidence relates to
    topics: List[str]  # topic tags for this evidence
    score_adjustment: float  # -0.3 to +0.3 adjustment based on LLM analysis
    notes: Optional[str] = None  # optional explanation


@dataclass
class EvidenceSelectionMeta:
    """
    Metadata about the evidence selection process.
    """
    total_candidates: int
    selected_count: int
    discarded_count: int
    processing_notes: str = ""


@dataclass
class EvidenceSelectionResult:
    """
    Result of evidence selection from candidate evidence.
    """
    evidence: List[EvidenceItem]
    meta: EvidenceSelectionMeta


@dataclass
class Tension:
    """
    Represents a tension, gap, or contradiction identified during analysis.

    Tensions are the "fuel" for generating challenging questions.
    """
    id: str  # e.g., "T1", "T2"
    category: TensionCategory  # type of tension
    severity: TensionSeverity  # how significant is this tension
    headline: str  # short human-readable summary (e.g., "Cost claim contradicts industry data")
    description: str  # 1-3 sentence detailed description
    related_claim_ids: List[str] = field(default_factory=list)  # claims involved
    supporting_evidence_ids: List[str] = field(default_factory=list)  # evidence that supports claims
    contradicting_evidence_ids: List[str] = field(default_factory=list)  # evidence that contradicts
    risk_tags: List[str] = field(default_factory=list)  # topic tags for risk areas
    question_seed: Optional[str] = None  # rough question template for downstream use
    notes: Optional[str] = None  # additional context


@dataclass
class AnalysisMeta:
    """
    Metadata about the evidence analysis process.
    """
    slide_id: str
    num_claims: int
    num_evidence_items: int
    num_tensions: int
    processing_notes: str = ""


@dataclass
class AnalysisResult:
    """
    Result of evidence analysis for a slide.

    Contains identified tensions that can fuel challenge generation.
    """
    slide_id: str
    tensions: List[Tension]
    meta: AnalysisMeta


class QuestionDifficulty(str, Enum):
    """Difficulty level for challenge questions."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


@dataclass
class IdealAnswer:
    """
    Represents the ideal answer for a challenge question.

    Grounded in actual evidence with extracted key points.
    """
    text: str  # Full answer text
    key_points: List[str]  # 3-6 extracted bullet points
    evidence_ids: List[str]  # Must correspond to actual EvidenceItem IDs


@dataclass
class ChallengeQuestion:
    """
    A synthesized challenge question derived from a tension.

    Links to the source tension, claims, and evidence for traceability.
    """
    id: str  # e.g., "Q1", "Q2"
    tension_id: str  # The tension this question targets
    question: str  # The actual question text
    persona: Optional[str]  # "CFO", "CTO", etc., optional for now
    difficulty: str  # "easy" | "medium" | "hard"
    related_claim_ids: List[str]  # Claims this question challenges
    evidence_ids: List[str]  # Evidence supporting the question
    ideal_answer: IdealAnswer  # Grounded ideal answer
    grounded: bool = True  # Whether the question passed grounding verification
    notes: Optional[str] = None  # Additional context


@dataclass
class QuestionSynthesisMeta:
    """
    Metadata about the question synthesis process.
    """
    slide_id: str
    num_tensions: int  # Number of tensions processed
    num_questions: int  # Number of questions generated
    grounded: bool  # True if all questions passed grounding check
    notes: Optional[str] = None  # Processing notes


@dataclass
class QuestionSynthesisResult:
    """
    Result of question synthesis for a slide.

    Contains generated challenge questions and metadata.
    """
    questions: List[ChallengeQuestion]
    meta: QuestionSynthesisMeta


@dataclass
class PipelineConfig:
    """
    Configuration for the ChallengerPipeline.
    """
    min_tensions: int = 1  # Minimum tensions required to generate questions
    max_questions_per_slide: int = 3  # Maximum questions per slide
    include_low_severity: bool = False  # Include LOW severity tensions
    grounding_retries: int = 2  # Number of retries for grounding verification


@dataclass
class PipelineMeta:
    """
    Metadata about the pipeline execution for a single slide.
    """
    slide_index: int
    processing_time_ms: int = 0
    steps_completed: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


@dataclass
class PipelineResult:
    """
    Result of processing a single slide through the challenger pipeline.

    Contains all intermediate and final outputs from each step.
    """
    slide_id: str
    claims: List[Claim] = field(default_factory=list)
    evidence: List[EvidenceItem] = field(default_factory=list)
    tensions: List[Tension] = field(default_factory=list)
    questions: List[ChallengeQuestion] = field(default_factory=list)
    meta: PipelineMeta = field(default_factory=lambda: PipelineMeta(slide_index=0))
