"""
Adaptive Difficulty Calculator for challenge questions.

Calculates question difficulty based on multiple weighted factors:
1. Tension severity (base factor)
2. Evidence strength (contradicting ratio)
3. Claim importance
4. Evidence ambiguity
5. Question complexity (claim count)
"""
from dataclasses import dataclass
from typing import List, Dict

from backend.models.core import (
    Claim,
    ClaimImportance,
    EvidenceItem,
    EvidenceStance,
    Tension,
    TensionSeverity,
)
from backend.logger import get_logger

logger = get_logger(__name__)


@dataclass
class DifficultyFactors:
    """
    Individual factors contributing to difficulty calculation.

    All factors are normalized to 0.0-1.0 range.
    """
    tension_severity: float      # 0.0-1.0 based on severity level
    evidence_strength: float     # 0.0-1.0 ratio of contradicting evidence
    claim_importance: float      # 0.0-1.0 based on claim importance
    evidence_ambiguity: float    # 0.0-1.0 ratio of neutral/unclear evidence
    question_complexity: float   # 0.0-1.0 based on number of related claims

    def to_dict(self) -> Dict[str, float]:
        """Convert factors to dictionary for logging/debugging."""
        return {
            "tension_severity": self.tension_severity,
            "evidence_strength": self.evidence_strength,
            "claim_importance": self.claim_importance,
            "evidence_ambiguity": self.evidence_ambiguity,
            "question_complexity": self.question_complexity,
        }


class DifficultyCalculator:
    """
    Calculates adaptive difficulty for challenge questions.

    Uses weighted factors to determine question difficulty rather than
    a simple severity-to-difficulty mapping.
    """

    # Default weights for each factor
    DEFAULT_WEIGHTS: Dict[str, float] = {
        "tension_severity": 0.30,
        "evidence_strength": 0.25,
        "claim_importance": 0.20,
        "evidence_ambiguity": 0.15,
        "question_complexity": 0.10,
    }

    # Thresholds for difficulty levels
    HARD_THRESHOLD = 0.65
    MEDIUM_THRESHOLD = 0.35

    def __init__(self, weights: Dict[str, float] = None):
        """
        Initialize the DifficultyCalculator.

        Args:
            weights: Optional custom weights for factors.
                     Must sum to 1.0 if provided.
        """
        self.weights = weights or self.DEFAULT_WEIGHTS.copy()

        # Validate weights sum to ~1.0
        weight_sum = sum(self.weights.values())
        if abs(weight_sum - 1.0) > 0.01:
            logger.warning(f"Difficulty weights sum to {weight_sum}, normalizing")
            self.weights = {k: v / weight_sum for k, v in self.weights.items()}

    def calculate(
        self,
        tension: Tension,
        claims: List[Claim],
        evidence: List[EvidenceItem]
    ) -> str:
        """
        Calculate the difficulty level for a question.

        Args:
            tension: The tension being targeted by the question.
            claims: Claims related to the question.
            evidence: Evidence items related to the question.

        Returns:
            Difficulty level: "easy", "medium", or "hard".
        """
        factors = self.compute_factors(tension, claims, evidence)
        score = self.weighted_score(factors)
        difficulty = self.score_to_difficulty(score)

        logger.debug(
            f"Difficulty calculation: factors={factors.to_dict()}, "
            f"score={score:.3f}, difficulty={difficulty}"
        )

        return difficulty

    def calculate_with_explanation(
        self,
        tension: Tension,
        claims: List[Claim],
        evidence: List[EvidenceItem]
    ) -> tuple:
        """
        Calculate difficulty with detailed explanation.

        Args:
            tension: The tension being targeted.
            claims: Related claims.
            evidence: Related evidence.

        Returns:
            Tuple of (difficulty, score, factors, explanation)
        """
        factors = self.compute_factors(tension, claims, evidence)
        score = self.weighted_score(factors)
        difficulty = self.score_to_difficulty(score)
        explanation = self._build_explanation(factors, score, difficulty)

        return difficulty, score, factors, explanation

    def compute_factors(
        self,
        tension: Tension,
        claims: List[Claim],
        evidence: List[EvidenceItem]
    ) -> DifficultyFactors:
        """
        Compute all difficulty factors.

        Args:
            tension: The tension being analyzed.
            claims: Claims related to the tension.
            evidence: Evidence items related to the tension.

        Returns:
            DifficultyFactors with normalized values.
        """
        return DifficultyFactors(
            tension_severity=self._compute_severity_factor(tension),
            evidence_strength=self._compute_evidence_strength(tension, evidence),
            claim_importance=self._compute_claim_importance(tension, claims),
            evidence_ambiguity=self._compute_evidence_ambiguity(evidence),
            question_complexity=self._compute_question_complexity(tension, claims),
        )

    def weighted_score(self, factors: DifficultyFactors) -> float:
        """
        Calculate weighted score from factors.

        Args:
            factors: The computed difficulty factors.

        Returns:
            Weighted score between 0.0 and 1.0.
        """
        score = (
            self.weights["tension_severity"] * factors.tension_severity +
            self.weights["evidence_strength"] * factors.evidence_strength +
            self.weights["claim_importance"] * factors.claim_importance +
            self.weights["evidence_ambiguity"] * factors.evidence_ambiguity +
            self.weights["question_complexity"] * factors.question_complexity
        )
        return min(max(score, 0.0), 1.0)

    def score_to_difficulty(self, score: float) -> str:
        """
        Convert numerical score to difficulty level.

        Args:
            score: Weighted score between 0.0 and 1.0.

        Returns:
            "easy", "medium", or "hard".
        """
        if score >= self.HARD_THRESHOLD:
            return "hard"
        elif score >= self.MEDIUM_THRESHOLD:
            return "medium"
        return "easy"

    def _compute_severity_factor(self, tension: Tension) -> float:
        """
        Compute factor based on tension severity.

        HIGH -> 1.0, MEDIUM -> 0.5, LOW -> 0.2
        """
        severity_map = {
            TensionSeverity.HIGH: 1.0,
            TensionSeverity.MEDIUM: 0.5,
            TensionSeverity.LOW: 0.2,
        }
        return severity_map.get(tension.severity, 0.5)

    def _compute_evidence_strength(
        self,
        tension: Tension,
        evidence: List[EvidenceItem]
    ) -> float:
        """
        Compute factor based on evidence contradicting claims.

        Higher ratio of contradicting evidence = harder question.
        """
        if not evidence:
            return 0.3  # No evidence means moderate difficulty

        # Get evidence related to this tension
        related_evidence = [
            e for e in evidence
            if e.id in tension.contradicting_evidence_ids or
               e.id in tension.supporting_evidence_ids
        ]

        if not related_evidence:
            # Check if any evidence relates to the tension's claims
            related_evidence = [
                e for e in evidence
                if any(cid in e.related_claim_ids for cid in tension.related_claim_ids)
            ]

        if not related_evidence:
            return 0.3

        # Count contradicting vs total
        contradicting_count = sum(
            1 for e in related_evidence
            if e.stance == EvidenceStance.CONTRADICTS
        )

        ratio = contradicting_count / len(related_evidence)
        return ratio

    def _compute_claim_importance(
        self,
        tension: Tension,
        claims: List[Claim]
    ) -> float:
        """
        Compute factor based on importance of related claims.

        Higher importance claims = harder questions.
        """
        if not claims or not tension.related_claim_ids:
            return 0.5

        related_claims = [
            c for c in claims
            if c.id in tension.related_claim_ids
        ]

        if not related_claims:
            return 0.5

        # Calculate average importance
        importance_values = {
            ClaimImportance.HIGH: 1.0,
            ClaimImportance.MEDIUM: 0.5,
            ClaimImportance.LOW: 0.2,
        }

        total = sum(
            importance_values.get(c.importance, 0.5)
            for c in related_claims
        )
        return total / len(related_claims)

    def _compute_evidence_ambiguity(
        self,
        evidence: List[EvidenceItem]
    ) -> float:
        """
        Compute factor based on ambiguous/unclear evidence.

        More ambiguous evidence = harder to answer definitively.
        """
        if not evidence:
            return 0.5  # No evidence is moderately ambiguous

        # Count neutral/unclear evidence
        ambiguous_count = sum(
            1 for e in evidence
            if e.stance == EvidenceStance.NEUTRAL_OR_UNCLEAR
        )

        return ambiguous_count / len(evidence)

    def _compute_question_complexity(
        self,
        tension: Tension,
        claims: List[Claim]
    ) -> float:
        """
        Compute factor based on number of related claims.

        More claims involved = more complex question.
        """
        num_related = len(tension.related_claim_ids)

        if num_related == 0:
            return 0.2
        elif num_related == 1:
            return 0.3
        elif num_related == 2:
            return 0.6
        else:
            return min(1.0, 0.3 + (num_related * 0.2))

    def _build_explanation(
        self,
        factors: DifficultyFactors,
        score: float,
        difficulty: str
    ) -> str:
        """
        Build human-readable explanation of difficulty calculation.

        Args:
            factors: Computed factors.
            score: Weighted score.
            difficulty: Resulting difficulty level.

        Returns:
            Explanation string.
        """
        parts = [f"Difficulty: {difficulty} (score: {score:.2f})"]

        # Add factor contributions
        contributions = []
        if factors.tension_severity >= 0.7:
            contributions.append("high tension severity")
        if factors.evidence_strength >= 0.5:
            contributions.append("strong contradicting evidence")
        if factors.claim_importance >= 0.7:
            contributions.append("high importance claims")
        if factors.evidence_ambiguity >= 0.5:
            contributions.append("ambiguous evidence")
        if factors.question_complexity >= 0.6:
            contributions.append("multiple related claims")

        if contributions:
            parts.append(f"Key factors: {', '.join(contributions)}")

        return ". ".join(parts)


def calculate_difficulty(
    tension: Tension,
    claims: List[Claim],
    evidence: List[EvidenceItem]
) -> str:
    """
    Convenience function for calculating difficulty.

    Args:
        tension: The tension being targeted.
        claims: Related claims.
        evidence: Related evidence.

    Returns:
        Difficulty level: "easy", "medium", or "hard".
    """
    calculator = DifficultyCalculator()
    return calculator.calculate(tension, claims, evidence)
