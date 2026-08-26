"""
test_sprints.py
---------------
Unit tests for Model Router, Deliverables Generation (Word/Excel),
Code Execution Sandbox, and Sovereignty Network Audit.
"""

import pytest
from pathlib import Path
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.services.model_router import get_model_for_intent, detect_intent
from app.services.output_generator import generate_approval_note, generate_excel_report
from app.services.code_sandbox import execute_python_sandbox
from app.services.network_logger import record_network_call, get_network_telemetry


def test_model_router_intent_mapping():
    """Verify task intents map to the correct Ollama models."""
    assert get_model_for_intent("code") == "codellama:7b"
    assert get_model_for_intent("coding_qa") == "codellama:7b"
    assert get_model_for_intent("vision") == "llava:7b"
    assert get_model_for_intent("document_qa") == "llama3.1:8b"
    assert get_model_for_intent("general_qa") == "llama3.1:8b"


def test_detect_intent_keywords():
    """Verify automatic intent detection from user queries."""
    assert detect_intent("Write a python script to parse CSV") == "code"
    assert detect_intent("Inspect this engineering drawing diagram") == "vision"
    assert detect_intent("Summarize the uploaded PDF manual") == "document_summarization"


def test_code_sandbox_execution():
    """Verify code sandbox executes valid python code and captures output."""
    res = execute_python_sandbox("print(10 + 20)")
    assert res["success"] is True
    assert res["output"] == "30"
    assert res["error"] is None

    # Test security restriction
    res_bad = execute_python_sandbox("import os.system")
    assert res_bad["success"] is False
    assert "Security Violation" in res_bad["error"]


def test_deliverable_generation():
    """Verify Word (.docx) and Excel (.xlsx) file creation."""
    doc_path = generate_approval_note(
        title="Test Approval Note",
        content="This is a test summary for unit tests.",
        findings=["Finding 1: All clear", "Finding 2: No anomalies"],
    )
    assert doc_path.exists()
    assert doc_path.suffix == ".docx"

    excel_path = generate_excel_report(
        title="Test Report",
        rows=[{"Item": "Pump P-101", "Status": "Normal", "Pressure": 12.5}],
    )
    assert excel_path.exists()
    assert excel_path.suffix == ".xlsx"


def test_network_telemetry():
    """Verify network call recording and 0-external-call sovereignty auditing."""
    record_network_call(
        destination="http://127.0.0.1:11434/api/generate",
        method="POST",
        purpose="Local Test Call",
        bytes_sent=100,
        bytes_received=200,
    )
    telemetry = get_network_telemetry()
    assert telemetry["external_calls_count"] == 0
    assert telemetry["sovereign_status"] == "AIR_GAPPED_VERIFIED"
    assert telemetry["total_audited_calls"] > 0


@pytest.mark.asyncio
async def test_api_endpoints():
    """Test API routes for Sandbox, Deliverables, and Telemetry."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Test Sandbox API
        sandbox_resp = await client.post("/api/sandbox/run", json={"code": "print('hello sandbox')"})
        assert sandbox_resp.status_code == 200
        assert sandbox_resp.json()["output"] == "hello sandbox"

        # Test Telemetry API
        telem_resp = await client.get("/api/telemetry/network-calls")
        assert telem_resp.status_code == 200
        assert telem_resp.json()["external_calls_count"] == 0
