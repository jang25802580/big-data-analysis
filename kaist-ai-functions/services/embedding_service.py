"""Google Gemini text embedding service via langchain-google-genai."""

from __future__ import annotations

import logging

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from tenacity import retry, stop_after_attempt, wait_exponential

from shared.config import get_config
from shared.exceptions import EmbeddingError

logger = logging.getLogger(__name__)

_EMBEDDING_MODEL = "models/text-embedding-004"


class EmbeddingService:
    """Wraps GoogleGenerativeAIEmbeddings for batch text embedding."""

    def __init__(self) -> None:
        config = get_config()
        self._embeddings = GoogleGenerativeAIEmbeddings(
            model=_EMBEDDING_MODEL,
            google_api_key=config.GOOGLE_API_KEY,
        )

    def ping(self) -> None:
        """Verify Gemini embedding API is reachable by embedding a short probe string."""
        try:
            self._embeddings.embed_query("ping")
        except Exception as exc:
            raise EmbeddingError(f"Gemini embedding ping failed: {exc}") from exc

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=20),
        reraise=True,
    )
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of *texts* and return their float vectors.

        Args:
            texts: Non-empty list of strings to embed.

        Returns:
            List of float vectors, one per input text.
        """
        if not texts:
            return []
        try:
            vectors = self._embeddings.embed_documents(texts)
            logger.info("Embedded %d texts with model %s", len(texts), _EMBEDDING_MODEL)
            return vectors
        except Exception as exc:
            raise EmbeddingError(f"Embedding failed for {len(texts)} texts: {exc}") from exc
