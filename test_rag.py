#!/usr/bin/env python3
"""
Test script for RAG (Retrieval-Augmented Generation) functionality.
Run this after starting the server to test Q&A capabilities.
"""

import requests
import json
import sys
from pathlib import Path

BASE_URL = "http://localhost:8000"


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_simple_question(question: str):
    """Test a simple question without conversation history."""
    print_section(f"Question: {question}")

    payload = {
        "question": question,
        "top_k": 5,
        "include_sources": True
    }

    response = requests.post(
        f"{BASE_URL}/api/rag/ask",
        json=payload,
        headers={"Content-Type": "application/json"}
    )

    if response.status_code == 200:
        data = response.json()
        print(f"\n📝 Answer:\n{data['answer']}\n")
        print(f"🔍 Confidence: {data['confidence']}")
        print(f"📊 Context used: {data['context_used']} chunks")
        print(f"💬 Model: {data['model']}")
        print(f"🔢 Tokens: {data['usage']['total_tokens']}")

        if data['sources']:
            print(f"\n📚 Sources ({len(data['sources'])}):")
            for i, source in enumerate(data['sources'], 1):
                print(f"\n  {i}. {source['document_title']} (Page {source['page_number']})")
                print(f"     Relevance: {source['relevance_score']:.4f}")
                print(f"     Preview: {source['content_preview'][:100]}...")
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"   {response.text}")


def test_conversation():
    """Test conversation with history."""
    print_section("Conversation Test")

    conversation_history = []
    questions = [
        "What are the main topics in my documents?",
        "Can you elaborate on the first topic?",
        "What are the key takeaways?"
    ]

    for i, question in enumerate(questions, 1):
        print(f"\n💭 Turn {i}: {question}")

        payload = {
            "question": question,
            "conversation_history": conversation_history,
            "top_k": 5
        }

        response = requests.post(
            f"{BASE_URL}/api/rag/conversation",
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            data = response.json()
            answer = data['answer']
            print(f"\n🤖 Answer: {answer[:200]}...")

            # Add to conversation history
            conversation_history.append({"role": "user", "content": question})
            conversation_history.append({"role": "assistant", "content": answer})
        else:
            print(f"❌ Error: {response.status_code}")
            break


def test_streaming_question(question: str):
    """Test streaming response."""
    print_section(f"Streaming Question: {question}")

    payload = {
        "question": question,
        "top_k": 5
    }

    print("\n🌊 Streaming answer:\n")

    response = requests.post(
        f"{BASE_URL}/api/rag/ask/stream",
        json=payload,
        headers={"Content-Type": "application/json"},
        stream=True
    )

    if response.status_code == 200:
        sources_received = False
        answer_chunks = []

        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    data = json.loads(line_str[6:])

                    if data['type'] == 'sources':
                        if not sources_received:
                            print(f"📚 Retrieved {len(data['data'])} sources\n")
                            sources_received = True

                    elif data['type'] == 'answer':
                        print(data['data'], end='', flush=True)
                        answer_chunks.append(data['data'])

                    elif data['type'] == 'done':
                        print("\n\n✅ Streaming complete")

        print(f"\n📊 Total answer length: {len(''.join(answer_chunks))} characters")
    else:
        print(f"❌ Error: {response.status_code}")


def test_document_summary():
    """Test document summarization."""
    print_section("Document Summary Test")

    # First, get list of documents
    response = requests.get(f"{BASE_URL}/api/documents")

    if response.status_code == 200:
        data = response.json()
        if data['total'] > 0:
            doc = data['documents'][0]
            doc_id = doc['id']
            doc_title = doc['title']

            print(f"\n📄 Summarizing: {doc_title}")

            summary_payload = {"document_id": doc_id}
            summary_response = requests.post(
                f"{BASE_URL}/api/rag/summarize",
                json=summary_payload,
                headers={"Content-Type": "application/json"}
            )

            if summary_response.status_code == 200:
                summary_data = summary_response.json()
                print(f"\n📝 Summary:\n{summary_data['summary']}\n")
                print(f"📊 Pages: {summary_data['page_count']}")
                print(f"🧩 Chunks analyzed: {summary_data['chunks_analyzed']}")
            else:
                print(f"❌ Error getting summary: {summary_response.status_code}")
        else:
            print("⚠️  No documents found. Please upload some documents first.")
    else:
        print(f"❌ Error listing documents: {response.status_code}")


def main():
    """Run all RAG tests."""
    print("\n" + "🧠" * 35)
    print("Second Brain - RAG Testing Suite")
    print("🧠" * 35)

    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code != 200:
            print("\n❌ Server is not responding correctly.")
            print("   Start it with: python -m app.main")
            return
    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to server at {BASE_URL}")
        print("   Start it with: python -m app.main")
        return

    print("\n✅ Server is running!")

    # Check if we have documents
    docs_response = requests.get(f"{BASE_URL}/api/documents")
    if docs_response.status_code == 200:
        doc_count = docs_response.json()['total']
        print(f"📚 Found {doc_count} documents in database")

        if doc_count == 0:
            print("\n⚠️  Warning: No documents found!")
            print("   Upload some PDFs first using: python test_api.py")
            upload = input("\n   Continue anyway? (y/n): ").strip().lower()
            if upload != 'y':
                return

    # Test 1: Simple questions
    print("\n" + "─" * 70)
    print("Test 1: Simple Questions")
    print("─" * 70)

    questions = [
        "What are the main topics discussed in my documents?",
        "Summarize the key findings",
        "What methodologies are mentioned?"
    ]

    use_default = input("\nUse default questions? (y/n): ").strip().lower()

    if use_default == 'y':
        for q in questions:
            test_simple_question(q)
    else:
        while True:
            q = input("\nEnter a question (or 'skip' to continue): ").strip()
            if q.lower() in ['skip', 's', '']:
                break
            test_simple_question(q)

    # Test 2: Streaming
    print("\n" + "─" * 70)
    print("Test 2: Streaming Response")
    print("─" * 70)

    test_streaming = input("\nTest streaming response? (y/n): ").strip().lower()
    if test_streaming == 'y':
        question = input("Enter question: ").strip() or "Explain the main concept in detail"
        test_streaming_question(question)

    # Test 3: Conversation
    print("\n" + "─" * 70)
    print("Test 3: Conversation with History")
    print("─" * 70)

    test_conv = input("\nTest conversation mode? (y/n): ").strip().lower()
    if test_conv == 'y':
        test_conversation()

    # Test 4: Document Summary
    print("\n" + "─" * 70)
    print("Test 4: Document Summary")
    print("─" * 70)

    test_summ = input("\nTest document summarization? (y/n): ").strip().lower()
    if test_summ == 'y':
        test_document_summary()

    print("\n" + "=" * 70)
    print("✅ RAG Testing Complete!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Testing interrupted. Bye!")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
