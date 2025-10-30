from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import shutil
from pathlib import Path
import time

from app.database.connection import get_db
from app.database.models import Document, ContentChunk
from app.database.vector_store import vector_store
from app.models.schemas import (
    DocumentResponse,
    DocumentListResponse,
    QueryRequest,
    QueryResponse,
    UploadResponse,
    HealthResponse
)
from app.services.pdf_processor import pdf_processor
from app.services.chunker import text_chunker
from app.services.embedder import embedding_service
from app.services.search import search_service
from app.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload and process a PDF file.

    Args:
        file: PDF file to upload
        db: Database session

    Returns:
        Upload response with document details
    """
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported"
        )

    # Validate file size
    file_content = await file.read()
    file_size = len(file_content)

    if file_size > settings.max_file_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum allowed size of {settings.max_file_size_mb}MB"
        )

    # Save file temporarily
    file_path = Path(settings.upload_dir) / file.filename
    with open(file_path, "wb") as f:
        f.write(file_content)

    try:
        # Validate PDF
        is_valid, error_msg = pdf_processor.validate_pdf(str(file_path))
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )

        # Calculate content hash
        content_hash = pdf_processor.calculate_file_hash(str(file_path))

        # Check for duplicates
        existing_doc = db.query(Document).filter(Document.content_hash == content_hash).first()
        if existing_doc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Document already exists with ID: {existing_doc.id}"
            )

        # Extract text and metadata
        pages_data, pdf_metadata = pdf_processor.extract_text_with_pages(str(file_path))

        # Get PDF info
        pdf_info = pdf_processor.get_pdf_info(str(file_path))

        # Extract title
        title = pdf_processor.extract_title_from_pdf(str(file_path), pdf_metadata)

        # Create document record
        document = Document(
            title=title,
            file_path=str(file_path),
            file_size=file_size,
            page_count=pdf_info["page_count"],
            content_hash=content_hash,
            doc_metadata=pdf_metadata
        )
        db.add(document)
        db.flush()  # Get document ID

        # Chunk the text
        chunks = text_chunker.chunk_pages(pages_data)

        # Generate embeddings
        chunk_texts = [chunk["content"] for chunk in chunks]
        embeddings = embedding_service.generate_embeddings_batch(chunk_texts)

        # Prepare data for vector store
        chunk_ids = []
        chunk_metadatas = []
        chunk_records = []

        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_id = f"{document.id}_chunk_{i}"
            chunk_ids.append(chunk_id)

            # Create chunk record
            chunk_record = ContentChunk(
                id=chunk_id,
                document_id=document.id,
                chunk_index=chunk["chunk_index"],
                content=chunk["content"],
                page_number=chunk.get("page_number"),
                embedding_id=chunk_id,
                chunk_metadata=chunk.get("metadata", {})
            )
            chunk_records.append(chunk_record)

            # Prepare metadata for vector store
            chunk_metadatas.append({
                "document_id": document.id,
                "user_id": document.user_id,
                "chunk_index": chunk["chunk_index"],
                "page_number": chunk.get("page_number"),
                "title": document.title
            })

        # Store in vector database
        vector_store.add_embeddings(
            embeddings=embeddings,
            documents=chunk_texts,
            metadatas=chunk_metadatas,
            ids=chunk_ids
        )

        # Store chunks in database
        db.add_all(chunk_records)
        db.commit()
        db.refresh(document)

        logger.info(f"Successfully processed document {document.id} with {len(chunks)} chunks")

        return UploadResponse(
            document_id=document.id,
            title=document.title,
            page_count=document.page_count,
            file_size=document.file_size,
            chunks_created=len(chunks),
            message="PDF uploaded and processed successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error processing PDF: {str(e)}")
        # Clean up file
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing PDF: {str(e)}"
        )


@router.post("/query", response_model=QueryResponse)
async def query_documents(
    request: QueryRequest,
    db: Session = Depends(get_db)
):
    """
    Search documents using semantic search.

    Args:
        request: Query request with search parameters
        db: Database session

    Returns:
        Query response with search results
    """
    start_time = time.time()

    try:
        # Perform semantic search
        results = search_service.semantic_search(
            query=request.query,
            db=db,
            top_k=request.top_k,
            user_id=request.user_id
        )

        # Re-rank results (currently pass-through)
        results = search_service.rerank_results(results)

        processing_time = (time.time() - start_time) * 1000  # Convert to ms

        return QueryResponse(
            query=request.query,
            results=results,
            total_results=len(results),
            processing_time_ms=round(processing_time, 2)
        )

    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}"
        )


@router.get("/documents", response_model=DocumentListResponse)
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all documents.

    Args:
        skip: Number of documents to skip
        limit: Maximum number of documents to return
        db: Database session

    Returns:
        List of documents
    """
    documents = db.query(Document).offset(skip).limit(limit).all()
    total = db.query(Document).count()

    return DocumentListResponse(
        documents=documents,
        total=total
    )


@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific document by ID.

    Args:
        document_id: Document ID
        db: Database session

    Returns:
        Document details
    """
    document = db.query(Document).filter(Document.id == document_id).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    return document


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a document and all its chunks.

    Args:
        document_id: Document ID
        db: Database session
    """
    document = db.query(Document).filter(Document.id == document_id).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    try:
        # Delete from vector store
        vector_store.delete_by_document_id(document_id)

        # Delete file
        file_path = Path(document.file_path)
        if file_path.exists():
            file_path.unlink()

        # Delete from database (cascades to chunks)
        db.delete(document)
        db.commit()

        logger.info(f"Successfully deleted document {document_id}")

    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting document: {str(e)}"
        )


@router.get("/health", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint.

    Args:
        db: Database session

    Returns:
        Health status
    """
    try:
        # Check database
        document_count = db.query(Document).count()

        # Check vector store
        vector_stats = vector_store.get_collection_stats()

        return HealthResponse(
            status="healthy",
            vector_db_count=vector_stats["count"],
            database_documents=document_count
        )

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unhealthy: {str(e)}"
        )
