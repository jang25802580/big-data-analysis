"""Pydantic v2 data models for Cosmos DB records and API request/response contracts."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Cosmos DB document models
# ---------------------------------------------------------------------------

class DocumentRecord(BaseModel):
    """Represents a row in the Cosmos DB 'documents' container."""

    id: str
    type: str = "document"
    file_name: str
    blob_url: str
    status: str = "pending"          # pending | processing | completed | failed
    uploaded_at: str
    processed_at: Optional[str] = None
    size: int = 0
    page_count: int = 0
    chunk_count: int = 0
    progress: int = 0
    description: Optional[str] = None
    error: Optional[str] = None
    partition_key: str = Field(default="default", alias="_partitionKey")

    model_config = {"populate_by_name": True}


class ChunkRecord(BaseModel):
    """Represents a row in the Cosmos DB 'chunks' container (with embedding)."""

    id: str
    type: str = "chunk"
    document_id: str
    chunk_index: int
    text: str
    embedding: list[float]
    page_number: Optional[int] = None
    created_at: str
    partition_key: str = Field(default="default", alias="_partitionKey")

    model_config = {"populate_by_name": True}


class ChatMessage(BaseModel):
    message_id: str
    role: str                        # user | assistant
    content: str
    timestamp: str
    sources: list[dict] = Field(default_factory=list)


class ChatSession(BaseModel):
    """Represents a row in the Cosmos DB 'sessions' container."""

    id: str
    type: str = "session"
    created_at: str
    updated_at: str
    messages: list[ChatMessage] = Field(default_factory=list)
    partition_key: str = Field(default="default", alias="_partitionKey")

    model_config = {"populate_by_name": True}


# ---------------------------------------------------------------------------
# API response models
# ---------------------------------------------------------------------------

class UploadResponse(BaseModel):
    document_id: str
    file_name: str
    status: str
    uploaded_at: str


class StatusResponse(BaseModel):
    document_id: str
    status: str
    progress: int = 0
    chunk_count: int = 0
    error: Optional[str] = None


# ---------------------------------------------------------------------------
# Chat API models
# ---------------------------------------------------------------------------

class ChatQueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    document_ids: Optional[list[str]] = None


class SourceReference(BaseModel):
    document_id: str
    file_name: str
    chunk_id: str
    relevance_score: float
    excerpt: str


class ChatQueryResponse(BaseModel):
    answer: str
    sources: list[SourceReference] = Field(default_factory=list)
    message_id: str
    timestamp: str
