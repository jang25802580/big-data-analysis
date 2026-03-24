"""Factory function for the Gemini embeddings client via langchain-google-genai."""

from __future__ import annotations

from langchain_google_genai import GoogleGenerativeAIEmbeddings

from shared.config import get_config


def get_embeddings() -> GoogleGenerativeAIEmbeddings:
    """Return a configured :class:`GoogleGenerativeAIEmbeddings` instance.

    The model name and API key are read from :func:`shared.config.get_config`
    so they can be overridden via environment variables without code changes.

    Returns:
        Ready-to-use ``GoogleGenerativeAIEmbeddings`` client.
    """
    config = get_config()
    return GoogleGenerativeAIEmbeddings(
        model=config.EMBEDDING_MODEL,
        google_api_key=config.GOOGLE_API_KEY,
    )
