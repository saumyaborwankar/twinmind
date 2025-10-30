# Architecture Documentation

## System Overview

The Second Brain MVP is a PDF processing and semantic search system built on a modular, service-oriented architecture.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Layer                          │
│  (HTTP Clients, curl, Python SDK, Web Browser)              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Application                       │
│                     (app/main.py)                           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      API Routes                              │
│                   (app/api/routes.py)                       │
│  /upload  /query  /documents  /health  /delete             │
└────────────────────────┬────────────────────────────────────┘
                         │
            ┌────────────┼────────────┐
            ▼            ▼            ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   PDF        │ │   Search     │ │  Embedding   │
│  Processor   │ │   Service    │ │   Service    │
│              │ │              │ │              │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       ▼                ▼                ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   Chunker    │ │  Vector DB   │ │  OpenAI API  │
│              │ │  (ChromaDB)  │ │              │
└──────────────┘ └──────────────┘ └──────────────┘
                         │
                         ▼
                 ┌──────────────┐
                 │   SQLite     │
                 │   Database   │
                 └──────────────┘
```

## Component Breakdown

### 1. API Layer (`app/api/`)

**Purpose**: Handle HTTP requests and responses

**Files**:
- `routes.py`: API endpoint definitions

**Endpoints**:
- `POST /api/upload`: Upload PDF files
- `POST /api/query`: Search documents
- `GET /api/documents`: List all documents
- `GET /api/documents/{id}`: Get document details
- `DELETE /api/documents/{id}`: Delete document
- `GET /api/health`: Health check

### 2. Service Layer (`app/services/`)

**Purpose**: Business logic and processing

#### PDF Processor (`pdf_processor.py`)
- File validation
- Text extraction with pdfplumber
- Metadata extraction
- Hash calculation for deduplication

#### Text Chunker (`chunker.py`)
- Semantic text splitting
- Token counting with tiktoken
- Chunk overlap management
- Metadata preservation

#### Embedding Service (`embedder.py`)
- OpenAI API integration
- Batch embedding generation
- Error handling and retries

#### Search Service (`search.py`)
- Vector similarity search
- Result ranking
- Context retrieval from database

### 3. Database Layer (`app/database/`)

**Purpose**: Data persistence and retrieval

#### SQLAlchemy Models (`models.py`)
```python
Document
├── id (UUID)
├── title (String)
├── file_path (Text)
├── page_count (Integer)
├── content_hash (String)
├── metadata (JSON)
└── chunks (Relationship) →

ContentChunk
├── id (UUID)
├── document_id (FK)
├── chunk_index (Integer)
├── content (Text)
├── page_number (Integer)
├── embedding_id (String)
└── metadata (JSON)
```

#### Vector Store (`vector_store.py`)
- ChromaDB wrapper
- Embedding storage and retrieval
- Cosine similarity search
- Metadata filtering

### 4. Data Models (`app/models/`)

**Purpose**: Request/response validation

**Files**:
- `schemas.py`: Pydantic models for API validation

## Data Flow

### Upload Flow

```
1. Client uploads PDF
   │
2. API validates file (size, type)
   │
3. PDFProcessor extracts text by page
   │
4. Chunker splits text into segments
   │
5. Embedder generates vectors (OpenAI API)
   │
6. VectorStore saves embeddings (ChromaDB)
   │
7. Database saves metadata (SQLite)
   │
8. Return document_id to client
```

### Search Flow

```
1. Client submits query text
   │
2. Embedder generates query vector (OpenAI API)
   │
3. VectorStore performs similarity search (ChromaDB)
   │
4. SearchService fetches full context (SQLite)
   │
5. Results ranked by relevance
   │
6. Return top-k results to client
```

## Database Schema

### SQLite Tables

```sql
documents
├── id (PRIMARY KEY)
├── user_id
├── title
├── file_path
├── file_size
├── page_count
├── content_hash (UNIQUE)
├── created_at
└── metadata (JSON)

content_chunks
├── id (PRIMARY KEY)
├── document_id (FOREIGN KEY)
├── chunk_index
├── content
├── page_number
├── embedding_id
├── created_at
└── metadata (JSON)
```

### ChromaDB Collection

```
Collection: "second_brain_embeddings"
├── Embeddings: [3072-dimensional vectors]
├── Documents: [Original text chunks]
├── Metadata:
│   ├── document_id
│   ├── user_id
│   ├── chunk_index
│   ├── page_number
│   └── title
└── IDs: [Unique chunk identifiers]
```

## Configuration Management

**File**: `app/config.py`

Uses Pydantic Settings for environment-based configuration:
- OpenAI API credentials
- File size limits
- Chunk parameters
- Database paths
- API server settings

## Key Design Decisions

### 1. Why ChromaDB?
- Built-in HNSW index for fast similarity search
- Simple Python API
- Local persistence (no external services)
- Good for MVP scale (<100k documents)

### 2. Why SQLite?
- Zero configuration
- Perfect for MVP
- ACID compliance
- Easy migration to PostgreSQL later

### 3. Why Separate Vector and SQL Databases?
- Vector DB optimized for similarity search
- SQL DB better for structured queries
- Allows independent scaling
- Clear separation of concerns

### 4. Why Service Layer Pattern?
- Testability: Each service can be tested independently
- Reusability: Services can be used by multiple endpoints
- Maintainability: Clear responsibility boundaries
- Scalability: Easy to extract into microservices later

## Scalability Considerations

### Current Limitations (MVP)
- Single server deployment
- Local file storage
- No caching layer
- Synchronous processing

### Future Enhancements
1. **Horizontal Scaling**:
   - Move to PostgreSQL with read replicas
   - Use Pinecone/Weaviate for distributed vector search
   - Add Redis for caching

2. **Async Processing**:
   - Celery/RQ for background jobs
   - Webhook notifications for completion
   - Batch processing for multiple uploads

3. **Storage Optimization**:
   - S3/MinIO for file storage
   - CDN for frequently accessed content
   - Compression for large documents

4. **Performance**:
   - Query result caching
   - Embedding caching
   - Connection pooling
   - Load balancing

## Security Considerations

### Current Implementation
- File type validation
- File size limits
- Content hash verification

### Production Requirements
- User authentication (JWT)
- Rate limiting
- Input sanitization
- API key rotation
- Encryption at rest
- HTTPS only
- CORS configuration

## Monitoring & Observability

### Recommended Additions
1. **Logging**: Structured logging with timestamps
2. **Metrics**: Request latency, error rates, upload sizes
3. **Tracing**: OpenTelemetry for request tracing
4. **Health Checks**: Database connectivity, API availability
5. **Alerting**: Error rate thresholds, disk space

## Testing Strategy

### Unit Tests
- Service layer logic
- Data validation
- Utility functions

### Integration Tests
- API endpoint tests
- Database operations
- External API mocking

### End-to-End Tests
- Full upload-to-search workflow
- Error handling scenarios
- Performance benchmarks

## Deployment

### Development
```bash
python -m app.main
```

### Production (Recommended)
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Docker (Future)
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Cost Analysis

### OpenAI Embeddings
- Model: text-embedding-3-large
- Cost: $0.13 per 1M tokens
- Average document: ~5,000 tokens
- 100 documents: ~$0.065

### Storage
- SQLite: Free (local disk)
- ChromaDB: Free (local disk)
- 100 PDFs: ~500MB

### Compute
- Development: Local (free)
- Production: ~$10-20/month (small VM)

**Total MVP Cost**: < $1/month for 100 documents

## Migration Path

### SQLite → PostgreSQL
1. Export data with `sqlite3 .dump`
2. Convert to PostgreSQL format
3. Update `DATABASE_URL` in config
4. Test thoroughly

### Local ChromaDB → Cloud Vector DB
1. Export embeddings from ChromaDB
2. Batch upload to Pinecone/Weaviate
3. Update vector store implementation
4. Verify search results match

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [ChromaDB Docs](https://docs.trychroma.com/)
- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
