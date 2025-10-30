# Second Brain - MVP (PDF Processing)

A personal knowledge management system that ingests PDF documents and provides intelligent semantic search capabilities using AI embeddings.

## Features

- PDF upload and processing
- Automatic text extraction with page tracking
- Semantic chunking with overlap
- OpenAI embeddings (text-embedding-3-large)
- Vector similarity search using ChromaDB
- RESTful API with FastAPI
- Duplicate detection via content hashing

## Architecture

```
[PDF Upload] → [Text Extraction] → [Chunking] → [Embedding] → [Vector DB + SQLite]
                                                                        ↓
[User Query] → [Query Processing] → [Semantic Search] → [Results]
```

## Tech Stack

- **Backend**: FastAPI
- **PDF Processing**: PyPDF2, pdfplumber
- **Embeddings**: OpenAI API
- **Vector DB**: ChromaDB
- **Primary DB**: SQLite
- **Text Processing**: LangChain

## Installation

### Prerequisites

- Python 3.10+
- OpenAI API key

### Setup

1. Clone the repository:
```bash
cd twinmind
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

## Configuration

Edit the `.env` file:

```env
OPENAI_API_KEY=your_api_key_here
MAX_FILE_SIZE_MB=50
CHUNK_SIZE=500
CHUNK_OVERLAP=50
EMBEDDING_MODEL=text-embedding-3-large
```

## Usage

### Start the API Server

```bash
python -m app.main
```

The API will be available at `http://localhost:8000`

### API Documentation

Interactive API docs: `http://localhost:8000/docs`

### API Endpoints

#### Upload PDF
```bash
POST /api/upload
Content-Type: multipart/form-data

# Example with curl:
curl -X POST "http://localhost:8000/api/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/document.pdf"
```

#### Search Documents
```bash
POST /api/query
Content-Type: application/json

{
  "query": "your search query here",
  "top_k": 5,
  "user_id": "default_user"
}

# Example with curl:
curl -X POST "http://localhost:8000/api/query" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning", "top_k": 5}'
```

#### List Documents
```bash
GET /api/documents?skip=0&limit=100
```

#### Get Document Details
```bash
GET /api/documents/{document_id}
```

#### Delete Document
```bash
DELETE /api/documents/{document_id}
```

#### Health Check
```bash
GET /api/health
```

## Project Structure

```
twinmind/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── config.py              # Configuration
│   ├── models/
│   │   └── schemas.py         # Pydantic models
│   ├── services/
│   │   ├── pdf_processor.py  # PDF extraction
│   │   ├── chunker.py         # Text chunking
│   │   ├── embedder.py        # Embedding generation
│   │   └── search.py          # Search service
│   ├── database/
│   │   ├── models.py          # SQLAlchemy models
│   │   ├── connection.py      # DB connection
│   │   └── vector_store.py    # ChromaDB wrapper
│   └── api/
│       └── routes.py          # API endpoints
├── data/
│   ├── uploads/               # Uploaded PDFs
│   ├── chroma_db/            # Vector database
│   └── sqlite.db             # SQLite database
├── tests/
├── requirements.txt
└── README.md
```

## How It Works

### 1. PDF Upload Flow

1. User uploads PDF via `/api/upload`
2. System validates file (type, size, readability)
3. Content hash calculated for duplicate detection
4. Text extracted page-by-page using pdfplumber
5. Text split into semantic chunks (500 tokens, 50 overlap)
6. Embeddings generated for each chunk via OpenAI API
7. Embeddings stored in ChromaDB
8. Metadata stored in SQLite
9. Document ID returned to user

### 2. Search Flow

1. User submits query via `/api/query`
2. Query converted to embedding via OpenAI API
3. Vector similarity search in ChromaDB
4. Top K most similar chunks retrieved
5. Full context fetched from SQLite
6. Results ranked and returned with metadata

## Cost Estimation

**OpenAI Embeddings** (~$0.13 per 1M tokens):
- 100 PDFs × 10 pages × 500 tokens/page = 500K tokens
- Cost: ~$0.065

**Storage**: Local (free)

**Total MVP**: < $1 for 100 documents

## Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black app/
```

## Troubleshooting

### Common Issues

1. **"ModuleNotFoundError"**: Ensure virtual environment is activated
2. **"OpenAI API Error"**: Check your API key in `.env`
3. **"PDF Processing Error"**: Verify PDF is not encrypted or corrupted
4. **"Database Lock Error"**: Close other connections to SQLite

## Future Enhancements

- Multi-user authentication
- Image and table extraction from PDFs
- Temporal/date-based queries
- Advanced re-ranking algorithms
- Web scraping support
- Audio transcription
- Graph-based relationships
- PostgreSQL migration for production

## License

MIT

## Support

For issues and questions, please open an issue on GitHub.
