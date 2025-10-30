from sqlalchemy import Column, String, Integer, Text, ForeignKey, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid


Base = declarative_base()


def generate_uuid():
    """Generate a UUID string."""
    return str(uuid.uuid4())


class Document(Base):
    """Document metadata table."""

    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, default="default_user")  # For future multi-user support
    title = Column(String(500), nullable=False)
    file_path = Column(Text, nullable=False)
    file_size = Column(Integer, nullable=False)
    page_count = Column(Integer, nullable=False)
    content_hash = Column(String(64), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    doc_metadata = Column(JSON, default=dict)

    # Relationship
    chunks = relationship("ContentChunk", back_populates="document", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Document(id={self.id}, title={self.title})>"


class ContentChunk(Base):
    """Content chunks table for storing processed text segments."""

    __tablename__ = "content_chunks"

    id = Column(String, primary_key=True, default=generate_uuid)
    document_id = Column(String, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    page_number = Column(Integer)
    embedding_id = Column(String(100))  # Reference to vector DB
    created_at = Column(DateTime, default=datetime.utcnow)
    chunk_metadata = Column(JSON, default=dict)

    # Relationship
    document = relationship("Document", back_populates="chunks")

    def __repr__(self):
        return f"<ContentChunk(id={self.id}, document_id={self.document_id}, chunk_index={self.chunk_index})>"
