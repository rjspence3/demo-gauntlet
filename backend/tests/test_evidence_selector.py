"""
Tests for the EvidenceSelectionAgent.
"""
import pytest
from unittest.mock import MagicMock
from backend.challenges.evidence_selector import (
    EvidenceSelectionAgent,
    _format_claims_for_prompt,
    _format_candidates_for_prompt,
    _build_user_prompt,
    _parse_relevance,
    _parse_stance,
    _parse_source,
    _clamp_score_adjustment,
    _parse_evidence_response,
    EVIDENCE_SELECTION_SYSTEM_PROMPT,
)
from backend.models.core import (
    Claim,
    ClaimType,
    ClaimImportance,
    CandidateEvidence,
    EvidenceItem,
    EvidenceRelevance,
    EvidenceStance,
    EvidenceSource,
    EvidenceSelectionMeta,
    EvidenceSelectionResult,
)
from backend.models.llm import MockLLM


class TestRelevanceParser:
    """Tests for relevance parsing."""

    def test_parse_high(self):
        """Test parsing high relevance."""
        assert _parse_relevance("high") == EvidenceRelevance.HIGH
        assert _parse_relevance("HIGH") == EvidenceRelevance.HIGH

    def test_parse_medium(self):
        """Test parsing medium relevance."""
        assert _parse_relevance("medium") == EvidenceRelevance.MEDIUM

    def test_parse_low(self):
        """Test parsing low relevance."""
        assert _parse_relevance("low") == EvidenceRelevance.LOW

    def test_parse_unknown_defaults_to_low(self):
        """Test that unknown relevance defaults to low."""
        assert _parse_relevance("unknown") == EvidenceRelevance.LOW
        assert _parse_relevance("") == EvidenceRelevance.LOW


class TestStanceParser:
    """Tests for stance parsing."""

    def test_parse_supports(self):
        """Test parsing supports stance."""
        assert _parse_stance("supports") == EvidenceStance.SUPPORTS
        assert _parse_stance("SUPPORTS") == EvidenceStance.SUPPORTS

    def test_parse_contradicts(self):
        """Test parsing contradicts stance."""
        assert _parse_stance("contradicts") == EvidenceStance.CONTRADICTS

    def test_parse_neutral_or_unclear(self):
        """Test parsing neutral_or_unclear stance."""
        assert _parse_stance("neutral_or_unclear") == EvidenceStance.NEUTRAL_OR_UNCLEAR

    def test_parse_neutral_shorthand(self):
        """Test parsing neutral shorthand."""
        assert _parse_stance("neutral") == EvidenceStance.NEUTRAL_OR_UNCLEAR

    def test_parse_unclear_shorthand(self):
        """Test parsing unclear shorthand."""
        assert _parse_stance("unclear") == EvidenceStance.NEUTRAL_OR_UNCLEAR

    def test_parse_unknown_defaults_to_neutral(self):
        """Test that unknown stance defaults to neutral_or_unclear."""
        assert _parse_stance("unknown") == EvidenceStance.NEUTRAL_OR_UNCLEAR


class TestSourceParser:
    """Tests for source parsing."""

    def test_parse_deck(self):
        """Test parsing deck source."""
        assert _parse_source("deck") == EvidenceSource.DECK

    def test_parse_research(self):
        """Test parsing research source."""
        assert _parse_source("research") == EvidenceSource.RESEARCH

    def test_parse_unknown_defaults_to_deck(self):
        """Test that unknown source defaults to deck."""
        assert _parse_source("unknown") == EvidenceSource.DECK


class TestClampScoreAdjustment:
    """Tests for score adjustment clamping."""

    def test_clamp_within_range(self):
        """Test values within range are unchanged."""
        assert _clamp_score_adjustment(0.0) == 0.0
        assert _clamp_score_adjustment(0.15) == 0.15
        assert _clamp_score_adjustment(-0.15) == -0.15
        assert _clamp_score_adjustment(0.3) == 0.3
        assert _clamp_score_adjustment(-0.3) == -0.3

    def test_clamp_above_max(self):
        """Test values above max are clamped."""
        assert _clamp_score_adjustment(0.5) == 0.3
        assert _clamp_score_adjustment(1.0) == 0.3

    def test_clamp_below_min(self):
        """Test values below min are clamped."""
        assert _clamp_score_adjustment(-0.5) == -0.3
        assert _clamp_score_adjustment(-1.0) == -0.3


class TestFormatClaimsForPrompt:
    """Tests for formatting claims for prompt."""

    def test_format_empty_claims(self):
        """Test formatting with no claims."""
        result = _format_claims_for_prompt([])
        assert "No claims provided" in result

    def test_format_single_claim(self):
        """Test formatting a single claim."""
        claims = [
            Claim(
                id="C1",
                text="Revenue will grow 50%",
                claim_type=ClaimType.FORECAST,
                importance=ClaimImportance.HIGH,
                confidence=0.8,
                tags=["revenue", "growth"]
            )
        ]
        result = _format_claims_for_prompt(claims)

        assert "[C1]" in result
        assert "forecast" in result
        assert "high" in result
        assert "Revenue will grow 50%" in result
        assert "revenue" in result
        assert "growth" in result

    def test_format_multiple_claims(self):
        """Test formatting multiple claims."""
        claims = [
            Claim(
                id="C1",
                text="Claim one",
                claim_type=ClaimType.FACTUAL,
                importance=ClaimImportance.MEDIUM,
                confidence=0.7
            ),
            Claim(
                id="C2",
                text="Claim two",
                claim_type=ClaimType.ASSUMPTION,
                importance=ClaimImportance.LOW,
                confidence=0.5
            )
        ]
        result = _format_claims_for_prompt(claims)

        assert "[C1]" in result
        assert "[C2]" in result
        assert "Claim one" in result
        assert "Claim two" in result


class TestFormatCandidatesForPrompt:
    """Tests for formatting candidates for prompt."""

    def test_format_empty_candidates(self):
        """Test formatting with no candidates."""
        result = _format_candidates_for_prompt([])
        assert "No candidate evidence" in result

    def test_format_single_candidate(self):
        """Test formatting a single candidate."""
        candidates = [
            CandidateEvidence(
                id="ev1",
                text="Evidence text here",
                source=EvidenceSource.DECK,
                collection="deck_chunks",
                base_score=0.85
            )
        ]
        result = _format_candidates_for_prompt(candidates)

        assert "[E1]" in result
        assert "deck" in result
        assert "deck_chunks" in result
        assert "0.850" in result
        assert "Evidence text here" in result

    def test_format_multiple_candidates(self):
        """Test formatting multiple candidates."""
        candidates = [
            CandidateEvidence(
                id="ev1",
                text="First evidence",
                source=EvidenceSource.DECK,
                collection="deck_chunks",
                base_score=0.9
            ),
            CandidateEvidence(
                id="ev2",
                text="Second evidence",
                source=EvidenceSource.RESEARCH,
                collection="research_facts",
                base_score=0.75
            )
        ]
        result = _format_candidates_for_prompt(candidates)

        assert "[E1]" in result
        assert "[E2]" in result
        assert "First evidence" in result
        assert "Second evidence" in result
        assert "deck" in result
        assert "research" in result


class TestBuildUserPrompt:
    """Tests for building user prompt."""

    def test_build_prompt_structure(self):
        """Test that user prompt has proper structure."""
        claims = [
            Claim(
                id="C1",
                text="Test claim",
                claim_type=ClaimType.FACTUAL,
                importance=ClaimImportance.MEDIUM,
                confidence=0.8
            )
        ]
        candidates = [
            CandidateEvidence(
                id="ev1",
                text="Test evidence",
                source=EvidenceSource.DECK,
                collection="deck_chunks",
                base_score=0.8
            )
        ]
        result = _build_user_prompt(claims, candidates)

        assert "Claims to evaluate" in result
        assert "Candidate Evidence" in result
        assert "Test claim" in result
        assert "Test evidence" in result


class TestParseEvidenceResponse:
    """Tests for parsing evidence response."""

    def test_parse_empty_response(self):
        """Test parsing empty response."""
        candidates = [
            CandidateEvidence(
                id="ev1",
                text="Test",
                source=EvidenceSource.DECK,
                collection="test",
                base_score=0.8
            )
        ]
        result = _parse_evidence_response({}, candidates)

        assert len(result.evidence) == 0
        assert result.meta.total_candidates == 1

    def test_parse_full_response(self):
        """Test parsing a complete response."""
        candidates = [
            CandidateEvidence(
                id="ev1",
                text="Evidence about costs",
                source=EvidenceSource.RESEARCH,
                collection="research_facts",
                base_score=0.85
            ),
            CandidateEvidence(
                id="ev2",
                text="Evidence about timeline",
                source=EvidenceSource.DECK,
                collection="deck_chunks",
                base_score=0.7
            )
        ]
        response = {
            "evidence": [
                {
                    "id": "E1",
                    "relevance": "high",
                    "stance": "contradicts",
                    "related_claim_ids": ["C1", "C2"],
                    "topics": ["cost", "roi"],
                    "score_adjustment": 0.2,
                    "notes": "Strong contradicting evidence"
                }
            ],
            "meta": {
                "total_candidates": 2,
                "selected_count": 1,
                "discarded_count": 1,
                "processing_notes": "One item discarded as irrelevant"
            }
        }

        result = _parse_evidence_response(response, candidates)

        assert len(result.evidence) == 1
        ev = result.evidence[0]
        assert ev.id == "ev1"  # Original ID preserved
        assert ev.text == "Evidence about costs"
        assert ev.source == EvidenceSource.RESEARCH
        assert ev.collection == "research_facts"
        assert ev.relevance == EvidenceRelevance.HIGH
        assert ev.stance == EvidenceStance.CONTRADICTS
        assert ev.related_claim_ids == ["C1", "C2"]
        assert ev.topics == ["cost", "roi"]
        assert ev.score_adjustment == 0.2
        assert ev.notes == "Strong contradicting evidence"

        assert result.meta.total_candidates == 2
        assert result.meta.selected_count == 1
        assert result.meta.discarded_count == 1

    def test_parse_response_with_missing_optional_fields(self):
        """Test parsing response with missing optional fields."""
        candidates = [
            CandidateEvidence(
                id="ev1",
                text="Test",
                source=EvidenceSource.DECK,
                collection="test",
                base_score=0.8
            )
        ]
        response = {
            "evidence": [
                {
                    "id": "E1"
                }
            ],
            "meta": {}
        }

        result = _parse_evidence_response(response, candidates)

        assert len(result.evidence) == 1
        ev = result.evidence[0]
        assert ev.relevance == EvidenceRelevance.LOW  # default
        assert ev.stance == EvidenceStance.NEUTRAL_OR_UNCLEAR  # default
        assert ev.related_claim_ids == []
        assert ev.topics == []
        assert ev.score_adjustment == 0.0
        assert ev.notes is None

    def test_parse_skips_unknown_evidence_ids(self):
        """Test that unknown evidence IDs are skipped."""
        candidates = [
            CandidateEvidence(
                id="ev1",
                text="Test",
                source=EvidenceSource.DECK,
                collection="test",
                base_score=0.8
            )
        ]
        response = {
            "evidence": [
                {
                    "id": "E99",  # doesn't exist
                    "relevance": "high",
                    "stance": "supports"
                }
            ],
            "meta": {}
        }

        result = _parse_evidence_response(response, candidates)
        assert len(result.evidence) == 0

    def test_parse_score_adjustment_clamping(self):
        """Test that score adjustment is clamped during parsing."""
        candidates = [
            CandidateEvidence(
                id="ev1",
                text="Test",
                source=EvidenceSource.DECK,
                collection="test",
                base_score=0.8
            )
        ]
        response = {
            "evidence": [
                {
                    "id": "E1",
                    "score_adjustment": 0.9  # out of range
                }
            ],
            "meta": {}
        }

        result = _parse_evidence_response(response, candidates)
        assert result.evidence[0].score_adjustment == 0.3  # clamped


class TestEvidenceSelectionAgent:
    """Tests for the EvidenceSelectionAgent class."""

    def test_init(self):
        """Test agent initialization."""
        llm_client = MockLLM()
        agent = EvidenceSelectionAgent(llm_client)
        assert agent.llm_client == llm_client

    def test_select_evidence_with_mock_llm(self):
        """Test evidence selection with mock LLM."""
        llm_client = MockLLM()
        agent = EvidenceSelectionAgent(llm_client)

        claims = [
            Claim(
                id="C1",
                text="Test claim",
                claim_type=ClaimType.FACTUAL,
                importance=ClaimImportance.MEDIUM,
                confidence=0.8
            )
        ]
        candidates = [
            CandidateEvidence(
                id="ev1",
                text="Test evidence",
                source=EvidenceSource.DECK,
                collection="deck_chunks",
                base_score=0.8
            ),
            CandidateEvidence(
                id="ev2",
                text="Another evidence",
                source=EvidenceSource.RESEARCH,
                collection="research_facts",
                base_score=0.7
            )
        ]

        result = agent.select_evidence(claims, candidates)

        assert isinstance(result, EvidenceSelectionResult)
        assert len(result.evidence) >= 1  # MockLLM returns at least one item
        assert isinstance(result.meta, EvidenceSelectionMeta)

    def test_select_evidence_with_no_claims(self):
        """Test evidence selection with no claims."""
        llm_client = MockLLM()
        agent = EvidenceSelectionAgent(llm_client)

        candidates = [
            CandidateEvidence(
                id="ev1",
                text="Test",
                source=EvidenceSource.DECK,
                collection="test",
                base_score=0.8
            )
        ]

        result = agent.select_evidence([], candidates)

        assert len(result.evidence) == 0
        assert result.meta.selected_count == 0
        assert "No claims" in result.meta.processing_notes

    def test_select_evidence_with_no_candidates(self):
        """Test evidence selection with no candidates."""
        llm_client = MockLLM()
        agent = EvidenceSelectionAgent(llm_client)

        claims = [
            Claim(
                id="C1",
                text="Test claim",
                claim_type=ClaimType.FACTUAL,
                importance=ClaimImportance.MEDIUM,
                confidence=0.8
            )
        ]

        result = agent.select_evidence(claims, [])

        assert len(result.evidence) == 0
        assert result.meta.total_candidates == 0
        assert "No candidate evidence" in result.meta.processing_notes

    def test_select_evidence_handles_exception(self):
        """Test that selection handles exceptions gracefully."""
        llm_client = MagicMock()
        llm_client.complete_with_system.side_effect = Exception("API Error")

        agent = EvidenceSelectionAgent(llm_client)
        claims = [
            Claim(
                id="C1",
                text="Test",
                claim_type=ClaimType.FACTUAL,
                importance=ClaimImportance.MEDIUM,
                confidence=0.8
            )
        ]
        candidates = [
            CandidateEvidence(
                id="ev1",
                text="Test",
                source=EvidenceSource.DECK,
                collection="test",
                base_score=0.8
            )
        ]

        result = agent.select_evidence(claims, candidates)

        assert len(result.evidence) == 0
        assert "Selection failed" in result.meta.processing_notes

    def test_select_evidence_for_slide_combines_sources(self):
        """Test convenience method combines deck and research sources."""
        llm_client = MockLLM()
        agent = EvidenceSelectionAgent(llm_client)

        claims = [
            Claim(
                id="C1",
                text="Test claim",
                claim_type=ClaimType.FACTUAL,
                importance=ClaimImportance.MEDIUM,
                confidence=0.8
            )
        ]
        deck_chunks = [
            CandidateEvidence(
                id="deck1",
                text="Deck evidence",
                source=EvidenceSource.DECK,
                collection="deck_chunks",
                base_score=0.9
            )
        ]
        research_facts = [
            CandidateEvidence(
                id="research1",
                text="Research evidence",
                source=EvidenceSource.RESEARCH,
                collection="research_facts",
                base_score=0.85
            )
        ]

        result = agent.select_evidence_for_slide(claims, deck_chunks, research_facts)

        assert isinstance(result, EvidenceSelectionResult)
        # The mock returns a response, actual combination is done internally


class TestSystemPrompt:
    """Tests for the system prompt constant."""

    def test_system_prompt_contains_key_instructions(self):
        """Test that system prompt contains essential instructions."""
        prompt = EVIDENCE_SELECTION_SYSTEM_PROMPT.lower()

        assert "evidence" in prompt
        assert "filter" in prompt
        assert "link" in prompt
        assert "stance" in prompt
        assert "supports" in prompt
        assert "contradicts" in prompt
        assert "neutral" in prompt
        assert "relevance" in prompt
        assert "high" in prompt
        assert "medium" in prompt
        assert "low" in prompt
        assert "score_adjustment" in prompt
        assert "json" in prompt


class TestIntegration:
    """Integration tests for the evidence selection flow."""

    def test_full_flow_with_realistic_data(self):
        """Test full flow with realistic claims and evidence."""
        # Setup mock LLM that returns realistic response
        llm_client = MagicMock()
        llm_client.complete_with_system.return_value = {
            "evidence": [
                {
                    "id": "E1",
                    "relevance": "high",
                    "stance": "contradicts",
                    "related_claim_ids": ["C1"],
                    "topics": ["cost", "implementation"],
                    "score_adjustment": 0.25,
                    "notes": "Industry benchmarks contradict the 40% cost reduction claim"
                },
                {
                    "id": "E3",
                    "relevance": "medium",
                    "stance": "supports",
                    "related_claim_ids": ["C2"],
                    "topics": ["timeline", "adoption"],
                    "score_adjustment": 0.1,
                    "notes": "Similar timeline for other enterprise rollouts"
                }
            ],
            "meta": {
                "total_candidates": 4,
                "selected_count": 2,
                "discarded_count": 2,
                "processing_notes": "Two items were off-topic"
            }
        }

        agent = EvidenceSelectionAgent(llm_client)

        claims = [
            Claim(
                id="C1",
                text="Our AI solution reduces costs by 40%",
                claim_type=ClaimType.METRIC,
                importance=ClaimImportance.HIGH,
                confidence=0.9,
                tags=["cost", "roi"]
            ),
            Claim(
                id="C2",
                text="Full deployment in 6 months",
                claim_type=ClaimType.FORECAST,
                importance=ClaimImportance.MEDIUM,
                confidence=0.7,
                tags=["timeline", "implementation"]
            )
        ]
        candidates = [
            CandidateEvidence(
                id="ev1",
                text="Industry average cost reduction for AI solutions is 15-25%",
                source=EvidenceSource.RESEARCH,
                collection="research_facts",
                base_score=0.88
            ),
            CandidateEvidence(
                id="ev2",
                text="Our proprietary algorithms optimize resource allocation",
                source=EvidenceSource.DECK,
                collection="deck_chunks",
                base_score=0.75
            ),
            CandidateEvidence(
                id="ev3",
                text="Enterprise AI deployments typically take 4-8 months",
                source=EvidenceSource.RESEARCH,
                collection="research_facts",
                base_score=0.82
            ),
            CandidateEvidence(
                id="ev4",
                text="Weather patterns in Q3 2024",
                source=EvidenceSource.RESEARCH,
                collection="research_facts",
                base_score=0.3
            )
        ]

        result = agent.select_evidence(claims, candidates)

        # Verify structure
        assert isinstance(result, EvidenceSelectionResult)
        assert len(result.evidence) == 2

        # Verify first evidence item (contradicting cost claim)
        ev1 = result.evidence[0]
        assert ev1.id == "ev1"
        assert ev1.relevance == EvidenceRelevance.HIGH
        assert ev1.stance == EvidenceStance.CONTRADICTS
        assert "C1" in ev1.related_claim_ids
        assert ev1.score_adjustment == 0.25

        # Verify second evidence item (supporting timeline claim)
        ev2 = result.evidence[1]
        assert ev2.id == "ev3"
        assert ev2.relevance == EvidenceRelevance.MEDIUM
        assert ev2.stance == EvidenceStance.SUPPORTS
        assert "C2" in ev2.related_claim_ids

        # Verify metadata
        assert result.meta.total_candidates == 4
        assert result.meta.selected_count == 2
        assert result.meta.discarded_count == 2
