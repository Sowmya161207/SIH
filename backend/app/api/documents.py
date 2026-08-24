from fastapi import APIRouter, UploadFile, File, status
from app.models.document import DocumentUploadResponse, DocumentStatusResponse
from app.services.document_service import document_service

router = APIRouter(tags=["Documents"])


@router.post(
    "/documents",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload PDF document",
    description="Upload a PDF file to be validated, stored, and tracked."
)
async def upload_document(file: UploadFile = File(...)) -> DocumentUploadResponse:
    """Accept and process PDF file upload."""
    return await document_service.upload_document(file)


@router.get(
    "/documents/{document_id}",
    response_model=DocumentStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Get document status",
    description="Retrieve status and metadata for a previously uploaded document."
)
async def get_document_status(document_id: str) -> DocumentStatusResponse:
    """Get metadata for a specific document ID."""
    return await document_service.get_document_status(document_id)
