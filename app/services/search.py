from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.database.vector_store import vector_store
from app.database.models import ContentChunk, Document
from app.services.embedder import embedding_service
import logging

logger = logging.getLogger(__name__)


class SearchService:
    """Service for searching and retrieving documents."""

    def __init__(self):
        """Initialize the search service."""
        self.vector_store = vector_store
        self.embedder = embedding_service

    def semantic_search(
        self,
        query: str,
        db: Session,
        top_k: int = 5,
        user_id: str = "default_user"
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search using vector similarity.

        Args:
            query: Search query text
            db: Database session
            top_k: Number of results to return
            user_id: User ID for filtering

        Returns:
            List of search results with relevance scores
        """
        # Generate query embedding
        logger.info(f"Searching for: {query}")
        query_embedding = self.embedder.generate_embedding(query)

        # Search vector database (try with filter first)
        vector_results = self.vector_store.search(
            query_embedding=query_embedding,
            n_results=top_k,
            filter_metadata={"user_id": user_id}
        )

        # If no results with filter, try without filter
        if not vector_results["ids"] or len(vector_results["ids"][0]) == 0:
            logger.warning(f"No results found with user_id filter, searching without filter")
            vector_results = self.vector_store.search(
                query_embedding=query_embedding,
                n_results=top_k,
                filter_metadata=None
            )

        # Process results
        results = []
        if vector_results["ids"] and len(vector_results["ids"][0]) > 0:
            chunk_ids = vector_results["ids"][0]
            distances = vector_results["distances"][0]
            documents = vector_results["documents"][0]
            metadatas = vector_results["metadatas"][0]

            for i, chunk_id in enumerate(chunk_ids):
                # Fetch chunk and document from database
                chunk = db.query(ContentChunk).filter(ContentChunk.id == chunk_id).first()
                if not chunk:
                    continue

                document = db.query(Document).filter(Document.id == chunk.document_id).first()
                if not document:
                    continue

                # Convert distance to similarity score (0-1, higher is better)
                # ChromaDB returns L2 distance, convert to similarity
                similarity_score = 1 / (1 + distances[i])

                result = {
                    "chunk_id": chunk_id,
                    "document_id": chunk.document_id,
                    "document_title": document.title,
                    "content": chunk.content,
                    "page_number": chunk.page_number,
                    "relevance_score": round(similarity_score, 4),
                    "metadata": {
                        **chunk.chunk_metadata,
                        "chunk_index": chunk.chunk_index,
                        "created_at": chunk.created_at.isoformat()
                    }
                }
                results.append(result)

        logger.info(f"Found {len(results)} results")
        return results

    def get_document_chunks(self, document_id: str, db: Session) -> List[ContentChunk]:
        """
        Get all chunks for a specific document.

        Args:
            document_id: Document ID
            db: Database session

        Returns:
            List of ContentChunk objects
        """
        chunks = db.query(ContentChunk).filter(
            ContentChunk.document_id == document_id
        ).order_by(ContentChunk.chunk_index).all()

        return chunks

    def rerank_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Re-rank search results (placeholder for future enhancement).

        Args:
            results: Initial search results

        Returns:
            Re-ranked results
        """
        # For MVP, just return as-is
        # Future: implement cross-encoder re-ranking, diversity, etc.
        return results


# Singleton instance
search_service = SearchService()
