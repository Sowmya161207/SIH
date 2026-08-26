"""
generate.py
-----------
FastAPI routes for generating formal deliverables (Word .docx, Excel .xlsx).
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse

from app.services.output_generator import generate_approval_note, generate_excel_report

router = APIRouter(prefix="/api/generate", tags=["Deliverables Generation"])


class ApprovalNoteRequest(BaseModel):
    title: str = "Approval Note — Technical Review"
    content: str
    findings: Optional[List[str]] = None
    signatory: Optional[str] = "Authorised Officer / Unit Head"


class ExcelReportRequest(BaseModel):
    title: str = "Analytical Data Export"
    data: List[Dict[str, Any]]
    sheet_name: Optional[str] = "Data Output"


@router.post(
    "/approval-note",
    summary="Generate Word (.docx) Approval Note",
    description="Generates a formatted, corporate-styled Word approval note from LLM summary/content."
)
async def create_approval_note(req: ApprovalNoteRequest):
    try:
        file_path = generate_approval_note(
            title=req.title,
            content=req.content,
            findings=req.findings,
            signatory=req.signatory or "Authorised Officer / Unit Head",
        )
        return FileResponse(
            path=file_path,
            filename=file_path.name,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate Word document: {str(exc)}",
        ) from exc


@router.post(
    "/excel-report",
    summary="Generate Excel (.xlsx) Analytical Report",
    description="Generates a styled Excel report from structured tabular data."
)
async def create_excel_report(req: ExcelReportRequest):
    try:
        file_path = generate_excel_report(
            title=req.title,
            rows=req.data,
            sheet_name=req.sheet_name or "Data Output",
        )
        return FileResponse(
            path=file_path,
            filename=file_path.name,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate Excel document: {str(exc)}",
        ) from exc
