import hashlib
import pdfplumber
from pathlib import Path
from typing import List, Dict, Any, Tuple
from PyPDF2 import PdfReader
import logging

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Service for processing PDF files."""

    @staticmethod
    def calculate_file_hash(file_path: str) -> str:
        """
        Calculate SHA-256 hash of a file.

        Args:
            file_path: Path to the file

        Returns:
            Hexadecimal hash string
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    @staticmethod
    def validate_pdf(file_path: str) -> Tuple[bool, str]:
        """
        Validate if file is a readable PDF.

        Args:
            file_path: Path to the PDF file

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            with open(file_path, "rb") as f:
                reader = PdfReader(f)
                if len(reader.pages) == 0:
                    return False, "PDF has no pages"
            return True, ""
        except Exception as e:
            return False, f"Invalid PDF: {str(e)}"

    @staticmethod
    def extract_text_with_pages(file_path: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Extract text from PDF with page-level metadata.

        Args:
            file_path: Path to the PDF file

        Returns:
            Tuple of (pages_data, metadata)
            pages_data: List of dicts with page_number and text
            metadata: Dict with PDF metadata (title, author, etc.)
        """
        pages_data = []
        metadata = {}

        try:
            # Extract text using pdfplumber (better text extraction)
            with pdfplumber.open(file_path) as pdf:
                # Extract metadata
                if pdf.metadata:
                    metadata = {
                        "title": pdf.metadata.get("Title", ""),
                        "author": pdf.metadata.get("Author", ""),
                        "subject": pdf.metadata.get("Subject", ""),
                        "creator": pdf.metadata.get("Creator", ""),
                        "producer": pdf.metadata.get("Producer", ""),
                    }

                # Extract text from each page
                for i, page in enumerate(pdf.pages, start=1):
                    text = page.extract_text() or ""
                    pages_data.append({
                        "page_number": i,
                        "text": text.strip(),
                        "char_count": len(text)
                    })

            # Add total page count to metadata
            metadata["total_pages"] = len(pages_data)
            metadata["total_chars"] = sum(p["char_count"] for p in pages_data)

            logger.info(f"Extracted {len(pages_data)} pages from PDF")
            return pages_data, metadata

        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise

    @staticmethod
    def get_pdf_info(file_path: str) -> Dict[str, Any]:
        """
        Get basic information about a PDF file.

        Args:
            file_path: Path to the PDF file

        Returns:
            Dictionary with PDF information
        """
        file_path_obj = Path(file_path)
        file_size = file_path_obj.stat().st_size

        with open(file_path, "rb") as f:
            reader = PdfReader(f)
            page_count = len(reader.pages)

            info = {
                "filename": file_path_obj.name,
                "file_size": file_size,
                "page_count": page_count,
                "file_path": str(file_path_obj.absolute())
            }

        return info

    @staticmethod
    def extract_title_from_pdf(file_path: str, metadata: Dict[str, Any]) -> str:
        """
        Extract or generate a title for the PDF.

        Args:
            file_path: Path to the PDF file
            metadata: PDF metadata dictionary

        Returns:
            Title string
        """
        # Try to get title from metadata
        if metadata.get("title") and metadata["title"].strip():
            return metadata["title"].strip()

        # Fall back to filename without extension
        filename = Path(file_path).stem
        return filename


# Singleton instance
pdf_processor = PDFProcessor()
