"""
Evidence Selection Agent for filtering and enriching candidate evidence.

This is Step 2 in the multi-step reasoning chain for challenger agents.
"""
from typing import List, Dict, Any
from backend.models.core import (
    Claim,
    CandidateEvidence,
    EvidenceItem,
    EvidenceRelevance,
    EvidenceStance,
    EvidenceSource,
    EvidenceSelectionMeta,
    EvidenceSelectionResult,
)
from backend.models.llm import LLMClient
from backend.logger import get_logger

logger = get_logger(__name__)

EVIDENCE_SELECTION_SYSTEM_PROMPT = """You are an evidence analysis specialist. Given a set of claims and candidate evidence snippets, your job is to:

1. **Filter**: Discard evidence that is not relevant to any of the claims.
2. **Link**: For each relevant piece of evidence, identify which claim(s) it relates to.
3. **Classify Stance**: Determine if the evidence supports, contradicts, or is neutral/unclear relative to the linked claims.
4. **Rate Relevance**: Rate how relevant the evidence is (high/medium/low).
5. **Adjust Score**: Provide a score adjustment (-0.3 to +0.3) based on quality and usefulness:
   - +0.3: Highly credible, directly addresses claims with concrete data
   - +0.1 to +0.2: Good quality, relevant but not exceptional
   - 0.0: Average quality
   - -0.1 to -0.2: Somewhat tangential or low quality
   - -0.3: Barely relevant, should probably be discarded
6. **Tag Topics**: Identify topic tags for each evidence piece.

IMPORTANT RULES:
- Only include evidence that has at least "low" relevance to at least one claim.
- Contradicting evidence is VALUABLE - do not discard it. Mark it as "contradicts" stance.
- If evidence partially supports and partially contradicts, choose the dominant stance or "neutral_or_unclear".
- Be conservative with "high" relevance - reserve it for evidence that directly addresses a claim's core assertion.

Output ONLY valid JSON matching this schema:
{
  "evidence": [
    {
      "id": "E1",
      "relevance": "high | medium | low",
      "stance": "supports | contradicts | neutral_or_unclear",
      "related_claim_ids": ["C1", "C2"],
      "topics": ["cost", "roi", "implementation"],
      "score_adjustment": 0.15,
      "notes": "Brief explanation of why this evidence matters"
    }
  ],
  "meta": {
    "total_candidates": 10,
    "selected_count": 6,
    "discarded_count": 4,
    "processing_notes": "Any overall notes about the evidence quality"
  }
}

Note: Only output the evidence items that passed filtering. Discarded items should not appear in the evidence array."""


def _format_claims_for_prompt(claims: List[Claim]) -> str:
    """Format claims for inclusion in the LLM prompt."""
    if not claims:
        return "No claims provided."

    lines = []
    for claim in claims:
        claim_type = claim.claim_type.value if hasattr(claim.claim_type, 'value') else str(claim.claim_type)
        importance = claim.importance.value if hasattr(claim.importance, 'value') else str(claim.importance)
        lines.append(f"- [{claim.id}] ({claim_type}, {importance}): {claim.text}")
        if claim.tags:
            lines.append(f"  Tags: {', '.join(claim.tags)}")
    return "\n".join(lines)


def _format_candidates_for_prompt(candidates: List[CandidateEvidence]) -> str:
    """Format candidate evidence for inclusion in the LLM prompt."""
    if not candidates:
        return "No candidate evidence provided."

    lines = []
    for i, candidate in enumerate(candidates):
        source = candidate.source.value if hasattr(candidate.source, 'value') else str(candidate.source)
        lines.append(f"[E{i+1}] (source: {source}, collection: {candidate.collection}, score: {candidate.base_score:.3f})")
        lines.append(f"  Text: {candidate.text}")
        lines.append("")
    return "\n".join(lines)


def _build_user_prompt(claims: List[Claim], candidates: List[CandidateEvidence]) -> str:
    """Build the user prompt for evidence selection."""
    claims_text = _format_claims_for_prompt(claims)
    candidates_text = _format_candidates_for_prompt(candidates)

    return f"""## Claims to evaluate evidence against:
{claims_text}

## Candidate Evidence (from vector search):
{candidates_text}

Analyze each piece of candidate evidence and output JSON with only the relevant items."""


def _parse_relevance(relevance_str: str) -> EvidenceRelevance:
    """Parse relevance string to enum."""
    relevance_map = {
        "high": EvidenceRelevance.HIGH,
        "medium": EvidenceRelevance.MEDIUM,
        "low": EvidenceRelevance.LOW,
    }
    return relevance_map.get(relevance_str.lower(), EvidenceRelevance.LOW)


def _parse_stance(stance_str: str) -> EvidenceStance:
    """Parse stance string to enum."""
    stance_map = {
        "supports": EvidenceStance.SUPPORTS,
        "contradicts": EvidenceStance.CONTRADICTS,
        "neutral_or_unclear": EvidenceStance.NEUTRAL_OR_UNCLEAR,
        "neutral": EvidenceStance.NEUTRAL_OR_UNCLEAR,
        "unclear": EvidenceStance.NEUTRAL_OR_UNCLEAR,
    }
    return stance_map.get(stance_str.lower(), EvidenceStance.NEUTRAL_OR_UNCLEAR)


def _parse_source(source_str: str) -> EvidenceSource:
    """Parse source string to enum."""
    source_map = {
        "deck": EvidenceSource.DECK,
        "research": EvidenceSource.RESEARCH,
    }
    return source_map.get(source_str.lower(), EvidenceSource.DECK)


def _clamp_score_adjustment(value: float) -> float:
    """Clamp score adjustment to valid range [-0.3, 0.3]."""
    return max(-0.3, min(0.3, float(value)))


def _parse_evidence_response(
    response: Dict[str, Any],
    candidates: List[CandidateEvidence]
) -> EvidenceSelectionResult:
    """Parse the LLM response into EvidenceSelectionResult."""
    evidence_data = response.get("evidence", [])
    meta_data = response.get("meta", {})

    # Build a map from evidence ID (E1, E2, etc.) to original candidate
    candidate_map: Dict[str, CandidateEvidence] = {}
    for i, candidate in enumerate(candidates):
        candidate_map[f"E{i+1}"] = candidate
        # Also map by original ID in case LLM uses it
        candidate_map[candidate.id] = candidate

    evidence_items = []
    for ev_dict in evidence_data:
        ev_id = ev_dict.get("id", "")

        # Find the original candidate to get source info
        original_candidate = candidate_map.get(ev_id)
        if not original_candidate:
            # Try to find by index if ID doesn't match
            logger.warning(f"Evidence ID {ev_id} not found in candidates, skipping")
            continue

        evidence_item = EvidenceItem(
            id=original_candidate.id,  # Use original ID
            text=original_candidate.text,
            source=original_candidate.source,
            collection=original_candidate.collection,
            relevance=_parse_relevance(ev_dict.get("relevance", "low")),
            stance=_parse_stance(ev_dict.get("stance", "neutral_or_unclear")),
            related_claim_ids=ev_dict.get("related_claim_ids", []),
            topics=ev_dict.get("topics", []),
            score_adjustment=_clamp_score_adjustment(ev_dict.get("score_adjustment", 0.0)),
            notes=ev_dict.get("notes")
        )
        evidence_items.append(evidence_item)

    meta = EvidenceSelectionMeta(
        total_candidates=meta_data.get("total_candidates", len(candidates)),
        selected_count=meta_data.get("selected_count", len(evidence_items)),
        discarded_count=meta_data.get("discarded_count", len(candidates) - len(evidence_items)),
        processing_notes=meta_data.get("processing_notes", "")
    )

    return EvidenceSelectionResult(evidence=evidence_items, meta=meta)


class EvidenceSelectionAgent:
    """
    Agent responsible for filtering and enriching candidate evidence.

    This is the second step in the reasoning chain:
    1. Claim Extraction -> extracts structured claims
    2. Evidence Selection (this) -> filters and links evidence to claims
    3. Challenge Formulation -> generates targeted questions
    """

    def __init__(self, llm_client: LLMClient):
        """Initialize the EvidenceSelectionAgent."""
        self.llm_client = llm_client

    def select_evidence(
        self,
        claims: List[Claim],
        candidates: List[CandidateEvidence]
    ) -> EvidenceSelectionResult:
        """
        Select and enrich evidence from candidate snippets.

        Args:
            claims: List of claims to evaluate evidence against.
            candidates: List of candidate evidence from vector search.

        Returns:
            EvidenceSelectionResult containing filtered and enriched evidence.
        """
        if not claims:
            logger.warning("No claims provided for evidence selection")
            return EvidenceSelectionResult(
                evidence=[],
                meta=EvidenceSelectionMeta(
                    total_candidates=len(candidates),
                    selected_count=0,
                    discarded_count=len(candidates),
                    processing_notes="No claims to evaluate against"
                )
            )

        if not candidates:
            logger.warning("No candidate evidence provided for selection")
            return EvidenceSelectionResult(
                evidence=[],
                meta=EvidenceSelectionMeta(
                    total_candidates=0,
                    selected_count=0,
                    discarded_count=0,
                    processing_notes="No candidate evidence to evaluate"
                )
            )

        user_prompt = _build_user_prompt(claims, candidates)

        logger.info(f"Selecting evidence: {len(candidates)} candidates for {len(claims)} claims")

        try:
            response = self.llm_client.complete_with_system(
                system_prompt=EVIDENCE_SELECTION_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                structured=True
            )

            if isinstance(response, dict):
                result = _parse_evidence_response(response, candidates)
            else:
                result = EvidenceSelectionResult(
                    evidence=[],
                    meta=EvidenceSelectionMeta(
                        total_candidates=len(candidates),
                        selected_count=0,
                        discarded_count=len(candidates),
                        processing_notes="Unexpected response type from LLM"
                    )
                )

            logger.info(
                f"Evidence selection complete: {result.meta.selected_count} selected, "
                f"{result.meta.discarded_count} discarded"
            )
            return result

        except Exception as e:
            logger.error(f"Failed to select evidence: {e}")
            return EvidenceSelectionResult(
                evidence=[],
                meta=EvidenceSelectionMeta(
                    total_candidates=len(candidates),
                    selected_count=0,
                    discarded_count=len(candidates),
                    processing_notes=f"Selection failed: {str(e)}"
                )
            )

    def select_evidence_for_slide(
        self,
        claims: List[Claim],
        deck_chunks: List[CandidateEvidence],
        research_facts: List[CandidateEvidence]
    ) -> EvidenceSelectionResult:
        """
        Convenience method to select evidence from both deck and research sources.

        Args:
            claims: List of claims to evaluate evidence against.
            deck_chunks: Candidate evidence from deck chunks.
            research_facts: Candidate evidence from research facts.

        Returns:
            EvidenceSelectionResult containing filtered and enriched evidence.
        """
        # Combine all candidates
        all_candidates = deck_chunks + research_facts
        return self.select_evidence(claims, all_candidates)
