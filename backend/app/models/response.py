from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """Standardized error detail format."""
    code: str
    message: str


class ErrorResponse(BaseModel):
    """Standardized application error response wrapper."""
    error: ErrorDetail


class HealthResponse(BaseModel):
    """Health check endpoint response model."""
    status: str = "ok"
