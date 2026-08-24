import os
import uuid
import logging
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any

from fastapi import UploadFile

from app.core.config import settings
from app.core.exceptions import (
    InvalidFileException,
    FileNotFoundException,
    FileTooLargeException,
)
from app.models.document import (
    DocumentUploadResponse,
    DocumentStatusResponse,
)

logger = logging.getLogger(__name__)


def _get_rag_services():
    """
    Import the RAG service from the project-level RAG directory.

    Project structure:

        SIH/
        ├── backend/
        ├── frontend/
        └── RAG/
            └── rag_services.py
    """

    project_root = Path(__file__).resolve().parents[3]
    rag_dir = project_root / "RAG"

    if str(rag_dir) not in sys.path:
        sys.path.insert(0, str(rag_dir))

    from rag_services import ingest_pdf

    return ingest_pdf


class DocumentService:
    """Service for managing document uploads, validation, storage, and metadata."""

    def __init__(self):
        # In-memory document metadata storage for hackathon phase
        self._documents: Dict[str, Dict[str, Any]] = {}
        self._ensure_upload_directory()

    def _ensure_upload_directory(self) -> str:
        """Ensure the target upload directory exists on disk."""

        upload_path = os.path.abspath(settings.UPLOAD_DIR)
        os.makedirs(upload_path, exist_ok=True)

        return upload_path

    async def upload_document(
        self,
        file: UploadFile
    ) -> DocumentUploadResponse:

        """Validate, store, and track an uploaded PDF document."""

        logger.info(
            f"Receiving document upload request for file: {file.filename}"
        )

        # ---------------------------------------------------------
        # 1. File existence check
        # ---------------------------------------------------------

        if not file or not file.filename:
            raise InvalidFileException(
                "No file provided in request."
            )

        # ---------------------------------------------------------
        # 2. Extension validation
        # ---------------------------------------------------------

        filename = file.filename.strip()

        _, ext = os.path.splitext(filename)

        if ext.lower() != ".pdf":
            raise InvalidFileException(
                "Only PDF files are supported."
            )

        # ---------------------------------------------------------
        # 3. MIME type validation
        # ---------------------------------------------------------

        if (
            file.content_type
            and file.content_type.lower()
            not in [
                "application/pdf",
                "application/x-pdf",
                "application/octet-stream",
            ]
        ):
            raise InvalidFileException(
                "Uploaded file MIME type must be application/pdf."
            )

        # ---------------------------------------------------------
        # 4. Read content and validate size
        # ---------------------------------------------------------

        content = await file.read()

        file_size = len(content)

        if file_size == 0:
            raise InvalidFileException(
                "Uploaded file is empty."
            )

        if file_size > settings.max_file_size_bytes:
            raise FileTooLargeException(
                f"The uploaded file size ({file_size} bytes) "
                f"exceeds the maximum allowed limit of "
                f"{settings.MAX_FILE_SIZE_MB}MB."
            )

        # ---------------------------------------------------------
        # 5. Generate document ID and file path
        # ---------------------------------------------------------

        document_id = uuid.uuid4().hex[:8]

        stored_filename = f"{document_id}.pdf"

        upload_dir = self._ensure_upload_directory()

        file_path = os.path.join(
            upload_dir,
            stored_filename
        )

        if os.path.exists(file_path):

            document_id = uuid.uuid4().hex

            stored_filename = f"{document_id}.pdf"

            file_path = os.path.join(
                upload_dir,
                stored_filename
            )

        # ---------------------------------------------------------
        # 6. Save PDF
        # ---------------------------------------------------------

        with open(file_path, "wb") as f:
            f.write(content)

        created_at = datetime.now(timezone.utc)

        # ---------------------------------------------------------
        # 7. Store document metadata
        # ---------------------------------------------------------

        metadata = {
            "document_id": document_id,
            "filename": filename,
            "status": "uploaded",
            "size_bytes": file_size,
            "created_at": created_at,
            "path": file_path,
            "rag_status": "pending",
        }

        self._documents[document_id] = metadata

        logger.info(
            f"Successfully uploaded and stored document "
            f"ID: {document_id} ({filename})"
        )

        # ---------------------------------------------------------
        # 8. RAG ingestion
        # ---------------------------------------------------------

        try:

            ingest_pdf = _get_rag_services()

            rag_metadata = {
                "document_id": document_id,
                "title": filename,
                "equipment": "Unknown",
                "document_type": "general",
                "classification": "internal",
                "allowed_roles": [],
            }

            logger.info(
                f"Starting RAG ingestion for document "
                f"{document_id}"
            )

            rag_result = await asyncio.to_thread(
                ingest_pdf,
                pdf_path=file_path,
                metadata=rag_metadata,
                reset_store=False,
            )

            logger.info(
                f"RAG ingestion completed for document "
                f"{document_id}: {rag_result}"
            )

            self._documents[document_id]["rag_status"] = "indexed"

            self._documents[document_id]["rag_result"] = rag_result

        except Exception as exc:

            # -----------------------------------------------------
            # IMPORTANT:
            # Upload should NOT fail just because RAG failed.
            # -----------------------------------------------------

            logger.exception(
                f"RAG ingestion failed for document "
                f"{document_id}: {exc}"
            )

            self._documents[document_id]["rag_status"] = "failed"

            self._documents[document_id]["rag_error"] = str(exc)

        # ---------------------------------------------------------
        # 9. Return existing API response
        # ---------------------------------------------------------

        return DocumentUploadResponse(
            document_id=document_id,
            filename=filename,
            status="uploaded",
            size_bytes=file_size,
            created_at=created_at,
        )

    async def get_document_status(
        self,
        document_id: str
    ) -> DocumentStatusResponse:

        """Retrieve status and metadata for a given document ID."""

        logger.info(
            f"Document lookup requested for ID: {document_id}"
        )

        if document_id not in self._documents:

            raise FileNotFoundException(
                f"Document with ID '{document_id}' was not found."
            )

        meta = self._documents[document_id]

        return DocumentStatusResponse(
            document_id=meta["document_id"],
            filename=meta["filename"],
            status=meta["status"],
            size_bytes=meta["size_bytes"],
            created_at=meta["created_at"],
        )


document_service = DocumentService()