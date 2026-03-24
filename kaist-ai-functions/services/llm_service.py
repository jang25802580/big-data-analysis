"""Google Gemini LLM service for RAG answer generation via langchain-google-genai."""

from __future__ import annotations

import logging

from langchain_core.prompts import ChatPromptTemplate
from tenacity import retry, stop_after_attempt, wait_exponential

from shared.llm import get_llm

logger = logging.getLogger(__name__)

_RAG_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "You are a helpful assistant that answers questions based strictly on "
                "the provided context. If the answer is not contained in the context, "
                "say 'I could not find the answer in the provided documents.'\n\n"
                "Context:\n{context}"
            ),
        ),
        ("human", "{query}"),
    ]
)


class LLMService:
    """Wraps ChatGoogleGenerativeAI for retrieval-augmented generation."""

    def __init__(self) -> None:
        self._llm = get_llm(temperature=0.2)
        self._chain = _RAG_PROMPT | self._llm

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=20),
        reraise=True,
    )
    def generate_rag_answer(self, query: str, context_chunks: list[str]) -> str:
        """Generate an answer for *query* grounded in *context_chunks*.

        Args:
            query: User's natural language question.
            context_chunks: List of relevant text excerpts retrieved from Cosmos DB.

        Returns:
            LLM-generated answer string.
        """
        context = "\n\n---\n\n".join(context_chunks) if context_chunks else "(no context)"
        try:
            result = self._chain.invoke({"query": query, "context": context})
            answer = result.content if hasattr(result, "content") else str(result)
            logger.info(
                "Generated RAG answer for query='%s...' using %d chunks",
                query[:50],
                len(context_chunks),
            )
            return answer
        except Exception as exc:
            logger.exception("LLM RAG generation failed")
            raise RuntimeError(f"LLM generation failed: {exc}") from exc
