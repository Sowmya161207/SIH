import os
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.config import settings
from app.core.security import create_access_token


def auth_headers(role: str = "admin") -> dict:
    token = create_access_token({"sub": "testadmin", "role": role})
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_document_upload_and_status():
    """Test valid PDF document upload and subsequent status retrieval."""
    pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Title (Test Document) >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF"
    files = {"file": ("test_report.pdf", pdf_content, "application/pdf")}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Upload Document
        upload_resp = await client.post("/api/documents", files=files, headers=auth_headers())
        assert upload_resp.status_code == 200
        upload_data = upload_resp.json()

        assert "document_id" in upload_data
        doc_id = upload_data["document_id"]
        assert upload_data["filename"] == "test_report.pdf"
        # After background-task refactor the status is 'processing' immediately on upload
        assert upload_data["status"] in ["uploaded", "ready", "processing"]
        assert upload_data["size_bytes"] == len(pdf_content)
        assert "created_at" in upload_data

        # 2. Check File Exists on Disk
        stored_file_path = os.path.join(settings.UPLOAD_DIR, f"{doc_id}.pdf")
        assert os.path.exists(stored_file_path)

        # 3. Retrieve Document Status
        status_resp = await client.get(f"/api/documents/{doc_id}", headers=auth_headers())
        assert status_resp.status_code == 200
        status_data = status_resp.json()
        assert status_data["document_id"] == doc_id
        assert status_data["filename"] == "test_report.pdf"
        # Status may be 'processing', 'ready', or 'failed' (background task)
        assert status_data["status"] in ["uploaded", "ready", "processing", "failed"]
        assert status_data["size_bytes"] == len(pdf_content)


@pytest.mark.asyncio
async def test_document_upload_invalid_type():
    """Test uploading unsupported document returns 400 bad request error."""
    exe_content = b"MZ binary data"
    files = {"file": ("program.exe", exe_content, "application/octet-stream")}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/documents", files=files, headers=auth_headers())

    assert response.status_code == 400
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "INVALID_FILE"


@pytest.mark.asyncio
async def test_document_upload_file_too_large():
    """Test uploading file exceeding MAX_FILE_SIZE_MB returns 413 error."""
    large_size = settings.max_file_size_bytes + 100
    large_content = b"%PDF-1.4 " + (b"0" * large_size)
    files = {"file": ("large.pdf", large_content, "application/pdf")}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/documents", files=files, headers=auth_headers())

    assert response.status_code == 413
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "FILE_TOO_LARGE"


@pytest.mark.asyncio
async def test_document_status_not_found():
    """Test requesting status for non-existent document ID returns 404."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/documents/non_existent_id", headers=auth_headers())

    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "DOCUMENT_NOT_FOUND"
