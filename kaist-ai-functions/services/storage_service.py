"""Azure Blob Storage service — upload, download, delete PDF files."""

from __future__ import annotations

import logging

from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, ContentSettings
from tenacity import retry, stop_after_attempt, wait_exponential

from shared.config import get_config
from shared.exceptions import StorageError

logger = logging.getLogger(__name__)

_ACCOUNT_URL_TEMPLATE = "https://{}.blob.core.windows.net"


class BlobStorageService:
    """Thin wrapper around Azure Blob Storage for PDF file operations.

    Uses DefaultAzureCredential so local developers can authenticate via
    `az login`, while the deployed Function App uses its Managed Identity.
    """

    def __init__(self) -> None:
        config = get_config()
        account_url = _ACCOUNT_URL_TEMPLATE.format(config.STORAGE_ACCOUNT_NAME)
        self._client = BlobServiceClient(
            account_url=account_url,
            credential=DefaultAzureCredential(),
        )
        self._container = config.PDF_CONTAINER_NAME

    def ping(self) -> None:
        """Raise StorageError if the storage account is unreachable."""
        try:
            container_client = self._client.get_container_client(self._container)
            container_client.get_container_properties()
        except Exception as exc:
            raise StorageError(f"Storage ping failed: {exc}") from exc

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    def upload_pdf(self, file_bytes: bytes, blob_name: str) -> str:
        """Upload *file_bytes* as *blob_name* and return the blob URL."""
        try:
            blob_client = self._client.get_blob_client(
                container=self._container, blob=blob_name
            )
            blob_client.upload_blob(
                file_bytes,
                overwrite=True,
                content_settings=ContentSettings(content_type="application/pdf"),
            )
            logger.info("Uploaded blob %s (%d bytes)", blob_name, len(file_bytes))
            return blob_client.url
        except Exception as exc:
            raise StorageError(f"Failed to upload {blob_name}: {exc}") from exc

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    def download_pdf(self, blob_name: str) -> bytes:
        """Download and return the raw bytes for *blob_name*."""
        try:
            blob_client = self._client.get_blob_client(
                container=self._container, blob=blob_name
            )
            stream = blob_client.download_blob()
            return stream.readall()
        except ResourceNotFoundError as exc:
            raise StorageError(f"Blob not found: {blob_name}") from exc
        except Exception as exc:
            raise StorageError(f"Failed to download {blob_name}: {exc}") from exc

    def delete_pdf(self, blob_name: str) -> None:
        """Delete *blob_name* from storage (no-op if it does not exist)."""
        try:
            blob_client = self._client.get_blob_client(
                container=self._container, blob=blob_name
            )
            blob_client.delete_blob(delete_snapshots="include")
            logger.info("Deleted blob %s", blob_name)
        except ResourceNotFoundError:
            logger.warning("Blob %s not found during delete — ignored", blob_name)
        except Exception as exc:
            raise StorageError(f"Failed to delete {blob_name}: {exc}") from exc
