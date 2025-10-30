from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
import tiktoken
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class TextChunker:
    """Service for chunking text into semantic segments."""

    def __init__(self):
        """Initialize the text chunker with configuration."""
        self.chunk_size = settings.chunk_size
        self.chunk_overlap = settings.chunk_overlap
        self.encoding = tiktoken.get_encoding("cl100k_base")  # OpenAI's encoding

        # Initialize LangChain text splitter
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=self._token_length,
            separators=["\n\n", "\n", ". ", " ", ""],
            keep_separator=True
        )

    def _token_length(self, text: str) -> int:
        """
        Calculate token length using tiktoken.

        Args:
            text: Input text

        Returns:
            Number of tokens
        """
        return len(self.encoding.encode(text))

    def chunk_pages(self, pages_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Chunk text from pages while preserving page metadata.

        Args:
            pages_data: List of page dictionaries with page_number and text

        Returns:
            List of chunk dictionaries with content and metadata
        """
        all_chunks = []
        chunk_index = 0

        for page_data in pages_data:
            page_number = page_data["page_number"]
            page_text = page_data["text"]

            if not page_text.strip():
                logger.debug(f"Skipping empty page {page_number}")
                continue

            # Split the page text into chunks
            text_chunks = self.splitter.split_text(page_text)

            for chunk_text in text_chunks:
                chunk = {
                    "content": chunk_text,
                    "chunk_index": chunk_index,
                    "page_number": page_number,
                    "token_count": self._token_length(chunk_text),
                    "metadata": {
                        "page_number": page_number,
                        "char_count": len(chunk_text)
                    }
                }
                all_chunks.append(chunk)
                chunk_index += 1

        logger.info(f"Created {len(all_chunks)} chunks from {len(pages_data)} pages")
        return all_chunks

    def chunk_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Chunk plain text without page information.

        Args:
            text: Input text to chunk
            metadata: Optional metadata to attach to chunks

        Returns:
            List of chunk dictionaries
        """
        text_chunks = self.splitter.split_text(text)
        chunks = []

        for i, chunk_text in enumerate(text_chunks):
            chunk = {
                "content": chunk_text,
                "chunk_index": i,
                "token_count": self._token_length(chunk_text),
                "metadata": metadata or {}
            }
            chunks.append(chunk)

        logger.info(f"Created {len(chunks)} chunks from text")
        return chunks

    def get_chunk_stats(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get statistics about chunks.

        Args:
            chunks: List of chunk dictionaries

        Returns:
            Statistics dictionary
        """
        if not chunks:
            return {
                "total_chunks": 0,
                "total_tokens": 0,
                "avg_tokens_per_chunk": 0,
                "min_tokens": 0,
                "max_tokens": 0
            }

        token_counts = [c["token_count"] for c in chunks]

        return {
            "total_chunks": len(chunks),
            "total_tokens": sum(token_counts),
            "avg_tokens_per_chunk": sum(token_counts) / len(token_counts),
            "min_tokens": min(token_counts),
            "max_tokens": max(token_counts)
        }


# Singleton instance
text_chunker = TextChunker()
