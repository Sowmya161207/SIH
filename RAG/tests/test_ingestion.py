"""
tests/test_ingestion.py
-----------------------
Unit tests for the PDF extraction, cleaning, and chunking pipeline.
These tests work without a vector store or embedding model.
"""

import sys
import os
from pathlib import Path

# Ensure the RAG package is importable
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from rag.ingestion.cleaner import clean_text, is_meaningful
from rag.ingestion.chunker import chunk_text, chunk_document


# ─── Cleaner tests ─────────────────────────────────────────────────────────────

class TestCleaner:

    def test_basic_cleaning(self):
        raw = "Hello   World\n\n\n\nNext Paragraph"
        result = clean_text(raw)
        assert "  " not in result          # no double spaces
        assert "\n\n\n" not in result      # no triple newlines

    def test_hyphen_linebreak_removal(self):
        raw = "pump main-\ntenance procedure"
        result = clean_text(raw)
        assert "maintenance" in result

    def test_empty_string(self):
        assert clean_text("") == ""

    def test_control_chars_removed(self):
        raw = "Hello\x00World\x07Test"
        result = clean_text(raw)
        assert "\x00" not in result
        assert "\x07" not in result

    def test_is_meaningful_true(self):
        text = "The bearing temperature exceeded 85 degrees Celsius on 28 May 2025."
        assert is_meaningful(text) is True

    def test_is_meaningful_false_short(self):
        assert is_meaningful("Hi") is False

    def test_is_meaningful_false_empty(self):
        assert is_meaningful("") is False

    def test_is_meaningful_false_no_words(self):
        assert is_meaningful("123456789012345678901234") is False


# ─── Chunker tests ─────────────────────────────────────────────────────────────

class TestChunker:

    def _make_meta(self):
        return {
            "document_id":   "test_doc",
            "title":         "Test Document",
            "page":          1,
            "equipment":     "Pump P-101",
            "document_type": "maintenance",
            "classification":"internal",
            "allowed_roles": ["maintenance_engineer"],
            "source_file":   "test.pdf",
            "total_pages":   5,
        }

    def test_short_text_returns_one_chunk(self):
        text = "The bearing temperature exceeded 85°C on the drive end, requiring immediate attention."
        chunks = chunk_text(text, self._make_meta(), chunk_size=400, chunk_overlap=80)
        assert len(chunks) == 1

    def test_long_text_returns_multiple_chunks(self):
        text = "A" * 1200  # 1200 chars with chunk_size=400
        chunks = chunk_text(text, self._make_meta(), chunk_size=400, chunk_overlap=80)
        assert len(chunks) > 1

    def test_chunk_has_required_fields(self):
        text = "Pump P-101 bearing inspection revealed significant wear."
        chunks = chunk_text(text, self._make_meta())
        assert len(chunks) >= 1
        chunk = chunks[0]
        for field in ["chunk_id", "document_id", "title", "page", "text",
                       "equipment", "document_type", "classification",
                       "allowed_roles", "source_file"]:
            assert field in chunk, f"Missing field: {field}"

    def test_chunk_id_format(self):
        text = "Bearing inspection: drive end bearing shows pitting on outer race."
        chunks = chunk_text(text, self._make_meta())
        assert chunks[0]["chunk_id"] == "test_doc_p1_c0"

    def test_metadata_propagated(self):
        text = "Lubrication: Shell Gadus S3 V220C applied per maintenance schedule."
        chunks = chunk_text(text, self._make_meta())
        c = chunks[0]
        assert c["equipment"] == "Pump P-101"
        assert c["document_type"] == "maintenance"
        assert "maintenance_engineer" in c["allowed_roles"]

    def test_empty_text_returns_no_chunks(self):
        chunks = chunk_text("", self._make_meta())
        assert chunks == []

    def test_very_short_text_filtered(self):
        chunks = chunk_text("Hi", self._make_meta())
        assert chunks == []

    def test_chunk_document_all_pages(self):
        pages = [
            {"page": 1, "text": "First page content " * 20, "total_pages": 2},
            {"page": 2, "text": "Second page content " * 20, "total_pages": 2},
        ]
        doc_meta = {
            "document_id": "multi_page_doc",
            "title": "Multi Page",
            "equipment": "P-101",
            "document_type": "manual",
            "classification": "internal",
            "allowed_roles": [],
            "source_file": "test.pdf",
        }
        chunks = chunk_document(pages, doc_meta)
        assert len(chunks) > 0
        pages_seen = {c["page"] for c in chunks}
        assert 1 in pages_seen
        assert 2 in pages_seen


# ─── Integration: extract + clean + chunk ─────────────────────────────────────

class TestIngestionIntegration:

    def test_sample_pdf_extraction(self):
        """Test that the sample PDF in the RAG root can be extracted."""
        sample = Path(__file__).parent.parent / "sample.pdf"
        if not sample.exists():
            pytest.skip("sample.pdf not found — skipping integration test")
        if sample.stat().st_size == 0:
            pytest.skip("sample.pdf is empty — skipping integration test")

        from rag.ingestion.pdf_extractor import extract_pdf
        pages = extract_pdf(sample)
        assert isinstance(pages, list)
        assert len(pages) > 0
        assert "page" in pages[0]
        assert "text" in pages[0]

    def test_missing_pdf_raises(self):
        from rag.ingestion.pdf_extractor import extract_pdf
        with pytest.raises(FileNotFoundError):
            extract_pdf("/nonexistent/path/to/file.pdf")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
