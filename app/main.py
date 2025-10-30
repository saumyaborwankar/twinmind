from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.api.routes import router
from app.api.rag_routes import router as rag_router
from app.database.connection import init_db
from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info("Starting Second Brain API...")
    init_db()
    logger.info("Database initialized")
    yield
    # Shutdown
    logger.info("Shutting down Second Brain API...")


# Create FastAPI application
app = FastAPI(
    title="Second Brain API",
    description="AI-powered personal knowledge management system with PDF ingestion, semantic search, and RAG-based Q&A",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api", tags=["Documents & Search"])
app.include_router(rag_router, prefix="/api/rag", tags=["RAG & Q&A"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Second Brain API with RAG",
        "version": "2.0.0",
        "features": [
            "PDF Upload & Processing",
            "Semantic Search",
            "RAG-based Q&A",
            "Document Summarization",
            "Conversation History"
        ],
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
