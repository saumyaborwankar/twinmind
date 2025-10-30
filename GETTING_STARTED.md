# Getting Started with Second Brain

Welcome! This guide will get you up and running with your Second Brain AI companion in just a few minutes.

## What You've Built

A complete PDF processing and semantic search system that:
- 📄 Ingests PDF documents
- ✂️ Intelligently chunks text
- 🧠 Generates AI embeddings
- 🔍 Provides semantic search
- 🚀 Offers a REST API

## Prerequisites

- Python 3.10 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- 500MB free disk space

## Installation (5 minutes)

### Option 1: Automated Setup (Recommended)

```bash
# Run the setup script
./setup.sh

# Edit .env and add your OpenAI API key
nano .env  # or use your preferred editor

# Activate virtual environment
source venv/bin/activate

# Start the server
python -m app.main
```

### Option 2: Manual Setup

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file
cp .env.example .env

# 4. Edit .env and add your OPENAI_API_KEY
echo "OPENAI_API_KEY=sk-your-key-here" >> .env

# 5. Create data directories
mkdir -p data/uploads data/chroma_db

# 6. Start the server
python -m app.main
```

## Verification

If everything is working, you should see:

```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Second Brain API initialized
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Visit http://localhost:8000/docs to see the API documentation.

## Your First Upload

### Using the Test Script

```bash
# In a new terminal
cd twinmind
source venv/bin/activate
python test_api.py
```

Follow the prompts to upload a PDF and search it.

### Using curl

```bash
# Upload a PDF
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@/path/to/your/document.pdf"

# Search
curl -X POST "http://localhost:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "your search here", "top_k": 5}'
```

### Using Python

```python
from example_usage import SecondBrainClient

# Initialize client
client = SecondBrainClient()

# Upload a PDF
result = client.upload_pdf("my_document.pdf")
print(f"✅ Uploaded: {result['title']}")
print(f"📄 Pages: {result['page_count']}")
print(f"🧩 Chunks: {result['chunks_created']}")

# Search
results = client.search("machine learning", top_k=5)
print(f"\n🔍 Found {results['total_results']} results:")

for i, result in enumerate(results['results'], 1):
    print(f"\n{i}. {result['document_title']} (page {result['page_number']})")
    print(f"   Score: {result['relevance_score']:.4f}")
    print(f"   {result['content'][:100]}...")
```

## Understanding the System

### What Happens When You Upload

1. **Validation**: File is checked for type and size
2. **Extraction**: Text is extracted page-by-page
3. **Chunking**: Text is split into 500-token segments
4. **Embedding**: Each chunk gets a 3072-dimensional vector
5. **Storage**: Vectors go to ChromaDB, metadata to SQLite
6. **Ready**: Your document is now searchable!

### What Happens When You Search

1. **Embedding**: Your query becomes a vector
2. **Search**: System finds similar vectors (cosine similarity)
3. **Retrieval**: Full text is fetched from database
4. **Ranking**: Results sorted by relevance
5. **Return**: Top matches sent back to you

## API Endpoints Quick Reference

| Endpoint | Method | Purpose | Example |
|----------|--------|---------|---------|
| `/api/upload` | POST | Upload PDF | `curl -F "file=@doc.pdf" ...` |
| `/api/query` | POST | Search | `{"query": "ML", "top_k": 5}` |
| `/api/documents` | GET | List all | `curl http://localhost:8000/api/documents` |
| `/api/documents/{id}` | GET | Get one | `curl http://localhost:8000/api/documents/abc123` |
| `/api/documents/{id}` | DELETE | Delete | `curl -X DELETE http://localhost:8000/api/documents/abc123` |
| `/api/health` | GET | Status | `curl http://localhost:8000/api/health` |

## File Organization

```
twinmind/
├── 📘 Documentation
│   ├── README.md              ← Full documentation
│   ├── QUICKSTART.md         ← Quick start guide
│   ├── ARCHITECTURE.md       ← Technical details
│   ├── PROJECT_SUMMARY.md    ← What's been built
│   └── GETTING_STARTED.md    ← This file
│
├── 🐍 Python Code
│   ├── app/
│   │   ├── main.py           ← FastAPI app
│   │   ├── config.py         ← Settings
│   │   ├── api/routes.py     ← Endpoints
│   │   ├── services/         ← Business logic
│   │   ├── database/         ← Data layer
│   │   └── models/           ← Schemas
│   │
│   ├── test_api.py           ← Test suite
│   └── example_usage.py      ← Usage examples
│
├── ⚙️ Configuration
│   ├── requirements.txt      ← Dependencies
│   ├── .env.example          ← Config template
│   ├── .gitignore           ← Git ignores
│   ├── setup.sh             ← Setup script
│   └── Makefile             ← Commands
│
└── 💾 Data (created on first run)
    └── data/
        ├── uploads/          ← PDF files
        ├── chroma_db/       ← Vector DB
        └── sqlite.db        ← Metadata
```

## Common Tasks

### Start the Server
```bash
source venv/bin/activate
python -m app.main
```

### Run Tests
```bash
python test_api.py
```

### Check Health
```bash
curl http://localhost:8000/api/health
```

### View Logs
Watch the terminal where you started the server.

### Stop the Server
Press `Ctrl+C` in the terminal running the server.

## Troubleshooting

### Problem: "ModuleNotFoundError"
**Solution**: Activate virtual environment
```bash
source venv/bin/activate
```

### Problem: "OpenAI API Error"
**Solution**: Check your API key
```bash
# Verify .env file has your key
cat .env | grep OPENAI_API_KEY

# Test key validity
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Problem: "Connection refused"
**Solution**: Start the server
```bash
python -m app.main
```

### Problem: "Port already in use"
**Solution**: Change port in .env
```bash
echo "API_PORT=8001" >> .env
```

### Problem: "PDF processing failed"
**Possible causes**:
- PDF is encrypted (not supported yet)
- PDF is scanned image (OCR not implemented yet)
- File is corrupted

**Solution**: Try a different PDF or decrypt it first.

## Understanding the Results

### Search Response Format

```json
{
  "query": "machine learning",
  "results": [
    {
      "chunk_id": "abc123",
      "document_id": "def456",
      "document_title": "ML Guide.pdf",
      "content": "Machine learning is...",
      "page_number": 5,
      "relevance_score": 0.8765,
      "metadata": {
        "chunk_index": 12,
        "char_count": 487
      }
    }
  ],
  "total_results": 5,
  "processing_time_ms": 123.45
}
```

### Relevance Score
- Range: 0.0 to 1.0
- Higher is more relevant
- >0.8: Highly relevant
- 0.6-0.8: Relevant
- <0.6: Somewhat relevant

## Best Practices

### Uploading Documents
- ✅ Use text-based PDFs (not scanned images)
- ✅ Keep files under 50MB
- ✅ Use descriptive filenames
- ❌ Don't upload encrypted PDFs
- ❌ Don't upload duplicate files

### Searching
- ✅ Use natural language queries
- ✅ Be specific about what you want
- ✅ Try different phrasings
- ✅ Use context in your query
- ❌ Don't use single words (too broad)
- ❌ Don't use exact text matching (that's keyword search)

### Examples of Good Queries
- "What are the main findings about climate change?"
- "How does the authentication system work?"
- "Explain the methodology used in the study"
- "What are the recommendations for improving performance?"

## Next Steps

1. **Build Your Knowledge Base**
   - Upload 10-20 documents
   - Try different types of content
   - See what works best

2. **Experiment with Search**
   - Try various query types
   - Note what works well
   - Iterate on your approach

3. **Integrate into Your Workflow**
   - Use the Python client in your scripts
   - Create shortcuts for common queries
   - Build custom interfaces

4. **Extend the System**
   - Add new features (see [ARCHITECTURE.md](ARCHITECTURE.md))
   - Customize for your use case
   - Deploy to production

## Learning Resources

### Documentation
- [README.md](README.md) - Complete documentation
- [ARCHITECTURE.md](ARCHITECTURE.md) - System design
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - What's included

### Interactive Learning
- API Docs: http://localhost:8000/docs
- Test Script: `python test_api.py`
- Example Code: [example_usage.py](example_usage.py)

### External Resources
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
- [ChromaDB Documentation](https://docs.trychroma.com/)

## Getting Help

### Self-Service
1. Check this guide
2. Read the error message carefully
3. Check [README.md](README.md) for details
4. Review [ARCHITECTURE.md](ARCHITECTURE.md) for technical info

### Debug Mode
Enable verbose logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Tips for Success

1. **Start Simple**: Upload 1-2 PDFs and test thoroughly
2. **Iterate**: Try different query styles and learn what works
3. **Monitor Costs**: Check OpenAI usage dashboard regularly
4. **Back Up Data**: Copy `data/` directory periodically
5. **Read Logs**: The terminal shows helpful debug information

## What's Next?

Now that you're up and running:

1. ✅ Upload your first PDF
2. ✅ Try some searches
3. ✅ Check the API docs
4. ✅ Run the test suite
5. ✅ Read the architecture docs
6. ✅ Plan your enhancements

**You're ready to build your Second Brain! 🧠✨**

For detailed information, see:
- Technical details: [ARCHITECTURE.md](ARCHITECTURE.md)
- Full documentation: [README.md](README.md)
- Quick reference: [QUICKSTART.md](QUICKSTART.md)
