import os
import uuid
import logging
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


class DocumentService:
    """Service for managing document uploads, validation, storage,
    metadata, and RAG ingestion.
    """

    def __init__(self):
        # In-memory document metadata storage for hackathon phase.
        self._documents: Dict[str, Dict[str, Any]] = {}
        self._ensure_upload_directory()

    def _ensure_upload_directory(self) -> str:
        """Ensure the target upload directory exists on disk."""

        upload_path = os.path.abspath(settings.UPLOAD_DIR)
        os.makedirs(upload_path, exist_ok=True)

        return upload_path

    async def upload_document(
        self,
        file: UploadFile,
    ) -> DocumentUploadResponse:
        """Validate, store, track, and ingest an uploaded PDF document."""

        logger.info(
            "Receiving document upload request for file: %s",
            file.filename if file else None,
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
            stored_filename,
        )

        if os.path.exists(file_path):
            document_id = uuid.uuid4().hex
            stored_filename = f"{document_id}.pdf"
            file_path = os.path.join(
                upload_dir,
                stored_filename,
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

        # ---------------------------------------------------------
        # 8. RAG ingestion using the improved RAG service
        # ---------------------------------------------------------

        try:
            from app.services.rag_service import ingest_document

            logger.info(
                "Starting improved RAG ingestion for document %s",
                document_id,
            )

            ingest_result = ingest_document(
                document_id=document_id,
                file_path=file_path,
                metadata={
                    "filename": filename,
                    "title": filename,
                },
            )

            logger.info(
                "RAG ingestion completed for document %s: %s",
                document_id,
                ingest_result,
            )

            self._documents[document_id]["rag_status"] = "indexed"
            self._documents[document_id]["rag_result"] = ingest_result

        except Exception as exc:
            # Upload should not fail merely because RAG ingestion failed.
            logger.exception(
                "RAG ingestion failed for document %s: %s",
                document_id,
                exc,
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
        document_id: str,
    ) -> DocumentStatusResponse:
        """Retrieve metadata for a given document ID."""

        logger.info(
            "Document lookup requested for ID: %s",
            document_id,
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