from typing import Any
try:
    from backend.evaluation.engine import EvaluationEngine
except ImportError:
    # Fallback for when running as script
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
    from backend.evaluation.engine import EvaluationEngine

# Global instance to avoid reloading models on every call
_engine = None

def get_engine():
    global _engine
    if _engine is None:
        _engine = EvaluationEngine()
    return _engine

def gauntlet_metric(gold: Any, pred: Any, trace: Any = None) -> float:
    """
    DSPy metric wrapper for the proprietary Gauntlet EvaluationEngine.
    
    Args:
        gold: The 'ideal answer' from the dataset.
        pred: The agent's generated answer.
        trace: (Optional) Internal trace for debugging.
        
    Returns:
        float: Normalized score between 0.0 and 1.0
    """
    engine = get_engine()
    
    # Extract text from gold/pred objects
    # pred is usually a dspy.Prediction with a 'response' field (from Signature)
    user_response = getattr(pred, 'response', "")
    if not user_response and isinstance(pred, str):
        user_response = pred
        
    # gold can be a dspy.Example with an 'answer' field
    ideal_response = getattr(gold, 'answer', "")
    
    # Handle case where ideal_answer is an explicit object with .text (from our core models)
    if hasattr(ideal_response, 'text'):
        ideal_response = ideal_response.text
    
    if not user_response or not ideal_response:
        return 0.0

    # Calculate score using the existing heuristic engine
    # Returns EvaluationResult where score is 0-100
    try:
        result = engine.evaluate(
            user_answer=user_response,
            ideal_answer=ideal_response
        )
        return float(result.score) / 100.0
    except Exception as e:
        print(f"Error in metric calculation: {e}")
        return 0.0
