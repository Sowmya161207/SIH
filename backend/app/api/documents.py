from typing import List

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    UploadFile,
    File,
    status,
)

from app.core.security import get_current_user

from app.models.document import (
    DocumentUploadResponse,
    DocumentStatusResponse,
)

from app.services.document_service import document_service


router = APIRouter(tags=["Documents"])


@router.post(
    "/documents",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload PDF document",
    description="Upload a file to be validated, stored, and ingested into RAG in the background.",
)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
) -> DocumentUploadResponse:
    """Accept and process file upload. RAG ingestion runs in the background."""

    return await document_service.upload_document(
        file=file,
        user_role=current_user["role"],
        background_tasks=background_tasks,
    )


@router.get(
    "/documents",
    response_model=List[DocumentStatusResponse],
    status_code=status.HTTP_200_OK,
    summary="List all documents",
    description="Return all documents tracked in the current session.",
)
async def list_documents(
    current_user: dict = Depends(get_current_user),
) -> List[DocumentStatusResponse]:
    """Return all tracked documents."""
    return document_service.list_documents()


@router.get(
    "/documents/{document_id}",
    response_model=DocumentStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Get document status",
    description="Retrieve status and metadata for a previously uploaded document.",
)
async def get_document_status(
    document_id: str,
    current_user: dict = Depends(get_current_user),
) -> DocumentStatusResponse:
    """Get metadata for a specific document ID."""

    return await document_service.get_document_status(document_id)