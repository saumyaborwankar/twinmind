from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import AsyncIterator
import json
import logging

from app.database.connection import get_db
from app.models.schemas import (
    QuestionRequest,
    QuestionResponse,
    ConversationRequest,
    DocumentSummaryRequest,
    DocumentSummaryResponse
)
from app.services.rag_service import rag_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/ask", response_model=QuestionResponse)
async def ask_question(
    request: QuestionRequest,
    db: Session = Depends(get_db)
):
    """
    Answer a question using RAG (Retrieval-Augmented Generation).

    This endpoint:
    1. Retrieves relevant context from your documents
    2. Uses an LLM to generate a comprehensive answer
    3. Provides source citations for transparency

    Args:
        request: Question request with parameters
        db: Database session

    Returns:
        Answer with sources and metadata
    """
    try:
        result = rag_service.answer_question(
            question=request.question,
            db=db,
            top_k=request.top_k,
            user_id=request.user_id,
            system_prompt=request.system_prompt,
            include_sources=request.include_sources
        )

        return QuestionResponse(**result)

    except Exception as e:
        logger.error(f"Error in ask endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing question: {str(e)}"
        )


@router.post("/ask/stream")
async def ask_question_stream(
    request: QuestionRequest,
    db: Session = Depends(get_db)
):
    """
    Answer a question with streaming response.

    This endpoint streams the answer in real-time as it's generated,
    providing a better user experience for longer responses.

    Args:
        request: Question request with parameters
        db: Database session

    Returns:
        Streaming response with answer chunks and sources
    """
    try:
        # Get answer stream and sources
        answer_stream, sources = rag_service.answer_question_stream(
            question=request.question,
            db=db,
            top_k=request.top_k,
            user_id=request.user_id,
            system_prompt=request.system_prompt
        )

        async def generate_response() -> AsyncIterator[str]:
            """Generate server-sent events with answer and sources."""
            # First, send sources
            sources_data = {
                "type": "sources",
                "data": [
                    {
                        "source_id": s["source_id"],
                        "document_title": s["document_title"],
                        "page_number": s["page_number"],
                        "relevance_score": s["relevance_score"],
                        "content_preview": s["content_preview"]
                    }
                    for s in sources
                ]
            }
            yield f"data: {json.dumps(sources_data)}\n\n"

            # Then stream the answer
            for chunk in answer_stream:
                answer_data = {
                    "type": "answer",
                    "data": chunk
                }
                yield f"data: {json.dumps(answer_data)}\n\n"

            # Send completion signal
            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        return StreamingResponse(
            generate_response(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )

    except Exception as e:
        logger.error(f"Error in streaming ask endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing question: {str(e)}"
        )


@router.post("/conversation", response_model=QuestionResponse)
async def conversation_qa(
    request: ConversationRequest,
    db: Session = Depends(get_db)
):
    """
    Answer a question with conversation history context.

    This endpoint maintains conversation context, allowing for
    follow-up questions and multi-turn dialogues.

    Args:
        request: Conversation request with history
        db: Database session

    Returns:
        Answer with sources and metadata
    """
    try:
        # Convert conversation history to format expected by LLM
        conversation_history = [
            {"role": msg.role, "content": msg.content}
            for msg in request.conversation_history
        ]

        result = rag_service.answer_question(
            question=request.question,
            db=db,
            top_k=request.top_k,
            user_id=request.user_id,
            conversation_history=conversation_history,
            include_sources=True
        )

        return QuestionResponse(**result)

    except Exception as e:
        logger.error(f"Error in conversation endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing conversation: {str(e)}"
        )


@router.post("/summarize", response_model=DocumentSummaryResponse)
async def summarize_document(
    request: DocumentSummaryRequest,
    db: Session = Depends(get_db)
):
    """
    Generate a summary of a specific document.

    This endpoint analyzes a document and creates a concise summary
    of its main points and content.

    Args:
        request: Document summary request
        db: Database session

    Returns:
        Document summary with metadata
    """
    try:
        result = rag_service.get_document_summary(
            document_id=request.document_id,
            db=db
        )

        return DocumentSummaryResponse(**result)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in summarize endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error summarizing document: {str(e)}"
        )
