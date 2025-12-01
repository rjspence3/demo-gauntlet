from dataclasses import dataclass
from typing import List
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

@dataclass
class EvaluationResult:
    score: int
    breakdown: dict
    feedback: str

class EvaluationEngine:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        
        # Weights
        self.weights = {
            "accuracy": 0.45,
            "completeness": 0.35,
            "clarity": 0.15,
            "truth_alignment": 0.05
        }

    def evaluate(self, user_answer: str, ideal_answer: str) -> EvaluationResult:
        if not user_answer.strip():
            return EvaluationResult(score=0, breakdown={}, feedback="No answer provided.")

        # 1. Accuracy (Embedding Similarity)
        embeddings = self.model.encode([user_answer, ideal_answer])
        accuracy = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0] * 100
        accuracy = max(0, min(100, accuracy))

        # 2. Completeness (Length ratio heuristic for MVP, ideally keyword coverage)
        # Assuming ideal answer is "complete", user answer should be comparable in length
        len_ratio = len(user_answer) / len(ideal_answer) if len(ideal_answer) > 0 else 0
        completeness = min(100, len_ratio * 100)
        if len_ratio > 1.5: # Penalize verbosity slightly? Or just cap at 100
            completeness = 100

        # 3. Clarity (Heuristic: Flesch-Kincaid Grade Level approximation)
        clarity = self._calculate_readability(user_answer)

    def _calculate_readability(self, text: str) -> int:
        """
        Approximates readability. Higher score = clearer (easier to read).
        Uses a simplified Flesch Reading Ease formula.
        """
        if not text:
            return 0
            
        sentences = text.count('.') + text.count('!') + text.count('?')
        sentences = max(1, sentences)
        words = len(text.split())
        words = max(1, words)
        syllables = sum([self._count_syllables(w) for w in text.split()])
        
        # Flesch Reading Ease
        # 206.835 - 1.015 * (total words / total sentences) - 84.6 * (total syllables / total words)
        score = 206.835 - 1.015 * (words / sentences) - 84.6 * (syllables / words)
        
        # Normalize to 0-100 (standard Flesch is 0-100, but can go outside)
        return int(max(0, min(100, score)))

    def _count_syllables(self, word: str) -> int:
        word = word.lower()
        count = 0
        vowels = "aeiouy"
        if word[0] in vowels:
            count += 1
        for i in range(1, len(word)):
            if word[i] in vowels and word[i - 1] not in vowels:
                count += 1
        if word.endswith("e"):
            count -= 1
        if count == 0:
            count += 1
        return count

        # 4. Truth Alignment (Heuristic: presence of key terms from ideal answer)
        # Simple keyword overlap
        ideal_words = set(ideal_answer.lower().split())
        user_words = set(user_answer.lower().split())
        overlap = len(ideal_words.intersection(user_words))
        truth_alignment = (overlap / len(ideal_words) * 100) if ideal_words else 100

        # Weighted Score
        final_score = (
            accuracy * self.weights["accuracy"] +
            completeness * self.weights["completeness"] +
            clarity * self.weights["clarity"] +
            truth_alignment * self.weights["truth_alignment"]
        )
        final_score = int(max(0, min(100, final_score)))

        # Feedback
        if final_score >= 80:
            feedback = "Excellent! Your answer aligns perfectly with the research."
        elif final_score >= 50:
            feedback = "Good answer, but could be more specific. Try to reference the research directly."
        else:
            feedback = "Weak answer. You missed the core objection. Review the research dossier."
            
        return EvaluationResult(
            score=final_score,
            breakdown={
                "accuracy": int(accuracy),
                "completeness": int(completeness),
                "clarity": int(clarity),
                "truth_alignment": int(truth_alignment)
            },
            feedback=feedback
        )
