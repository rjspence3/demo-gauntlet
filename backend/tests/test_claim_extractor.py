"""
Tests for the ClaimExtractionAgent.
"""
import pytest
from unittest.mock import MagicMock, patch
from backend.challenges.claim_extractor import (
    ClaimExtractionAgent,
    _build_user_prompt,
    _parse_claim_type,
    _parse_importance,
    _parse_origin,
    _parse_source_spans,
    _parse_claims_response,
    CLAIM_EXTRACTION_SYSTEM_PROMPT
)
from backend.models.core import (
    Slide,
    Claim,
    ClaimType,
    ClaimImportance,
    SourceOrigin,
    SourceSpan,
    ClaimExtractionMeta,
    ClaimExtractionResult
)
from backend.models.llm import MockLLM


class TestClaimTypeParser:
    """Tests for claim type parsing."""

    def test_parse_factual(self):
        """Test parsing factual claim type."""
        assert _parse_claim_type("factual") == ClaimType.FACTUAL
        assert _parse_claim_type("FACTUAL") == ClaimType.FACTUAL

    def test_parse_forecast(self):
        """Test parsing forecast claim type."""
        assert _parse_claim_type("forecast") == ClaimType.FORECAST

    def test_parse_assumption(self):
        """Test parsing assumption claim type."""
        assert _parse_claim_type("assumption") == ClaimType.ASSUMPTION

    def test_parse_recommendation(self):
        """Test parsing recommendation claim type."""
        assert _parse_claim_type("recommendation") == ClaimType.RECOMMENDATION

    def test_parse_metric(self):
        """Test parsing metric claim type."""
        assert _parse_claim_type("metric") == ClaimType.METRIC

    def test_parse_unknown_defaults_to_factual(self):
        """Test that unknown types default to factual."""
        assert _parse_claim_type("unknown") == ClaimType.FACTUAL
        assert _parse_claim_type("") == ClaimType.FACTUAL


class TestImportanceParser:
    """Tests for importance parsing."""

    def test_parse_high(self):
        """Test parsing high importance."""
        assert _parse_importance("high") == ClaimImportance.HIGH
        assert _parse_importance("HIGH") == ClaimImportance.HIGH

    def test_parse_medium(self):
        """Test parsing medium importance."""
        assert _parse_importance("medium") == ClaimImportance.MEDIUM

    def test_parse_low(self):
        """Test parsing low importance."""
        assert _parse_importance("low") == ClaimImportance.LOW

    def test_parse_unknown_defaults_to_medium(self):
        """Test that unknown importance defaults to medium."""
        assert _parse_importance("unknown") == ClaimImportance.MEDIUM


class TestOriginParser:
    """Tests for source origin parsing."""

    def test_parse_slide_body(self):
        """Test parsing slide_body origin."""
        assert _parse_origin("slide_body") == SourceOrigin.SLIDE_BODY

    def test_parse_speaker_notes(self):
        """Test parsing speaker_notes origin."""
        assert _parse_origin("speaker_notes") == SourceOrigin.SPEAKER_NOTES

    def test_parse_title(self):
        """Test parsing title origin."""
        assert _parse_origin("title") == SourceOrigin.TITLE

    def test_parse_unknown_defaults_to_slide_body(self):
        """Test that unknown origin defaults to slide_body."""
        assert _parse_origin("unknown") == SourceOrigin.SLIDE_BODY


class TestSourceSpanParser:
    """Tests for source span parsing."""

    def test_parse_empty_list(self):
        """Test parsing empty span list."""
        result = _parse_source_spans([], 100)
        assert result == []

    def test_parse_single_span(self):
        """Test parsing a single span."""
        spans_data = [{"start": 0, "end": 42, "origin": "slide_body"}]
        result = _parse_source_spans(spans_data, 100)

        assert len(result) == 1
        assert result[0].start == 0
        assert result[0].end == 42
        assert result[0].origin == SourceOrigin.SLIDE_BODY

    def test_parse_span_with_from_to_keys(self):
        """Test parsing span with 'from' and 'to' keys (alternative format)."""
        spans_data = [{"from": 10, "to": 50, "origin": "title"}]
        result = _parse_source_spans(spans_data, 100)

        assert len(result) == 1
        assert result[0].start == 10
        assert result[0].end == 50
        assert result[0].origin == SourceOrigin.TITLE

    def test_parse_multiple_spans(self):
        """Test parsing multiple spans."""
        spans_data = [
            {"start": 0, "end": 20, "origin": "title"},
            {"start": 25, "end": 100, "origin": "slide_body"},
        ]
        result = _parse_source_spans(spans_data, 200)

        assert len(result) == 2
        assert result[0].origin == SourceOrigin.TITLE
        assert result[1].origin == SourceOrigin.SLIDE_BODY


class TestBuildUserPrompt:
    """Tests for user prompt building."""

    def test_build_prompt_without_notes(self):
        """Test building prompt for slide without speaker notes."""
        slide = Slide(
            index=0,
            title="Introduction",
            text="This is the slide content.",
            notes=""
        )
        prompt = _build_user_prompt(slide)

        assert "### Slide 0" in prompt
        assert "**Title:** Introduction" in prompt
        assert "**Body:**" in prompt
        assert "This is the slide content." in prompt
        assert "**Speaker Notes:**" not in prompt

    def test_build_prompt_with_notes(self):
        """Test building prompt for slide with speaker notes."""
        slide = Slide(
            index=1,
            title="Key Metrics",
            text="Revenue growth: 150%",
            notes="Emphasize the growth trajectory"
        )
        prompt = _build_user_prompt(slide)

        assert "### Slide 1" in prompt
        assert "**Title:** Key Metrics" in prompt
        assert "Revenue growth: 150%" in prompt
        assert "**Speaker Notes:**" in prompt
        assert "Emphasize the growth trajectory" in prompt


class TestParseClaimsResponse:
    """Tests for parsing LLM response into ClaimExtractionResult."""

    def test_parse_empty_response(self):
        """Test parsing empty response."""
        slide = Slide(index=0, title="Test", text="Content", notes="")
        result = _parse_claims_response({}, slide)

        assert len(result.claims) == 0
        assert result.meta.slide_index == 0

    def test_parse_full_response(self):
        """Test parsing a complete response."""
        response = {
            "claims": [
                {
                    "id": "C1",
                    "text": "Revenue will grow 150% next year",
                    "type": "forecast",
                    "importance": "high",
                    "confidence": 0.75,
                    "tags": ["revenue", "growth"],
                    "source_spans": [
                        {"start": 0, "end": 35, "origin": "slide_body"}
                    ]
                }
            ],
            "meta": {
                "slide_index": 2,
                "used_speaker_notes": True,
                "notes": "High-confidence forecast"
            }
        }

        slide = Slide(index=2, title="Test", text="Content that is long enough to cover the span range of 35 characters.", notes="")
        result = _parse_claims_response(response, slide)

        assert len(result.claims) == 1
        claim = result.claims[0]
        assert claim.id == "C1"
        assert claim.text == "Revenue will grow 150% next year"
        assert claim.claim_type == ClaimType.FORECAST
        assert claim.importance == ClaimImportance.HIGH
        assert claim.confidence == 0.75
        assert claim.tags == ["revenue", "growth"]
        assert len(claim.source_spans) == 1
        assert claim.source_spans[0].start == 0
        assert claim.source_spans[0].end == 35

        assert result.meta.slide_index == 2
        assert result.meta.used_speaker_notes is True
        assert result.meta.notes == "High-confidence forecast"

    def test_parse_response_with_missing_optional_fields(self):
        """Test parsing response with missing optional fields."""
        response = {
            "claims": [
                {
                    "id": "C1",
                    "text": "Simple claim"
                }
            ],
            "meta": {}
        }

        slide = Slide(index=5, title="Test", text="Content", notes="")
        result = _parse_claims_response(response, slide)

        assert len(result.claims) == 1
        claim = result.claims[0]
        assert claim.id == "C1"
        assert claim.text == "Simple claim"
        assert claim.claim_type == ClaimType.FACTUAL  # default
        assert claim.importance == ClaimImportance.MEDIUM  # default
        assert claim.confidence == 0.5  # default
        assert claim.tags == []
        assert claim.source_spans == []

        assert result.meta.slide_index == 5  # Uses passed value when not in response


class TestClaimExtractionAgent:
    """Tests for the ClaimExtractionAgent class."""

    def test_init(self):
        """Test agent initialization."""
        llm_client = MockLLM()
        agent = ClaimExtractionAgent(llm_client)
        assert agent.llm_client == llm_client

    def test_extract_claims_with_mock_llm(self):
        """Test claim extraction with mock LLM."""
        llm_client = MockLLM()
        agent = ClaimExtractionAgent(llm_client)

        slide = Slide(
            index=0,
            title="Test Slide",
            text="Our AI solution reduces costs by 40%.",
            notes=""
        )

        result = agent.extract_claims(slide)

        # MockLLM returns a default claim structure
        assert isinstance(result, ClaimExtractionResult)
        assert len(result.claims) >= 1
        assert result.meta.slide_index == 0

    def test_extract_claims_batch(self):
        """Test batch claim extraction."""
        llm_client = MockLLM()
        agent = ClaimExtractionAgent(llm_client)

        slides = [
            Slide(index=0, title="Slide 1", text="Content 1", notes=""),
            Slide(index=1, title="Slide 2", text="Content 2", notes=""),
            Slide(index=2, title="Slide 3", text="Content 3", notes=""),
        ]

        results = agent.extract_claims_batch(slides)

        assert len(results) == 3
        for i, result in enumerate(results):
            assert isinstance(result, ClaimExtractionResult)

    def test_extract_claims_handles_exception(self):
        """Test that extraction handles exceptions gracefully."""
        llm_client = MagicMock()
        llm_client.complete_with_system.side_effect = Exception("API Error")

        agent = ClaimExtractionAgent(llm_client)
        slide = Slide(index=0, title="Test", text="Content", notes="")

        result = agent.extract_claims(slide)

        # Should return empty result on error
        assert len(result.claims) == 0
        assert "Extraction failed" in result.meta.notes


class TestSystemPrompt:
    """Tests for the system prompt constant."""

    def test_system_prompt_contains_key_instructions(self):
        """Test that system prompt contains essential instructions."""
        assert "claim extraction specialist" in CLAIM_EXTRACTION_SYSTEM_PROMPT.lower()
        assert "factual" in CLAIM_EXTRACTION_SYSTEM_PROMPT.lower()
        assert "forecast" in CLAIM_EXTRACTION_SYSTEM_PROMPT.lower()
        assert "assumption" in CLAIM_EXTRACTION_SYSTEM_PROMPT.lower()
        assert "importance" in CLAIM_EXTRACTION_SYSTEM_PROMPT.lower()
        assert "confidence" in CLAIM_EXTRACTION_SYSTEM_PROMPT.lower()
        assert "json" in CLAIM_EXTRACTION_SYSTEM_PROMPT.lower()
