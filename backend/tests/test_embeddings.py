from typing import Any
from unittest.mock import MagicMock, patch
from backend.models.embeddings import EmbeddingModel

@patch("backend.models.embeddings.SentenceTransformer")
def test_generate_embeddings(mock_st_cls: Any) -> None:
    """Test generating embeddings."""
    mock_embeddings = MagicMock()
    mock_embeddings.tolist.return_value = [[0.1, 0.2, 0.3]]

    mock_model = MagicMock()
    mock_model.encode.return_value = mock_embeddings
    mock_st_cls.return_value = mock_model

    model = EmbeddingModel()
    embeddings = model.encode(["test text"])

    assert len(embeddings) == 1
    assert embeddings[0] == [0.1, 0.2, 0.3]
    mock_model.encode.assert_called_once()
