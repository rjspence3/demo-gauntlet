"""
Tests for store.
"""
from typing import Any
from unittest.mock import MagicMock, patch
from backend.models.store import VectorStore
from backend.models.core import Chunk

@patch("backend.models.store.chromadb.PersistentClient")
@patch("backend.models.store.EmbeddingModel")
def test_add_chunks(mock_emb_cls: Any, mock_client_cls: Any) -> None:
    """Test adding chunks to the store."""
    # Mock Embedding Model
    mock_emb_instance = MagicMock()
    mock_emb_instance.encode.return_value = [[0.1, 0.2, 0.3]]
    mock_emb_cls.return_value = mock_emb_instance

    # Mock Chroma Client
    mock_collection = MagicMock()
    mock_client_instance = MagicMock()
    mock_client_instance.get_or_create_collection.return_value = mock_collection
    mock_client_cls.return_value = mock_client_instance

    store = VectorStore()
    
    chunk = Chunk(
        id="1",
        slide_index=0,
        text="test",
        metadata={"title": "Test"}
    )
    
    store.add_chunks([chunk])
    
    mock_collection.add.assert_called_once()
    mock_emb_instance.encode.assert_called()

@patch("backend.models.store.chromadb.PersistentClient")
@patch("backend.models.store.EmbeddingModel")
def test_query_similar(mock_emb_cls: Any, mock_client_cls: Any) -> None:
    """Test querying similar chunks."""
    # Mock Embedding Model
    mock_emb_instance = MagicMock()
    mock_emb_instance.encode.return_value = [[0.1, 0.2, 0.3]]
    mock_emb_cls.return_value = mock_emb_instance

    # Mock Chroma Client
    mock_collection = MagicMock()
    mock_collection.query.return_value = {
        "ids": [["1"]],
        "documents": [["test"]],
        "metadatas": [[{"title": "t", "slide_index": 0}]]
    }
    mock_client_instance = MagicMock()
    mock_client_instance.get_or_create_collection.return_value = mock_collection
    mock_client_cls.return_value = mock_client_instance

    store = VectorStore()
    results = store.get_nearest_chunks("query", k=1)

    assert len(results) == 1
    assert results[0].id == "1"
    assert results[0].text == "test"
