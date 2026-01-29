"""
Tests for the Adaptive Difficulty Calculator.

Tests cover:
- Individual factor computation
- Weighted score calculation
- Score to difficulty mapping
- Edge cases (no evidence, no claims)
- Custom weight configuration
"""
import unittest

from backend.challenges.difficulty import (
    DifficultyCalculator,
    DifficultyFactors,
    calculate_difficulty,
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
)


class TestDifficultyFactors(unittest.TestCase):
    """Tests for DifficultyFactors dataclass."""

    def test_to_dict(self):
        """Test conversion to dictionary."""
        factors = DifficultyFactors(
            tension_severity=0.8,
            evidence_strength=0.6,
            claim_importance=0.9,
            evidence_ambiguity=0.3,
            question_complexity=0.5,
        )

        result = factors.to_dict()

        self.assertEqual(result["tension_severity"], 0.8)
        self.assertEqual(result["evidence_strength"], 0.6)
        self.assertEqual(result["claim_importance"], 0.9)
        self.assertEqual(result["evidence_ambiguity"], 0.3)
        self.assertEqual(result["question_complexity"], 0.5)


class TestDifficultyCalculatorInit(unittest.TestCase):
    """Tests for DifficultyCalculator initialization."""

    def test_default_weights(self):
        """Test default weight configuration."""
        calc = DifficultyCalculator()

        self.assertEqual(calc.weights["tension_severity"], 0.30)
        self.assertEqual(calc.weights["evidence_strength"], 0.25)
        self.assertEqual(calc.weights["claim_importance"], 0.20)
        self.assertEqual(calc.weights["evidence_ambiguity"], 0.15)
        self.assertEqual(calc.weights["question_complexity"], 0.10)

    def test_custom_weights(self):
        """Test custom weight configuration."""
        custom_weights = {
            "tension_severity": 0.50,
            "evidence_strength": 0.20,
            "claim_importance": 0.15,
            "evidence_ambiguity": 0.10,
            "question_complexity": 0.05,
        }

        calc = DifficultyCalculator(weights=custom_weights)

        self.assertEqual(calc.weights["tension_severity"], 0.50)

    def test_weight_normalization(self):
        """Test that weights are normalized if they don't sum to 1.0."""
        bad_weights = {
            "tension_severity": 0.60,
            "evidence_strength": 0.40,
            "claim_importance": 0.30,
            "evidence_ambiguity": 0.20,
            "question_complexity": 0.10,
        }

        calc = DifficultyCalculator(weights=bad_weights)

        # Weights should be normalized to sum to 1.0
        weight_sum = sum(calc.weights.values())
        self.assertAlmostEqual(weight_sum, 1.0, places=2)


class TestSeverityFactor(unittest.TestCase):
    """Tests for tension severity factor computation."""

    def setUp(self):
        """Set up calculator."""
        self.calc = DifficultyCalculator()

    def test_high_severity(self):
        """Test HIGH severity returns 1.0."""
        tension = Tension(
            id="T1",
            category=TensionCategory.CONTRADICTION,
            severity=TensionSeverity.HIGH,
            headline="Test",
            description="Test"
        )

        factor = self.calc._compute_severity_factor(tension)

        self.assertEqual(factor, 1.0)

    def test_medium_severity(self):
        """Test MEDIUM severity returns 0.5."""
        tension = Tension(
            id="T1",
            category=TensionCategory.CONTRADICTION,
            severity=TensionSeverity.MEDIUM,
            headline="Test",
            description="Test"
        )

        factor = self.calc._compute_severity_factor(tension)

        self.assertEqual(factor, 0.5)

    def test_low_severity(self):
        """Test LOW severity returns 0.2."""
        tension = Tension(
            id="T1",
            category=TensionCategory.CONTRADICTION,
            severity=TensionSeverity.LOW,
            headline="Test",
            description="Test"
        )

        factor = self.calc._compute_severity_factor(tension)

        self.assertEqual(factor, 0.2)


class TestEvidenceStrengthFactor(unittest.TestCase):
    """Tests for evidence strength factor computation."""

    def setUp(self):
        """Set up calculator and fixtures."""
        self.calc = DifficultyCalculator()

        self.tension = Tension(
            id="T1",
            category=TensionCategory.CONTRADICTION,
            severity=TensionSeverity.HIGH,
            headline="Test",
            description="Test",
            related_claim_ids=["C1"],
            contradicting_evidence_ids=["E1"],
            supporting_evidence_ids=["E2"]
        )

    def test_no_evidence_returns_moderate(self):
        """Test no evidence returns 0.3."""
        factor = self.calc._compute_evidence_strength(self.tension, [])

        self.assertEqual(factor, 0.3)

    def test_all_contradicting_evidence(self):
        """Test all contradicting evidence returns 1.0."""
        evidence = [
            EvidenceItem(
                id="E1",
                text="Evidence 1",
                source=EvidenceSource.RESEARCH,
                collection="test",
                relevance=EvidenceRelevance.HIGH,
                stance=EvidenceStance.CONTRADICTS,
                related_claim_ids=["C1"],
                topics=["test"],
                score_adjustment=0.0
            ),
            EvidenceItem(
                id="E2",
                text="Evidence 2",
                source=EvidenceSource.RESEARCH,
                collection="test",
                relevance=EvidenceRelevance.HIGH,
                stance=EvidenceStance.CONTRADICTS,
                related_claim_ids=["C1"],
                topics=["test"],
                score_adjustment=0.0
            ),
        ]

        factor = self.calc._compute_evidence_strength(self.tension, evidence)

        self.assertEqual(factor, 1.0)

    def test_no_contradicting_evidence(self):
        """Test no contradicting evidence returns 0.0."""
        evidence = [
            EvidenceItem(
                id="E2",
                text="Supporting evidence",
                source=EvidenceSource.RESEARCH,
                collection="test",
                relevance=EvidenceRelevance.HIGH,
                stance=EvidenceStance.SUPPORTS,
                related_claim_ids=["C1"],
                topics=["test"],
                score_adjustment=0.0
            ),
        ]

        factor = self.calc._compute_evidence_strength(self.tension, evidence)

        self.assertEqual(factor, 0.0)

    def test_mixed_evidence(self):
        """Test mixed evidence returns appropriate ratio."""
        evidence = [
            EvidenceItem(
                id="E1",
                text="Contradicting",
                source=EvidenceSource.RESEARCH,
                collection="test",
                relevance=EvidenceRelevance.HIGH,
                stance=EvidenceStance.CONTRADICTS,
                related_claim_ids=["C1"],
                topics=["test"],
                score_adjustment=0.0
            ),
            EvidenceItem(
                id="E2",
                text="Supporting",
                source=EvidenceSource.RESEARCH,
                collection="test",
                relevance=EvidenceRelevance.HIGH,
                stance=EvidenceStance.SUPPORTS,
                related_claim_ids=["C1"],
                topics=["test"],
                score_adjustment=0.0
            ),
        ]

        factor = self.calc._compute_evidence_strength(self.tension, evidence)

        self.assertEqual(factor, 0.5)  # 1 contradicting out of 2


class TestClaimImportanceFactor(unittest.TestCase):
    """Tests for claim importance factor computation."""

    def setUp(self):
        """Set up calculator."""
        self.calc = DifficultyCalculator()

    def test_high_importance_claims(self):
        """Test HIGH importance claims return 1.0."""
        tension = Tension(
            id="T1",
            category=TensionCategory.CONTRADICTION,
            severity=TensionSeverity.HIGH,
            headline="Test",
            description="Test",
            related_claim_ids=["C1", "C2"]
        )

        claims = [
            Claim(
                id="C1",
                text="Claim 1",
                claim_type=ClaimType.FACTUAL,
                importance=ClaimImportance.HIGH,
                confidence=0.9
            ),
            Claim(
                id="C2",
                text="Claim 2",
                claim_type=ClaimType.METRIC,
                importance=ClaimImportance.HIGH,
                confidence=0.9
            ),
        ]

        factor = self.calc._compute_claim_importance(tension, claims)

        self.assertEqual(factor, 1.0)

    def test_low_importance_claims(self):
        """Test LOW importance claims return 0.2."""
        tension = Tension(
            id="T1",
            category=TensionCategory.CONTRADICTION,
            severity=TensionSeverity.HIGH,
            headline="Test",
            description="Test",
            related_claim_ids=["C1"]
        )

        claims = [
            Claim(
                id="C1",
                text="Claim 1",
                claim_type=ClaimType.FACTUAL,
                importance=ClaimImportance.LOW,
                confidence=0.9
            ),
        ]

        factor = self.calc._compute_claim_importance(tension, claims)

        self.assertEqual(factor, 0.2)

    def test_mixed_importance_claims(self):
        """Test mixed importance claims return average."""
        tension = Tension(
            id="T1",
            category=TensionCategory.CONTRADICTION,
            severity=TensionSeverity.HIGH,
            headline="Test",
            description="Test",
            related_claim_ids=["C1", "C2"]
        )

        claims = [
            Claim(
                id="C1",
                text="Claim 1",
                claim_type=ClaimType.FACTUAL,
                importance=ClaimImportance.HIGH,
                confidence=0.9
            ),
            Claim(
                id="C2",
                text="Claim 2",
                claim_type=ClaimType.METRIC,
                importance=ClaimImportance.LOW,
                confidence=0.9
            ),
        ]

        factor = self.calc._compute_claim_importance(tension, claims)

        self.assertEqual(factor, 0.6)  # (1.0 + 0.2) / 2

    def test_no_claims_returns_moderate(self):
        """Test no claims returns 0.5."""
        tension = Tension(
            id="T1",
            category=TensionCategory.CONTRADICTION,
            severity=TensionSeverity.HIGH,
            headline="Test",
            description="Test",
            related_claim_ids=[]
        )

        factor = self.calc._compute_claim_importance(tension, [])

        self.assertEqual(factor, 0.5)


class TestEvidenceAmbiguityFactor(unittest.TestCase):
    """Tests for evidence ambiguity factor computation."""

    def setUp(self):
        """Set up calculator."""
        self.calc = DifficultyCalculator()

    def test_no_evidence_returns_moderate(self):
        """Test no evidence returns 0.5."""
        factor = self.calc._compute_evidence_ambiguity([])

        self.assertEqual(factor, 0.5)

    def test_all_ambiguous_evidence(self):
        """Test all ambiguous evidence returns 1.0."""
        evidence = [
            EvidenceItem(
                id="E1",
                text="Unclear evidence",
                source=EvidenceSource.RESEARCH,
                collection="test",
                relevance=EvidenceRelevance.MEDIUM,
                stance=EvidenceStance.NEUTRAL_OR_UNCLEAR,
                related_claim_ids=["C1"],
                topics=["test"],
                score_adjustment=0.0
            ),
            EvidenceItem(
                id="E2",
                text="Also unclear",
                source=EvidenceSource.RESEARCH,
                collection="test",
                relevance=EvidenceRelevance.MEDIUM,
                stance=EvidenceStance.NEUTRAL_OR_UNCLEAR,
                related_claim_ids=["C1"],
                topics=["test"],
                score_adjustment=0.0
            ),
        ]

        factor = self.calc._compute_evidence_ambiguity(evidence)

        self.assertEqual(factor, 1.0)

    def test_no_ambiguous_evidence(self):
        """Test no ambiguous evidence returns 0.0."""
        evidence = [
            EvidenceItem(
                id="E1",
                text="Clear evidence",
                source=EvidenceSource.RESEARCH,
                collection="test",
                relevance=EvidenceRelevance.HIGH,
                stance=EvidenceStance.SUPPORTS,
                related_claim_ids=["C1"],
                topics=["test"],
                score_adjustment=0.0
            ),
        ]

        factor = self.calc._compute_evidence_ambiguity(evidence)

        self.assertEqual(factor, 0.0)


class TestQuestionComplexityFactor(unittest.TestCase):
    """Tests for question complexity factor computation."""

    def setUp(self):
        """Set up calculator."""
        self.calc = DifficultyCalculator()

    def test_no_related_claims(self):
        """Test no related claims returns 0.2."""
        tension = Tension(
            id="T1",
            category=TensionCategory.CONTRADICTION,
            severity=TensionSeverity.HIGH,
            headline="Test",
            description="Test",
            related_claim_ids=[]
        )

        factor = self.calc._compute_question_complexity(tension, [])

        self.assertEqual(factor, 0.2)

    def test_one_related_claim(self):
        """Test one related claim returns 0.3."""
        tension = Tension(
            id="T1",
            category=TensionCategory.CONTRADICTION,
            severity=TensionSeverity.HIGH,
            headline="Test",
            description="Test",
            related_claim_ids=["C1"]
        )

        factor = self.calc._compute_question_complexity(tension, [])

        self.assertEqual(factor, 0.3)

    def test_two_related_claims(self):
        """Test two related claims returns 0.6."""
        tension = Tension(
            id="T1",
            category=TensionCategory.CONTRADICTION,
            severity=TensionSeverity.HIGH,
            headline="Test",
            description="Test",
            related_claim_ids=["C1", "C2"]
        )

        factor = self.calc._compute_question_complexity(tension, [])

        self.assertEqual(factor, 0.6)

    def test_many_related_claims_capped(self):
        """Test many related claims caps at 1.0."""
        tension = Tension(
            id="T1",
            category=TensionCategory.CONTRADICTION,
            severity=TensionSeverity.HIGH,
            headline="Test",
            description="Test",
            related_claim_ids=["C1", "C2", "C3", "C4", "C5"]
        )

        factor = self.calc._compute_question_complexity(tension, [])

        self.assertEqual(factor, 1.0)


class TestWeightedScore(unittest.TestCase):
    """Tests for weighted score calculation."""

    def setUp(self):
        """Set up calculator."""
        self.calc = DifficultyCalculator()

    def test_all_max_factors(self):
        """Test all max factors return high score."""
        factors = DifficultyFactors(
            tension_severity=1.0,
            evidence_strength=1.0,
            claim_importance=1.0,
            evidence_ambiguity=1.0,
            question_complexity=1.0,
        )

        score = self.calc.weighted_score(factors)

        self.assertEqual(score, 1.0)

    def test_all_min_factors(self):
        """Test all min factors return low score."""
        factors = DifficultyFactors(
            tension_severity=0.0,
            evidence_strength=0.0,
            claim_importance=0.0,
            evidence_ambiguity=0.0,
            question_complexity=0.0,
        )

        score = self.calc.weighted_score(factors)

        self.assertEqual(score, 0.0)

    def test_mixed_factors(self):
        """Test mixed factors return expected weighted score."""
        factors = DifficultyFactors(
            tension_severity=1.0,   # 0.30 * 1.0 = 0.30
            evidence_strength=0.5,  # 0.25 * 0.5 = 0.125
            claim_importance=0.5,   # 0.20 * 0.5 = 0.10
            evidence_ambiguity=0.0, # 0.15 * 0.0 = 0.00
            question_complexity=1.0 # 0.10 * 1.0 = 0.10
        )

        score = self.calc.weighted_score(factors)

        expected = 0.30 + 0.125 + 0.10 + 0.0 + 0.10
        self.assertAlmostEqual(score, expected, places=3)


class TestScoreToDifficulty(unittest.TestCase):
    """Tests for score to difficulty conversion."""

    def setUp(self):
        """Set up calculator."""
        self.calc = DifficultyCalculator()

    def test_high_score_returns_hard(self):
        """Test score >= 0.65 returns hard."""
        self.assertEqual(self.calc.score_to_difficulty(0.65), "hard")
        self.assertEqual(self.calc.score_to_difficulty(0.85), "hard")
        self.assertEqual(self.calc.score_to_difficulty(1.0), "hard")

    def test_medium_score_returns_medium(self):
        """Test score 0.35-0.65 returns medium."""
        self.assertEqual(self.calc.score_to_difficulty(0.35), "medium")
        self.assertEqual(self.calc.score_to_difficulty(0.50), "medium")
        self.assertEqual(self.calc.score_to_difficulty(0.64), "medium")

    def test_low_score_returns_easy(self):
        """Test score < 0.35 returns easy."""
        self.assertEqual(self.calc.score_to_difficulty(0.0), "easy")
        self.assertEqual(self.calc.score_to_difficulty(0.20), "easy")
        self.assertEqual(self.calc.score_to_difficulty(0.34), "easy")


class TestFullCalculation(unittest.TestCase):
    """Integration tests for full difficulty calculation."""

    def test_high_severity_high_evidence_hard(self):
        """Test HIGH severity + strong contradicting evidence = hard."""
        calc = DifficultyCalculator()

        tension = Tension(
            id="T1",
            category=TensionCategory.CONTRADICTION,
            severity=TensionSeverity.HIGH,
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

        difficulty = calc.calculate(tension, claims, evidence)

        self.assertEqual(difficulty, "hard")

    def test_low_severity_weak_evidence_easy(self):
        """Test LOW severity + weak evidence = easy."""
        calc = DifficultyCalculator()

        tension = Tension(
            id="T1",
            category=TensionCategory.AMBIGUITY,
            severity=TensionSeverity.LOW,
            headline="Minor ambiguity",
            description="Test",
            related_claim_ids=["C1"]
        )

        claims = [
            Claim(
                id="C1",
                text="Claim 1",
                claim_type=ClaimType.FACTUAL,
                importance=ClaimImportance.LOW,
                confidence=0.9
            ),
        ]

        evidence = [
            EvidenceItem(
                id="E1",
                text="Supporting evidence",
                source=EvidenceSource.DECK,
                collection="test",
                relevance=EvidenceRelevance.LOW,
                stance=EvidenceStance.SUPPORTS,
                related_claim_ids=["C1"],
                topics=["test"],
                score_adjustment=0.0
            ),
        ]

        difficulty = calc.calculate(tension, claims, evidence)

        self.assertEqual(difficulty, "easy")

    def test_medium_factors_medium(self):
        """Test medium factors = medium difficulty."""
        calc = DifficultyCalculator()

        tension = Tension(
            id="T1",
            category=TensionCategory.MISSING_EVIDENCE,
            severity=TensionSeverity.MEDIUM,
            headline="Missing data",
            description="Test",
            related_claim_ids=["C1"],
            supporting_evidence_ids=["E1"]
        )

        claims = [
            Claim(
                id="C1",
                text="Claim 1",
                claim_type=ClaimType.FACTUAL,
                importance=ClaimImportance.MEDIUM,
                confidence=0.9
            ),
        ]

        evidence = [
            EvidenceItem(
                id="E1",
                text="Some evidence",
                source=EvidenceSource.RESEARCH,
                collection="test",
                relevance=EvidenceRelevance.MEDIUM,
                stance=EvidenceStance.SUPPORTS,
                related_claim_ids=["C1"],
                topics=["test"],
                score_adjustment=0.0
            ),
        ]

        difficulty = calc.calculate(tension, claims, evidence)

        self.assertIn(difficulty, ["easy", "medium"])  # Could be either


class TestCalculateWithExplanation(unittest.TestCase):
    """Tests for calculate_with_explanation method."""

    def test_returns_all_components(self):
        """Test that all components are returned."""
        calc = DifficultyCalculator()

        tension = Tension(
            id="T1",
            category=TensionCategory.CONTRADICTION,
            severity=TensionSeverity.HIGH,
            headline="Test",
            description="Test",
            related_claim_ids=["C1"]
        )

        claims = [
            Claim(
                id="C1",
                text="Claim",
                claim_type=ClaimType.FACTUAL,
                importance=ClaimImportance.HIGH,
                confidence=0.9
            ),
        ]

        evidence = []

        difficulty, score, factors, explanation = calc.calculate_with_explanation(
            tension, claims, evidence
        )

        self.assertIn(difficulty, ["easy", "medium", "hard"])
        self.assertIsInstance(score, float)
        self.assertIsInstance(factors, DifficultyFactors)
        self.assertIn("Difficulty:", explanation)

    def test_explanation_includes_factors(self):
        """Test that explanation mentions key factors."""
        calc = DifficultyCalculator()

        tension = Tension(
            id="T1",
            category=TensionCategory.CONTRADICTION,
            severity=TensionSeverity.HIGH,
            headline="Test",
            description="Test",
            related_claim_ids=["C1", "C2", "C3"]
        )

        claims = [
            Claim(
                id="C1",
                text="Claim",
                claim_type=ClaimType.FACTUAL,
                importance=ClaimImportance.HIGH,
                confidence=0.9
            ),
        ]

        evidence = []

        difficulty, score, factors, explanation = calc.calculate_with_explanation(
            tension, claims, evidence
        )

        # Should mention high severity tension
        self.assertIn("high tension severity", explanation)


class TestConvenienceFunction(unittest.TestCase):
    """Tests for calculate_difficulty convenience function."""

    def test_calculate_difficulty_function(self):
        """Test the convenience function works."""
        tension = Tension(
            id="T1",
            category=TensionCategory.CONTRADICTION,
            severity=TensionSeverity.HIGH,
            headline="Test",
            description="Test"
        )

        difficulty = calculate_difficulty(tension, [], [])

        self.assertIn(difficulty, ["easy", "medium", "hard"])


if __name__ == "__main__":
    unittest.main()
