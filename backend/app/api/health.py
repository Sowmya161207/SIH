from fastapi import APIRouter, status
from app.models.response import HealthResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Check the operational status of the Sovereign AI Workbench backend API."
)
async def health_check() -> HealthResponse:
    """Returns application health status."""
    return HealthResponse(status="ok")
