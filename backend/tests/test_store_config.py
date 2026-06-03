import unittest
from unittest.mock import patch
from backend.models.store import DeckRetriever

class TestStoreConfig(unittest.TestCase):
    @patch("backend.models.store.config")
    @patch("chromadb.PersistentClient")
    @patch("chromadb.HttpClient")
    @patch("backend.models.embeddings.EmbeddingModel")
    def test_http_client_init(self, mock_embedding, mock_http, mock_persistent, mock_config):
        mock_config.CHROMA_SERVER_HOST = "localhost"
        mock_config.CHROMA_SERVER_PORT = 8000

        DeckRetriever()

        mock_http.assert_called_with(host="localhost", port=8000)

    @patch("backend.models.store.config")
    @patch("chromadb.PersistentClient")
    @patch("chromadb.HttpClient")
    @patch("backend.models.embeddings.EmbeddingModel")
    def test_persistent_client_init(self, mock_embedding, mock_http, mock_persistent, mock_config):
        mock_config.CHROMA_SERVER_HOST = None
        mock_config.CHROMA_SERVER_PORT = None
        mock_config.CHROMA_PERSISTENCE_PATH = "./data"

        DeckRetriever()

        mock_persistent.assert_called_with(path="./data")
