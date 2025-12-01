from typing import List
import chromadb
from backend.models.core import Fact
from backend.models.embeddings import EmbeddingModel

class FactStore:
    def __init__(self, path: str = "./data/chroma_db"):
        self.client = chromadb.PersistentClient(path=path)
        self.collection = self.client.get_or_create_collection("research_facts")
        self.embedding_model = EmbeddingModel()

    def add_facts(self, facts: List[Fact]) -> None:
        """
        Adds facts to the vector store.
        """
        if not facts:
            return

        ids = [f.id for f in facts]
        documents = [f.text for f in facts]
        
        # Prepare metadata
        metadatas = []
        for f in facts:
            metadatas.append({
                "topic": f.topic,
                "source_url": f.source_url,
                "source_title": f.source_title,
                "domain": f.domain,
                "snippet": f.snippet
            })

        # Generate embeddings
        embeddings = self.embedding_model.encode(documents)

        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings, # type: ignore
            metadatas=metadatas # type: ignore
        )

    def get_facts_by_topic(self, topic: str, limit: int = 5) -> List[Fact]:
        """
        Retrieves facts by topic using metadata filtering.
        """
        results = self.collection.get(
            where={"topic": topic},
            limit=limit
        )
        
        return self._results_to_facts(results)

    def search_facts(self, query: str, k: int = 5) -> List[Fact]:
        """
        Semantic search for facts.
        """
        query_embedding = self.embedding_model.encode(query)[0]
        
        results = self.collection.query(
            query_embeddings=[query_embedding], # type: ignore
            n_results=k
        )
        
        return self._results_to_facts(results) # type: ignore

    def _results_to_facts(self, results: dict) -> List[Fact]:
        facts = []
        if not results.get("ids"):
            return facts
            
        # Handle both 'get' and 'query' result structures
        # 'get' returns lists directly, 'query' returns list of lists
        ids = results["ids"]
        documents = results["documents"]
        metadatas = results["metadatas"]
        
        # Check if it's a query result (list of lists)
        if isinstance(ids[0], list):
             ids = ids[0]
             documents = documents[0]
             metadatas = metadatas[0]

        for i in range(len(ids)):
            meta = metadatas[i]
            facts.append(Fact(
                id=ids[i],
                topic=meta.get("topic", ""),
                text=documents[i],
                source_url=meta.get("source_url", ""),
                source_title=meta.get("source_title", ""),
                domain=meta.get("domain", ""),
                snippet=meta.get("snippet", "")
            ))
            
        return facts
