from typing import List, cast
import chromadb
from backend.models.core import Chunk
from backend.models.embeddings import EmbeddingModel

class DeckRetriever:
    def __init__(self, path: str = "./data/chroma_db"):
        self.client = chromadb.PersistentClient(path=path)
        self.collection = self.client.get_or_create_collection("demo_gauntlet")
        self.embedding_model = EmbeddingModel()

    def add_chunks(self, chunks: List[Chunk]) -> None:
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

    def get_nearest_chunks(self, query: str, k: int = 5) -> List[Chunk]:
        """
        Queries the store for similar chunks.
        """
        query_embedding = self.embedding_model.encode(query)[0]

        results = self.collection.query(
            query_embeddings=[query_embedding], # type: ignore
            n_results=k
        )
        
        return self._results_to_chunks(results)

    def get_chunks_for_slide(self, slide_index: int) -> List[Chunk]:
        """
        Retrieves all chunks for a specific slide.
        """
        results = self.collection.get(
            where={"slide_index": slide_index}
        )
        
        return self._results_to_chunks(results)

    def _results_to_chunks(self, results: dict) -> List[Chunk]:
        chunks = []
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
