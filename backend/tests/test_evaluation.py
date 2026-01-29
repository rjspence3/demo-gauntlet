"""
Tests for evaluation.
"""
from backend.evaluation.engine import EvaluationEngine

def test_evaluation_engine() -> None:
    """Test evaluation engine scoring logic."""
    engine = EvaluationEngine()
    
    # Test high similarity
    result = engine.evaluate(
        "We use AES-256 encryption for all data at rest.",
        "Our platform secures data at rest using AES-256 encryption."
    )
    assert result.score >= 80
    assert "Good" in result.feedback
    
    # Test low similarity
    result = engine.evaluate(
        "I like pizza.",
        "Our platform secures data at rest using AES-256 encryption."
    )
    assert result.score < 50
    assert "Weak" in result.feedback
    
    # Test empty
    result = engine.evaluate("", "Answer")
    assert result.score == 0
