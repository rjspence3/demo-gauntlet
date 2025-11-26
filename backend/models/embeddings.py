from typing import List, Union
from sentence_transformers import SentenceTransformer

class EmbeddingModel:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def encode(self, texts: Union[str, List[str]]) -> List[List[float]]:
        """
        Generate embeddings for text(s).

        Args:
            texts: Single string or list of strings.

        Returns:
            List of embeddings (lists of floats).
        """
        if isinstance(texts, str):
            texts = [texts]

        embeddings = self.model.encode(texts)
        # Convert numpy array to list of lists
        return list(embeddings.tolist())
