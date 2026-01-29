"""
Tests for the QuestionSynthesisAgent.

Tests cover:
- Happy path synthesis with various tension types
- Grounding verification
- Grounding failure and retry logic
- Malformed JSON fallback handling
- Empty tensions handling
- Persona-specific synthesis
"""
import unittest
from unittest.mock import MagicMock, call

from backend.challenges.question_synthesizer import (
    QuestionSynthesisAgent,
    QUESTION_SYNTHESIS_SYSTEM_PROMPT,
    GROUNDING_VERIFICATION_PROMPT,
    _format_tensions_for_prompt,
    _format_claims_for_prompt,
    _format_evidence_for_prompt,
    _build_synthesis_user_prompt,
    _build_persona_context,
    _filter_tensions_for_persona,
    _severity_to_difficulty,
    _create_fallback_question,
    _parse_ideal_answer,
    _parse_question,
)
from backend.models.core import (
    Claim,
    ClaimType,
    ClaimImportance,
    EvidenceItem,
    EvidenceSource,
    EvidenceRelevance,
    EvidenceStance,
    Tension,
    TensionCategory,
    TensionSeverity,
    AnalysisResult,
    AnalysisMeta,
    IdealAnswer,
    ChallengeQuestion,
    QuestionSynthesisMeta,
    QuestionSynthesisResult,
    ChallengerPersona,
)
from backend.models.llm import MockLLM


class TestHelperFunctions(unittest.TestCase):
    """Tests for helper functions."""

    def test_severity_to_difficulty_high(self):
        """Test HIGH severity maps to hard difficulty."""
        self.assertEqual(_severity_to_difficulty(TensionSeverity.HIGH), "hard")

    def test_severity_to_difficulty_medium(self):
        """Test MEDIUM severity maps to medium difficulty."""
        self.assertEqual(_severity_to_difficulty(TensionSeverity.MEDIUM), "medium")

    def test_severity_to_difficulty_low(self):
        """Test LOW severity maps to easy difficulty."""
        self.assertEqual(_severity_to_difficulty(TensionSeverity.LOW), "easy")

    def test_parse_ideal_answer(self):
        """Test parsing ideal answer from dict."""
        data = {
            "text": "Test answer",
            "key_points": ["point1", "point2"],
            "evidence_ids": ["E1", "E2"]
        }
        result = _parse_ideal_answer(data)
        self.assertEqual(result.text, "Test answer")
        self.assertEqual(result.key_points, ["point1", "point2"])
        self.assertEqual(result.evidence_ids, ["E1", "E2"])

    def test_parse_ideal_answer_empty(self):
        """Test parsing ideal answer with missing fields."""
        result = _parse_ideal_answer({})
        self.assertEqual(result.text, "")
        self.assertEqual(result.key_points, [])
        self.assertEqual(result.evidence_ids, [])

    def test_parse_question(self):
        """Test parsing question from dict."""
        data = {
            "id": "Q1",
            "tension_id": "T1",
            "question": "Test question?",
            "persona": "CFO",
            "difficulty": "hard",
            "related_claim_ids": ["C1"],
            "evidence_ids": ["E1"],
            "ideal_answer": {
                "text": "Answer text",
                "key_points": ["point"],
                "evidence_ids": ["E1"]
            },
            "notes": "Test notes"
        }
        result = _parse_question(data)
        self.assertEqual(result.id, "Q1")
        self.assertEqual(result.tension_id, "T1")
        self.assertEqual(result.question, "Test question?")
        self.assertEqual(result.persona, "CFO")
        self.assertEqual(result.difficulty, "hard")
        self.assertEqual(result.ideal_answer.text, "Answer text")

    def test_format_tensions_for_prompt_empty(self):
        """Test formatting empty tensions list."""
        result = _format_tensions_for_prompt([])
        self.assertEqual(result, "No tensions provided.")

    def test_format_tensions_for_prompt(self):
        """Test formatting tensions for prompt."""
        tensions = [
            Tension(
                id="T1",
                category=TensionCategory.CONTRADICTION,
                severity=TensionSeverity.HIGH,
                headline="Test tension",
                description="Test description",
                related_claim_ids=["C1"],
                contradicting_evidence_ids=["E1"],
                question_seed="Test seed?"
            )
        ]
        result = _format_tensions_for_prompt(tensions)
        self.assertIn("[T1]", result)
        self.assertIn("contradiction", result)
        self.assertIn("high", result)
        self.assertIn("Test tension", result)
        self.assertIn("Test seed?", result)

    def test_format_claims_for_prompt_empty(self):
        """Test formatting empty claims list."""
        result = _format_claims_for_prompt([])
        self.assertEqual(result, "No claims provided.")

    def test_format_claims_for_prompt(self):
        """Test formatting claims for prompt."""
        claims = [
            Claim(
                id="C1",
                text="Test claim",
                claim_type=ClaimType.FACTUAL,
                importance=ClaimImportance.HIGH,
                confidence=0.9
            )
        ]
        result = _format_claims_for_prompt(claims)
        self.assertIn("[C1]", result)
        self.assertIn("factual", result)
        self.assertIn("Test claim", result)

    def test_format_evidence_for_prompt_empty(self):
        """Test formatting empty evidence list."""
        result = _format_evidence_for_prompt([])
        self.assertEqual(result, "No evidence provided.")

    def test_format_evidence_for_prompt(self):
        """Test formatting evidence for prompt."""
        evidence = [
            EvidenceItem(
                id="E1",
                text="Test evidence",
                source=EvidenceSource.RESEARCH,
                collection="test",
                relevance=EvidenceRelevance.HIGH,
                stance=EvidenceStance.CONTRADICTS,
                related_claim_ids=["C1"],
                topics=["test"],
                score_adjustment=0.1
            )
        ]
        result = _format_evidence_for_prompt(evidence)
        self.assertIn("[E1]", result)
        self.assertIn("contradicts", result)
        self.assertIn("Test evidence", result)

    def test_build_synthesis_user_prompt(self):
        """Test building synthesis user prompt."""
        tensions = [
            Tension(
                id="T1",
                category=TensionCategory.CONTRADICTION,
                severity=TensionSeverity.HIGH,
                headline="Test",
                description="Test desc"
            )
        ]
        claims = [
            Claim(
                id="C1",
                text="Test claim",
                claim_type=ClaimType.FACTUAL,
                importance=ClaimImportance.HIGH,
                confidence=0.9
            )
        ]
        evidence = [
            EvidenceItem(
                id="E1",
                text="Test evidence",
                source=EvidenceSource.RESEARCH,
                collection="test",
                relevance=EvidenceRelevance.HIGH,
                stance=EvidenceStance.CONTRADICTS,
                related_claim_ids=["C1"],
                topics=["test"],
                score_adjustment=0.1
            )
        ]
        result = _build_synthesis_user_prompt("slide_0", tensions, claims, evidence)
        self.assertIn("slide_0", result)
        self.assertIn("Tensions (1 total)", result)
        self.assertIn("Claims (1 total)", result)
        self.assertIn("Evidence (1 total)", result)

    def test_build_synthesis_user_prompt_with_persona(self):
        """Test building synthesis user prompt with persona."""
        result = _build_synthesis_user_prompt("slide_0", [], [], [], persona="CFO")
        self.assertIn("CFO", result)
        self.assertIn("Persona Context", result)


class TestFallbackQuestion(unittest.TestCase):
    """Tests for fallback question generation."""

    def test_create_fallback_question(self):
        """Test creating a fallback question from tension."""
        tension = Tension(
            id="T1",
            category=TensionCategory.CONTRADICTION,
            severity=TensionSeverity.HIGH,
            headline="Cost savings discrepancy",
            description="The claimed savings don't match industry data",
            related_claim_ids=["C1"],
            contradicting_evidence_ids=["E1"]
        )
        result = _create_fallback_question(tension, 1)

        self.assertEqual(result.id, "Q1")
        self.assertEqual(result.tension_id, "T1")
        self.assertIn("Cost savings discrepancy", result.question)
        self.assertEqual(result.difficulty, "hard")
        self.assertEqual(result.related_claim_ids, ["C1"])
        self.assertIn("E1", result.evidence_ids)
        self.assertIn("Fallback question", result.notes)

    def test_create_fallback_question_medium_severity(self):
        """Test fallback question has medium difficulty for medium severity."""
        tension = Tension(
            id="T2",
            category=TensionCategory.MISSING_EVIDENCE,
            severity=TensionSeverity.MEDIUM,
            headline="Missing data",
            description="No supporting evidence"
        )
        result = _create_fallback_question(tension, 2)
        self.assertEqual(result.difficulty, "medium")


class TestQuestionSynthesisAgent(unittest.TestCase):
    """Tests for QuestionSynthesisAgent."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_llm = MockLLM()
        self.agent = QuestionSynthesisAgent(self.mock_llm)

        # Sample test data
        self.sample_claims = [
            Claim(
                id="C1",
                text="We achieve 40% cost savings",
                claim_type=ClaimType.METRIC,
                importance=ClaimImportance.HIGH,
                confidence=0.9
            ),
            Claim(
                id="C2",
                text="Implementation takes 6 months",
                claim_type=ClaimType.FORECAST,
                importance=ClaimImportance.MEDIUM,
                confidence=0.7
            )
        ]

        self.sample_evidence = [
            EvidenceItem(
                id="E1",
                text="Industry benchmarks show 15-25% typical cost savings",
                source=EvidenceSource.RESEARCH,
                collection="research_facts",
                relevance=EvidenceRelevance.HIGH,
                stance=EvidenceStance.CONTRADICTS,
                related_claim_ids=["C1"],
                topics=["cost", "benchmarks"],
                score_adjustment=0.2
            ),
            EvidenceItem(
                id="E2",
                text="Enterprise deployments typically take 9-12 months",
                source=EvidenceSource.RESEARCH,
                collection="research_facts",
                relevance=EvidenceRelevance.MEDIUM,
                stance=EvidenceStance.CONTRADICTS,
                related_claim_ids=["C2"],
                topics=["timeline", "deployment"],
                score_adjustment=0.1
            )
        ]

        self.sample_tensions = [
            Tension(
                id="T1",
                category=TensionCategory.CONTRADICTION,
                severity=TensionSeverity.HIGH,
                headline="Cost savings claim contradicts industry data",
                description="The claimed 40% cost reduction conflicts with benchmarks",
                related_claim_ids=["C1"],
                contradicting_evidence_ids=["E1"],
                question_seed="How do you reconcile cost savings claims?"
            ),
            Tension(
                id="T2",
                category=TensionCategory.MISSING_EVIDENCE,
                severity=TensionSeverity.MEDIUM,
                headline="Timeline lacks supporting data",
                description="No evidence supports the 6-month timeline",
                related_claim_ids=["C2"],
                contradicting_evidence_ids=["E2"]
            )
        ]

        self.sample_analysis = AnalysisResult(
            slide_id="slide_0",
            tensions=self.sample_tensions,
            meta=AnalysisMeta(
                slide_id="slide_0",
                num_claims=2,
                num_evidence_items=2,
                num_tensions=2,
                processing_notes="Test analysis"
            )
        )

    def test_synthesize_happy_path(self):
        """Test successful question synthesis."""
        result = self.agent.synthesize(
            slide_id="slide_0",
            analysis=self.sample_analysis,
            claims=self.sample_claims,
            evidence=self.sample_evidence
        )

        self.assertIsInstance(result, QuestionSynthesisResult)
        self.assertEqual(len(result.questions), 1)  # MockLLM returns 1 question
        self.assertEqual(result.meta.slide_id, "slide_0")
        self.assertTrue(result.meta.grounded)

    def test_synthesize_returns_valid_question_structure(self):
        """Test that synthesized questions have valid structure."""
        result = self.agent.synthesize(
            slide_id="slide_0",
            analysis=self.sample_analysis,
            claims=self.sample_claims,
            evidence=self.sample_evidence
        )

        question = result.questions[0]
        self.assertEqual(question.id, "Q1")
        self.assertEqual(question.tension_id, "T1")
        self.assertIn("cost savings", question.question.lower())
        self.assertEqual(question.difficulty, "hard")
        self.assertIsInstance(question.ideal_answer, IdealAnswer)
        self.assertTrue(len(question.ideal_answer.key_points) >= 1)

    def test_synthesize_empty_tensions(self):
        """Test synthesis with no tensions returns empty result."""
        empty_analysis = AnalysisResult(
            slide_id="slide_0",
            tensions=[],
            meta=AnalysisMeta(
                slide_id="slide_0",
                num_claims=2,
                num_evidence_items=2,
                num_tensions=0,
                processing_notes="No tensions"
            )
        )

        result = self.agent.synthesize(
            slide_id="slide_0",
            analysis=empty_analysis,
            claims=self.sample_claims,
            evidence=self.sample_evidence
        )

        self.assertEqual(len(result.questions), 0)
        self.assertEqual(result.meta.num_questions, 0)
        self.assertTrue(result.meta.grounded)
        self.assertIn("No tensions", result.meta.notes)

    def test_synthesize_with_persona(self):
        """Test synthesis with persona context."""
        llm_client = MagicMock()
        llm_client.complete_with_system.side_effect = [
            {
                "questions": [
                    {
                        "id": "Q1",
                        "tension_id": "T1",
                        "question": "From a CFO perspective, how do you justify the 40% cost savings?",
                        "persona": "CFO",
                        "difficulty": "hard",
                        "related_claim_ids": ["C1"],
                        "evidence_ids": ["E1"],
                        "ideal_answer": {
                            "text": "Financial analysis shows...",
                            "key_points": ["ROI breakdown", "TCO analysis"],
                            "evidence_ids": ["E1"]
                        }
                    }
                ],
                "meta": {
                    "slide_id": "slide_0",
                    "num_tensions": 1,
                    "num_questions": 1,
                    "grounded": True
                }
            },
            {"grounded": True, "issues": []}
        ]

        agent = QuestionSynthesisAgent(llm_client)
        result = agent.synthesize(
            slide_id="slide_0",
            analysis=self.sample_analysis,
            claims=self.sample_claims,
            evidence=self.sample_evidence,
            persona="CFO"
        )

        self.assertEqual(result.questions[0].persona, "CFO")
        # Verify persona was included in the prompt
        call_args = llm_client.complete_with_system.call_args
        self.assertIn("CFO", call_args[1]["user_prompt"])

    def test_synthesize_filters_low_severity_when_enough_tensions(self):
        """Test that LOW severity tensions are filtered when there are enough HIGH/MEDIUM."""
        # Add a low severity tension
        tensions_with_low = self.sample_tensions + [
            Tension(
                id="T3",
                category=TensionCategory.AMBIGUITY,
                severity=TensionSeverity.LOW,
                headline="Minor ambiguity",
                description="Slightly unclear wording"
            )
        ]

        analysis = AnalysisResult(
            slide_id="slide_0",
            tensions=tensions_with_low,
            meta=AnalysisMeta(
                slide_id="slide_0",
                num_claims=2,
                num_evidence_items=2,
                num_tensions=3
            )
        )

        llm_client = MagicMock()
        # First call: synthesis, Second call: grounding verification
        llm_client.complete_with_system.side_effect = [
            {
                "questions": [
                    {
                        "id": "Q1",
                        "tension_id": "T1",
                        "question": "Test question?",
                        "difficulty": "hard",
                        "related_claim_ids": ["C1"],
                        "evidence_ids": ["E1"],
                        "ideal_answer": {"text": "Answer", "key_points": ["point"], "evidence_ids": ["E1"]}
                    }
                ],
                "meta": {"slide_id": "slide_0", "num_tensions": 2, "num_questions": 1, "grounded": True}
            },
            {"grounded": True, "issues": []}  # Grounding verification
        ]

        agent = QuestionSynthesisAgent(llm_client)
        agent.synthesize(
            slide_id="slide_0",
            analysis=analysis,
            claims=self.sample_claims,
            evidence=self.sample_evidence
        )

        # Check that the user prompt only includes HIGH and MEDIUM severity tensions
        # Get the first call (synthesis) args
        first_call_args = llm_client.complete_with_system.call_args_list[0]
        user_prompt = first_call_args[1]["user_prompt"]
        self.assertIn("T1", user_prompt)
        self.assertIn("T2", user_prompt)
        # T3 (LOW severity) should be excluded
        self.assertNotIn("Minor ambiguity", user_prompt)


class TestGroundingVerification(unittest.TestCase):
    """Tests for grounding verification."""

    def setUp(self):
        """Set up test fixtures."""
        self.sample_evidence = [
            EvidenceItem(
                id="E1",
                text="Industry benchmarks show 15-25% savings",
                source=EvidenceSource.RESEARCH,
                collection="test",
                relevance=EvidenceRelevance.HIGH,
                stance=EvidenceStance.CONTRADICTS,
                related_claim_ids=["C1"],
                topics=["cost"],
                score_adjustment=0.1
            )
        ]

        self.sample_question = ChallengeQuestion(
            id="Q1",
            tension_id="T1",
            question="How do you justify 40% savings?",
            persona=None,
            difficulty="hard",
            related_claim_ids=["C1"],
            evidence_ids=["E1"],
            ideal_answer=IdealAnswer(
                text="The savings include direct and indirect benefits",
                key_points=["Direct savings 20%", "Indirect savings 20%"],
                evidence_ids=["E1"]
            )
        )

    def test_verify_grounding_success(self):
        """Test successful grounding verification."""
        agent = QuestionSynthesisAgent(MockLLM())
        result = agent.verify_grounding(self.sample_question, self.sample_evidence)
        self.assertTrue(result)

    def test_verify_grounding_failure(self):
        """Test grounding verification failure."""
        llm_client = MagicMock()
        llm_client.complete_with_system.return_value = {
            "grounded": False,
            "issues": ["Evidence ID E3 not found in provided evidence"]
        }

        agent = QuestionSynthesisAgent(llm_client)
        result = agent.verify_grounding(self.sample_question, self.sample_evidence)
        self.assertFalse(result)

    def test_verify_grounding_exception_handling(self):
        """Test grounding verification handles exceptions."""
        llm_client = MagicMock()
        llm_client.complete_with_system.side_effect = Exception("LLM error")

        agent = QuestionSynthesisAgent(llm_client)
        result = agent.verify_grounding(self.sample_question, self.sample_evidence)
        self.assertFalse(result)


class TestGroundingRetry(unittest.TestCase):
    """Tests for grounding retry logic."""

    def setUp(self):
        """Set up test fixtures."""
        self.sample_claims = [
            Claim(
                id="C1",
                text="We achieve 40% cost savings",
                claim_type=ClaimType.METRIC,
                importance=ClaimImportance.HIGH,
                confidence=0.9
            )
        ]

        self.sample_evidence = [
            EvidenceItem(
                id="E1",
                text="Industry benchmarks show 15-25% savings",
                source=EvidenceSource.RESEARCH,
                collection="test",
                relevance=EvidenceRelevance.HIGH,
                stance=EvidenceStance.CONTRADICTS,
                related_claim_ids=["C1"],
                topics=["cost"],
                score_adjustment=0.1
            )
        ]

        self.sample_tensions = [
            Tension(
                id="T1",
                category=TensionCategory.CONTRADICTION,
                severity=TensionSeverity.HIGH,
                headline="Cost savings discrepancy",
                description="Claimed savings don't match industry data",
                related_claim_ids=["C1"],
                contradicting_evidence_ids=["E1"]
            )
        ]

        self.sample_analysis = AnalysisResult(
            slide_id="slide_0",
            tensions=self.sample_tensions,
            meta=AnalysisMeta(
                slide_id="slide_0",
                num_claims=1,
                num_evidence_items=1,
                num_tensions=1
            )
        )

    def test_retry_on_grounding_failure(self):
        """Test that questions are retried when grounding fails."""
        llm_client = MagicMock()

        # First call: synthesis returns ungrounded question
        # Second call: grounding verification returns false
        # Third call: retry synthesis returns new question
        # Fourth call: grounding verification returns true
        llm_client.complete_with_system.side_effect = [
            # Initial synthesis
            {
                "questions": [{
                    "id": "Q1",
                    "tension_id": "T1",
                    "question": "Ungrounded question?",
                    "difficulty": "hard",
                    "related_claim_ids": ["C1"],
                    "evidence_ids": ["E999"],  # Invalid evidence ID
                    "ideal_answer": {
                        "text": "Bad answer",
                        "key_points": ["point"],
                        "evidence_ids": ["E999"]
                    }
                }],
                "meta": {"slide_id": "slide_0", "num_tensions": 1, "num_questions": 1, "grounded": True}
            },
            # First grounding check - fails
            {"grounded": False, "issues": ["E999 not found"]},
            # Retry synthesis
            {
                "id": "Q1",
                "tension_id": "T1",
                "question": "Properly grounded question?",
                "difficulty": "hard",
                "related_claim_ids": ["C1"],
                "evidence_ids": ["E1"],
                "ideal_answer": {
                    "text": "Good answer citing E1",
                    "key_points": ["Benchmarks show 15-25%"],
                    "evidence_ids": ["E1"]
                }
            },
            # Second grounding check - succeeds
            {"grounded": True, "issues": []}
        ]

        agent = QuestionSynthesisAgent(llm_client)
        result = agent.synthesize(
            slide_id="slide_0",
            analysis=self.sample_analysis,
            claims=self.sample_claims,
            evidence=self.sample_evidence
        )

        # Should have retried and gotten the grounded question
        self.assertEqual(len(result.questions), 1)
        self.assertIn("grounded", result.questions[0].question.lower())
        self.assertTrue(result.meta.grounded)

    def test_retry_failure_drops_ungrounded_question(self):
        """Test that ungrounded questions are dropped if retry also fails."""
        llm_client = MagicMock()

        llm_client.complete_with_system.side_effect = [
            # Initial synthesis
            {
                "questions": [{
                    "id": "Q1",
                    "tension_id": "T1",
                    "question": "Ungrounded question?",
                    "difficulty": "hard",
                    "related_claim_ids": ["C1"],
                    "evidence_ids": ["E999"],
                    "ideal_answer": {"text": "Bad", "key_points": ["x"], "evidence_ids": ["E999"]}
                }],
                "meta": {"slide_id": "slide_0", "num_tensions": 1, "num_questions": 1, "grounded": True}
            },
            # First grounding check - fails
            {"grounded": False, "issues": ["E999 not found"]},
            # Retry synthesis - also bad
            {
                "id": "Q1",
                "tension_id": "T1",
                "question": "Still ungrounded?",
                "difficulty": "hard",
                "related_claim_ids": ["C1"],
                "evidence_ids": ["E888"],
                "ideal_answer": {"text": "Still bad", "key_points": ["y"], "evidence_ids": ["E888"]}
            },
            # Second grounding check - also fails
            {"grounded": False, "issues": ["E888 not found"]}
        ]

        agent = QuestionSynthesisAgent(llm_client)
        result = agent.synthesize(
            slide_id="slide_0",
            analysis=self.sample_analysis,
            claims=self.sample_claims,
            evidence=self.sample_evidence
        )

        # Should have dropped the question
        self.assertEqual(len(result.questions), 0)
        self.assertFalse(result.meta.grounded)


class TestFallbackBehavior(unittest.TestCase):
    """Tests for fallback behavior on LLM errors."""

    def setUp(self):
        """Set up test fixtures."""
        self.sample_claims = [
            Claim(
                id="C1",
                text="Test claim",
                claim_type=ClaimType.FACTUAL,
                importance=ClaimImportance.HIGH,
                confidence=0.9
            )
        ]

        self.sample_evidence = [
            EvidenceItem(
                id="E1",
                text="Test evidence",
                source=EvidenceSource.RESEARCH,
                collection="test",
                relevance=EvidenceRelevance.HIGH,
                stance=EvidenceStance.CONTRADICTS,
                related_claim_ids=["C1"],
                topics=["test"],
                score_adjustment=0.1
            )
        ]

        self.sample_tensions = [
            Tension(
                id="T1",
                category=TensionCategory.CONTRADICTION,
                severity=TensionSeverity.HIGH,
                headline="Test tension headline",
                description="Test description",
                related_claim_ids=["C1"],
                contradicting_evidence_ids=["E1"]
            )
        ]

        self.sample_analysis = AnalysisResult(
            slide_id="slide_0",
            tensions=self.sample_tensions,
            meta=AnalysisMeta(
                slide_id="slide_0",
                num_claims=1,
                num_evidence_items=1,
                num_tensions=1
            )
        )

    def test_fallback_on_exception(self):
        """Test fallback questions are generated on LLM exception."""
        llm_client = MagicMock()
        llm_client.complete_with_system.side_effect = Exception("LLM unavailable")

        agent = QuestionSynthesisAgent(llm_client)
        result = agent.synthesize(
            slide_id="slide_0",
            analysis=self.sample_analysis,
            claims=self.sample_claims,
            evidence=self.sample_evidence
        )

        self.assertEqual(len(result.questions), 1)
        self.assertIn("risks", result.questions[0].question.lower())
        self.assertIn("Test tension headline", result.questions[0].question)
        self.assertFalse(result.meta.grounded)
        self.assertIn("Fallback", result.meta.notes)

    def test_fallback_on_non_dict_response(self):
        """Test fallback when LLM returns non-dict response."""
        llm_client = MagicMock()
        llm_client.complete_with_system.return_value = "Invalid string response"

        agent = QuestionSynthesisAgent(llm_client)
        result = agent.synthesize(
            slide_id="slide_0",
            analysis=self.sample_analysis,
            claims=self.sample_claims,
            evidence=self.sample_evidence
        )

        self.assertEqual(len(result.questions), 1)
        self.assertFalse(result.meta.grounded)

    def test_fallback_preserves_tension_data(self):
        """Test that fallback questions preserve tension information."""
        llm_client = MagicMock()
        llm_client.complete_with_system.side_effect = Exception("Error")

        agent = QuestionSynthesisAgent(llm_client)
        result = agent.synthesize(
            slide_id="slide_0",
            analysis=self.sample_analysis,
            claims=self.sample_claims,
            evidence=self.sample_evidence
        )

        question = result.questions[0]
        self.assertEqual(question.tension_id, "T1")
        self.assertEqual(question.related_claim_ids, ["C1"])
        self.assertIn("E1", question.evidence_ids)
        self.assertEqual(question.difficulty, "hard")  # HIGH severity -> hard


class TestMultipleTensions(unittest.TestCase):
    """Tests for handling multiple tensions."""

    def test_synthesize_multiple_tensions(self):
        """Test synthesis with multiple different tension types."""
        llm_client = MagicMock()
        # First call: synthesis, then grounding verification for each question
        llm_client.complete_with_system.side_effect = [
            {
                "questions": [
                    {
                        "id": "Q1",
                        "tension_id": "T1",
                        "question": "How do you reconcile the cost discrepancy?",
                        "difficulty": "hard",
                        "related_claim_ids": ["C1"],
                        "evidence_ids": ["E1"],
                        "ideal_answer": {
                            "text": "Answer 1",
                            "key_points": ["point1"],
                            "evidence_ids": ["E1"]
                        }
                    },
                    {
                        "id": "Q2",
                        "tension_id": "T2",
                        "question": "What evidence supports the timeline?",
                        "difficulty": "medium",
                        "related_claim_ids": ["C2"],
                        "evidence_ids": ["E2"],
                        "ideal_answer": {
                            "text": "Answer 2",
                            "key_points": ["point2"],
                            "evidence_ids": ["E2"]
                        }
                    }
                ],
                "meta": {
                    "slide_id": "slide_0",
                    "num_tensions": 2,
                    "num_questions": 2,
                    "grounded": True
                }
            },
            {"grounded": True, "issues": []},  # Grounding verification for Q1
            {"grounded": True, "issues": []}   # Grounding verification for Q2
        ]

        tensions = [
            Tension(
                id="T1",
                category=TensionCategory.CONTRADICTION,
                severity=TensionSeverity.HIGH,
                headline="Cost discrepancy",
                description="Cost claims conflict"
            ),
            Tension(
                id="T2",
                category=TensionCategory.MISSING_EVIDENCE,
                severity=TensionSeverity.MEDIUM,
                headline="Missing timeline data",
                description="No evidence for timeline"
            )
        ]

        analysis = AnalysisResult(
            slide_id="slide_0",
            tensions=tensions,
            meta=AnalysisMeta(
                slide_id="slide_0",
                num_claims=2,
                num_evidence_items=2,
                num_tensions=2
            )
        )

        # Disable adaptive difficulty to test LLM-assigned difficulty is preserved
        agent = QuestionSynthesisAgent(llm_client, use_adaptive_difficulty=False)
        result = agent.synthesize(
            slide_id="slide_0",
            analysis=analysis,
            claims=[],
            evidence=[]
        )

        self.assertEqual(len(result.questions), 2)
        self.assertEqual(result.questions[0].difficulty, "hard")
        self.assertEqual(result.questions[1].difficulty, "medium")


class TestAdaptiveDifficulty(unittest.TestCase):
    """Tests for adaptive difficulty feature."""

    def test_adaptive_difficulty_recalculates(self):
        """Test that adaptive difficulty overrides LLM-assigned difficulty."""
        llm_client = MagicMock()
        llm_client.complete_with_system.side_effect = [
            {
                "questions": [{
                    "id": "Q1",
                    "tension_id": "T1",
                    "question": "Test question?",
                    "difficulty": "easy",  # LLM says easy
                    "related_claim_ids": ["C1", "C2"],
                    "evidence_ids": ["E1", "E2"],
                    "ideal_answer": {
                        "text": "Answer",
                        "key_points": ["point"],
                        "evidence_ids": ["E1"]
                    }
                }],
                "meta": {"slide_id": "slide_0", "num_tensions": 1, "num_questions": 1, "grounded": True}
            },
            {"grounded": True, "issues": []}
        ]

        tension = Tension(
            id="T1",
            category=TensionCategory.CONTRADICTION,
            severity=TensionSeverity.HIGH,  # HIGH severity
            headline="Major contradiction",
            description="Test",
            related_claim_ids=["C1", "C2"],
            contradicting_evidence_ids=["E1", "E2"]
        )

        claims = [
            Claim(
                id="C1",
                text="Claim 1",
                claim_type=ClaimType.METRIC,
                importance=ClaimImportance.HIGH,
                confidence=0.9
            ),
            Claim(
                id="C2",
                text="Claim 2",
                claim_type=ClaimType.FACTUAL,
                importance=ClaimImportance.HIGH,
                confidence=0.9
            ),
        ]

        evidence = [
            EvidenceItem(
                id="E1",
                text="Contradicting evidence 1",
                source=EvidenceSource.RESEARCH,
                collection="test",
                relevance=EvidenceRelevance.HIGH,
                stance=EvidenceStance.CONTRADICTS,
                related_claim_ids=["C1"],
                topics=["test"],
                score_adjustment=0.1
            ),
            EvidenceItem(
                id="E2",
                text="Contradicting evidence 2",
                source=EvidenceSource.RESEARCH,
                collection="test",
                relevance=EvidenceRelevance.HIGH,
                stance=EvidenceStance.CONTRADICTS,
                related_claim_ids=["C2"],
                topics=["test"],
                score_adjustment=0.1
            ),
        ]

        analysis = AnalysisResult(
            slide_id="slide_0",
            tensions=[tension],
            meta=AnalysisMeta(
                slide_id="slide_0",
                num_claims=2,
                num_evidence_items=2,
                num_tensions=1
            )
        )

        # With adaptive difficulty enabled (default)
        agent = QuestionSynthesisAgent(llm_client, use_adaptive_difficulty=True)
        result = agent.synthesize(
            slide_id="slide_0",
            analysis=analysis,
            claims=claims,
            evidence=evidence
        )

        # Should recalculate to "hard" due to HIGH severity + HIGH importance + contradicting evidence
        self.assertEqual(len(result.questions), 1)
        self.assertEqual(result.questions[0].difficulty, "hard")
        self.assertIn("Difficulty:", result.questions[0].notes)

    def test_adaptive_difficulty_disabled(self):
        """Test that adaptive difficulty can be disabled."""
        llm_client = MagicMock()
        llm_client.complete_with_system.side_effect = [
            {
                "questions": [{
                    "id": "Q1",
                    "tension_id": "T1",
                    "question": "Test?",
                    "difficulty": "easy",  # LLM says easy
                    "related_claim_ids": [],
                    "evidence_ids": [],
                    "ideal_answer": {"text": "A", "key_points": ["p"], "evidence_ids": []}
                }],
                "meta": {"slide_id": "slide_0", "num_tensions": 1, "num_questions": 1, "grounded": True}
            },
            {"grounded": True, "issues": []}
        ]

        tension = Tension(
            id="T1",
            category=TensionCategory.CONTRADICTION,
            severity=TensionSeverity.HIGH,  # Would be recalculated to hard
            headline="Test",
            description="Test"
        )

        analysis = AnalysisResult(
            slide_id="slide_0",
            tensions=[tension],
            meta=AnalysisMeta(
                slide_id="slide_0",
                num_claims=0,
                num_evidence_items=0,
                num_tensions=1
            )
        )

        # Explicitly disable adaptive difficulty
        agent = QuestionSynthesisAgent(llm_client, use_adaptive_difficulty=False)
        result = agent.synthesize(
            slide_id="slide_0",
            analysis=analysis,
            claims=[],
            evidence=[]
        )

        # Should keep LLM-assigned "easy"
        self.assertEqual(result.questions[0].difficulty, "easy")


class TestPersonaContext(unittest.TestCase):
    """Tests for persona context building."""

    def test_build_persona_context_full(self):
        """Test building context for a fully configured persona."""
        persona = ChallengerPersona(
            id="cfo_1",
            name="Sarah Chen",
            role="Chief Financial Officer",
            style="Data-driven, focused on ROI metrics",
            focus_areas=["cost analysis", "budget impact", "ROI"],
            domain_tags=["finance", "cost", "budget"]
        )

        context = _build_persona_context(persona)

        self.assertIn("Sarah Chen", context)
        self.assertIn("Chief Financial Officer", context)
        self.assertIn("Data-driven", context)
        self.assertIn("cost analysis", context)
        self.assertIn("finance", context)

    def test_build_persona_context_empty_focus_areas(self):
        """Test context with empty focus areas uses fallback."""
        persona = ChallengerPersona(
            id="generic_1",
            name="Test User",
            role="Stakeholder",
            style="Direct",
            focus_areas=[],
            domain_tags=[]
        )

        context = _build_persona_context(persona)

        self.assertIn("General business concerns", context)
        self.assertIn("General", context)

    def test_build_persona_context_formats_lists(self):
        """Test that focus areas and domain tags are formatted as comma-separated lists."""
        persona = ChallengerPersona(
            id="cto_1",
            name="Tech Lead",
            role="CTO",
            style="Technical",
            focus_areas=["scalability", "security", "performance"],
            domain_tags=["technical", "architecture"]
        )

        context = _build_persona_context(persona)

        self.assertIn("scalability, security, performance", context)
        self.assertIn("technical, architecture", context)


class TestPersonaTensionFiltering(unittest.TestCase):
    """Tests for persona-based tension filtering."""

    def setUp(self):
        """Set up test fixtures."""
        self.finance_tension = Tension(
            id="T1",
            category=TensionCategory.CONTRADICTION,
            severity=TensionSeverity.MEDIUM,
            headline="Cost discrepancy",
            description="Cost claims conflict",
            risk_tags=["finance", "cost"]
        )

        self.technical_tension = Tension(
            id="T2",
            category=TensionCategory.RISK_EXPOSURE,
            severity=TensionSeverity.MEDIUM,
            headline="Scalability risk",
            description="Architecture may not scale",
            risk_tags=["technical", "scalability"]
        )

        self.high_severity_tension = Tension(
            id="T3",
            category=TensionCategory.MISSING_EVIDENCE,
            severity=TensionSeverity.HIGH,
            headline="Critical missing data",
            description="No evidence for core claim",
            risk_tags=["compliance"]
        )

        self.low_severity_tension = Tension(
            id="T4",
            category=TensionCategory.AMBIGUITY,
            severity=TensionSeverity.LOW,
            headline="Minor ambiguity",
            description="Slightly unclear wording",
            risk_tags=["clarity"]
        )

        self.all_tensions = [
            self.finance_tension,
            self.technical_tension,
            self.high_severity_tension,
            self.low_severity_tension
        ]

    def test_filter_by_domain_tags(self):
        """Test filtering tensions by persona domain tags."""
        finance_persona = ChallengerPersona(
            id="cfo_1",
            name="CFO",
            role="Chief Financial Officer",
            style="Data-driven",
            focus_areas=["cost analysis"],
            domain_tags=["finance", "cost"]
        )

        result = _filter_tensions_for_persona(self.all_tensions, finance_persona)

        # Should include finance tension and high severity tension
        tension_ids = [t.id for t in result]
        self.assertIn("T1", tension_ids)  # finance matches
        self.assertIn("T3", tension_ids)  # HIGH severity always included
        self.assertNotIn("T2", tension_ids)  # technical doesn't match
        self.assertNotIn("T4", tension_ids)  # LOW severity, no match

    def test_filter_includes_high_severity_regardless_of_tags(self):
        """Test that HIGH severity tensions are always included."""
        unrelated_persona = ChallengerPersona(
            id="hr_1",
            name="HR Director",
            role="Human Resources",
            style="People-focused",
            focus_areas=["team impact"],
            domain_tags=["hr", "team"]
        )

        result = _filter_tensions_for_persona(self.all_tensions, unrelated_persona)

        # High severity should always be included
        tension_ids = [t.id for t in result]
        self.assertIn("T3", tension_ids)

    def test_filter_fallback_when_no_tag_matches_and_no_high_severity(self):
        """Test fallback to top 2 by severity when no tags match and no HIGH severity."""
        # Create tensions without HIGH severity
        tensions_no_high = [
            self.finance_tension,   # MEDIUM
            self.technical_tension, # MEDIUM
            self.low_severity_tension  # LOW
        ]

        unrelated_persona = ChallengerPersona(
            id="other_1",
            name="Other",
            role="Other Role",
            style="Other style",
            focus_areas=["other"],
            domain_tags=["unrelated_tag"]
        )

        result = _filter_tensions_for_persona(tensions_no_high, unrelated_persona)

        # Should return top 2 by severity (T1 MEDIUM, T2 MEDIUM)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].severity, TensionSeverity.MEDIUM)

    def test_filter_includes_only_high_severity_when_no_tag_matches(self):
        """Test that HIGH severity tensions are included even when no tags match."""
        unrelated_persona = ChallengerPersona(
            id="other_1",
            name="Other",
            role="Other Role",
            style="Other style",
            focus_areas=["other"],
            domain_tags=["unrelated_tag"]
        )

        result = _filter_tensions_for_persona(self.all_tensions, unrelated_persona)

        # Should only return HIGH severity (T3) since tags don't match others
        tension_ids = [t.id for t in result]
        self.assertIn("T3", tension_ids)
        self.assertEqual(result[0].severity, TensionSeverity.HIGH)

    def test_filter_no_domain_tags_returns_all(self):
        """Test that empty domain_tags returns all tensions."""
        generic_persona = ChallengerPersona(
            id="generic_1",
            name="Generic",
            role="Stakeholder",
            style="Direct",
            focus_areas=[],
            domain_tags=[]
        )

        result = _filter_tensions_for_persona(self.all_tensions, generic_persona)

        # No filtering should occur
        self.assertEqual(len(result), len(self.all_tensions))

    def test_filter_empty_tensions_list(self):
        """Test filtering empty tensions list returns empty."""
        persona = ChallengerPersona(
            id="cfo_1",
            name="CFO",
            role="CFO",
            style="Direct",
            focus_areas=["cost"],
            domain_tags=["finance"]
        )

        result = _filter_tensions_for_persona([], persona)

        self.assertEqual(result, [])

    def test_filter_multiple_matching_tags(self):
        """Test tension with multiple matching tags is included once."""
        broad_persona = ChallengerPersona(
            id="exec_1",
            name="Executive",
            role="CEO",
            style="Strategic",
            focus_areas=["overall strategy"],
            domain_tags=["finance", "cost", "technical", "scalability"]
        )

        result = _filter_tensions_for_persona(self.all_tensions, broad_persona)

        # Finance and technical tensions should match, plus high severity
        tension_ids = [t.id for t in result]
        self.assertIn("T1", tension_ids)
        self.assertIn("T2", tension_ids)
        self.assertIn("T3", tension_ids)


class TestSynthesizeWithChallengerPersona(unittest.TestCase):
    """Tests for synthesize() with ChallengerPersona objects."""

    def setUp(self):
        """Set up test fixtures."""
        self.sample_claims = [
            Claim(
                id="C1",
                text="We achieve 40% cost savings",
                claim_type=ClaimType.METRIC,
                importance=ClaimImportance.HIGH,
                confidence=0.9
            )
        ]

        self.sample_evidence = [
            EvidenceItem(
                id="E1",
                text="Industry benchmarks show 15-25% savings",
                source=EvidenceSource.RESEARCH,
                collection="test",
                relevance=EvidenceRelevance.HIGH,
                stance=EvidenceStance.CONTRADICTS,
                related_claim_ids=["C1"],
                topics=["cost"],
                score_adjustment=0.1
            )
        ]

        self.finance_tension = Tension(
            id="T1",
            category=TensionCategory.CONTRADICTION,
            severity=TensionSeverity.HIGH,
            headline="Cost savings discrepancy",
            description="Claimed savings don't match industry data",
            related_claim_ids=["C1"],
            contradicting_evidence_ids=["E1"],
            risk_tags=["finance", "cost"]
        )

        self.technical_tension = Tension(
            id="T2",
            category=TensionCategory.RISK_EXPOSURE,
            severity=TensionSeverity.MEDIUM,
            headline="Technical risk",
            description="Technical risk not addressed",
            risk_tags=["technical", "security"]
        )

        self.sample_analysis = AnalysisResult(
            slide_id="slide_0",
            tensions=[self.finance_tension, self.technical_tension],
            meta=AnalysisMeta(
                slide_id="slide_0",
                num_claims=1,
                num_evidence_items=1,
                num_tensions=2
            )
        )

        self.cfo_persona = ChallengerPersona(
            id="cfo_1",
            name="Sarah Chen",
            role="Chief Financial Officer",
            style="Data-driven, focused on ROI metrics",
            focus_areas=["cost analysis", "budget impact", "ROI"],
            domain_tags=["finance", "cost", "budget"]
        )

    def test_synthesize_with_challenger_persona_filters_tensions(self):
        """Test that ChallengerPersona triggers tension filtering."""
        llm_client = MagicMock()
        llm_client.complete_with_system.side_effect = [
            {
                "questions": [{
                    "id": "Q1",
                    "tension_id": "T1",
                    "question": "CFO question about costs?",
                    "difficulty": "hard",
                    "related_claim_ids": ["C1"],
                    "evidence_ids": ["E1"],
                    "ideal_answer": {
                        "text": "Answer",
                        "key_points": ["point"],
                        "evidence_ids": ["E1"]
                    }
                }],
                "meta": {"slide_id": "slide_0", "num_tensions": 1, "num_questions": 1, "grounded": True}
            },
            {"grounded": True, "issues": []}
        ]

        agent = QuestionSynthesisAgent(llm_client)
        result = agent.synthesize(
            slide_id="slide_0",
            analysis=self.sample_analysis,
            claims=self.sample_claims,
            evidence=self.sample_evidence,
            persona=self.cfo_persona
        )

        # Verify the prompt only contains finance-related tension (T1)
        # T2 (technical) should be filtered out for CFO
        call_args = llm_client.complete_with_system.call_args_list[0]
        user_prompt = call_args[1]["user_prompt"]
        self.assertIn("T1", user_prompt)
        self.assertIn("Cost savings discrepancy", user_prompt)

    def test_synthesize_with_challenger_persona_includes_persona_context(self):
        """Test that ChallengerPersona context is included in prompt."""
        llm_client = MagicMock()
        llm_client.complete_with_system.side_effect = [
            {
                "questions": [{
                    "id": "Q1",
                    "tension_id": "T1",
                    "question": "Question?",
                    "difficulty": "hard",
                    "related_claim_ids": ["C1"],
                    "evidence_ids": ["E1"],
                    "ideal_answer": {"text": "Answer", "key_points": ["p"], "evidence_ids": ["E1"]}
                }],
                "meta": {"slide_id": "slide_0", "num_tensions": 1, "num_questions": 1, "grounded": True}
            },
            {"grounded": True, "issues": []}
        ]

        agent = QuestionSynthesisAgent(llm_client)
        agent.synthesize(
            slide_id="slide_0",
            analysis=self.sample_analysis,
            claims=self.sample_claims,
            evidence=self.sample_evidence,
            persona=self.cfo_persona
        )

        # Check persona context was included
        call_args = llm_client.complete_with_system.call_args_list[0]
        user_prompt = call_args[1]["user_prompt"]
        self.assertIn("Sarah Chen", user_prompt)
        self.assertIn("Chief Financial Officer", user_prompt)
        self.assertIn("Data-driven", user_prompt)
        self.assertIn("cost analysis", user_prompt)

    def test_synthesize_string_persona_vs_challenger_persona(self):
        """Test different behavior between string and ChallengerPersona."""
        llm_client = MagicMock()
        llm_client.complete_with_system.side_effect = [
            {
                "questions": [{
                    "id": "Q1",
                    "tension_id": "T1",
                    "question": "Question?",
                    "difficulty": "hard",
                    "related_claim_ids": ["C1"],
                    "evidence_ids": ["E1"],
                    "ideal_answer": {"text": "Answer", "key_points": ["p"], "evidence_ids": ["E1"]}
                }],
                "meta": {"slide_id": "slide_0", "num_tensions": 1, "num_questions": 1, "grounded": True}
            },
            {"grounded": True, "issues": []}
        ]

        agent = QuestionSynthesisAgent(llm_client)

        # String persona - simple context
        agent.synthesize(
            slide_id="slide_0",
            analysis=self.sample_analysis,
            claims=self.sample_claims,
            evidence=self.sample_evidence,
            persona="CFO"
        )

        call_args = llm_client.complete_with_system.call_args_list[0]
        user_prompt = call_args[1]["user_prompt"]

        # String persona should include both tensions (no filtering)
        self.assertIn("T1", user_prompt)
        self.assertIn("T2", user_prompt)
        self.assertIn("CFO stakeholder", user_prompt)


class TestBuildSynthesisPromptWithPersona(unittest.TestCase):
    """Tests for _build_synthesis_user_prompt with persona types."""

    def test_build_prompt_with_string_persona(self):
        """Test prompt building with string persona."""
        tensions = [
            Tension(
                id="T1",
                category=TensionCategory.CONTRADICTION,
                severity=TensionSeverity.HIGH,
                headline="Test",
                description="Test desc"
            )
        ]

        prompt = _build_synthesis_user_prompt(
            slide_id="slide_0",
            tensions=tensions,
            claims=[],
            evidence=[],
            persona="CFO"
        )

        self.assertIn("CFO stakeholder", prompt)
        self.assertNotIn("Communication Style:", prompt)  # Full context not included

    def test_build_prompt_with_challenger_persona(self):
        """Test prompt building with ChallengerPersona object."""
        tensions = [
            Tension(
                id="T1",
                category=TensionCategory.CONTRADICTION,
                severity=TensionSeverity.HIGH,
                headline="Test",
                description="Test desc"
            )
        ]

        persona = ChallengerPersona(
            id="cfo_1",
            name="Sarah Chen",
            role="CFO",
            style="Data-driven",
            focus_areas=["cost analysis"],
            domain_tags=["finance"]
        )

        prompt = _build_synthesis_user_prompt(
            slide_id="slide_0",
            tensions=tensions,
            claims=[],
            evidence=[],
            persona=persona
        )

        self.assertIn("Sarah Chen", prompt)
        self.assertIn("Communication Style:", prompt)
        self.assertIn("Data-driven", prompt)

    def test_build_prompt_without_persona(self):
        """Test prompt building without any persona."""
        tensions = [
            Tension(
                id="T1",
                category=TensionCategory.CONTRADICTION,
                severity=TensionSeverity.HIGH,
                headline="Test",
                description="Test desc"
            )
        ]

        prompt = _build_synthesis_user_prompt(
            slide_id="slide_0",
            tensions=tensions,
            claims=[],
            evidence=[],
            persona=None
        )

        self.assertNotIn("Persona Context", prompt)
        self.assertIn("Generate challenge questions", prompt)


class TestSystemPromptContent(unittest.TestCase):
    """Tests for system prompt content."""

    def test_system_prompt_contains_question_patterns(self):
        """Test that system prompt includes all question patterns."""
        self.assertIn("CONTRADICTION", QUESTION_SYNTHESIS_SYSTEM_PROMPT)
        self.assertIn("MISSING_EVIDENCE", QUESTION_SYNTHESIS_SYSTEM_PROMPT)
        self.assertIn("RISK_EXPOSURE", QUESTION_SYNTHESIS_SYSTEM_PROMPT)
        self.assertIn("COMPETITIVE_GAP", QUESTION_SYNTHESIS_SYSTEM_PROMPT)
        self.assertIn("AMBIGUITY", QUESTION_SYNTHESIS_SYSTEM_PROMPT)

    def test_system_prompt_contains_output_format(self):
        """Test that system prompt specifies JSON output format."""
        self.assertIn("JSON", QUESTION_SYNTHESIS_SYSTEM_PROMPT)
        self.assertIn("questions", QUESTION_SYNTHESIS_SYSTEM_PROMPT)
        self.assertIn("ideal_answer", QUESTION_SYNTHESIS_SYSTEM_PROMPT)

    def test_grounding_prompt_contains_criteria(self):
        """Test that grounding prompt includes verification criteria."""
        self.assertIn("grounded", GROUNDING_VERIFICATION_PROMPT)
        self.assertIn("evidence", GROUNDING_VERIFICATION_PROMPT.lower())
        self.assertIn("issues", GROUNDING_VERIFICATION_PROMPT)


if __name__ == "__main__":
    unittest.main()
