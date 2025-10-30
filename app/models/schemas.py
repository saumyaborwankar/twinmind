from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# Document Schemas
class DocumentBase(BaseModel):
    """Base document schema."""
    title: str
    user_id: str = "default_user"


class DocumentCreate(DocumentBase):
    """Schema for creating a document."""
    file_path: str
    file_size: int
    page_count: int
    content_hash: str
    doc_metadata: Optional[Dict[str, Any]] = {}


class DocumentResponse(DocumentBase):
    """Schema for document response."""
    id: str
    file_path: str
    file_size: int
    page_count: int
    content_hash: str
    created_at: datetime
    doc_metadata: Dict[str, Any]

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """Schema for list of documents."""
    documents: List[DocumentResponse]
    total: int


# Chunk Schemas
class ChunkBase(BaseModel):
    """Base chunk schema."""
    content: str
    chunk_index: int
    page_number: Optional[int] = None


class ChunkCreate(ChunkBase):
    """Schema for creating a chunk."""
    document_id: str
    embedding_id: str
    chunk_metadata: Optional[Dict[str, Any]] = {}


class ChunkResponse(ChunkBase):
    """Schema for chunk response."""
    id: str
    document_id: str
    embedding_id: str
    created_at: datetime
    chunk_metadata: Dict[str, Any]

    class Config:
        from_attributes = True


# Query Schemas
class QueryRequest(BaseModel):
    """Schema for search query request."""
    query: str = Field(..., min_length=1, description="Search query text")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of results to return")
    user_id: str = Field(default="default_user", description="User ID for filtering")


class SearchResult(BaseModel):
    """Schema for a single search result."""
    chunk_id: str
    document_id: str
    document_title: str
    content: str
    page_number: Optional[int]
    relevance_score: float
    metadata: Dict[str, Any]


class QueryResponse(BaseModel):
    """Schema for query response."""
    query: str
    results: List[SearchResult]
    total_results: int
    processing_time_ms: float


# Upload Schemas
class UploadResponse(BaseModel):
    """Schema for upload response."""
    document_id: str
    title: str
    page_count: int
    file_size: int
    chunks_created: int
    message: str


# Health Check Schema
class HealthResponse(BaseModel):
    """Schema for health check response."""
    status: str
    vector_db_count: int
    database_documents: int


# RAG/Q&A Schemas
class QuestionRequest(BaseModel):
    """Schema for question answering request."""
    question: str = Field(..., min_length=1, description="Question to answer")
    top_k: int = Field(default=5, ge=1, le=10, description="Number of context chunks to retrieve")
    user_id: str = Field(default="default_user", description="User ID for filtering")
    include_sources: bool = Field(default=True, description="Whether to include source citations")
    system_prompt: Optional[str] = Field(default=None, description="Custom system prompt")


class SourceCitation(BaseModel):
    """Schema for a source citation."""
    source_id: int
    document_title: str
    page_number: Any
    relevance_score: float
    chunk_id: str
    document_id: str
    content_preview: str


class QuestionResponse(BaseModel):
    """Schema for question answering response."""
    answer: str
    sources: List[SourceCitation]
    context_used: int
    confidence: str
    model: str
    usage: Dict[str, int]


class ConversationMessage(BaseModel):
    """Schema for a conversation message."""
    role: str = Field(..., description="Role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")


class ConversationRequest(BaseModel):
    """Schema for conversation-based Q&A."""
    question: str = Field(..., min_length=1, description="Current question")
    conversation_history: List[ConversationMessage] = Field(
        default=[],
        description="Previous conversation history"
    )
    top_k: int = Field(default=5, ge=1, le=10, description="Number of context chunks")
    user_id: str = Field(default="default_user", description="User ID")


class DocumentSummaryRequest(BaseModel):
    """Schema for document summary request."""
    document_id: str = Field(..., description="Document ID to summarize")


class DocumentSummaryResponse(BaseModel):
    """Schema for document summary response."""
    document_id: str
    document_title: str
    summary: str
    page_count: int
    chunks_analyzed: int
