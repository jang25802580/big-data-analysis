"""Factory function for the Gemini LLM client via langchain-google-genai."""

from __future__ import annotations

from langchain_google_genai import ChatGoogleGenerativeAI

from shared.config import get_config


def get_llm(temperature: float = 0.2) -> ChatGoogleGenerativeAI:
    """Return a configured :class:`ChatGoogleGenerativeAI` instance.

    The model name and API key are read from :func:`shared.config.get_config`
    so they can be overridden via environment variables without code changes.

    Args:
        temperature: Sampling temperature (0.0–1.0). Defaults to 0.2 for RAG.

    Returns:
        Ready-to-use ``ChatGoogleGenerativeAI`` client.
    """
    config = get_config()
    return ChatGoogleGenerativeAI(
        model=config.LLM_MODEL,
        google_api_key=config.GOOGLE_API_KEY,
        temperature=temperature,
    )
