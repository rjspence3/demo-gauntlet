from dataclasses import dataclass
from typing import List
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

@dataclass
class EvaluationResult:
    score: int
    feedback: str

class EvaluationEngine:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def evaluate(self, user_answer: str, ideal_answer: str) -> EvaluationResult:
        if not user_answer.strip():
            return EvaluationResult(score=0, feedback="No answer provided.")

        # Compute cosine similarity
        embeddings = self.model.encode([user_answer, ideal_answer])
        similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
        
        # Scale to 0-100
        score = int(similarity * 100)
        
        # Determine feedback
        if score >= 85:
            feedback = "Excellent! Your answer aligns perfectly with the research."
        elif score >= 70:
            feedback = "Good answer. You covered the main points but missed some nuance."
        elif score >= 50:
            feedback = "Okay, but could be more specific. Try to reference the research directly."
        else:
            feedback = "Weak answer. You missed the core objection. Review the research dossier."
            
        return EvaluationResult(score=score, feedback=feedback)
