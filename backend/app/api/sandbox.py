"""
sandbox.py
----------
FastAPI endpoints for sandbox code execution and verification.
"""

from typing import Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, status

from app.services.code_sandbox import execute_python_sandbox

router = APIRouter(prefix="/api/sandbox", tags=["Code Sandbox Execution"])


class CodeExecutionRequest(BaseModel):
    code: str = Field(..., description="Python code string to execute in the sandbox.")
    language: Optional[str] = Field("python", description="Language environment (default: python)")


class CodeExecutionResponse(BaseModel):
    success: bool
    output: str
    error: Optional[str] = None
    execution_time_ms: int
    stdout: str
    stderr: str


@router.post(
    "/run",
    response_model=CodeExecutionResponse,
    summary="Execute Python code in isolated sandbox",
    description="Runs Python code in a secure, isolated local subprocess with timeout and output capture."
)
async def run_code_in_sandbox(req: CodeExecutionRequest):
    try:
        result = execute_python_sandbox(req.code)
        return CodeExecutionResponse(**result)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sandbox execution failed: {str(exc)}"
        ) from exc
