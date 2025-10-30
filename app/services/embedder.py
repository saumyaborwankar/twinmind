from typing import List
from openai import OpenAI
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating text embeddings using OpenAI."""

    def __init__(self):
        """Initialize the embedding service."""
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.embedding_model
        self.embedding_dimensions = 3072  # text-embedding-3-large dimensions

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Input text

        Returns:
            Embedding vector as list of floats
        """
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )
            embedding = response.data[0].embedding
            logger.debug(f"Generated embedding for text of length {len(text)}")
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise

    def generate_embeddings_batch(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batches.

        Args:
            texts: List of input texts
            batch_size: Number of texts to process per batch

        Returns:
            List of embedding vectors
        """
        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]

            try:
                response = self.client.embeddings.create(
                    model=self.model,
                    input=batch
                )
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)

                logger.info(f"Generated embeddings for batch {i // batch_size + 1} "
                           f"({len(batch)} texts)")

            except Exception as e:
                logger.error(f"Error generating batch embeddings: {str(e)}")
                raise

        logger.info(f"Generated {len(all_embeddings)} embeddings total")
        return all_embeddings

    def get_embedding_dimensions(self) -> int:
        """Get the dimension size of embeddings."""
        return self.embedding_dimensions


# Singleton instance
embedding_service = EmbeddingService()
