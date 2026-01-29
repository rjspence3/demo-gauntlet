"""
Tests for the ChallengerPipeline.

Tests cover:
- Single slide processing through all 4 steps
- Multi-slide deck processing
- Error handling and recovery
- Evidence retrieval from deck and facts
- Configuration options
"""
import unittest
from unittest.mock import MagicMock, patch
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

from backend.challenges.pipeline import (
    ChallengerPipeline,
    _chunk_to_candidate,
    _fact_to_candidate,
)
from backend.models.core import (
    Slide,
    Chunk,
    Fact,
    Claim,
    ClaimType,
    ClaimImportance,
    CandidateEvidence,
    EvidenceItem,
    EvidenceSource,
    EvidenceRelevance,
    EvidenceStance,
    Tension,
    TensionCategory,
    TensionSeverity,
    ChallengeQuestion,
    IdealAnswer,
    ClaimExtractionResult,
    ClaimExtractionMeta,
    EvidenceSelectionResult,
    EvidenceSelectionMeta,
    AnalysisResult,
    AnalysisMeta,
    QuestionSynthesisResult,
    QuestionSynthesisMeta,
    PipelineConfig,
    PipelineResult,
)
from backend.models.llm import MockLLM


class MockDeckRetriever:
    """Mock deck retriever for testing."""

    def __init__(self, chunks: Optional[List[Chunk]] = None):
        self.chunks = chunks or []

    def get_chunks_for_slide(self, slide_index: int, session_id: Optional[str] = None) -> List[Chunk]:
        return [c for c in self.chunks if c.slide_index == slide_index]


class MockFactStore:
    """Mock fact store for testing."""

    def __init__(self, facts: Optional[List[Fact]] = None):
        self.facts = facts or []

    def get_facts_by_topic(self, topic: str, limit: int = 5) -> List[Fact]:
        return [f for f in self.facts if f.topic == topic][:limit]


class TestHelperFunctions(unittest.TestCase):
    """Tests for helper conversion functions."""

    def test_chunk_to_candidate(self):
        """Test converting Chunk to CandidateEvidence."""
        chunk = Chunk(
            id="chunk_1",
            slide_index=0,
            text="Test chunk text",
            metadata={"key": "value"}
        )
        result = _chunk_to_candidate(chunk, 0)

        self.assertEqual(result.id, "chunk_1")
        self.assertEqual(result.text, "Test chunk text")
        self.assertEqual(result.source, EvidenceSource.DECK)
        self.assertEqual(result.collection, "deck_chunks")
        self.assertEqual(result.base_score, 1.0)

    def test_chunk_to_candidate_without_id(self):
        """Test chunk conversion generates ID when missing."""
        chunk = Chunk(
            id="",
            slide_index=0,
            text="Test chunk"
        )
        result = _chunk_to_candidate(chunk, 5)
        self.assertEqual(result.id, "chunk_5")

    def test_fact_to_candidate(self):
        """Test converting Fact to CandidateEvidence."""
        fact = Fact(
            id="fact_1",
            topic="cost",
            text="Industry benchmarks show 15-25% savings",
            source_url="https://example.com",
            source_title="Industry Report",
            domain="example.com",
            snippet="Savings range..."
        )
        result = _fact_to_candidate(fact, 0)

        self.assertEqual(result.id, "fact_1")
        self.assertEqual(result.text, "Industry benchmarks show 15-25% savings")
        self.assertEqual(result.source, EvidenceSource.RESEARCH)
        self.assertEqual(result.collection, "research_facts")
        self.assertEqual(result.base_score, 0.8)
        self.assertEqual(result.metadata["topic"], "cost")


class TestPipelineInit(unittest.TestCase):
    """Tests for pipeline initialization."""

    def test_init_with_defaults(self):
        """Test pipeline initializes with default config."""
        llm = MockLLM()
        retriever = MockDeckRetriever()
        fact_store = MockFactStore()

        pipeline = ChallengerPipeline(llm, retriever, fact_store)

        self.assertIsNotNone(pipeline.claim_extractor)
        self.assertIsNotNone(pipeline.evidence_selector)
        self.assertIsNotNone(pipeline.evidence_analyzer)
        self.assertIsNotNone(pipeline.question_synthesizer)
        self.assertEqual(pipeline.config.max_questions_per_slide, 3)

    def test_init_with_custom_config(self):
        """Test pipeline respects custom config."""
        config = PipelineConfig(
            min_tensions=2,
            max_questions_per_slide=5,
            include_low_severity=True
        )
        pipeline = ChallengerPipeline(
            MockLLM(), MockDeckRetriever(), MockFactStore(), config
        )

        self.assertEqual(pipeline.config.max_questions_per_slide, 5)
        self.assertTrue(pipeline.config.include_low_severity)


class TestProcessSlide(unittest.TestCase):
    """Tests for process_slide method."""

    def setUp(self):
        """Set up test fixtures."""
        self.sample_slide = Slide(
            index=0,
            title="Cost Savings",
            text="We achieve 40% cost savings through automation.",
            notes="Key selling point"
        )

        self.sample_chunks = [
            Chunk(
                id="chunk_0",
                slide_index=0,
                text="Automation reduces manual processes"
            )
        ]

        self.sample_facts = [
            Fact(
                id="fact_1",
                topic="cost",
                text="Industry benchmarks show 15-25% typical savings",
                source_url="https://example.com",
                source_title="Report",
                domain="example.com",
                snippet="Savings..."
            )
        ]

    def test_process_slide_happy_path(self):
        """Test successful processing of a single slide."""
        # Create mock LLM with sequential responses
        llm = MagicMock()
        llm.complete_with_system.side_effect = [
            # Step 1: Claim extraction
            {
                "claims": [{
                    "id": "C1",
                    "text": "We achieve 40% cost savings",
                    "type": "metric",
                    "importance": "high",
                    "confidence": 0.9,
                    "tags": ["cost"],
                    "source_spans": []
                }],
                "meta": {"slide_index": 0, "used_speaker_notes": False}
            },
            # Step 2: Evidence selection
            {
                "evidence": [{
                    "id": "E1",
                    "relevance": "high",
                    "stance": "contradicts",
                    "related_claim_ids": ["C1"],
                    "topics": ["cost"],
                    "score_adjustment": 0.1,
                    "notes": "Contradicts claim"
                }],
                "meta": {"total_candidates": 2, "selected_count": 1, "discarded_count": 1}
            },
            # Step 3: Evidence analysis
            {
                "tensions": [{
                    "id": "T1",
                    "category": "contradiction",
                    "severity": "high",
                    "headline": "Cost claim contradicts benchmarks",
                    "description": "40% savings vs 15-25% typical",
                    "related_claim_ids": ["C1"],
                    "contradicting_evidence_ids": ["E1"],
                    "question_seed": "How do you justify 40%?"
                }],
                "meta": {"slide_id": "slide_0", "num_tensions": 1}
            },
            # Step 4: Question synthesis
            {
                "questions": [{
                    "id": "Q1",
                    "tension_id": "T1",
                    "question": "How do you justify 40% savings when benchmarks show 15-25%?",
                    "difficulty": "hard",
                    "related_claim_ids": ["C1"],
                    "evidence_ids": ["E1"],
                    "ideal_answer": {
                        "text": "Our savings include direct and indirect benefits",
                        "key_points": ["Direct 20%", "Indirect 20%"],
                        "evidence_ids": ["E1"]
                    }
                }],
                "meta": {"slide_id": "slide_0", "num_questions": 1, "grounded": True}
            },
            # Grounding verification
            {"grounded": True, "issues": []}
        ]

        pipeline = ChallengerPipeline(
            llm,
            MockDeckRetriever(self.sample_chunks),
            MockFactStore(self.sample_facts)
        )

        result = pipeline.process_slide(self.sample_slide)

        self.assertEqual(result.slide_id, "slide_0")
        self.assertEqual(len(result.claims), 1)
        self.assertEqual(len(result.questions), 1)
        self.assertIn("claim_extraction", result.meta.steps_completed)
        self.assertIn("question_synthesis", result.meta.steps_completed)
        self.assertEqual(len(result.meta.errors), 0)

    def test_process_slide_no_claims(self):
        """Test processing slide with no extractable claims."""
        llm = MagicMock()
        llm.complete_with_system.return_value = {
            "claims": [],
            "meta": {"slide_index": 0, "used_speaker_notes": False}
        }

        pipeline = ChallengerPipeline(
            llm, MockDeckRetriever(), MockFactStore()
        )

        result = pipeline.process_slide(self.sample_slide)

        self.assertEqual(len(result.claims), 0)
        self.assertEqual(len(result.questions), 0)
        self.assertIn("no_claims", result.meta.steps_completed)

    def test_process_slide_no_tensions(self):
        """Test processing slide where no tensions are identified."""
        llm = MagicMock()
        llm.complete_with_system.side_effect = [
            # Claim extraction
            {
                "claims": [{
                    "id": "C1",
                    "text": "Test claim",
                    "type": "factual",
                    "importance": "medium",
                    "confidence": 0.8,
                    "tags": [],
                    "source_spans": []
                }],
                "meta": {"slide_index": 0, "used_speaker_notes": False}
            },
            # Evidence selection - no evidence found
            {
                "evidence": [],
                "meta": {"total_candidates": 0, "selected_count": 0, "discarded_count": 0}
            },
            # Evidence analysis - no tensions
            {
                "tensions": [],
                "meta": {"slide_id": "slide_0", "num_tensions": 0}
            }
        ]

        pipeline = ChallengerPipeline(
            llm, MockDeckRetriever(), MockFactStore()
        )

        result = pipeline.process_slide(self.sample_slide)

        self.assertEqual(len(result.tensions), 0)
        self.assertEqual(len(result.questions), 0)
        self.assertIn("no_tensions", result.meta.steps_completed)

    def test_process_slide_with_persona(self):
        """Test processing slide with persona context."""
        llm = MagicMock()
        llm.complete_with_system.side_effect = [
            # Claim extraction
            {"claims": [{"id": "C1", "text": "Test", "type": "factual", "importance": "high", "confidence": 0.9, "tags": ["cost"], "source_spans": []}], "meta": {"slide_index": 0, "used_speaker_notes": False}},
            # Evidence selection
            {"evidence": [{"id": "E1", "relevance": "high", "stance": "contradicts", "related_claim_ids": ["C1"], "topics": ["cost"], "score_adjustment": 0.1}], "meta": {"total_candidates": 1, "selected_count": 1, "discarded_count": 0}},
            # Evidence analysis
            {"tensions": [{"id": "T1", "category": "contradiction", "severity": "high", "headline": "Test", "description": "Test", "related_claim_ids": ["C1"], "contradicting_evidence_ids": ["E1"]}], "meta": {"slide_id": "slide_0", "num_tensions": 1}},
            # Question synthesis
            {"questions": [{"id": "Q1", "tension_id": "T1", "question": "CFO question?", "persona": "CFO", "difficulty": "hard", "related_claim_ids": ["C1"], "evidence_ids": ["E1"], "ideal_answer": {"text": "Answer", "key_points": ["point"], "evidence_ids": ["E1"]}}], "meta": {"slide_id": "slide_0", "num_questions": 1, "grounded": True}},
            {"grounded": True, "issues": []}
        ]

        pipeline = ChallengerPipeline(
            llm,
            MockDeckRetriever(self.sample_chunks),
            MockFactStore(self.sample_facts)
        )

        result = pipeline.process_slide(self.sample_slide, persona="CFO")

        # Verify persona was passed to question synthesis
        synthesis_call = llm.complete_with_system.call_args_list[3]
        self.assertIn("CFO", synthesis_call[1]["user_prompt"])


class TestProcessDeck(unittest.TestCase):
    """Tests for process_deck method."""

    def test_process_deck_multiple_slides(self):
        """Test processing a deck with multiple slides."""
        slides = [
            Slide(index=0, title="Slide 1", text="Content 1"),
            Slide(index=1, title="Slide 2", text="Content 2"),
            Slide(index=2, title="Slide 3", text="Content 3")
        ]

        llm = MagicMock()
        # Return empty claims for simplicity
        llm.complete_with_system.return_value = {
            "claims": [],
            "meta": {"slide_index": 0, "used_speaker_notes": False}
        }

        pipeline = ChallengerPipeline(
            llm, MockDeckRetriever(), MockFactStore()
        )

        results = pipeline.process_deck(slides)

        self.assertEqual(len(results), 3)
        self.assertEqual(results[0].slide_id, "slide_0")
        self.assertEqual(results[1].slide_id, "slide_1")
        self.assertEqual(results[2].slide_id, "slide_2")

    def test_process_deck_with_session_id(self):
        """Test that session_id is passed to retriever."""
        slides = [Slide(index=0, title="Test", text="Test")]

        retriever = MagicMock()
        retriever.get_chunks_for_slide.return_value = []

        fact_store = MagicMock()
        fact_store.get_facts_by_topic.return_value = []

        llm = MagicMock()
        # Return a claim with tags so facts are queried
        llm.complete_with_system.side_effect = [
            # Claim extraction - return claim with tags
            {"claims": [{"id": "C1", "text": "Test", "type": "factual", "importance": "high", "confidence": 0.9, "tags": ["cost"], "source_spans": []}], "meta": {"slide_index": 0, "used_speaker_notes": False}},
            # Evidence analysis (no evidence selection since no candidates)
            {"tensions": [], "meta": {"slide_id": "slide_0", "num_tensions": 0}}
        ]

        pipeline = ChallengerPipeline(llm, retriever, fact_store)
        pipeline.process_deck(slides, session_id="test_session")

        retriever.get_chunks_for_slide.assert_called_with(0, session_id="test_session")


class TestEvidenceRetrieval(unittest.TestCase):
    """Tests for evidence retrieval."""

    def test_retrieves_chunks_and_facts(self):
        """Test that both chunks and facts are retrieved."""
        chunks = [
            Chunk(id="c1", slide_index=0, text="Chunk text")
        ]
        facts = [
            Fact(id="f1", topic="cost", text="Fact text", source_url="", source_title="", domain="", snippet="")
        ]

        claims = [
            Claim(id="C1", text="Test claim", claim_type=ClaimType.METRIC, importance=ClaimImportance.HIGH, confidence=0.9, tags=["cost"])
        ]

        llm = MagicMock()
        # Only claim extraction needed for this test
        llm.complete_with_system.return_value = {
            "claims": [],
            "meta": {"slide_index": 0, "used_speaker_notes": False}
        }

        pipeline = ChallengerPipeline(
            llm,
            MockDeckRetriever(chunks),
            MockFactStore(facts)
        )

        slide = Slide(index=0, title="Test", text="Test")
        candidates = pipeline._retrieve_evidence(slide, claims)

        self.assertEqual(len(candidates), 2)
        sources = {c.source for c in candidates}
        self.assertIn(EvidenceSource.DECK, sources)
        self.assertIn(EvidenceSource.RESEARCH, sources)

    def test_deduplicates_facts(self):
        """Test that duplicate facts are not added."""
        facts = [
            Fact(id="f1", topic="cost", text="Fact 1", source_url="", source_title="", domain="", snippet=""),
            Fact(id="f1", topic="finance", text="Fact 1", source_url="", source_title="", domain="", snippet="")  # Same ID
        ]

        claims = [
            Claim(id="C1", text="Test", claim_type=ClaimType.METRIC, importance=ClaimImportance.HIGH, confidence=0.9, tags=["cost", "finance"])
        ]

        pipeline = ChallengerPipeline(
            MockLLM(),
            MockDeckRetriever(),
            MockFactStore(facts)
        )

        slide = Slide(index=0, title="Test", text="Test")
        candidates = pipeline._retrieve_evidence(slide, claims)

        # Should only have 1 fact (deduplicated)
        fact_candidates = [c for c in candidates if c.source == EvidenceSource.RESEARCH]
        self.assertEqual(len(fact_candidates), 1)


class TestErrorHandling(unittest.TestCase):
    """Tests for error handling and recovery."""

    def test_claim_extraction_failure_returns_early(self):
        """Test that claim extraction failure returns empty result."""
        # The ClaimExtractionAgent catches exceptions internally and returns empty,
        # so we test that behavior instead
        llm = MagicMock()
        llm.complete_with_system.side_effect = Exception("LLM error")

        pipeline = ChallengerPipeline(
            llm, MockDeckRetriever(), MockFactStore()
        )

        slide = Slide(index=0, title="Test", text="Test")
        result = pipeline.process_slide(slide)

        # ClaimExtractionAgent returns empty claims on error
        self.assertEqual(len(result.claims), 0)
        self.assertEqual(len(result.questions), 0)
        # Pipeline should complete step but with no claims
        self.assertIn("no_claims", result.meta.steps_completed)

    def test_evidence_selection_failure_continues(self):
        """Test that evidence selection failure allows pipeline to continue."""
        # Create chunks so evidence selection is actually called
        chunks = [Chunk(id="c1", slide_index=0, text="Test chunk")]

        llm = MagicMock()
        llm.complete_with_system.side_effect = [
            # Claim extraction succeeds
            {"claims": [{"id": "C1", "text": "Test", "type": "factual", "importance": "high", "confidence": 0.9, "tags": [], "source_spans": []}], "meta": {"slide_index": 0, "used_speaker_notes": False}},
            # Evidence selection fails (agent handles internally, returns empty)
            Exception("Selection error"),
            # Evidence analysis continues with empty evidence
            {"tensions": [], "meta": {"slide_id": "slide_0", "num_tensions": 0}}
        ]

        pipeline = ChallengerPipeline(
            llm, MockDeckRetriever(chunks), MockFactStore()
        )

        slide = Slide(index=0, title="Test", text="Test")
        result = pipeline.process_slide(slide)

        # Claims extracted successfully
        self.assertEqual(len(result.claims), 1)
        # Evidence selection step completed (agent handles errors internally)
        self.assertIn("evidence_selection", result.meta.steps_completed)
        # Evidence is empty due to internal failure
        self.assertEqual(len(result.evidence), 0)

    def test_retriever_failure_graceful(self):
        """Test that retriever failure doesn't crash pipeline."""
        retriever = MagicMock()
        retriever.get_chunks_for_slide.side_effect = Exception("DB error")

        fact_store = MagicMock()
        fact_store.get_facts_by_topic.side_effect = Exception("DB error")

        llm = MagicMock()
        llm.complete_with_system.return_value = {
            "claims": [{"id": "C1", "text": "Test", "type": "factual", "importance": "high", "confidence": 0.9, "tags": ["test"], "source_spans": []}],
            "meta": {"slide_index": 0, "used_speaker_notes": False}
        }

        pipeline = ChallengerPipeline(llm, retriever, fact_store)

        slide = Slide(index=0, title="Test", text="Test")
        # Should not raise
        candidates = pipeline._retrieve_evidence(
            slide,
            [Claim(id="C1", text="Test", claim_type=ClaimType.FACTUAL, importance=ClaimImportance.HIGH, confidence=0.9, tags=["test"])]
        )

        self.assertEqual(len(candidates), 0)


class TestMaxQuestionsLimit(unittest.TestCase):
    """Tests for max questions configuration."""

    def test_limits_questions_per_slide(self):
        """Test that questions are limited per configuration."""
        config = PipelineConfig(max_questions_per_slide=1)

        # Add chunks so evidence selection is called
        chunks = [Chunk(id="c1", slide_index=0, text="Test chunk")]

        llm = MagicMock()
        llm.complete_with_system.side_effect = [
            # Claim extraction
            {"claims": [{"id": "C1", "text": "Test", "type": "factual", "importance": "high", "confidence": 0.9, "tags": [], "source_spans": []}], "meta": {"slide_index": 0, "used_speaker_notes": False}},
            # Evidence selection
            {"evidence": [{"id": "E1", "relevance": "high", "stance": "contradicts", "related_claim_ids": ["C1"], "topics": [], "score_adjustment": 0.1}], "meta": {"total_candidates": 1, "selected_count": 1, "discarded_count": 0}},
            # Evidence analysis - multiple tensions
            {"tensions": [
                {"id": "T1", "category": "contradiction", "severity": "high", "headline": "T1", "description": "D1", "related_claim_ids": ["C1"], "contradicting_evidence_ids": ["E1"]},
                {"id": "T2", "category": "ambiguity", "severity": "medium", "headline": "T2", "description": "D2", "related_claim_ids": ["C1"]}
            ], "meta": {"slide_id": "slide_0", "num_tensions": 2}},
            # Question synthesis - returns multiple questions
            {"questions": [
                {"id": "Q1", "tension_id": "T1", "question": "Q1?", "difficulty": "hard", "related_claim_ids": ["C1"], "evidence_ids": ["E1"], "ideal_answer": {"text": "A1", "key_points": ["point"], "evidence_ids": ["E1"]}},
                {"id": "Q2", "tension_id": "T2", "question": "Q2?", "difficulty": "medium", "related_claim_ids": ["C1"], "evidence_ids": [], "ideal_answer": {"text": "A2", "key_points": ["point"], "evidence_ids": []}}
            ], "meta": {"slide_id": "slide_0", "num_questions": 2, "grounded": True}},
            # Grounding verification for both questions
            {"grounded": True, "issues": []},
            {"grounded": True, "issues": []}
        ]

        pipeline = ChallengerPipeline(
            llm, MockDeckRetriever(chunks), MockFactStore(), config
        )

        slide = Slide(index=0, title="Test", text="Test")
        result = pipeline.process_slide(slide)

        # Should be limited to 1 question
        self.assertEqual(len(result.questions), 1)


class TestPipelineMeta(unittest.TestCase):
    """Tests for pipeline metadata."""

    def test_processing_time_recorded(self):
        """Test that processing time is recorded."""
        llm = MagicMock()
        llm.complete_with_system.return_value = {
            "claims": [],
            "meta": {"slide_index": 0, "used_speaker_notes": False}
        }

        pipeline = ChallengerPipeline(
            llm, MockDeckRetriever(), MockFactStore()
        )

        slide = Slide(index=0, title="Test", text="Test")
        result = pipeline.process_slide(slide)

        self.assertGreaterEqual(result.meta.processing_time_ms, 0)

    def test_slide_index_preserved(self):
        """Test that slide index is preserved in meta."""
        llm = MagicMock()
        llm.complete_with_system.return_value = {
            "claims": [],
            "meta": {"slide_index": 5, "used_speaker_notes": False}
        }

        pipeline = ChallengerPipeline(
            llm, MockDeckRetriever(), MockFactStore()
        )

        slide = Slide(index=5, title="Test", text="Test")
        result = pipeline.process_slide(slide)

        self.assertEqual(result.meta.slide_index, 5)
        self.assertEqual(result.slide_id, "slide_5")


if __name__ == "__main__":
    unittest.main()
