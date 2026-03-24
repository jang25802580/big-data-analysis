"""Azure Cosmos DB repository — documents, chunks, and chat sessions."""

from __future__ import annotations

import logging
from typing import Any, Optional

from azure.cosmos import CosmosClient, PartitionKey, exceptions
from azure.identity import DefaultAzureCredential
from tenacity import retry, stop_after_attempt, wait_exponential

from shared.config import get_config

logger = logging.getLogger(__name__)

_PARTITION_KEY = "/partition_key"
_DEFAULT_PARTITION = "default"


class CosmosRepository:
    """Repository pattern wrapper for Cosmos DB NoSQL API.

    Container layout (all in database *knowledgebase*):
      - documents  : DocumentRecord items
      - chunks     : ChunkRecord items (with embedding vectors)
      - sessions   : ChatSession items
    """

    def __init__(self) -> None:
        config = get_config()
        self._client = CosmosClient(
            url=config.COSMOS_ENDPOINT,
            credential=DefaultAzureCredential(),
        )
        self._db = self._client.get_database_client(config.COSMOS_DATABASE_NAME)
        self._documents = self._db.get_container_client("documents")
        self._chunks = self._db.get_container_client("chunks")
        self._sessions = self._db.get_container_client("sessions")

    def ping(self) -> None:
        """Raise if Cosmos DB is unreachable."""
        try:
            self._db.read()
        except Exception as exc:
            raise RuntimeError(f"Cosmos DB ping failed: {exc}") from exc

    # ------------------------------------------------------------------
    # Documents
    # ------------------------------------------------------------------

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8), reraise=True)
    def upsert_document(self, item: dict[str, Any]) -> None:
        item.setdefault("_partitionKey", _DEFAULT_PARTITION)
        self._documents.upsert_item(item)
        logger.debug("Upserted document id=%s", item.get("id"))

    def get_document(self, document_id: str) -> Optional[dict[str, Any]]:
        try:
            return self._documents.read_item(
                item=document_id, partition_key=_DEFAULT_PARTITION
            )
        except exceptions.CosmosResourceNotFoundError:
            return None

    def update_document_status(
        self,
        document_id: str,
        status: str,
        *,
        progress: int = 0,
        chunk_count: int = 0,
        error: Optional[str] = None,
    ) -> None:
        doc = self.get_document(document_id)
        if doc is None:
            logger.warning("update_document_status: document %s not found", document_id)
            return
        doc.update({"status": status, "progress": progress})
        if chunk_count:
            doc["chunk_count"] = chunk_count
        if error is not None:
            doc["error"] = error
        self.upsert_document(doc)

    # ------------------------------------------------------------------
    # Chunks
    # ------------------------------------------------------------------

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8), reraise=True)
    def upsert_chunk(self, item: dict[str, Any]) -> None:
        item.setdefault("_partitionKey", _DEFAULT_PARTITION)
        self._chunks.upsert_item(item)

    def get_chunks_by_document(self, document_id: str) -> list[dict[str, Any]]:
        query = "SELECT * FROM c WHERE c.document_id = @docId"
        params: list[dict[str, Any]] = [{"name": "@docId", "value": document_id}]
        return list(
            self._chunks.query_items(
                query=query,
                parameters=params,
                enable_cross_partition_query=True,
            )
        )

    def vector_search_chunks(
        self,
        query_embedding: list[float],
        document_ids: Optional[list[str]] = None,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """Return the top-k chunks by cosine similarity to *query_embedding*.

        Falls back to a full chunk scan and Python-side ranking when the
        container does not have a vector index policy configured.
        """
        all_chunks = list(
            self._chunks.query_items(
                query="SELECT * FROM c",
                enable_cross_partition_query=True,
            )
        )

        if document_ids:
            all_chunks = [c for c in all_chunks if c.get("document_id") in document_ids]

        def cosine_similarity(a: list[float], b: list[float]) -> float:
            import math

            dot = sum(x * y for x, y in zip(a, b))
            norm_a = math.sqrt(sum(x * x for x in a))
            norm_b = math.sqrt(sum(y * y for y in b))
            if norm_a == 0 or norm_b == 0:
                return 0.0
            return dot / (norm_a * norm_b)

        scored = [
            {**c, "score": cosine_similarity(query_embedding, c.get("embedding", []))}
            for c in all_chunks
            if c.get("embedding")
        ]
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

    # ------------------------------------------------------------------
    # Sessions
    # ------------------------------------------------------------------

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8), reraise=True)
    def upsert_session(self, item: dict[str, Any]) -> None:
        item.setdefault("_partitionKey", _DEFAULT_PARTITION)
        self._sessions.upsert_item(item)

    def get_session(self, session_id: str) -> Optional[dict[str, Any]]:
        try:
            return self._sessions.read_item(
                item=session_id, partition_key=_DEFAULT_PARTITION
            )
        except exceptions.CosmosResourceNotFoundError:
            return None
