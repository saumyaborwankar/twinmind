#!/usr/bin/env python3
"""
Quick script to delete and re-upload a document to fix missing embeddings.
"""

import requests
import sys

BASE_URL = "http://localhost:8000"

def delete_document(doc_id):
    """Delete a document."""
    print(f"🗑️  Deleting document {doc_id}...")
    response = requests.delete(f"{BASE_URL}/api/documents/{doc_id}")

    if response.status_code == 204:
        print("✅ Document deleted successfully")
        return True
    else:
        print(f"❌ Error deleting: {response.status_code}")
        print(response.text)
        return False

def upload_document(file_path):
    """Upload a document."""
    print(f"📤 Uploading {file_path}...")

    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{BASE_URL}/api/upload", files=files)

    if response.status_code == 201:
        data = response.json()
        print("✅ Upload successful!")
        print(f"   Document ID: {data['document_id']}")
        print(f"   Title: {data['title']}")
        print(f"   Chunks created: {data['chunks_created']}")
        return True
    else:
        print(f"❌ Error uploading: {response.status_code}")
        print(response.text)
        return False

def check_health():
    """Check system health."""
    response = requests.get(f"{BASE_URL}/api/health")
    if response.status_code == 200:
        data = response.json()
        print(f"\n📊 System Status:")
        print(f"   Vector DB chunks: {data['vector_db_count']}")
        print(f"   Documents: {data['database_documents']}")
        return data
    return None

def main():
    print("\n" + "="*60)
    print("  Document Fix Utility")
    print("="*60 + "\n")

    # Check initial state
    print("Checking current state...")
    health = check_health()

    if health and health['vector_db_count'] == 0 and health['database_documents'] > 0:
        print("\n⚠️  Issue detected: Documents exist but no embeddings!")
        print("   This means documents were uploaded before RAG was added.\n")

    # Get document to fix
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        doc_id = sys.argv[2] if len(sys.argv) > 2 else None
    else:
        # List documents
        response = requests.get(f"{BASE_URL}/api/documents")
        if response.status_code == 200:
            docs = response.json()['documents']
            if docs:
                print("\nExisting documents:")
                for i, doc in enumerate(docs, 1):
                    print(f"  {i}. {doc['title']} (ID: {doc['id'][:8]}...)")

                choice = input("\nWhich document to fix? (number or 'all'): ").strip()

                if choice.lower() == 'all':
                    print("\n" + "="*60)
                    print("  Fixing All Documents")
                    print("="*60)

                    for doc in docs:
                        print(f"\nProcessing: {doc['title']}")
                        delete_document(doc['id'])

                    print("\nAll documents deleted. Now re-upload your PDFs:")
                    print("  python test_api.py")
                    return

                try:
                    idx = int(choice) - 1
                    doc = docs[idx]
                    doc_id = doc['id']
                    print(f"\nSelected: {doc['title']}")
                except (ValueError, IndexError):
                    print("❌ Invalid selection")
                    return
            else:
                print("No documents found.")
                return

        file_path = input("\nEnter path to PDF file to re-upload: ").strip()

    if not file_path:
        print("No file path provided.")
        return

    print("\n" + "="*60)
    print("  Starting Fix Process")
    print("="*60 + "\n")

    # Delete if doc_id provided
    if 'doc_id' in locals() and doc_id:
        if not delete_document(doc_id):
            return
        print()

    # Upload new version
    if upload_document(file_path):
        print()
        check_health()
        print("\n✅ Fix complete! Try your query again:")
        print('   curl -X POST "http://localhost:8000/api/rag/ask" \\')
        print('     -H "Content-Type: application/json" \\')
        print('     -d \'{"question": "your question here"}\'')

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Aborted")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
