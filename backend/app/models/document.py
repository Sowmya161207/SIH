from datetime import datetime
from pydantic import BaseModel, ConfigDict


class DocumentUploadResponse(BaseModel):
    """Response returned upon successful document upload."""

    document_id: str
    filename: str
    status: str
    size_bytes: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentStatusResponse(BaseModel):
    """Response returned when querying document status."""

    document_id: str
    filename: str
    status: str
    size_bytes: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
