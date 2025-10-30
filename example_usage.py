#!/usr/bin/env python3
"""
Example usage of the Second Brain API.
This demonstrates how to integrate the API into your own applications.
"""

import requests
from pathlib import Path
from typing import List, Dict, Any


class SecondBrainClient:
    """Client for interacting with the Second Brain API."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the client.

        Args:
            base_url: Base URL of the API server
        """
        self.base_url = base_url
        self.api_base = f"{base_url}/api"

    def health_check(self) -> Dict[str, Any]:
        """Check if the API is healthy."""
        response = requests.get(f"{self.api_base}/health")
        response.raise_for_status()
        return response.json()

    def upload_pdf(self, file_path: str) -> Dict[str, Any]:
        """
        Upload a PDF file.

        Args:
            file_path: Path to the PDF file

        Returns:
            Upload response with document details
        """
        with open(file_path, "rb") as f:
            files = {"file": (Path(file_path).name, f, "application/pdf")}
            response = requests.post(f"{self.api_base}/upload", files=files)
            response.raise_for_status()
            return response.json()

    def search(self, query: str, top_k: int = 5, user_id: str = "default_user") -> Dict[str, Any]:
        """
        Search documents.

        Args:
            query: Search query text
            top_k: Number of results to return
            user_id: User ID for filtering

        Returns:
            Search results
        """
        payload = {"query": query, "top_k": top_k, "user_id": user_id}
        response = requests.post(f"{self.api_base}/query", json=payload)
        response.raise_for_status()
        return response.json()

    def list_documents(self, skip: int = 0, limit: int = 100) -> Dict[str, Any]:
        """
        List all documents.

        Args:
            skip: Number of documents to skip
            limit: Maximum number of documents to return

        Returns:
            List of documents
        """
        response = requests.get(f"{self.api_base}/documents", params={"skip": skip, "limit": limit})
        response.raise_for_status()
        return response.json()

    def get_document(self, document_id: str) -> Dict[str, Any]:
        """
        Get a specific document.

        Args:
            document_id: Document ID

        Returns:
            Document details
        """
        response = requests.get(f"{self.api_base}/documents/{document_id}")
        response.raise_for_status()
        return response.json()

    def delete_document(self, document_id: str) -> None:
        """
        Delete a document.

        Args:
            document_id: Document ID
        """
        response = requests.delete(f"{self.api_base}/documents/{document_id}")
        response.raise_for_status()


def example_workflow():
    """Example workflow demonstrating API usage."""
    # Initialize client
    client = SecondBrainClient()

    print("🧠 Second Brain Client - Example Workflow\n")

    # 1. Check health
    print("1️⃣ Checking API health...")
    health = client.health_check()
    print(f"   ✅ Status: {health['status']}")
    print(f"   📊 Documents: {health['database_documents']}")
    print()

    # 2. Upload a document (uncomment and provide a path)
    # print("2️⃣ Uploading a PDF...")
    # result = client.upload_pdf("/path/to/your/document.pdf")
    # print(f"   ✅ Uploaded: {result['title']}")
    # print(f"   📄 Pages: {result['page_count']}")
    # print(f"   🧩 Chunks: {result['chunks_created']}")
    # document_id = result['document_id']
    # print()

    # 3. List documents
    print("3️⃣ Listing documents...")
    docs = client.list_documents(limit=5)
    print(f"   📚 Total documents: {docs['total']}")
    for doc in docs['documents']:
        print(f"   - {doc['title']} ({doc['page_count']} pages)")
    print()

    # 4. Search
    print("4️⃣ Searching for 'machine learning'...")
    results = client.search("machine learning", top_k=3)
    print(f"   🔍 Found {results['total_results']} results in {results['processing_time_ms']:.2f}ms")
    for i, result in enumerate(results['results'], 1):
        print(f"\n   Result {i}:")
        print(f"   📄 Document: {result['document_title']}")
        print(f"   📃 Page: {result['page_number']}")
        print(f"   ⭐ Relevance: {result['relevance_score']:.4f}")
        print(f"   📝 Preview: {result['content'][:100]}...")
    print()

    # 5. Get specific document (uncomment if you uploaded one)
    # print("5️⃣ Getting document details...")
    # doc = client.get_document(document_id)
    # print(f"   📄 Title: {doc['title']}")
    # print(f"   📊 Size: {doc['file_size']} bytes")
    # print(f"   📅 Created: {doc['created_at']}")
    # print()

    print("✅ Workflow completed!")


if __name__ == "__main__":
    try:
        example_workflow()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to API server.")
        print("   Make sure the server is running: python -m app.main")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
