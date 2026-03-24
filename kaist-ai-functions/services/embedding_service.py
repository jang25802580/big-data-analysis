"""Google Gemini text embedding service via langchain-google-genai."""

from __future__ import annotations

import logging

from tenacity import retry, stop_after_attempt, wait_exponential

from shared.embeddings import get_embeddings
from shared.exceptions import EmbeddingError

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Wraps GoogleGenerativeAIEmbeddings for batch text embedding."""

    def __init__(self) -> None:
        self._embeddings = get_embeddings()

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
            logger.info("Embedded %d texts", len(texts))
            return vectors
        except Exception as exc:
            raise EmbeddingError(f"Embedding failed for {len(texts)} texts: {exc}") from exc
