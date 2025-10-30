#!/usr/bin/env python3
"""
Simple test script for the Second Brain API.
Run this after starting the server to verify everything works.
"""

import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8000"


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_health():
    """Test health check endpoint."""
    print_section("Health Check")
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_upload(pdf_path):
    """Test PDF upload."""
    print_section("Upload PDF")

    if not Path(pdf_path).exists():
        print(f"❌ File not found: {pdf_path}")
        return None

    with open(pdf_path, "rb") as f:
        files = {"file": (Path(pdf_path).name, f, "application/pdf")}
        response = requests.post(f"{BASE_URL}/api/upload", files=files)

    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        data = response.json()
        print(f"✅ Upload successful!")
        print(f"Document ID: {data['document_id']}")
        print(f"Title: {data['title']}")
        print(f"Pages: {data['page_count']}")
        print(f"Chunks created: {data['chunks_created']}")
        return data["document_id"]
    else:
        print(f"❌ Upload failed: {response.text}")
        return None


def test_list_documents():
    """Test listing documents."""
    print_section("List Documents")
    response = requests.get(f"{BASE_URL}/api/documents")
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Total documents: {data['total']}")
        for doc in data["documents"]:
            print(f"  - {doc['title']} (ID: {doc['id'][:8]}...)")
    else:
        print(f"❌ Failed: {response.text}")


def test_query(query_text, top_k=3):
    """Test semantic search."""
    print_section(f"Search Query: '{query_text}'")

    payload = {"query": query_text, "top_k": top_k, "user_id": "default_user"}

    response = requests.post(
        f"{BASE_URL}/api/query",
        json=payload,
        headers={"Content-Type": "application/json"},
    )

    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(
            f"✅ Found {data['total_results']} results in {data['processing_time_ms']:.2f}ms\n"
        )

        for i, result in enumerate(data["results"], 1):
            print(f"Result {i}:")
            print(f"  Document: {result['document_title']}")
            print(f"  Page: {result['page_number']}")
            print(f"  Relevance: {result['relevance_score']:.4f}")
            print(f"  Content preview: {result['content'][:150]}...")
            print()
    else:
        print(f"❌ Query failed: {response.text}")


def test_get_document(document_id):
    """Test getting document details."""
    print_section(f"Get Document Details")
    response = requests.get(f"{BASE_URL}/api/documents/{document_id}")
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Title: {data['title']}")
        print(f"Pages: {data['page_count']}")
        print(f"Size: {data['file_size']} bytes")
        print(f"Created: {data['created_at']}")
    else:
        print(f"❌ Failed: {response.text}")


def main():
    """Run all tests."""
    print("\n" + "🧠" * 30)
    print("Second Brain API - Test Suite")
    print("🧠" * 30)

    # Test 1: Health check
    if not test_health():
        print("\n❌ Server is not running. Start it with: python -m app.main")
        return

    # Test 2: List documents
    test_list_documents()

    # Test 3: Upload (optional - requires PDF file)
    print("\n" + "=" * 60)
    pdf_path = input(
        "\nEnter path to a PDF file to upload (or press Enter to skip): "
    ).strip()

    document_id = None
    if pdf_path:
        document_id = test_upload(pdf_path)

        if document_id:
            # Test 4: Get document details
            test_get_document(document_id)

    # Test 5: Search queries
    print("\n" + "=" * 60)
    print("Now you can test search queries.")
    print("=" * 60)

    queries = []

    use_default = input("\nUse default queries? (y/n): ").strip().lower()

    if use_default == "y":
        for query in queries:
            test_query(query, top_k=3)
    else:
        while True:
            query = input("\nEnter search query (or 'quit' to exit): ").strip()
            if query.lower() in ["quit", "exit", "q"]:
                break
            if query:
                test_query(query, top_k=3)

    print("\n" + "=" * 60)
    print("✅ Test suite completed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Bye!")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
