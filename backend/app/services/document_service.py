import os
import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from fastapi import BackgroundTasks, UploadFile

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
    metadata, and RAG ingestion (background).
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

    # ------------------------------------------------------------------
    # Background ingestion worker (called by FastAPI BackgroundTasks)
    # ------------------------------------------------------------------

    def _run_ingest(
        self,
        document_id: str,
        file_path: str,
        filename: str,
        allowed_roles: list,
    ) -> None:
        """
        Synchronous ingestion worker executed by FastAPI BackgroundTasks.
        Updates in-memory metadata when done so the status endpoint reflects
        the final state.
        """
        try:
            from app.services.rag_service import ingest_document

            logger.info(
                "Background RAG ingestion starting for document %s | allowed_roles=%s",
                document_id,
                allowed_roles,
            )

            ingest_result = ingest_document(
                document_id=document_id,
                file_path=file_path,
                metadata={
                    "filename": filename,
                    "title": filename,
                    "allowed_roles": allowed_roles,
                },
            )

            logger.info(
                "Background RAG ingestion completed for document %s: %s",
                document_id,
                ingest_result,
            )

            self._documents[document_id]["status"] = "ready"
            self._documents[document_id]["rag_status"] = "indexed"
            self._documents[document_id]["rag_result"] = ingest_result
            self._documents[document_id]["chunks_added"] = ingest_result.get("chunks_added", 0)

        except Exception as exc:
            logger.exception(
                "Background RAG ingestion failed for document %s: %s",
                document_id,
                exc,
            )
            self._documents[document_id]["status"] = "failed"
            self._documents[document_id]["rag_status"] = "failed"
            self._documents[document_id]["rag_error"] = str(exc)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def upload_document(
        self,
        file: UploadFile,
        user_role: str,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> DocumentUploadResponse:
        """
        Validate, store, and track an uploaded document.

        RAG ingestion is scheduled as a background task so this method
        returns immediately with ``status='processing'``.
        """

        logger.info(
            "Receiving document upload request for file: %s | role=%s",
            file.filename if file else None,
            user_role,
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
        ext_lower = ext.lower()

        allowed_extensions = {
            ".pdf", ".docx", ".doc", ".txt", ".png", ".jpg",
            ".jpeg", ".tiff", ".bmp", ".webp", ".ppt", ".pptx",
            ".csv", ".md", ".json", ".log"
        }

        if ext_lower not in allowed_extensions:
            raise InvalidFileException(
                f"Unsupported file extension '{ext}'. Allowed extensions: PDF, DOCX, TXT, PNG, JPG, PPTX."
            )

        # ---------------------------------------------------------
        # 3. Read content and validate size
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
        # 4. Generate document ID and file path
        # ---------------------------------------------------------

        document_id = uuid.uuid4().hex[:8]
        stored_filename = f"{document_id}{ext_lower}"
        upload_dir = self._ensure_upload_directory()

        file_path = os.path.join(
            upload_dir,
            stored_filename,
        )

        if os.path.exists(file_path):
            document_id = uuid.uuid4().hex
            stored_filename = f"{document_id}{ext_lower}"
            file_path = os.path.join(
                upload_dir,
                stored_filename,
            )

        # ---------------------------------------------------------
        # 5. Save file to disk
        # ---------------------------------------------------------

        with open(file_path, "wb") as f:
            f.write(content)

        created_at = datetime.now(timezone.utc)

        # ---------------------------------------------------------
        # 6. Determine document access roles
        # ---------------------------------------------------------

        ALL_ROLES = ["operator", "supervisor", "viewer", "manager", "admin"]

        role_access_policy = {
            "admin": ALL_ROLES,
            "manager": ALL_ROLES,
            "supervisor": ["operator", "supervisor", "manager", "admin"],
            "operator": ["operator", "supervisor", "manager", "admin"],
            "viewer": ["viewer", "manager", "admin"],
        }

        allowed_roles = role_access_policy.get(
            user_role,
            [user_role],
        )

        # ---------------------------------------------------------
        # 7. Store initial metadata (status=processing)
        # ---------------------------------------------------------

        self._documents[document_id] = {
            "document_id": document_id,
            "filename": filename,
            "status": "processing",
            "size_bytes": file_size,
            "created_at": created_at,
            "path": file_path,
            "rag_status": "pending",
            "uploaded_by_role": user_role,
            "allowed_roles": allowed_roles,
        }

        # ---------------------------------------------------------
        # 8. Schedule background RAG ingestion
        # ---------------------------------------------------------

        if background_tasks is not None:
            background_tasks.add_task(
                self._run_ingest,
                document_id=document_id,
                file_path=file_path,
                filename=filename,
                allowed_roles=allowed_roles,
            )
            logger.info(
                "RAG ingestion scheduled as background task for document %s",
                document_id,
            )
        else:
            # Fallback: run inline if no background task runner provided
            logger.warning(
                "No BackgroundTasks provided — running RAG ingestion inline for %s",
                document_id,
            )
            self._run_ingest(
                document_id=document_id,
                file_path=file_path,
                filename=filename,
                allowed_roles=allowed_roles,
            )

        # ---------------------------------------------------------
        # 9. Return immediately with processing status
        # ---------------------------------------------------------

        return DocumentUploadResponse(
            document_id=document_id,
            filename=filename,
            status=self._documents[document_id]["status"],
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
            chunks_indexed=meta.get("chunks_added"),
            rag_status=meta.get("rag_status"),
        )

    def list_documents(self) -> list:
        """Return all tracked documents as a list of DocumentStatusResponse."""
        result = []
        for meta in self._documents.values():
            result.append(DocumentStatusResponse(
                document_id=meta["document_id"],
                filename=meta["filename"],
                status=meta["status"],
                size_bytes=meta["size_bytes"],
                created_at=meta["created_at"],
                chunks_indexed=meta.get("chunks_added"),
                rag_status=meta.get("rag_status"),
            ))
        # newest first
        result.sort(key=lambda d: d.created_at, reverse=True)
        return result


document_service = DocumentService()