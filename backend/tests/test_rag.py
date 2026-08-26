import os
import pytest
from pathlib import Path
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.services.rag_service import ingest_document, retrieve, get_store_stats
from app.services.ingestion.pdf_extractor import extract_pdf
from app.services.ingestion.cleaner import clean_text
from app.services.ingestion.chunker import chunk_document
from app.services.embeddings.embedder import Embedder

TEST_PDF = Path(__file__).parent.parent.parent / "RAG" / "data" / "demo" / "incident_report_p101.pdf"
MANUAL_PDF = Path(__file__).parent.parent.parent / "RAG" / "data" / "demo" / "equipment_manual_p101.pdf"


def test_pdf_text_extraction():
    """Test extracting text from PDF page by page."""
    assert TEST_PDF.exists(), f"Test PDF not found at {TEST_PDF}"
    pages = extract_pdf(TEST_PDF)
    assert len(pages) > 0
    assert pages[0]["page"] == 1
    assert "Incident" in pages[0]["text"] or "P-101" in pages[0]["text"]


def test_chunking_with_metadata():
    """Test chunking attaching document_id, filename, and page metadata."""
    pages = extract_pdf(TEST_PDF)
    meta = {
        "document_id": "test_p101_inc",
        "filename": TEST_PDF.name,
        "equipment": "Pump P-101",
        "allowed_roles": ["safety_officer", "manager"]
    }
    chunks = chunk_document(pages, meta)
    assert len(chunks) > 0
    first_chunk = chunks[0]
    assert first_chunk["document_id"] == "test_p101_inc"
    assert first_chunk["filename"] == TEST_PDF.name
    assert "page" in first_chunk
    assert "text" in first_chunk


def test_embeddings_generation():
    """Test generating embeddings for extracted text."""
    embedder = Embedder()
    vec = embedder.embed("Pump P101 bearing failure investigation")
    assert vec.shape == (384,)


def test_ingest_and_retrieve_pump_failure():
    """Ingest Pump P101 document and query 'Why did Pump P101 fail?'."""
    assert TEST_PDF.exists()

    res = ingest_document(
        document_id="incident_p101_report",
        file_path=TEST_PDF,
        metadata={
            "filename": TEST_PDF.name,
            "title": "Incident Report - Pump P-101",
            "equipment": "Pump P-101",
            "document_type": "incident",
            "allowed_roles": ["safety_officer", "manager"]
        },
        reset_store=True
    )
    assert res["status"] == "ok"
    assert res["chunks_added"] > 0

    # Query RAG
    query = "Why did Pump P101 fail?"
    evidence = retrieve(query, top_k=5)

    assert len(evidence) > 0

    # Check evidence structure
    found_relevant = False
    for ev in evidence:
        assert "document_id" in ev
        assert "source" in ev
        assert "page" in ev
        assert "content" in ev
        assert "score" in ev

        text_lower = ev["content"].lower()
        if "bearing" in text_lower or "failure" in text_lower or "seizure" in text_lower or "fire" in text_lower:
            found_relevant = True

    assert found_relevant, f"Retrieval failed to return relevant failure chunks for query '{query}'"


from app.core.security import create_access_token


def auth_headers(role: str = "admin") -> dict:
    token = create_access_token({"sub": "testadmin", "role": role})
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_upload_api_triggers_rag_ingestion():
    """Test uploading PDF via /api/documents endpoint and verifying RAG indexing."""
    assert MANUAL_PDF.exists()

    with open(MANUAL_PDF, "rb") as f:
        pdf_bytes = f.read()

    files = {"file": ("upload_manual_p101.pdf", pdf_bytes, "application/pdf")}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/documents", files=files, headers=auth_headers())
        assert response.status_code == 200
        data = response.json()

        assert data["status"] in ["uploaded", "ready", "processing"]
        doc_id = data["document_id"]

        # Retrieve document via RAG
        retrieval = retrieve("troubleshooting bearing temperature", top_k=3)
        assert len(retrieval) > 0
