"""
telemetry.py
------------
FastAPI endpoint for Network Sovereignty and Air-Gap Audit Telemetry.
"""

from fastapi import APIRouter
from app.services.network_logger import get_network_telemetry

router = APIRouter(prefix="/api/telemetry", tags=["Sovereignty Audit Telemetry"])


@router.get(
    "/network-calls",
    summary="Get Network Sovereignty Audit Telemetry",
    description="Returns verified audit logs of all network calls confirming 0 external outbound requests."
)
async def get_network_audit():
    return get_network_telemetry()
