"""PDF text extraction and chunking using PyMuPDF (fitz)."""

from __future__ import annotations

import logging
from typing import Any

import fitz  # PyMuPDF

from shared.exceptions import PDFProcessingError

logger = logging.getLogger(__name__)


class PDFService:
    """Extracts text from PDF bytes and splits it into overlapping chunks."""

    def extract_text(self, pdf_bytes: bytes) -> list[dict[str, Any]]:
        """Extract text from every page of *pdf_bytes*.

        Returns a list of dicts:
          {"page_number": int, "text": str}
        """
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            pages: list[dict[str, Any]] = []
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text("text").strip()
                pages.append({"page_number": page_num + 1, "text": text})
            doc.close()
            logger.info("Extracted text from %d pages", len(pages))
            return pages
        except Exception as exc:
            raise PDFProcessingError(f"Text extraction failed: {exc}") from exc

    def chunk_text(
        self,
        pages: list[dict[str, Any]],
        chunk_size: int = 1000,
        overlap: int = 200,
    ) -> list[str]:
        """Flatten page texts and split into overlapping fixed-size chunks.

        Args:
            pages: Output of :meth:`extract_text`.
            chunk_size: Maximum characters per chunk.
            overlap: Number of characters to repeat between consecutive chunks.

        Returns:
            List of text chunk strings.
        """
        full_text = "\n\n".join(p["text"] for p in pages if p["text"])
        if not full_text:
            return []

        chunks: list[str] = []
        start = 0
        while start < len(full_text):
            end = start + chunk_size
            chunk = full_text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            start += chunk_size - overlap

        logger.info(
            "Created %d chunks (size=%d, overlap=%d) from %d chars",
            len(chunks),
            chunk_size,
            overlap,
            len(full_text),
        )
        return chunks
