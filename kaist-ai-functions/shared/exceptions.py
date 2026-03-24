"""Custom exception hierarchy for the kaist-ai-functions application."""


class AppError(Exception):
    """Base class for all application-level errors."""


class PDFProcessingError(AppError):
    """Raised when text extraction or chunking fails."""


class EmbeddingError(AppError):
    """Raised when the Gemini embedding API call fails."""


class StorageError(AppError):
    """Raised when an Azure Blob Storage operation fails."""


class DocumentNotFoundError(AppError):
    """Raised when a requested document ID does not exist in Cosmos DB."""

    def __init__(self, document_id: str) -> None:
        self.document_id = document_id
        super().__init__(f"Document not found: {document_id}")


class InvalidFileTypeError(AppError):
    """Raised when an uploaded file is not a valid PDF."""
