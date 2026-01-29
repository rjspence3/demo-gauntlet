"""
Claim Extraction Agent for extracting substantive claims from slides.

This is Step 1 in the multi-step reasoning chain for challenger agents.
"""
import json
from typing import List, Dict, Any, Optional
from backend.models.core import (
    Slide,
    Claim,
    ClaimType,
    ClaimImportance,
    SourceOrigin,
    SourceSpan,
    ClaimExtractionMeta,
    ClaimExtractionResult,
)
from backend.models.llm import LLMClient
from backend.logger import get_logger

logger = get_logger(__name__)

CLAIM_EXTRACTION_SYSTEM_PROMPT = """You are a claim extraction specialist. Given slide content (title, body, and optional speaker notes), identify all substantive claims the presenter makes. Focus on:
- Factual assertions (metrics, stats, historical data)
- Forecasts and projections (future outcomes, growth, timelines)
- Assumptions the slide relies on (unstated dependencies)
- Recommendations or calls-to-action
- Key metrics mentioned without proof

For each claim:
1. Write it as a clear, standalone statement.
2. Tag it by theme (ai, cost, risk, security, governance, adoption, roi, timeline, compliance, integration, etc.).
3. Rate importance (high/medium/low) and confidence (0-1 how clearly the slide states it).
4. Note the source span (character offsets, origin: title | slide_body | speaker_notes).

Output ONLY valid JSON matching this schema:
{
  "claims": [
    {
      "id": "C1",
      "text": "Concise statement of the claim",
      "type": "factual | forecast | assumption | recommendation | metric",
      "importance": "high | medium | low",
      "confidence": 0.0,
      "tags": ["ai", "governance", "cost"],
      "source_spans": [
        {"start": 0, "end": 42, "origin": "slide_body | speaker_notes | title"}
      ]
    }
  ],
  "meta": {
    "slide_index": 0,
    "used_speaker_notes": true,
    "notes": "Any brief notes for downstream agents"
  }
}"""


def _build_user_prompt(slide: Slide) -> str:
    """Build the user prompt for claim extraction from a slide."""
    prompt = f"""### Slide {slide.index}
**Title:** {slide.title}
**Body:**
{slide.text}
"""
    if slide.notes and slide.notes.strip():
        prompt += f"""
**Speaker Notes:**
{slide.notes}
"""
    prompt += "\nPlease output JSON following the schema."
    return prompt


def _parse_claim_type(type_str: str) -> ClaimType:
    """Parse claim type string to enum."""
    type_map = {
        "factual": ClaimType.FACTUAL,
        "forecast": ClaimType.FORECAST,
        "assumption": ClaimType.ASSUMPTION,
        "recommendation": ClaimType.RECOMMENDATION,
        "metric": ClaimType.METRIC,
    }
    return type_map.get(type_str.lower(), ClaimType.FACTUAL)


def _parse_importance(importance_str: str) -> ClaimImportance:
    """Parse importance string to enum."""
    importance_map = {
        "high": ClaimImportance.HIGH,
        "medium": ClaimImportance.MEDIUM,
        "low": ClaimImportance.LOW,
    }
    return importance_map.get(importance_str.lower(), ClaimImportance.MEDIUM)


def _parse_origin(origin_str: str) -> SourceOrigin:
    """Parse source origin string to enum."""
    origin_map = {
        "slide_body": SourceOrigin.SLIDE_BODY,
        "speaker_notes": SourceOrigin.SPEAKER_NOTES,
        "title": SourceOrigin.TITLE,
    }
    return origin_map.get(origin_str.lower(), SourceOrigin.SLIDE_BODY)


def _parse_source_spans(spans_data: List[Dict[str, Any]], slide_text_len: int) -> List[SourceSpan]:
    """Parse source spans from JSON data and validate against slide length."""
    result = []
    for span in spans_data:
        start = span.get("start", span.get("from", 0))
        end = span.get("end", span.get("to", 0))
        origin = _parse_origin(span.get("origin", "slide_body"))

        # H-3: Validate source spans
        if start < 0:
            start = 0
        
        # Only validate length for SLIDE_BODY origin as it maps to slide.text
        if origin == SourceOrigin.SLIDE_BODY:
            if end > slide_text_len:
                end = slide_text_len
            if start > slide_text_len:
                start = slide_text_len
        
        if end < start:
            end = start

        result.append(SourceSpan(
            start=start,
            end=end,
            origin=origin
        ))
    return result


def _parse_claims_response(response: Dict[str, Any], slide: Slide) -> ClaimExtractionResult:
    """Parse the LLM response into ClaimExtractionResult."""
    claims_data = response.get("claims", [])
    meta_data = response.get("meta", {})
    
    slide_text_len = len(slide.text)

    claims = []
    for claim_dict in claims_data:
        claim = Claim(
            id=claim_dict.get("id", f"C{len(claims)+1}"),
            text=claim_dict.get("text", ""),
            claim_type=_parse_claim_type(claim_dict.get("type", "factual")),
            importance=_parse_importance(claim_dict.get("importance", "medium")),
            confidence=float(claim_dict.get("confidence", 0.5)),
            tags=claim_dict.get("tags", []),
            source_spans=_parse_source_spans(
                claim_dict.get("source_spans", []), 
                slide_text_len
            )
        )
        claims.append(claim)

    meta = ClaimExtractionMeta(
        slide_index=meta_data.get("slide_index", slide.index),
        used_speaker_notes=meta_data.get("used_speaker_notes", False),
        notes=meta_data.get("notes", "")
    )

    return ClaimExtractionResult(claims=claims, meta=meta)


class ClaimExtractionAgent:
    """
    Agent responsible for extracting claims from presentation slides.

    This is the first step in the reasoning chain:
    1. Claim Extraction (this) -> extracts structured claims
    2. Evidence Retrieval -> finds supporting/contradicting evidence
    3. Challenge Formulation -> generates targeted questions
    """

    def __init__(self, llm_client: LLMClient):
        """Initialize the ClaimExtractionAgent."""
        self.llm_client = llm_client

    def extract_claims(self, slide: Slide) -> ClaimExtractionResult:
        """
        Extract claims from a single slide.

        Args:
            slide: The slide to extract claims from.

        Returns:
            ClaimExtractionResult containing extracted claims and metadata.
        """
        user_prompt = _build_user_prompt(slide)

        logger.info(f"Extracting claims from slide {slide.index}: {slide.title}")

        try:
            response = self.llm_client.complete_with_system(
                system_prompt=CLAIM_EXTRACTION_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                structured=True
            )
            # complete_with_system returns Dict when structured=True
            if isinstance(response, dict):
                result = _parse_claims_response(response, slide)
            else:
                result = ClaimExtractionResult(
                    claims=[],
                    meta=ClaimExtractionMeta(
                        slide_index=slide.index,
                        used_speaker_notes=bool(slide.notes),
                        notes="Unexpected response type"
                    )
                )
            logger.info(f"Extracted {len(result.claims)} claims from slide {slide.index}")
            return result
        except Exception as e:
            logger.error(f"Failed to extract claims from slide {slide.index}: {e}")
            # Return empty result on failure
            return ClaimExtractionResult(
                claims=[],
                meta=ClaimExtractionMeta(
                    slide_index=slide.index,
                    used_speaker_notes=bool(slide.notes),
                    notes=f"Extraction failed: {str(e)}"
                )
            )

    def extract_claims_batch(self, slides: List[Slide]) -> List[ClaimExtractionResult]:
        """
        Extract claims from multiple slides.

        Args:
            slides: List of slides to extract claims from.

        Returns:
            List of ClaimExtractionResult, one per slide.
        """
        results = []
        for slide in slides:
            result = self.extract_claims(slide)
            results.append(result)
        return results
