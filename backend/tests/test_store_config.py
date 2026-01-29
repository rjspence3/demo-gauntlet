import unittest
from unittest.mock import MagicMock, patch
from backend.models.store import DeckRetriever

class TestStoreConfig(unittest.TestCase):
    @patch("backend.models.store.config")
    @patch("backend.models.store.chromadb")
    @patch("backend.models.store.EmbeddingModel") # Mock this too as it is instantiated in __init__
    def test_http_client_init(self, mock_embedding, mock_chromadb, mock_config):
        mock_config.CHROMA_SERVER_HOST = "localhost"
        mock_config.CHROMA_SERVER_PORT = 8000
        
        DeckRetriever()
        
        mock_chromadb.HttpClient.assert_called_with(host="localhost", port=8000)
        
    @patch("backend.models.store.config")
    @patch("backend.models.store.chromadb")
    @patch("backend.models.store.EmbeddingModel")
    def test_persistent_client_init(self, mock_embedding, mock_chromadb, mock_config):
        mock_config.CHROMA_SERVER_HOST = None
        mock_config.CHROMA_SERVER_PORT = None
        mock_config.CHROMA_PERSISTENCE_PATH = "./data"
        
        DeckRetriever()
        
        mock_chromadb.PersistentClient.assert_called_with(path="./data")
