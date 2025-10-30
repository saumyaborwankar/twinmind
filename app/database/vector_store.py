import chromadb
from chromadb.config import Settings as ChromaSettings
from app.config import settings
from typing import List, Dict, Any, Optional


class VectorStore:
    """Vector database wrapper using ChromaDB."""

    def __init__(self):
        """Initialize ChromaDB client and collection."""
        self.client = chromadb.Client(
            ChromaSettings(
                persist_directory=settings.vector_db_path,
                anonymized_telemetry=False,
            )
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="second_brain_embeddings",
            metadata={"hnsw:space": "cosine"}
        )

    def add_embeddings(
        self,
        embeddings: List[List[float]],
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str]
    ) -> None:
        """
        Add embeddings to the vector store.

        Args:
            embeddings: List of embedding vectors
            documents: List of text content
            metadatas: List of metadata dictionaries
            ids: List of unique identifiers
        """
        self.collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    def search(
        self,
        query_embedding: List[float],
        n_results: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Search for similar embeddings.

        Args:
            query_embedding: Query vector
            n_results: Number of results to return
            filter_metadata: Optional metadata filter

        Returns:
            Search results with ids, documents, distances, and metadatas
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=filter_metadata if filter_metadata else None
        )
        return results

    def delete_by_document_id(self, document_id: str) -> None:
        """
        Delete all embeddings for a specific document.

        Args:
            document_id: Document ID to delete
        """
        self.collection.delete(
            where={"document_id": document_id}
        )

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection."""
        return {
            "count": self.collection.count(),
            "name": self.collection.name,
            "metadata": self.collection.metadata
        }


# Singleton instance
vector_store = VectorStore()
