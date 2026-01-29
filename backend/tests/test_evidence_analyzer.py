"""
Tests for the EvidenceAnalysisAgent.
"""
import pytest
from unittest.mock import MagicMock
from backend.challenges.evidence_analyzer import (
    EvidenceAnalysisAgent,
    _format_claims_for_prompt,
    _format_evidence_for_prompt,
    _build_user_prompt,
    _parse_category,
    _parse_severity,
    _parse_analysis_response,
    EVIDENCE_ANALYSIS_SYSTEM_PROMPT,
)
from backend.models.core import (
    Claim,
    ClaimType,
    ClaimImportance,
    EvidenceItem,
    EvidenceRelevance,
    EvidenceStance,
    EvidenceSource,
    Tension,
    TensionCategory,
    TensionSeverity,
    AnalysisMeta,
    AnalysisResult,
)
from backend.models.llm import MockLLM


class TestCategoryParser:
    """Tests for tension category parsing."""

    def test_parse_contradiction(self):
        """Test parsing contradiction category."""
        assert _parse_category("contradiction") == TensionCategory.CONTRADICTION
        assert _parse_category("CONTRADICTION") == TensionCategory.CONTRADICTION

    def test_parse_missing_evidence(self):
        """Test parsing missing_evidence category."""
        assert _parse_category("missing_evidence") == TensionCategory.MISSING_EVIDENCE

    def test_parse_risk_exposure(self):
        """Test parsing risk_exposure category."""
        assert _parse_category("risk_exposure") == TensionCategory.RISK_EXPOSURE

    def test_parse_competitive_gap(self):
        """Test parsing competitive_gap category."""
        assert _parse_category("competitive_gap") == TensionCategory.COMPETITIVE_GAP

    def test_parse_ambiguity(self):
        """Test parsing ambiguity category."""
        assert _parse_category("ambiguity") == TensionCategory.AMBIGUITY

    def test_parse_unknown_defaults_to_ambiguity(self):
        """Test that unknown category defaults to ambiguity."""
        assert _parse_category("unknown") == TensionCategory.AMBIGUITY
        assert _parse_category("") == TensionCategory.AMBIGUITY


class TestSeverityParser:
    """Tests for severity parsing."""

    def test_parse_high(self):
        """Test parsing high severity."""
        assert _parse_severity("high") == TensionSeverity.HIGH
        assert _parse_severity("HIGH") == TensionSeverity.HIGH

    def test_parse_medium(self):
        """Test parsing medium severity."""
        assert _parse_severity("medium") == TensionSeverity.MEDIUM

    def test_parse_low(self):
        """Test parsing low severity."""
        assert _parse_severity("low") == TensionSeverity.LOW

    def test_parse_unknown_defaults_to_medium(self):
        """Test that unknown severity defaults to medium."""
        assert _parse_severity("unknown") == TensionSeverity.MEDIUM
        assert _parse_severity("") == TensionSeverity.MEDIUM


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
        assert "0.80" in result
        assert "Revenue will grow 50%" in result
        assert "revenue" in result

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


class TestFormatEvidenceForPrompt:
    """Tests for formatting evidence for prompt."""

    def test_format_empty_evidence(self):
        """Test formatting with no evidence."""
        result = _format_evidence_for_prompt([])
        assert "No evidence provided" in result

    def test_format_single_evidence(self):
        """Test formatting a single evidence item."""
        evidence = [
            EvidenceItem(
                id="E1",
                text="Industry data shows 15-25% cost reduction",
                source=EvidenceSource.RESEARCH,
                collection="research_facts",
                relevance=EvidenceRelevance.HIGH,
                stance=EvidenceStance.CONTRADICTS,
                related_claim_ids=["C1"],
                topics=["cost", "benchmark"],
                score_adjustment=0.2,
                notes="From Gartner report"
            )
        ]
        result = _format_evidence_for_prompt(evidence)

        assert "[E1]" in result
        assert "research" in result
        assert "high" in result
        assert "contradicts" in result
        assert "Industry data shows" in result
        assert "C1" in result
        assert "cost" in result
        assert "Gartner" in result

    def test_format_multiple_evidence(self):
        """Test formatting multiple evidence items."""
        evidence = [
            EvidenceItem(
                id="E1",
                text="First evidence",
                source=EvidenceSource.DECK,
                collection="deck_chunks",
                relevance=EvidenceRelevance.HIGH,
                stance=EvidenceStance.SUPPORTS,
                related_claim_ids=["C1"],
                topics=["test"],
                score_adjustment=0.1
            ),
            EvidenceItem(
                id="E2",
                text="Second evidence",
                source=EvidenceSource.RESEARCH,
                collection="research_facts",
                relevance=EvidenceRelevance.MEDIUM,
                stance=EvidenceStance.CONTRADICTS,
                related_claim_ids=["C2"],
                topics=["test2"],
                score_adjustment=-0.1
            )
        ]
        result = _format_evidence_for_prompt(evidence)

        assert "[E1]" in result
        assert "[E2]" in result
        assert "First evidence" in result
        assert "Second evidence" in result


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
        evidence = [
            EvidenceItem(
                id="E1",
                text="Test evidence",
                source=EvidenceSource.DECK,
                collection="deck_chunks",
                relevance=EvidenceRelevance.HIGH,
                stance=EvidenceStance.SUPPORTS,
                related_claim_ids=["C1"],
                topics=["test"],
                score_adjustment=0.1
            )
        ]
        result = _build_user_prompt("slide_0", claims, evidence)

        assert "slide_0" in result
        assert "Claims (1 total)" in result
        assert "Evidence (1 total" in result
        assert "1 supporting" in result
        assert "Test claim" in result
        assert "Test evidence" in result

    def test_build_prompt_stance_counts(self):
        """Test that stance counts are correct in prompt."""
        claims = [
            Claim(
                id="C1",
                text="Claim",
                claim_type=ClaimType.FACTUAL,
                importance=ClaimImportance.MEDIUM,
                confidence=0.8
            )
        ]
        evidence = [
            EvidenceItem(
                id="E1", text="Ev1", source=EvidenceSource.DECK, collection="c",
                relevance=EvidenceRelevance.HIGH, stance=EvidenceStance.SUPPORTS,
                related_claim_ids=["C1"], topics=[], score_adjustment=0.0
            ),
            EvidenceItem(
                id="E2", text="Ev2", source=EvidenceSource.RESEARCH, collection="c",
                relevance=EvidenceRelevance.MEDIUM, stance=EvidenceStance.CONTRADICTS,
                related_claim_ids=["C1"], topics=[], score_adjustment=0.0
            ),
            EvidenceItem(
                id="E3", text="Ev3", source=EvidenceSource.RESEARCH, collection="c",
                relevance=EvidenceRelevance.LOW, stance=EvidenceStance.NEUTRAL_OR_UNCLEAR,
                related_claim_ids=["C1"], topics=[], score_adjustment=0.0
            ),
        ]
        result = _build_user_prompt("slide_0", claims, evidence)

        assert "3 total" in result
        assert "1 supporting" in result
        assert "1 contradicting" in result
        assert "1 neutral" in result


class TestParseAnalysisResponse:
    """Tests for parsing analysis response."""

    def test_parse_empty_response(self):
        """Test parsing empty response."""
        result = _parse_analysis_response({}, "slide_0", 2, 3)

        assert result.slide_id == "slide_0"
        assert len(result.tensions) == 0
        assert result.meta.num_claims == 2
        assert result.meta.num_evidence_items == 3

    def test_parse_full_response(self):
        """Test parsing a complete response."""
        response = {
            "tensions": [
                {
                    "id": "T1",
                    "category": "contradiction",
                    "severity": "high",
                    "headline": "Cost claim conflicts with benchmarks",
                    "description": "The 40% cost reduction claim contradicts industry data showing 15-25%.",
                    "related_claim_ids": ["C1"],
                    "supporting_evidence_ids": [],
                    "contradicting_evidence_ids": ["E1", "E2"],
                    "risk_tags": ["cost", "credibility"],
                    "question_seed": "How do you justify the 40% claim?",
                    "notes": "Critical issue"
                },
                {
                    "id": "T2",
                    "category": "missing_evidence",
                    "severity": "medium",
                    "headline": "Timeline lacks support",
                    "description": "No evidence supports the 6-month timeline.",
                    "related_claim_ids": ["C2"],
                    "supporting_evidence_ids": [],
                    "contradicting_evidence_ids": [],
                    "risk_tags": ["timeline"],
                    "question_seed": "What evidence supports the timeline?",
                    "notes": None
                }
            ],
            "meta": {
                "slide_id": "slide_0",
                "num_claims": 2,
                "num_evidence_items": 3,
                "num_tensions": 2,
                "processing_notes": "Two major tensions identified"
            }
        }

        result = _parse_analysis_response(response, "slide_0", 2, 3)

        assert result.slide_id == "slide_0"
        assert len(result.tensions) == 2

        t1 = result.tensions[0]
        assert t1.id == "T1"
        assert t1.category == TensionCategory.CONTRADICTION
        assert t1.severity == TensionSeverity.HIGH
        assert t1.headline == "Cost claim conflicts with benchmarks"
        assert "C1" in t1.related_claim_ids
        assert "E1" in t1.contradicting_evidence_ids
        assert "E2" in t1.contradicting_evidence_ids
        assert "cost" in t1.risk_tags
        assert t1.question_seed == "How do you justify the 40% claim?"
        assert t1.notes == "Critical issue"

        t2 = result.tensions[1]
        assert t2.id == "T2"
        assert t2.category == TensionCategory.MISSING_EVIDENCE
        assert t2.severity == TensionSeverity.MEDIUM

        assert result.meta.num_tensions == 2
        assert result.meta.processing_notes == "Two major tensions identified"

    def test_parse_response_with_missing_optional_fields(self):
        """Test parsing response with missing optional fields."""
        response = {
            "tensions": [
                {
                    "id": "T1",
                    "headline": "Basic tension"
                }
            ],
            "meta": {}
        }

        result = _parse_analysis_response(response, "slide_5", 3, 4)

        assert len(result.tensions) == 1
        t = result.tensions[0]
        assert t.id == "T1"
        assert t.category == TensionCategory.AMBIGUITY  # default
        assert t.severity == TensionSeverity.MEDIUM  # default
        assert t.headline == "Basic tension"
        assert t.description == ""
        assert t.related_claim_ids == []
        assert t.supporting_evidence_ids == []
        assert t.contradicting_evidence_ids == []
        assert t.risk_tags == []
        assert t.question_seed is None
        assert t.notes is None

        assert result.meta.slide_id == "slide_5"
        assert result.meta.num_claims == 3
        assert result.meta.num_evidence_items == 4


class TestEvidenceAnalysisAgent:
    """Tests for the EvidenceAnalysisAgent class."""

    def test_init(self):
        """Test agent initialization."""
        llm_client = MockLLM()
        agent = EvidenceAnalysisAgent(llm_client)
        assert agent.llm_client == llm_client

    def test_analyze_with_mock_llm(self):
        """Test analysis with mock LLM."""
        llm_client = MockLLM()
        agent = EvidenceAnalysisAgent(llm_client)

        claims = [
            Claim(
                id="C1",
                text="Our solution reduces costs by 40%",
                claim_type=ClaimType.METRIC,
                importance=ClaimImportance.HIGH,
                confidence=0.9
            )
        ]
        evidence = [
            EvidenceItem(
                id="E1",
                text="Industry benchmarks show 15-25% cost reduction",
                source=EvidenceSource.RESEARCH,
                collection="research_facts",
                relevance=EvidenceRelevance.HIGH,
                stance=EvidenceStance.CONTRADICTS,
                related_claim_ids=["C1"],
                topics=["cost", "benchmark"],
                score_adjustment=0.2
            )
        ]

        result = agent.analyze("slide_0", claims, evidence)

        assert isinstance(result, AnalysisResult)
        assert result.slide_id == "slide_0"
        assert len(result.tensions) >= 1  # MockLLM returns at least one tension
        assert isinstance(result.meta, AnalysisMeta)

    def test_analyze_with_no_claims(self):
        """Test analysis with no claims."""
        llm_client = MockLLM()
        agent = EvidenceAnalysisAgent(llm_client)

        evidence = [
            EvidenceItem(
                id="E1",
                text="Test",
                source=EvidenceSource.DECK,
                collection="test",
                relevance=EvidenceRelevance.HIGH,
                stance=EvidenceStance.SUPPORTS,
                related_claim_ids=[],
                topics=[],
                score_adjustment=0.0
            )
        ]

        result = agent.analyze("slide_0", [], evidence)

        assert len(result.tensions) == 0
        assert result.meta.num_claims == 0
        assert "No claims to analyze" in result.meta.processing_notes

    def test_analyze_with_no_evidence(self):
        """Test analysis with no evidence (should still work - may find missing evidence tensions)."""
        # Use a MagicMock to return specific response for this case
        llm_client = MagicMock()
        llm_client.complete_with_system.return_value = {
            "tensions": [
                {
                    "id": "T1",
                    "category": "missing_evidence",
                    "severity": "high",
                    "headline": "Claim lacks any supporting evidence",
                    "description": "No evidence available to support or contradict this claim.",
                    "related_claim_ids": ["C1"],
                    "risk_tags": ["credibility"]
                }
            ],
            "meta": {
                "slide_id": "slide_0",
                "num_claims": 1,
                "num_evidence_items": 0,
                "num_tensions": 1,
                "processing_notes": "No evidence available"
            }
        }
        agent = EvidenceAnalysisAgent(llm_client)

        claims = [
            Claim(
                id="C1",
                text="Test claim",
                claim_type=ClaimType.FACTUAL,
                importance=ClaimImportance.HIGH,
                confidence=0.8
            )
        ]

        result = agent.analyze("slide_0", claims, [])

        assert isinstance(result, AnalysisResult)
        assert result.meta.num_evidence_items == 0
        # Should still identify missing evidence tensions
        assert len(result.tensions) >= 1

    def test_analyze_handles_exception(self):
        """Test that analysis handles exceptions gracefully."""
        llm_client = MagicMock()
        llm_client.complete_with_system.side_effect = Exception("API Error")

        agent = EvidenceAnalysisAgent(llm_client)
        claims = [
            Claim(
                id="C1",
                text="Test",
                claim_type=ClaimType.FACTUAL,
                importance=ClaimImportance.MEDIUM,
                confidence=0.8
            )
        ]
        evidence = [
            EvidenceItem(
                id="E1",
                text="Test",
                source=EvidenceSource.DECK,
                collection="test",
                relevance=EvidenceRelevance.HIGH,
                stance=EvidenceStance.SUPPORTS,
                related_claim_ids=["C1"],
                topics=[],
                score_adjustment=0.0
            )
        ]

        result = agent.analyze("slide_0", claims, evidence)

        assert len(result.tensions) == 0
        assert "Analysis failed" in result.meta.processing_notes


class TestSystemPrompt:
    """Tests for the system prompt constant."""

    def test_system_prompt_contains_key_instructions(self):
        """Test that system prompt contains essential instructions."""
        prompt = EVIDENCE_ANALYSIS_SYSTEM_PROMPT.lower()

        # Tension categories
        assert "contradiction" in prompt
        assert "missing_evidence" in prompt
        assert "risk_exposure" in prompt
        assert "competitive_gap" in prompt
        assert "ambiguity" in prompt

        # Severity levels
        assert "high" in prompt
        assert "medium" in prompt
        assert "low" in prompt

        # Key concepts
        assert "tension" in prompt
        assert "question_seed" in prompt
        assert "json" in prompt


class TestIntegration:
    """Integration tests for the evidence analysis flow."""

    def test_full_flow_with_realistic_data(self):
        """Test full flow with realistic claims and evidence."""
        # Setup mock LLM that returns realistic response
        llm_client = MagicMock()
        llm_client.complete_with_system.return_value = {
            "tensions": [
                {
                    "id": "T1",
                    "category": "contradiction",
                    "severity": "high",
                    "headline": "Cost savings claim contradicts industry benchmarks",
                    "description": "The claimed 40% cost reduction is significantly higher than industry benchmarks of 15-25%. This discrepancy could undermine credibility with informed buyers.",
                    "related_claim_ids": ["C1"],
                    "supporting_evidence_ids": [],
                    "contradicting_evidence_ids": ["E1"],
                    "risk_tags": ["cost", "credibility", "roi"],
                    "question_seed": "How do you reconcile your 40% cost savings claim with Gartner's research showing typical AI implementations achieve 15-25% reduction?",
                    "notes": "Critical for CFO persona"
                },
                {
                    "id": "T2",
                    "category": "missing_evidence",
                    "severity": "medium",
                    "headline": "Timeline claim lacks supporting evidence",
                    "description": "The 6-month deployment timeline is stated without supporting data. Enterprise AI deployments typically take 4-12 months depending on scope.",
                    "related_claim_ids": ["C2"],
                    "supporting_evidence_ids": [],
                    "contradicting_evidence_ids": [],
                    "risk_tags": ["timeline", "implementation"],
                    "question_seed": "What specific evidence do you have that supports the 6-month deployment timeline?",
                    "notes": "Good for CTO persona"
                },
                {
                    "id": "T3",
                    "category": "risk_exposure",
                    "severity": "medium",
                    "headline": "Security compliance not addressed",
                    "description": "No mention of SOC2 or GDPR compliance, which are critical for enterprise buyers in regulated industries.",
                    "related_claim_ids": ["C1", "C3"],
                    "supporting_evidence_ids": [],
                    "contradicting_evidence_ids": [],
                    "risk_tags": ["security", "compliance", "governance"],
                    "question_seed": "How does your solution address SOC2 and GDPR compliance requirements?",
                    "notes": "Critical for compliance persona"
                }
            ],
            "meta": {
                "slide_id": "slide_0",
                "num_claims": 3,
                "num_evidence_items": 4,
                "num_tensions": 3,
                "processing_notes": "Three significant tensions identified. Cost claim contradiction is most critical."
            }
        }

        agent = EvidenceAnalysisAgent(llm_client)

        claims = [
            Claim(
                id="C1",
                text="Our AI solution reduces operational costs by 40%",
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
            ),
            Claim(
                id="C3",
                text="Enterprise-grade security built-in",
                claim_type=ClaimType.FACTUAL,
                importance=ClaimImportance.HIGH,
                confidence=0.8,
                tags=["security"]
            )
        ]

        evidence = [
            EvidenceItem(
                id="E1",
                text="Gartner research shows typical AI implementations achieve 15-25% cost reduction",
                source=EvidenceSource.RESEARCH,
                collection="research_facts",
                relevance=EvidenceRelevance.HIGH,
                stance=EvidenceStance.CONTRADICTS,
                related_claim_ids=["C1"],
                topics=["cost", "benchmark"],
                score_adjustment=0.25
            ),
            EvidenceItem(
                id="E2",
                text="Our proprietary optimization algorithms",
                source=EvidenceSource.DECK,
                collection="deck_chunks",
                relevance=EvidenceRelevance.MEDIUM,
                stance=EvidenceStance.SUPPORTS,
                related_claim_ids=["C1"],
                topics=["technology"],
                score_adjustment=0.1
            ),
            EvidenceItem(
                id="E3",
                text="Enterprise deployments typically take 4-12 months",
                source=EvidenceSource.RESEARCH,
                collection="research_facts",
                relevance=EvidenceRelevance.MEDIUM,
                stance=EvidenceStance.NEUTRAL_OR_UNCLEAR,
                related_claim_ids=["C2"],
                topics=["timeline"],
                score_adjustment=0.0
            ),
            EvidenceItem(
                id="E4",
                text="Security certifications mentioned on slide 5",
                source=EvidenceSource.DECK,
                collection="deck_chunks",
                relevance=EvidenceRelevance.LOW,
                stance=EvidenceStance.SUPPORTS,
                related_claim_ids=["C3"],
                topics=["security"],
                score_adjustment=-0.1
            )
        ]

        result = agent.analyze("slide_0", claims, evidence)

        # Verify structure
        assert isinstance(result, AnalysisResult)
        assert result.slide_id == "slide_0"
        assert len(result.tensions) == 3

        # Verify first tension (contradiction)
        t1 = result.tensions[0]
        assert t1.id == "T1"
        assert t1.category == TensionCategory.CONTRADICTION
        assert t1.severity == TensionSeverity.HIGH
        assert "C1" in t1.related_claim_ids
        assert "E1" in t1.contradicting_evidence_ids
        assert "cost" in t1.risk_tags
        assert t1.question_seed is not None
        assert "40%" in t1.question_seed

        # Verify second tension (missing evidence)
        t2 = result.tensions[1]
        assert t2.id == "T2"
        assert t2.category == TensionCategory.MISSING_EVIDENCE
        assert t2.severity == TensionSeverity.MEDIUM
        assert "C2" in t2.related_claim_ids

        # Verify third tension (risk exposure)
        t3 = result.tensions[2]
        assert t3.id == "T3"
        assert t3.category == TensionCategory.RISK_EXPOSURE
        assert "security" in t3.risk_tags
        assert "compliance" in t3.risk_tags

        # Verify metadata
        assert result.meta.num_claims == 3
        assert result.meta.num_evidence_items == 4
        assert result.meta.num_tensions == 3
        assert "Cost claim contradiction" in result.meta.processing_notes
