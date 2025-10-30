from typing import List, Dict, Any, Optional, Iterator
from sqlalchemy.orm import Session
from app.services.search import search_service
from app.services.llm_service import llm_service
import logging

logger = logging.getLogger(__name__)


class RAGService:
    """Service for Retrieval-Augmented Generation (RAG) Q&A."""

    def __init__(self):
        """Initialize the RAG service."""
        self.search_service = search_service
        self.llm_service = llm_service

    def answer_question(
        self,
        question: str,
        db: Session,
        top_k: int = 5,
        user_id: str = "default_user",
        system_prompt: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        include_sources: bool = True
    ) -> Dict[str, Any]:
        """
        Answer a question using RAG (Retrieval-Augmented Generation).

        Args:
            question: User's question
            db: Database session
            top_k: Number of context chunks to retrieve
            user_id: User ID for filtering
            system_prompt: Optional custom system prompt
            conversation_history: Optional conversation history
            include_sources: Whether to include source citations

        Returns:
            Dictionary with answer, sources, and metadata
        """
        logger.info(f"Processing question: {question}")

        # Step 1: Retrieve relevant context
        search_results = self.search_service.semantic_search(
            query=question,
            db=db,
            top_k=top_k,
            user_id=user_id
        )

        if not search_results:
            return {
                "answer": "I couldn't find any relevant information in your documents to answer this question.",
                "sources": [],
                "context_used": 0,
                "confidence": "none",
                "model": self.llm_service.model,
                "usage": {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0
                }
            }

        # Step 2: Build context from search results
        context_text, sources = self._build_context(search_results)

        # Step 3: Generate answer using LLM
        llm_response = self.llm_service.generate_answer(
            question=question,
            context=context_text,
            system_prompt=system_prompt,
            conversation_history=conversation_history
        )

        # Step 4: Prepare response
        response = {
            "answer": llm_response["answer"],
            "sources": sources if include_sources else [],
            "context_used": len(search_results),
            "model": llm_response["model"],
            "usage": llm_response["usage"],
            "confidence": self._estimate_confidence(search_results)
        }

        logger.info(f"Generated answer with {len(sources)} sources")
        return response

    def answer_question_stream(
        self,
        question: str,
        db: Session,
        top_k: int = 5,
        user_id: str = "default_user",
        system_prompt: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> tuple[Iterator[str], List[Dict[str, Any]]]:
        """
        Answer a question with streaming response.

        Args:
            question: User's question
            db: Database session
            top_k: Number of context chunks to retrieve
            user_id: User ID for filtering
            system_prompt: Optional custom system prompt
            conversation_history: Optional conversation history

        Returns:
            Tuple of (answer_stream, sources)
        """
        logger.info(f"Processing streaming question: {question}")

        # Retrieve relevant context
        search_results = self.search_service.semantic_search(
            query=question,
            db=db,
            top_k=top_k,
            user_id=user_id
        )

        if not search_results:
            def empty_stream():
                yield "I couldn't find any relevant information in your documents to answer this question."
            return empty_stream(), []

        # Build context
        context_text, sources = self._build_context(search_results)

        # Generate streaming answer
        answer_stream = self.llm_service.generate_answer_stream(
            question=question,
            context=context_text,
            system_prompt=system_prompt,
            conversation_history=conversation_history
        )

        return answer_stream, sources

    def _build_context(
        self,
        search_results: List[Dict[str, Any]]
    ) -> tuple[str, List[Dict[str, Any]]]:
        """
        Build context text and source citations from search results.

        Args:
            search_results: List of search result dictionaries

        Returns:
            Tuple of (context_text, sources)
        """
        context_parts = []
        sources = []

        for i, result in enumerate(search_results, 1):
            # Format each chunk with metadata
            doc_title = result["document_title"]
            page_num = result.get("page_number", "N/A")
            content = result["content"]
            relevance = result["relevance_score"]

            # Add to context
            context_parts.append(
                f"[Source {i}: {doc_title}, Page {page_num}, Relevance: {relevance:.2f}]\n{content}\n"
            )

            # Add to sources list
            sources.append({
                "source_id": i,
                "document_title": doc_title,
                "page_number": page_num,
                "relevance_score": relevance,
                "chunk_id": result["chunk_id"],
                "document_id": result["document_id"],
                "content_preview": content[:200] + "..." if len(content) > 200 else content
            })

        context_text = "\n---\n".join(context_parts)
        return context_text, sources

    def _estimate_confidence(self, search_results: List[Dict[str, Any]]) -> str:
        """
        Estimate confidence level based on search results.

        Args:
            search_results: List of search results

        Returns:
            Confidence level: "high", "medium", "low", or "none"
        """
        if not search_results:
            return "none"

        # Check top result relevance
        top_relevance = search_results[0]["relevance_score"]

        if top_relevance >= 0.8:
            return "high"
        elif top_relevance >= 0.6:
            return "medium"
        else:
            return "low"

    def multi_query_rag(
        self,
        questions: List[str],
        db: Session,
        top_k: int = 5,
        user_id: str = "default_user"
    ) -> List[Dict[str, Any]]:
        """
        Answer multiple questions in batch.

        Args:
            questions: List of questions
            db: Database session
            top_k: Number of context chunks per question
            user_id: User ID for filtering

        Returns:
            List of answer dictionaries
        """
        answers = []

        for question in questions:
            try:
                answer = self.answer_question(
                    question=question,
                    db=db,
                    top_k=top_k,
                    user_id=user_id
                )
                answers.append({
                    "question": question,
                    **answer
                })
            except Exception as e:
                logger.error(f"Error answering question '{question}': {str(e)}")
                answers.append({
                    "question": question,
                    "answer": f"Error processing question: {str(e)}",
                    "sources": [],
                    "error": True
                })

        return answers

    def get_document_summary(
        self,
        document_id: str,
        db: Session
    ) -> Dict[str, Any]:
        """
        Generate a summary of a specific document.

        Args:
            document_id: Document ID to summarize
            db: Database session

        Returns:
            Dictionary with summary and metadata
        """
        from app.database.models import Document, ContentChunk

        # Get document
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise ValueError(f"Document {document_id} not found")

        # Get all chunks for the document
        chunks = db.query(ContentChunk).filter(
            ContentChunk.document_id == document_id
        ).order_by(ContentChunk.chunk_index).all()

        # Combine chunk content (limit to avoid token overflow)
        full_text = " ".join([chunk.content for chunk in chunks[:20]])  # First 20 chunks

        # Generate summary
        summary = self.llm_service.summarize_text(full_text, max_length=300)

        return {
            "document_id": document_id,
            "document_title": document.title,
            "summary": summary,
            "page_count": document.page_count,
            "chunks_analyzed": min(len(chunks), 20)
        }


# Singleton instance
rag_service = RAGService()
