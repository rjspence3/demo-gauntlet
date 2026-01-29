"""
Evidence Analysis Agent for identifying contradictions, gaps, and tensions.

This is Step 3 in the multi-step reasoning chain for challenger agents.
"""
from typing import List, Dict, Any
from backend.models.core import (
    Claim,
    EvidenceItem,
    EvidenceStance,
    Tension,
    TensionCategory,
    TensionSeverity,
    AnalysisMeta,
    AnalysisResult,
)
from backend.models.llm import LLMClient
from backend.logger import get_logger

logger = get_logger(__name__)

EVIDENCE_ANALYSIS_SYSTEM_PROMPT = """You are a critical analysis specialist. Given a set of claims and their related evidence, your job is to identify TENSIONS - contradictions, gaps, risks, and ambiguities that would make good targets for challenging questions.

## Tension Categories

1. **CONTRADICTION**: Direct conflict between:
   - A claim and contradicting evidence
   - Two claims that are mutually inconsistent
   - A claim and industry/market reality

2. **MISSING_EVIDENCE**: Claims that lack support:
   - High-importance claims with no supporting evidence
   - Metrics or forecasts without data backing
   - Assumptions stated as facts

3. **RISK_EXPOSURE**: Unaddressed vulnerabilities:
   - Implementation risks not discussed
   - Security/compliance gaps
   - Dependencies or failure modes ignored

4. **COMPETITIVE_GAP**: Weaknesses vs alternatives:
   - Claims that ignore competitor strengths
   - Missing differentiation evidence
   - Industry benchmarks not addressed

5. **AMBIGUITY**: Vague or unclear claims:
   - Undefined terms or metrics
   - Unclear timelines or scope
   - Hedged language hiding weak positions

## Severity Guidelines

- **HIGH**: Fundamental issue that could derail the pitch. Claims core value proposition. Strong contradicting evidence.
- **MEDIUM**: Significant concern but not fatal. Important stakeholders would notice. Some counter-evidence.
- **LOW**: Minor issue or edge case. Nice-to-address but not critical.

## Question Seed Guidelines

For each tension, provide a rough "question_seed" - a template that a challenger persona could use:
- Focus on the tension point, not general questions
- Be specific: reference the claim and evidence
- Frame as genuine inquiry, not attack
- Examples:
  - "How do you reconcile your 40% cost savings claim with [evidence showing 15-25% is typical]?"
  - "What evidence supports the 6-month timeline given [evidence about enterprise deployment complexity]?"
  - "How does your solution address [specific risk mentioned in evidence]?"

## Output Format

Output ONLY valid JSON matching this schema:
{
  "tensions": [
    {
      "id": "T1",
      "category": "contradiction | missing_evidence | risk_exposure | competitive_gap | ambiguity",
      "severity": "high | medium | low",
      "headline": "Brief 5-10 word summary",
      "description": "1-3 sentence explanation of the tension",
      "related_claim_ids": ["C1", "C2"],
      "supporting_evidence_ids": ["E1"],
      "contradicting_evidence_ids": ["E3"],
      "risk_tags": ["cost", "timeline", "security"],
      "question_seed": "How would you justify X given Y?",
      "notes": "Optional additional context"
    }
  ],
  "meta": {
    "slide_id": "slide_0",
    "num_claims": 3,
    "num_evidence_items": 5,
    "num_tensions": 2,
    "processing_notes": "Brief notes about the analysis"
  }
}

IMPORTANT:
- Prioritize quality over quantity - 2-4 strong tensions are better than 10 weak ones.
- Every tension MUST have at least one related_claim_id.
- Contradictions require at least one contradicting_evidence_id.
- Missing evidence tensions should have empty or minimal supporting_evidence_ids.
- Be specific in descriptions - vague tensions are not useful."""


def _format_claims_for_prompt(claims: List[Claim]) -> str:
    """Format claims for inclusion in the LLM prompt."""
    if not claims:
        return "No claims provided."

    lines = []
    for claim in claims:
        claim_type = claim.claim_type.value if hasattr(claim.claim_type, 'value') else str(claim.claim_type)
        importance = claim.importance.value if hasattr(claim.importance, 'value') else str(claim.importance)
        lines.append(f"[{claim.id}] ({claim_type}, importance: {importance}, confidence: {claim.confidence:.2f})")
        lines.append(f"  Text: {claim.text}")
        if claim.tags:
            lines.append(f"  Tags: {', '.join(claim.tags)}")
        lines.append("")
    return "\n".join(lines)


def _format_evidence_for_prompt(evidence: List[EvidenceItem]) -> str:
    """Format evidence for inclusion in the LLM prompt."""
    if not evidence:
        return "No evidence provided."

    lines = []
    for ev in evidence:
        source = ev.source.value if hasattr(ev.source, 'value') else str(ev.source)
        relevance = ev.relevance.value if hasattr(ev.relevance, 'value') else str(ev.relevance)
        stance = ev.stance.value if hasattr(ev.stance, 'value') else str(ev.stance)

        lines.append(f"[{ev.id}] (source: {source}, relevance: {relevance}, stance: {stance})")
        lines.append(f"  Text: {ev.text}")
        lines.append(f"  Related claims: {', '.join(ev.related_claim_ids)}")
        if ev.topics:
            lines.append(f"  Topics: {', '.join(ev.topics)}")
        if ev.notes:
            lines.append(f"  Notes: {ev.notes}")
        lines.append("")
    return "\n".join(lines)


def _build_user_prompt(slide_id: str, claims: List[Claim], evidence: List[EvidenceItem]) -> str:
    """Build the user prompt for evidence analysis."""
    claims_text = _format_claims_for_prompt(claims)
    evidence_text = _format_evidence_for_prompt(evidence)

    # Summarize stance distribution
    supporting = sum(1 for e in evidence if e.stance == EvidenceStance.SUPPORTS)
    contradicting = sum(1 for e in evidence if e.stance == EvidenceStance.CONTRADICTS)
    neutral = sum(1 for e in evidence if e.stance == EvidenceStance.NEUTRAL_OR_UNCLEAR)

    return f"""## Slide: {slide_id}

## Claims ({len(claims)} total):
{claims_text}

## Evidence ({len(evidence)} total - {supporting} supporting, {contradicting} contradicting, {neutral} neutral/unclear):
{evidence_text}

Analyze the claims and evidence to identify tensions. Focus on:
1. Claims that evidence contradicts
2. High-importance claims lacking support
3. Risks or vulnerabilities not addressed
4. Competitive weaknesses or gaps
5. Ambiguous or vague claims

Output JSON with identified tensions."""


def _parse_category(category_str: str) -> TensionCategory:
    """Parse tension category string to enum."""
    category_map = {
        "contradiction": TensionCategory.CONTRADICTION,
        "missing_evidence": TensionCategory.MISSING_EVIDENCE,
        "risk_exposure": TensionCategory.RISK_EXPOSURE,
        "competitive_gap": TensionCategory.COMPETITIVE_GAP,
        "ambiguity": TensionCategory.AMBIGUITY,
    }
    return category_map.get(category_str.lower(), TensionCategory.AMBIGUITY)


def _parse_severity(severity_str: str) -> TensionSeverity:
    """Parse severity string to enum."""
    severity_map = {
        "high": TensionSeverity.HIGH,
        "medium": TensionSeverity.MEDIUM,
        "low": TensionSeverity.LOW,
    }
    return severity_map.get(severity_str.lower(), TensionSeverity.MEDIUM)


def _parse_analysis_response(
    response: Dict[str, Any],
    slide_id: str,
    num_claims: int,
    num_evidence: int
) -> AnalysisResult:
    """Parse the LLM response into AnalysisResult."""
    tensions_data = response.get("tensions", [])
    meta_data = response.get("meta", {})

    tensions = []
    for t_dict in tensions_data:
        tension = Tension(
            id=t_dict.get("id", f"T{len(tensions)+1}"),
            category=_parse_category(t_dict.get("category", "ambiguity")),
            severity=_parse_severity(t_dict.get("severity", "medium")),
            headline=t_dict.get("headline", "Unspecified tension"),
            description=t_dict.get("description", ""),
            related_claim_ids=t_dict.get("related_claim_ids", []),
            supporting_evidence_ids=t_dict.get("supporting_evidence_ids", []),
            contradicting_evidence_ids=t_dict.get("contradicting_evidence_ids", []),
            risk_tags=t_dict.get("risk_tags", []),
            question_seed=t_dict.get("question_seed"),
            notes=t_dict.get("notes")
        )
        tensions.append(tension)

    meta = AnalysisMeta(
        slide_id=meta_data.get("slide_id", slide_id),
        num_claims=meta_data.get("num_claims", num_claims),
        num_evidence_items=meta_data.get("num_evidence_items", num_evidence),
        num_tensions=meta_data.get("num_tensions", len(tensions)),
        processing_notes=meta_data.get("processing_notes", "")
    )

    return AnalysisResult(slide_id=slide_id, tensions=tensions, meta=meta)


class EvidenceAnalysisAgent:
    """
    Agent responsible for analyzing claims and evidence to identify tensions.

    This is the third step in the reasoning chain:
    1. Claim Extraction -> extracts structured claims
    2. Evidence Selection -> filters and links evidence to claims
    3. Evidence Analysis (this) -> identifies contradictions, gaps, and risks
    4. Question Synthesis -> generates targeted questions from tensions
    """

    def __init__(self, llm_client: LLMClient):
        """Initialize the EvidenceAnalysisAgent."""
        self.llm_client = llm_client

    def analyze(
        self,
        slide_id: str,
        claims: List[Claim],
        evidence: List[EvidenceItem]
    ) -> AnalysisResult:
        """
        Analyze claims and evidence to identify tensions.

        Args:
            slide_id: Identifier for the slide being analyzed.
            claims: List of claims extracted from the slide.
            evidence: List of evidence items linked to claims.

        Returns:
            AnalysisResult containing identified tensions and metadata.
        """
        if not claims:
            logger.warning(f"No claims provided for slide {slide_id}")
            return AnalysisResult(
                slide_id=slide_id,
                tensions=[],
                meta=AnalysisMeta(
                    slide_id=slide_id,
                    num_claims=0,
                    num_evidence_items=len(evidence),
                    num_tensions=0,
                    processing_notes="No claims to analyze"
                )
            )

        user_prompt = _build_user_prompt(slide_id, claims, evidence)

        logger.info(f"Analyzing {len(claims)} claims and {len(evidence)} evidence items for slide {slide_id}")

        try:
            response = self.llm_client.complete_with_system(
                system_prompt=EVIDENCE_ANALYSIS_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                structured=True
            )

            if isinstance(response, dict):
                result = _parse_analysis_response(response, slide_id, len(claims), len(evidence))
            else:
                result = AnalysisResult(
                    slide_id=slide_id,
                    tensions=[],
                    meta=AnalysisMeta(
                        slide_id=slide_id,
                        num_claims=len(claims),
                        num_evidence_items=len(evidence),
                        num_tensions=0,
                        processing_notes="Unexpected response type from LLM"
                    )
                )

            logger.info(f"Analysis complete for slide {slide_id}: {len(result.tensions)} tensions identified")
            return result

        except Exception as e:
            logger.error(f"Failed to analyze slide {slide_id}: {e}")
            return AnalysisResult(
                slide_id=slide_id,
                tensions=[],
                meta=AnalysisMeta(
                    slide_id=slide_id,
                    num_claims=len(claims),
                    num_evidence_items=len(evidence),
                    num_tensions=0,
                    processing_notes=f"Analysis failed: {str(e)}"
                )
            )

    def analyze_with_evidence_result(
        self,
        slide_id: str,
        claims: List[Claim],
        evidence_result: 'EvidenceSelectionResult'
    ) -> AnalysisResult:
        """
        Convenience method to analyze using an EvidenceSelectionResult.

        Args:
            slide_id: Identifier for the slide being analyzed.
            claims: List of claims extracted from the slide.
            evidence_result: Result from EvidenceSelectionAgent.

        Returns:
            AnalysisResult containing identified tensions.
        """
        # Import here to avoid circular imports
        from backend.models.core import EvidenceSelectionResult
        return self.analyze(slide_id, claims, evidence_result.evidence)
