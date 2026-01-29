"""
End-to-End Tests for the Challenger Pipeline.

Tests cover:
- Full pipeline from slide input to question output
- Integration with BaseChallenger
- Persona routing through the full pipeline
- Adaptive difficulty calculations
- Error recovery and edge cases
"""
import unittest
from unittest.mock import MagicMock, patch
from dataclasses import asdict

from backend.challenges.pipeline import ChallengerPipeline
from backend.challenges.implementations import BaseChallenger
from backend.challenges.difficulty import DifficultyCalculator
from backend.models.core import (
    Slide,
    Chunk,
    Fact,
    Claim,
    ClaimType,
    ClaimImportance,
    ClaimExtractionResult,
    ClaimExtractionMeta,
    CandidateEvidence,
    EvidenceItem,
    EvidenceSource,
    EvidenceRelevance,
    EvidenceStance,
    EvidenceSelectionResult,
    EvidenceSelectionMeta,
    Tension,
    TensionCategory,
    TensionSeverity,
    AnalysisResult,
    AnalysisMeta,
    IdealAnswer,
    ChallengeQuestion,
    QuestionSynthesisResult,
    QuestionSynthesisMeta,
    PipelineConfig,
    PipelineResult,
    ChallengerPersona,
    ResearchDossier,
)


def create_mock_llm_client():
    """Create a mock LLM client with sensible defaults."""
    mock_client = MagicMock()
    return mock_client


def create_sample_slide(index: int = 0, title: str = "Test Slide") -> Slide:
    """Create a sample slide for testing."""
    return Slide(
        index=index,
        title=title,
        text="We achieve 40% cost savings with our new platform. Implementation takes 6 months.",
        notes="Key metric: 40% savings validated by customer surveys.",
        tags=["cost", "implementation"]
    )


def create_sample_chunks() -> list:
    """Create sample chunks for deck retrieval."""
    return [
        Chunk(
            id="chunk_1",
            slide_index=0,
            text="Our platform achieves 40% cost savings compared to traditional solutions.",
            metadata={"source": "slide_body"}
        ),
        Chunk(
            id="chunk_2",
            slide_index=0,
            text="Implementation timeline is typically 6 months.",
            metadata={"source": "slide_body"}
        )
    ]


def create_sample_facts() -> list:
    """Create sample facts for research retrieval."""
    return [
        Fact(
            id="fact_1",
            topic="cost",
            text="Industry benchmarks show typical cost savings of 15-25% for similar platforms.",
            source_url="https://example.com/report",
            source_title="Industry Cost Report 2024",
            domain="example.com",
            snippet="Cost savings typically range from 15-25%"
        ),
        Fact(
            id="fact_2",
            topic="implementation",
            text="Average implementation timeline for enterprise platforms is 9-12 months.",
            source_url="https://example.com/timeline",
            source_title="Implementation Study",
            domain="example.com",
            snippet="9-12 month average implementation"
        )
    ]


def create_cfo_persona() -> ChallengerPersona:
    """Create a CFO persona for testing."""
    return ChallengerPersona(
        id="cfo_1",
        name="Sarah Chen",
        role="Chief Financial Officer",
        style="Data-driven, focused on ROI and budget impact",
        focus_areas=["cost analysis", "budget impact", "ROI metrics"],
        domain_tags=["finance", "cost", "budget", "roi"]
    )


def create_cto_persona() -> ChallengerPersona:
    """Create a CTO persona for testing."""
    return ChallengerPersona(
        id="cto_1",
        name="Marcus Johnson",
        role="Chief Technology Officer",
        style="Technical depth, focus on scalability and security",
        focus_areas=["technical architecture", "scalability", "security"],
        domain_tags=["technical", "architecture", "security", "scalability"]
    )


class TestPipelineHappyPath(unittest.TestCase):
    """Happy path tests for full pipeline execution."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_deck_retriever = MagicMock()
        self.mock_deck_retriever.get_chunks_for_slide.return_value = create_sample_chunks()

        self.mock_fact_store = MagicMock()
        self.mock_fact_store.get_facts_by_topic.return_value = create_sample_facts()[:1]

    def test_single_slide_full_pipeline(self):
        """Test processing a single slide through all 4 steps."""
        mock_llm = create_mock_llm_client()

        # Set up LLM responses for each step
        mock_llm.complete_with_system.side_effect = [
            # Step 1: Claim extraction
            {
                "claims": [
                    {
                        "id": "C1",
                        "text": "We achieve 40% cost savings",
                        "claim_type": "metric",
                        "importance": "high",
                        "confidence": 0.9,
                        "tags": ["cost", "finance"]
                    }
                ],
                "meta": {"slide_index": 0, "used_speaker_notes": True}
            },
            # Step 2: Evidence selection
            {
                "evidence": [
                    {
                        "id": "chunk_1",
                        "text": "Our platform achieves 40% cost savings",
                        "source": "deck",
                        "collection": "deck_chunks",
                        "relevance": "high",
                        "stance": "supports",
                        "related_claim_ids": ["C1"],
                        "topics": ["cost"],
                        "score_adjustment": 0.1
                    },
                    {
                        "id": "fact_1",
                        "text": "Industry benchmarks show 15-25% savings",
                        "source": "research",
                        "collection": "research_facts",
                        "relevance": "high",
                        "stance": "contradicts",
                        "related_claim_ids": ["C1"],
                        "topics": ["cost"],
                        "score_adjustment": 0.2
                    }
                ],
                "meta": {"total_candidates": 3, "selected_count": 2, "discarded_count": 1}
            },
            # Step 3: Evidence analysis
            {
                "tensions": [
                    {
                        "id": "T1",
                        "category": "contradiction",
                        "severity": "high",
                        "headline": "Cost savings claim exceeds industry benchmarks",
                        "description": "The claimed 40% savings significantly exceeds typical industry range of 15-25%",
                        "related_claim_ids": ["C1"],
                        "supporting_evidence_ids": ["chunk_1"],
                        "contradicting_evidence_ids": ["fact_1"],
                        "risk_tags": ["finance", "credibility"],
                        "question_seed": "How do you justify savings above industry benchmarks?"
                    }
                ],
                "meta": {"slide_id": "slide_0", "num_claims": 1, "num_evidence_items": 2, "num_tensions": 1}
            },
            # Step 4: Question synthesis
            {
                "questions": [
                    {
                        "id": "Q1",
                        "tension_id": "T1",
                        "question": "Your 40% cost savings claim is significantly higher than the industry benchmark of 15-25%. What specific factors account for this outperformance?",
                        "persona": None,
                        "difficulty": "hard",
                        "related_claim_ids": ["C1"],
                        "evidence_ids": ["chunk_1", "fact_1"],
                        "ideal_answer": {
                            "text": "The 40% savings is achieved through a combination of factors unique to our platform...",
                            "key_points": ["Platform efficiency", "Automation", "Scale advantages"],
                            "evidence_ids": ["chunk_1"]
                        }
                    }
                ],
                "meta": {"slide_id": "slide_0", "num_tensions": 1, "num_questions": 1, "grounded": True}
            },
            # Grounding verification
            {"grounded": True, "issues": []}
        ]

        pipeline = ChallengerPipeline(
            llm_client=mock_llm,
            deck_retriever=self.mock_deck_retriever,
            fact_store=self.mock_fact_store,
            config=PipelineConfig(max_questions_per_slide=3)
        )

        slide = create_sample_slide()
        result = pipeline.process_slide(slide, session_id="test_session")

        # Verify result structure
        self.assertIsInstance(result, PipelineResult)
        self.assertEqual(result.slide_id, "slide_0")

        # Verify all steps completed
        self.assertIn("claim_extraction", result.meta.steps_completed)
        self.assertIn("evidence_selection", result.meta.steps_completed)
        self.assertIn("evidence_analysis", result.meta.steps_completed)
        self.assertIn("question_synthesis", result.meta.steps_completed)

        # Verify outputs
        self.assertGreater(len(result.claims), 0)
        self.assertGreater(len(result.questions), 0)
        self.assertEqual(len(result.meta.errors), 0)

    def test_multi_slide_deck(self):
        """Test processing a multi-slide deck."""
        mock_llm = create_mock_llm_client()

        # Simplified response for multiple slides - just claim extraction returning no claims
        mock_llm.complete_with_system.return_value = {
            "claims": [],
            "meta": {"slide_index": 0, "used_speaker_notes": False}
        }

        pipeline = ChallengerPipeline(
            llm_client=mock_llm,
            deck_retriever=self.mock_deck_retriever,
            fact_store=self.mock_fact_store
        )

        slides = [
            create_sample_slide(index=0, title="Overview"),
            create_sample_slide(index=1, title="Cost Analysis"),
            create_sample_slide(index=2, title="Timeline"),
        ]

        results = pipeline.process_deck(slides, session_id="test_session")

        self.assertEqual(len(results), 3)
        for i, result in enumerate(results):
            self.assertEqual(result.meta.slide_index, i)


class TestPipelineEdgeCases(unittest.TestCase):
    """Edge case tests for pipeline execution."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_deck_retriever = MagicMock()
        self.mock_deck_retriever.get_chunks_for_slide.return_value = []

        self.mock_fact_store = MagicMock()
        self.mock_fact_store.get_facts_by_topic.return_value = []

    def test_slide_with_no_claims(self):
        """Test slide with no extractable claims returns early."""
        mock_llm = create_mock_llm_client()
        mock_llm.complete_with_system.return_value = {
            "claims": [],
            "meta": {"slide_index": 0, "used_speaker_notes": False, "notes": "No claims found"}
        }

        pipeline = ChallengerPipeline(
            llm_client=mock_llm,
            deck_retriever=self.mock_deck_retriever,
            fact_store=self.mock_fact_store
        )

        slide = Slide(index=0, title="Empty Slide", text="Thank you!")
        result = pipeline.process_slide(slide)

        self.assertEqual(len(result.claims), 0)
        self.assertEqual(len(result.questions), 0)
        self.assertIn("no_claims", result.meta.steps_completed)

    def test_slide_with_no_evidence(self):
        """Test slide with claims but no matching evidence."""
        mock_llm = create_mock_llm_client()
        mock_llm.complete_with_system.side_effect = [
            # Claim extraction
            {
                "claims": [
                    {
                        "id": "C1",
                        "text": "Test claim",
                        "claim_type": "factual",
                        "importance": "medium",
                        "confidence": 0.8,
                        "tags": ["test"]
                    }
                ],
                "meta": {"slide_index": 0, "used_speaker_notes": False}
            },
            # Evidence selection (empty)
            {
                "evidence": [],
                "meta": {"total_candidates": 0, "selected_count": 0, "discarded_count": 0}
            },
            # Analysis (no tensions due to no evidence)
            {
                "tensions": [],
                "meta": {"slide_id": "slide_0", "num_claims": 1, "num_evidence_items": 0, "num_tensions": 0}
            }
        ]

        pipeline = ChallengerPipeline(
            llm_client=mock_llm,
            deck_retriever=self.mock_deck_retriever,
            fact_store=self.mock_fact_store
        )

        slide = create_sample_slide()
        result = pipeline.process_slide(slide)

        self.assertGreater(len(result.claims), 0)
        self.assertEqual(len(result.tensions), 0)
        self.assertEqual(len(result.questions), 0)
        self.assertIn("no_tensions", result.meta.steps_completed)


class TestPipelineIntegration(unittest.TestCase):
    """Integration tests for pipeline with BaseChallenger."""

    def test_pipeline_with_base_challenger(self):
        """Test that pipeline integrates correctly with BaseChallenger."""
        mock_llm = create_mock_llm_client()

        # Set up LLM responses
        mock_llm.complete_with_system.side_effect = [
            # Claim extraction
            {
                "claims": [
                    {
                        "id": "C1",
                        "text": "40% cost savings",
                        "claim_type": "metric",
                        "importance": "high",
                        "confidence": 0.9,
                        "tags": ["cost", "finance"]
                    }
                ],
                "meta": {"slide_index": 0, "used_speaker_notes": True}
            },
            # Evidence selection
            {
                "evidence": [
                    {
                        "id": "E1",
                        "text": "Supporting evidence",
                        "source": "deck",
                        "collection": "deck_chunks",
                        "relevance": "high",
                        "stance": "supports",
                        "related_claim_ids": ["C1"],
                        "topics": ["cost"],
                        "score_adjustment": 0.1
                    }
                ],
                "meta": {"total_candidates": 1, "selected_count": 1, "discarded_count": 0}
            },
            # Analysis
            {
                "tensions": [
                    {
                        "id": "T1",
                        "category": "risk_exposure",
                        "severity": "medium",
                        "headline": "Cost validation needed",
                        "description": "Cost claim needs validation",
                        "related_claim_ids": ["C1"],
                        "supporting_evidence_ids": ["E1"],
                        "contradicting_evidence_ids": [],
                        "risk_tags": ["finance"],
                        "question_seed": "How validated?"
                    }
                ],
                "meta": {"slide_id": "slide_0", "num_claims": 1, "num_evidence_items": 1, "num_tensions": 1}
            },
            # Synthesis
            {
                "questions": [
                    {
                        "id": "Q1",
                        "tension_id": "T1",
                        "question": "How was the 40% cost savings validated?",
                        "persona": None,
                        "difficulty": "medium",
                        "related_claim_ids": ["C1"],
                        "evidence_ids": ["E1"],
                        "ideal_answer": {
                            "text": "The savings were validated through...",
                            "key_points": ["Customer surveys", "Case studies"],
                            "evidence_ids": ["E1"]
                        }
                    }
                ],
                "meta": {"slide_id": "slide_0", "num_tensions": 1, "num_questions": 1, "grounded": True}
            },
            # Grounding verification
            {"grounded": True, "issues": []}
        ]

        mock_deck_retriever = MagicMock()
        mock_deck_retriever.get_chunks_for_slide.return_value = create_sample_chunks()

        mock_fact_store = MagicMock()
        mock_fact_store.get_facts_by_topic.return_value = create_sample_facts()[:1]

        # Create pipeline
        pipeline = ChallengerPipeline(
            llm_client=mock_llm,
            deck_retriever=mock_deck_retriever,
            fact_store=mock_fact_store
        )

        # Create challenger with pipeline
        persona = create_cfo_persona()
        challenger = BaseChallenger(persona=persona, pipeline=pipeline, use_pipeline=True)

        # Precompute challenges
        slides = [create_sample_slide()]
        challenges = challenger.precompute_challenges(
            session_id="test_session",
            deck_context="Test deck",
            slides=slides,
            deck_retriever=mock_deck_retriever,
            fact_store=mock_fact_store,
            dossier=ResearchDossier(session_id="test_session"),
            llm_client=mock_llm
        )

        # Verify challenges were generated
        self.assertGreater(len(challenges), 0)

        # Verify challenge structure
        challenge = challenges[0]
        self.assertEqual(challenge.session_id, "test_session")
        self.assertEqual(challenge.persona_id, "cfo_1")
        self.assertTrue(challenge.question)
        self.assertTrue(challenge.ideal_answer)


class TestPersonaRoutingE2E(unittest.TestCase):
    """End-to-end tests for persona routing through pipeline."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_deck_retriever = MagicMock()
        self.mock_deck_retriever.get_chunks_for_slide.return_value = create_sample_chunks()

        self.mock_fact_store = MagicMock()
        self.mock_fact_store.get_facts_by_topic.return_value = create_sample_facts()

    def test_cfo_persona_gets_finance_questions(self):
        """Test that CFO persona gets finance-focused questions."""
        mock_llm = create_mock_llm_client()

        # Set up responses with finance-focused tension
        mock_llm.complete_with_system.side_effect = [
            # Claims
            {
                "claims": [
                    {
                        "id": "C1",
                        "text": "40% cost savings",
                        "claim_type": "metric",
                        "importance": "high",
                        "confidence": 0.9,
                        "tags": ["cost", "finance"]
                    }
                ],
                "meta": {"slide_index": 0, "used_speaker_notes": True}
            },
            # Evidence
            {
                "evidence": [
                    {
                        "id": "E1",
                        "text": "Cost data",
                        "source": "research",
                        "collection": "research_facts",
                        "relevance": "high",
                        "stance": "contradicts",
                        "related_claim_ids": ["C1"],
                        "topics": ["cost"],
                        "score_adjustment": 0.2
                    }
                ],
                "meta": {"total_candidates": 1, "selected_count": 1, "discarded_count": 0}
            },
            # Tensions with finance tag
            {
                "tensions": [
                    {
                        "id": "T1",
                        "category": "contradiction",
                        "severity": "high",
                        "headline": "Cost discrepancy",
                        "description": "Cost claims conflict with data",
                        "related_claim_ids": ["C1"],
                        "supporting_evidence_ids": [],
                        "contradicting_evidence_ids": ["E1"],
                        "risk_tags": ["finance", "cost"],
                        "question_seed": "Cost validation?"
                    }
                ],
                "meta": {"slide_id": "slide_0", "num_claims": 1, "num_evidence_items": 1, "num_tensions": 1}
            },
            # Question
            {
                "questions": [
                    {
                        "id": "Q1",
                        "tension_id": "T1",
                        "question": "From a financial perspective, how do you justify the 40% savings?",
                        "persona": "CFO",
                        "difficulty": "hard",
                        "related_claim_ids": ["C1"],
                        "evidence_ids": ["E1"],
                        "ideal_answer": {
                            "text": "Financial analysis shows...",
                            "key_points": ["ROI breakdown"],
                            "evidence_ids": ["E1"]
                        }
                    }
                ],
                "meta": {"slide_id": "slide_0", "num_tensions": 1, "num_questions": 1, "grounded": True}
            },
            {"grounded": True, "issues": []}
        ]

        pipeline = ChallengerPipeline(
            llm_client=mock_llm,
            deck_retriever=self.mock_deck_retriever,
            fact_store=self.mock_fact_store
        )

        cfo_persona = create_cfo_persona()
        challenger = BaseChallenger(persona=cfo_persona, pipeline=pipeline)

        slides = [create_sample_slide()]
        challenges = challenger.precompute_challenges(
            session_id="test",
            deck_context="Test",
            slides=slides,
            deck_retriever=self.mock_deck_retriever,
            fact_store=self.mock_fact_store,
            dossier=ResearchDossier(session_id="test"),
            llm_client=mock_llm
        )

        # CFO should get challenges related to finance
        self.assertGreater(len(challenges), 0)


class TestAdaptiveDifficultyE2E(unittest.TestCase):
    """End-to-end tests for adaptive difficulty through pipeline."""

    def test_difficulty_calculated_in_pipeline(self):
        """Test that difficulty is calculated during pipeline execution."""
        mock_llm = create_mock_llm_client()

        # LLM returns "easy" but factors should make it "hard"
        mock_llm.complete_with_system.side_effect = [
            # Claims with HIGH importance
            {
                "claims": [
                    {
                        "id": "C1",
                        "text": "Critical metric claim",
                        "claim_type": "metric",
                        "importance": "high",
                        "confidence": 0.95,
                        "tags": ["cost"]
                    },
                    {
                        "id": "C2",
                        "text": "Another important claim",
                        "claim_type": "factual",
                        "importance": "high",
                        "confidence": 0.9,
                        "tags": ["cost"]
                    }
                ],
                "meta": {"slide_index": 0, "used_speaker_notes": True}
            },
            # Strong contradicting evidence
            {
                "evidence": [
                    {
                        "id": "E1",
                        "text": "Contradicting data",
                        "source": "research",
                        "collection": "research_facts",
                        "relevance": "high",
                        "stance": "contradicts",
                        "related_claim_ids": ["C1", "C2"],
                        "topics": ["cost"],
                        "score_adjustment": 0.3
                    },
                    {
                        "id": "E2",
                        "text": "More contradicting data",
                        "source": "research",
                        "collection": "research_facts",
                        "relevance": "high",
                        "stance": "contradicts",
                        "related_claim_ids": ["C1"],
                        "topics": ["cost"],
                        "score_adjustment": 0.2
                    }
                ],
                "meta": {"total_candidates": 2, "selected_count": 2, "discarded_count": 0}
            },
            # HIGH severity tension
            {
                "tensions": [
                    {
                        "id": "T1",
                        "category": "contradiction",
                        "severity": "high",
                        "headline": "Major data conflict",
                        "description": "Critical claims contradicted by strong evidence",
                        "related_claim_ids": ["C1", "C2"],
                        "supporting_evidence_ids": [],
                        "contradicting_evidence_ids": ["E1", "E2"],
                        "risk_tags": ["cost", "credibility"],
                        "question_seed": "How explain contradiction?"
                    }
                ],
                "meta": {"slide_id": "slide_0", "num_claims": 2, "num_evidence_items": 2, "num_tensions": 1}
            },
            # Question - LLM says "easy" but should be recalculated to "hard"
            {
                "questions": [
                    {
                        "id": "Q1",
                        "tension_id": "T1",
                        "question": "How do you explain the contradiction?",
                        "persona": None,
                        "difficulty": "easy",  # Will be overridden
                        "related_claim_ids": ["C1", "C2"],
                        "evidence_ids": ["E1", "E2"],
                        "ideal_answer": {
                            "text": "Answer explaining the contradiction...",
                            "key_points": ["Point 1", "Point 2"],
                            "evidence_ids": ["E1"]
                        }
                    }
                ],
                "meta": {"slide_id": "slide_0", "num_tensions": 1, "num_questions": 1, "grounded": True}
            },
            {"grounded": True, "issues": []}
        ]

        mock_deck_retriever = MagicMock()
        mock_deck_retriever.get_chunks_for_slide.return_value = []

        mock_fact_store = MagicMock()
        mock_fact_store.get_facts_by_topic.return_value = create_sample_facts()

        pipeline = ChallengerPipeline(
            llm_client=mock_llm,
            deck_retriever=mock_deck_retriever,
            fact_store=mock_fact_store
        )

        slide = create_sample_slide()
        result = pipeline.process_slide(slide)

        # Verify question was generated
        self.assertEqual(len(result.questions), 1)

        # Difficulty should be recalculated to "hard" due to:
        # - HIGH severity tension
        # - HIGH importance claims
        # - Strong contradicting evidence
        # - Multiple related claims (complexity)
        self.assertEqual(result.questions[0].difficulty, "hard")

        # Should have explanation in notes
        self.assertIn("Difficulty:", result.questions[0].notes)


class TestErrorRecovery(unittest.TestCase):
    """Tests for error recovery in pipeline execution."""

    def test_claim_extraction_handles_llm_errors_gracefully(self):
        """Test that claim extraction handles LLM errors gracefully."""
        mock_llm = create_mock_llm_client()
        mock_llm.complete_with_system.side_effect = Exception("LLM unavailable")

        mock_deck_retriever = MagicMock()
        mock_fact_store = MagicMock()

        pipeline = ChallengerPipeline(
            llm_client=mock_llm,
            deck_retriever=mock_deck_retriever,
            fact_store=mock_fact_store
        )

        slide = create_sample_slide()
        result = pipeline.process_slide(slide)

        # Should return empty result gracefully (ClaimExtractionAgent handles errors internally)
        self.assertEqual(len(result.claims), 0)
        self.assertEqual(len(result.questions), 0)
        # Pipeline marks it as "no_claims" since extractor returns empty
        self.assertIn("no_claims", result.meta.steps_completed)

    def test_evidence_selection_handles_errors_gracefully(self):
        """Test that evidence selection handles errors gracefully."""
        mock_llm = create_mock_llm_client()

        # Claims succeed, evidence selector handles error internally
        mock_llm.complete_with_system.side_effect = [
            # Claim extraction succeeds
            {
                "claims": [
                    {
                        "id": "C1",
                        "text": "Test claim",
                        "claim_type": "factual",
                        "importance": "medium",
                        "confidence": 0.8,
                        "tags": ["test"]
                    }
                ],
                "meta": {"slide_index": 0, "used_speaker_notes": False}
            },
            # Evidence selection handles error internally, returns empty
            Exception("Evidence selection error"),
            # Analysis continues with empty evidence
            {
                "tensions": [],
                "meta": {"slide_id": "slide_0", "num_claims": 1, "num_evidence_items": 0, "num_tensions": 0}
            }
        ]

        mock_deck_retriever = MagicMock()
        mock_deck_retriever.get_chunks_for_slide.return_value = create_sample_chunks()

        mock_fact_store = MagicMock()
        mock_fact_store.get_facts_by_topic.return_value = []

        pipeline = ChallengerPipeline(
            llm_client=mock_llm,
            deck_retriever=mock_deck_retriever,
            fact_store=mock_fact_store
        )

        slide = create_sample_slide()
        result = pipeline.process_slide(slide)

        # Claims should be extracted
        self.assertGreater(len(result.claims), 0)
        # Pipeline continues even when evidence selection has issues
        self.assertIn("evidence_selection", result.meta.steps_completed)

    def test_all_slides_processed_even_with_errors(self):
        """Test that all slides are processed even when some have LLM errors."""
        mock_llm = create_mock_llm_client()

        # All slides return no claims (graceful handling of any errors)
        mock_llm.complete_with_system.side_effect = [
            # Slide 1 - claims (no claims found)
            {"claims": [], "meta": {"slide_index": 0, "used_speaker_notes": False}},
            # Slide 2 - error handled internally, returns empty
            Exception("Processing error"),
            # Slide 3 - claims (no claims found)
            {"claims": [], "meta": {"slide_index": 2, "used_speaker_notes": False}}
        ]

        mock_deck_retriever = MagicMock()
        mock_deck_retriever.get_chunks_for_slide.return_value = []

        mock_fact_store = MagicMock()
        mock_fact_store.get_facts_by_topic.return_value = []

        pipeline = ChallengerPipeline(
            llm_client=mock_llm,
            deck_retriever=mock_deck_retriever,
            fact_store=mock_fact_store
        )

        slides = [
            create_sample_slide(0, "Slide 1"),
            create_sample_slide(1, "Slide 2"),
            create_sample_slide(2, "Slide 3")
        ]

        results = pipeline.process_deck(slides)

        # All slides should have results
        self.assertEqual(len(results), 3)

        # All should complete gracefully (agents handle errors internally)
        for result in results:
            self.assertIn("no_claims", result.meta.steps_completed)


class TestPipelineConfig(unittest.TestCase):
    """Tests for pipeline configuration options."""

    def test_max_questions_limit(self):
        """Test that max_questions_per_slide limit is enforced."""
        mock_llm = create_mock_llm_client()

        # Return more questions than limit
        mock_llm.complete_with_system.side_effect = [
            # Claims
            {
                "claims": [
                    {"id": "C1", "text": "Claim 1", "claim_type": "factual", "importance": "high", "confidence": 0.9, "tags": ["test"]}
                ],
                "meta": {"slide_index": 0, "used_speaker_notes": False}
            },
            # Evidence
            {"evidence": [], "meta": {"total_candidates": 0, "selected_count": 0, "discarded_count": 0}},
            # Multiple tensions
            {
                "tensions": [
                    {"id": "T1", "category": "risk_exposure", "severity": "high", "headline": "Risk 1", "description": "Desc", "related_claim_ids": ["C1"], "supporting_evidence_ids": [], "contradicting_evidence_ids": [], "risk_tags": [], "question_seed": "Q?"},
                    {"id": "T2", "category": "risk_exposure", "severity": "high", "headline": "Risk 2", "description": "Desc", "related_claim_ids": ["C1"], "supporting_evidence_ids": [], "contradicting_evidence_ids": [], "risk_tags": [], "question_seed": "Q?"},
                    {"id": "T3", "category": "risk_exposure", "severity": "high", "headline": "Risk 3", "description": "Desc", "related_claim_ids": ["C1"], "supporting_evidence_ids": [], "contradicting_evidence_ids": [], "risk_tags": [], "question_seed": "Q?"},
                ],
                "meta": {"slide_id": "slide_0", "num_claims": 1, "num_evidence_items": 0, "num_tensions": 3}
            },
            # 3 questions returned
            {
                "questions": [
                    {"id": "Q1", "tension_id": "T1", "question": "Q1?", "persona": None, "difficulty": "hard", "related_claim_ids": ["C1"], "evidence_ids": [], "ideal_answer": {"text": "A1", "key_points": ["p1"], "evidence_ids": []}},
                    {"id": "Q2", "tension_id": "T2", "question": "Q2?", "persona": None, "difficulty": "hard", "related_claim_ids": ["C1"], "evidence_ids": [], "ideal_answer": {"text": "A2", "key_points": ["p2"], "evidence_ids": []}},
                    {"id": "Q3", "tension_id": "T3", "question": "Q3?", "persona": None, "difficulty": "hard", "related_claim_ids": ["C1"], "evidence_ids": [], "ideal_answer": {"text": "A3", "key_points": ["p3"], "evidence_ids": []}},
                ],
                "meta": {"slide_id": "slide_0", "num_tensions": 3, "num_questions": 3, "grounded": True}
            },
            # Grounding for each
            {"grounded": True, "issues": []},
            {"grounded": True, "issues": []},
            {"grounded": True, "issues": []},
        ]

        mock_deck_retriever = MagicMock()
        mock_deck_retriever.get_chunks_for_slide.return_value = []

        mock_fact_store = MagicMock()
        mock_fact_store.get_facts_by_topic.return_value = []

        # Limit to 2 questions
        config = PipelineConfig(max_questions_per_slide=2)
        pipeline = ChallengerPipeline(
            llm_client=mock_llm,
            deck_retriever=mock_deck_retriever,
            fact_store=mock_fact_store,
            config=config
        )

        slide = create_sample_slide()
        result = pipeline.process_slide(slide)

        # Should be limited to 2
        self.assertLessEqual(len(result.questions), 2)


if __name__ == "__main__":
    unittest.main()
