from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """Application configuration settings."""

    # OpenAI
    openai_api_key: str
    embedding_model: str = "text-embedding-3-large"

    # LLM Settings
    llm_model: str = "gpt-4-turbo-preview"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 1500

    # Application
    max_file_size_mb: int = 50
    chunk_size: int = 500
    chunk_overlap: int = 50

    # Database
    database_url: str = "sqlite:///./data/sqlite.db"
    vector_db_path: str = "./data/chroma_db"

    # Storage
    upload_dir: str = "./data/uploads"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def max_file_size_bytes(self) -> int:
        """Convert MB to bytes."""
        return self.max_file_size_mb * 1024 * 1024

    def ensure_directories(self):
        """Create necessary directories if they don't exist."""
        Path(self.upload_dir).mkdir(parents=True, exist_ok=True)
        Path(self.vector_db_path).mkdir(parents=True, exist_ok=True)
        Path("data").mkdir(exist_ok=True)


settings = Settings()
settings.ensure_directories()
