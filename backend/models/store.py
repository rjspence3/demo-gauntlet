"""
Module for storing and retrieving deck chunks using ChromaDB.
"""
from typing import List, cast, Optional, Dict, Any
import chromadb
from backend.models.core import Chunk
from backend.models.embeddings import EmbeddingModel
from backend.config import config

class DeckRetriever:
    """
    Manages storage and retrieval of deck chunks in ChromaDB.
    """
    def __init__(self):
        """
        Initialize the DeckRetriever.
        """
        
        if config.CHROMA_SERVER_HOST and config.CHROMA_SERVER_PORT:
            self.client = chromadb.HttpClient(host=config.CHROMA_SERVER_HOST, port=config.CHROMA_SERVER_PORT)
        else:
            self.client = chromadb.PersistentClient(path=config.CHROMA_PERSISTENCE_PATH)
        self.collection = self.client.get_or_create_collection("demo_gauntlet")
        self.embedding_model = EmbeddingModel()

    def add_chunks(self, chunks: List[Chunk], session_id: Optional[str] = None) -> None:
        """
        Adds chunks to the vector store.
        Generates embeddings if they are missing.
        """
        if not chunks:
            return

        ids = [c.id for c in chunks]
        documents = [c.text for c in chunks]

        # Prepare metadata (flat dict)
        metadatas = []
        for c in chunks:
            meta = c.metadata.copy()
            meta["slide_index"] = c.slide_index
            if session_id:
                meta["session_id"] = session_id
            metadatas.append(meta)

        # Generate embeddings if needed
        embeddings = [c.embedding for c in chunks]
        texts_to_embed = []
        indices_to_embed = []

        for i, emb in enumerate(embeddings):
            if not emb:
                texts_to_embed.append(documents[i])
                indices_to_embed.append(i)

        if texts_to_embed:
            new_embeddings = self.embedding_model.encode(texts_to_embed)
            for i, idx in enumerate(indices_to_embed):
                embeddings[idx] = new_embeddings[i]
                chunks[idx].embedding = new_embeddings[i] # Update chunk object too

        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings, # type: ignore
            metadatas=metadatas # type: ignore
        )

    def get_nearest_chunks(self, query: str, k: int = 5, session_id: Optional[str] = None) -> List[Chunk]:
        """
        Queries the store for similar chunks.
        """
        query_embedding = self.embedding_model.encode(query)[0]

        where_clause: Dict[str, Any] = {}
        if session_id:
            where_clause["session_id"] = session_id

        results = self.collection.query(
            query_embeddings=[query_embedding], # type: ignore
            n_results=k,
            where=where_clause if where_clause else None
        )
        
        return self._results_to_chunks(results)

    def get_all_chunks(self, session_id: Optional[str] = None) -> List[Chunk]:
        """
        Retrieves all chunks, optionally filtered by session_id.
        """
        where_clause: Dict[str, Any] = {}
        if session_id:
            where_clause["session_id"] = session_id

        results = self.collection.get(
            where=where_clause
        )
        
        return self._results_to_chunks(results)

    def get_chunks_for_slide(self, slide_index: int, session_id: Optional[str] = None) -> List[Chunk]:
        """
        Retrieves all chunks for a specific slide.
        """
        where_clause: Dict[str, Any] = {"slide_index": slide_index}
        if session_id:
            where_clause["session_id"] = session_id

        results = self.collection.get(
            where=where_clause
        )
        
        return self._results_to_chunks(results)

    def _results_to_chunks(self, results: Any) -> List[Chunk]:
        chunks: List[Chunk] = []
        if not results.get("ids"):
            return chunks
            
        # Handle both 'get' and 'query' result structures
        ids = results["ids"]
        documents = results["documents"]
        metadatas = results["metadatas"]
        
        # Check if it's a query result (list of lists)
        if isinstance(ids[0], list):
             ids = ids[0]
             documents = documents[0]
             metadatas = metadatas[0]

        for i in range(len(ids)):
            chunk_id = ids[i]
            text = documents[i]
            metadata = dict(metadatas[i])

            # Reconstruct Chunk
            slide_index = metadata.pop("slide_index", 0)

            chunks.append(Chunk(
                id=chunk_id,
                slide_index=slide_index,
                text=text,
                metadata=metadata
            ))
            
        return chunks

# Alias for backward compatibility if needed, but prefer DeckRetriever
VectorStore = DeckRetriever
