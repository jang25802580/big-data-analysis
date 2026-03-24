import logging

import azure.functions as func

from shared.config import get_config

logger = logging.getLogger(__name__)

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

# ---------------------------------------------------------------------------
# Health Check
# ---------------------------------------------------------------------------

@app.route(route="health", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def health(req: func.HttpRequest) -> func.HttpResponse:
    """Liveness probe — returns service connectivity status."""
    import json

    checks: dict[str, str] = {}

    # Azure Blob Storage
    try:
        from services.storage_service import BlobStorageService
        BlobStorageService().ping()
        checks["storage"] = "ok"
    except Exception as exc:
        logger.warning("Storage health check failed: %s", exc)
        checks["storage"] = "unavailable"

    # Azure Cosmos DB
    try:
        from services.cosmos_service import CosmosRepository
        CosmosRepository().ping()
        checks["cosmos"] = "ok"
    except Exception as exc:
        logger.warning("Cosmos health check failed: %s", exc)
        checks["cosmos"] = "unavailable"

    # Gemini API
    try:
        from services.embedding_service import EmbeddingService
        EmbeddingService().ping()
        checks["gemini"] = "ok"
    except Exception as exc:
        logger.warning("Gemini health check failed: %s", exc)
        checks["gemini"] = "unavailable"

    overall = "healthy" if all(v == "ok" for v in checks.values()) else "degraded"
    status_code = 200 if overall == "healthy" else 503

    return func.HttpResponse(
        body=json.dumps({"status": overall, "checks": checks}),
        status_code=status_code,
        mimetype="application/json",
    )


# ---------------------------------------------------------------------------
# PDF Upload
# ---------------------------------------------------------------------------

@app.route(route="pdf/upload", methods=["POST"])
def pdf_upload(req: func.HttpRequest) -> func.HttpResponse:
    """Upload a PDF file and enqueue it for processing."""
    import json
    import uuid
    from datetime import datetime, timezone

    from shared.exceptions import InvalidFileTypeError
    from services.storage_service import BlobStorageService
    from services.cosmos_service import CosmosRepository
    from shared.models import DocumentRecord, UploadResponse

    try:
        file = req.files.get("file")
        if file is None:
            return func.HttpResponse(
                json.dumps({"error": "No file provided. Send as multipart/form-data field 'file'."}),
                status_code=400,
                mimetype="application/json",
            )

        content_type = file.content_type or ""
        if "pdf" not in content_type.lower():
            raise InvalidFileTypeError(f"Expected application/pdf, got '{content_type}'")

        file_bytes = file.read()
        if len(file_bytes) > 50 * 1024 * 1024:  # 50 MB
            return func.HttpResponse(
                json.dumps({"error": "File exceeds 50 MB limit."}),
                status_code=413,
                mimetype="application/json",
            )

        document_id = str(uuid.uuid4())
        blob_name = f"{document_id}.pdf"
        original_filename = file.filename or blob_name

        storage = BlobStorageService()
        blob_url = storage.upload_pdf(file_bytes, blob_name)

        record = DocumentRecord(
            id=document_id,
            file_name=original_filename,
            blob_url=blob_url,
            status="pending",
            uploaded_at=datetime.now(timezone.utc).isoformat(),
            size=len(file_bytes),
        )
        CosmosRepository().upsert_document(record.model_dump())

        response = UploadResponse(
            document_id=document_id,
            file_name=original_filename,
            status="pending",
            uploaded_at=record.uploaded_at,
        )
        return func.HttpResponse(
            body=response.model_dump_json(),
            status_code=202,
            mimetype="application/json",
        )

    except InvalidFileTypeError as exc:
        return func.HttpResponse(
            json.dumps({"error": str(exc)}),
            status_code=400,
            mimetype="application/json",
        )
    except Exception as exc:
        logger.exception("Unexpected error during PDF upload")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error."}),
            status_code=500,
            mimetype="application/json",
        )


# ---------------------------------------------------------------------------
# PDF Processing Status
# ---------------------------------------------------------------------------

@app.route(route="pdf/status/{documentId}", methods=["GET"])
def pdf_status(req: func.HttpRequest) -> func.HttpResponse:
    """Return processing status for a given documentId."""
    import json

    from shared.exceptions import DocumentNotFoundError
    from services.cosmos_service import CosmosRepository
    from shared.models import StatusResponse

    document_id = req.route_params.get("documentId", "")

    try:
        repo = CosmosRepository()
        doc = repo.get_document(document_id)
        if doc is None:
            raise DocumentNotFoundError(document_id)

        response = StatusResponse(
            document_id=document_id,
            status=doc.get("status", "unknown"),
            progress=doc.get("progress", 0),
            chunk_count=doc.get("chunk_count", 0),
            error=doc.get("error"),
        )
        return func.HttpResponse(
            body=response.model_dump_json(),
            status_code=200,
            mimetype="application/json",
        )

    except DocumentNotFoundError:
        return func.HttpResponse(
            json.dumps({"error": f"Document '{document_id}' not found."}),
            status_code=404,
            mimetype="application/json",
        )
    except Exception:
        logger.exception("Error fetching document status")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error."}),
            status_code=500,
            mimetype="application/json",
        )


# ---------------------------------------------------------------------------
# PDF Process (internal trigger)
# ---------------------------------------------------------------------------

@app.route(route="pdf/process", methods=["POST"])
def pdf_process(req: func.HttpRequest) -> func.HttpResponse:
    """Extract text, generate embeddings, and store chunks for a document."""
    import json

    from services.cosmos_service import CosmosRepository
    from services.storage_service import BlobStorageService
    from services.pdf_service import PDFService
    from services.embedding_service import EmbeddingService
    from shared.models import ChunkRecord
    import uuid
    from datetime import datetime, timezone

    try:
        body = req.get_json()
        document_id = body.get("documentId")
        if not document_id:
            return func.HttpResponse(
                json.dumps({"error": "Missing 'documentId' in request body."}),
                status_code=400,
                mimetype="application/json",
            )

        blob_name = f"{document_id}.pdf"
        repo = CosmosRepository()
        storage = BlobStorageService()
        pdf_service = PDFService()
        embedding_service = EmbeddingService()

        # Update status → processing
        repo.update_document_status(document_id, "processing", progress=0)

        pdf_bytes = storage.download_pdf(blob_name)
        pages = pdf_service.extract_text(pdf_bytes)
        chunks = pdf_service.chunk_text(pages)

        embeddings = embedding_service.embed_texts(chunks)

        for idx, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
            chunk = ChunkRecord(
                id=str(uuid.uuid4()),
                document_id=document_id,
                chunk_index=idx,
                text=chunk_text,
                embedding=embedding,
                created_at=datetime.now(timezone.utc).isoformat(),
            )
            repo.upsert_chunk(chunk.model_dump())

        repo.update_document_status(
            document_id, "completed", progress=100, chunk_count=len(chunks)
        )

        return func.HttpResponse(
            json.dumps({"documentId": document_id, "chunkCount": len(chunks)}),
            status_code=200,
            mimetype="application/json",
        )

    except Exception:
        logger.exception("Error processing PDF document_id=%s", document_id)
        if document_id:
            try:
                CosmosRepository().update_document_status(
                    document_id, "failed", error="Processing error"
                )
            except Exception:
                pass
        return func.HttpResponse(
            json.dumps({"error": "Internal server error."}),
            status_code=500,
            mimetype="application/json",
        )


# ---------------------------------------------------------------------------
# Chat Query
# ---------------------------------------------------------------------------

@app.route(route="chat/query", methods=["POST"])
def chat_query(req: func.HttpRequest) -> func.HttpResponse:
    """Answer a user query using RAG over stored document chunks."""
    import json
    import uuid
    from datetime import datetime, timezone

    from shared.models import ChatQueryRequest, ChatQueryResponse, SourceReference
    from services.cosmos_service import CosmosRepository
    from services.embedding_service import EmbeddingService
    from services.llm_service import LLMService

    try:
        body = req.get_json()
        query_req = ChatQueryRequest.model_validate(body)

        embedding_service = EmbeddingService()
        repo = CosmosRepository()
        llm_service = LLMService()

        query_embedding = embedding_service.embed_texts([query_req.query])[0]
        top_chunks = repo.vector_search_chunks(
            query_embedding=query_embedding,
            document_ids=query_req.document_ids,
            top_k=5,
        )

        answer = llm_service.generate_rag_answer(
            query=query_req.query,
            context_chunks=[c["text"] for c in top_chunks],
        )

        sources = [
            SourceReference(
                document_id=c["document_id"],
                file_name=c.get("file_name", ""),
                chunk_id=c["id"],
                relevance_score=c.get("score", 0.0),
                excerpt=c["text"][:300],
            )
            for c in top_chunks
        ]

        response = ChatQueryResponse(
            answer=answer,
            sources=sources,
            message_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        return func.HttpResponse(
            body=response.model_dump_json(),
            status_code=200,
            mimetype="application/json",
        )

    except Exception:
        logger.exception("Error processing chat query")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error."}),
            status_code=500,
            mimetype="application/json",
        )


# ---------------------------------------------------------------------------
# Chat History
# ---------------------------------------------------------------------------

@app.route(route="chat/history", methods=["GET"])
def chat_history(req: func.HttpRequest) -> func.HttpResponse:
    """Return chat message history for a session."""
    import json

    from services.cosmos_service import CosmosRepository

    session_id = req.params.get("sessionId")
    try:
        limit = int(req.params.get("limit", "50"))
        offset = int(req.params.get("offset", "0"))
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "limit and offset must be integers."}),
            status_code=400,
            mimetype="application/json",
        )

    try:
        repo = CosmosRepository()
        session = repo.get_session(session_id) if session_id else None
        messages = (session or {}).get("messages", [])
        total = len(messages)
        page = messages[offset : offset + limit]

        return func.HttpResponse(
            json.dumps({"messages": page, "total": total, "hasMore": offset + limit < total}),
            status_code=200,
            mimetype="application/json",
        )

    except Exception:
        logger.exception("Error fetching chat history")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error."}),
            status_code=500,
            mimetype="application/json",
        )
