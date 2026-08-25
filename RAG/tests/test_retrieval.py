"""
tests/test_retrieval.py
-----------------------
Tests for the vector store and retrieval pipeline.
These tests build an in-memory index (not the persisted one) for isolation.
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import numpy as np


# ─── FAISSVectorStore tests ────────────────────────────────────────────────────

class TestFAISSVectorStore:

    @pytest.fixture
    def store(self):
        from rag.vector_store.faiss_store import FAISSVectorStore
        return FAISSVectorStore()

    @pytest.fixture
    def sample_chunks(self):
        return [
            {
                "chunk_id": "doc1_p1_c0",
                "document_id": "doc1",
                "title": "Maintenance Report",
                "page": 1,
                "text": "The bearing temperature exceeded 85 degrees Celsius.",
                "equipment": "Pump P-101",
                "document_type": "maintenance",
                "classification": "internal",
                "allowed_roles": ["maintenance_engineer", "manager"],
                "source_file": "maintenance_report_p101.pdf",
                "total_pages": 10,
            },
            {
                "chunk_id": "doc2_p1_c0",
                "document_id": "doc2",
                "title": "Equipment Manual",
                "page": 1,
                "text": "Never operate the pump against a closed discharge valve.",
                "equipment": "Pump P-101",
                "document_type": "manual",
                "classification": "internal",
                "allowed_roles": ["operator", "maintenance_engineer"],
                "source_file": "equipment_manual_p101.pdf",
                "total_pages": 20,
            },
            {
                "chunk_id": "doc3_p2_c0",
                "document_id": "doc3",
                "title": "Incident Report",
                "page": 2,
                "text": "Root cause: lubrication starvation caused bearing seizure and fire.",
                "equipment": "Pump P-101",
                "document_type": "incident",
                "classification": "confidential",
                "allowed_roles": ["safety_officer", "manager"],
                "source_file": "incident_report_p101.pdf",
                "total_pages": 8,
            },
        ]

    @pytest.fixture
    def embedder(self):
        try:
            from rag.embeddings.embedder import Embedder
            return Embedder()
        except ImportError:
            pytest.skip("sentence-transformers not installed")

    def test_empty_store_len(self, store):
        assert len(store) == 0

    def test_add_increases_count(self, store, sample_chunks, embedder):
        texts = [c["text"] for c in sample_chunks]
        vecs  = embedder.embed_batch(texts, show_progress=False)
        store.add(vecs, sample_chunks)
        assert len(store) == 3

    def test_search_returns_results(self, store, sample_chunks, embedder):
        texts = [c["text"] for c in sample_chunks]
        vecs  = embedder.embed_batch(texts, show_progress=False)
        store.add(vecs, sample_chunks)

        query_vec = embedder.embed("bearing temperature alarm")
        results   = store.search(query_vec, top_k=3)
        assert len(results) > 0

    def test_search_has_score_field(self, store, sample_chunks, embedder):
        texts = [c["text"] for c in sample_chunks]
        vecs  = embedder.embed_batch(texts, show_progress=False)
        store.add(vecs, sample_chunks)

        query_vec = embedder.embed("pump maintenance")
        results   = store.search(query_vec, top_k=2)
        for r in results:
            assert "score" in r
            assert 0.0 <= r["score"] <= 1.0 + 1e-4   # cosine sim, allow tiny float err

    def test_search_top_k_respected(self, store, sample_chunks, embedder):
        texts = [c["text"] for c in sample_chunks]
        vecs  = embedder.embed_batch(texts, show_progress=False)
        store.add(vecs, sample_chunks)

        query_vec = embedder.embed("pump")
        results   = store.search(query_vec, top_k=2)
        assert len(results) <= 2

    def test_search_empty_store_returns_empty(self, store, embedder):
        query_vec = embedder.embed("test query")
        results   = store.search(query_vec, top_k=5)
        assert results == []

    def test_save_and_load(self, store, sample_chunks, embedder):
        texts = [c["text"] for c in sample_chunks]
        vecs  = embedder.embed_batch(texts, show_progress=False)
        store.add(vecs, sample_chunks)

        with tempfile.TemporaryDirectory() as tmpdir:
            idx_path  = Path(tmpdir) / "test.index"
            meta_path = Path(tmpdir) / "test.pkl"
            store.save(idx_path, meta_path)

            from rag.vector_store.faiss_store import FAISSVectorStore
            loaded = FAISSVectorStore.load(idx_path, meta_path)
            assert len(loaded) == 3

            query_vec = embedder.embed("bearing temperature")
            results   = loaded.search(query_vec, top_k=2)
            assert len(results) > 0

    def test_mismatch_raises(self, store):
        import numpy as np
        vecs = np.random.rand(3, 384).astype(np.float32)
        meta = [{"a": 1}, {"b": 2}]   # only 2, but 3 vecs
        with pytest.raises(ValueError):
            store.add(vecs, meta)


# ─── Permission-aware retrieval tests ─────────────────────────────────────────

class TestPermissionFilter:
    """Test the _is_accessible function directly."""

    def setup_method(self):
        from rag.retrieval.retriever import _is_accessible
        self._check = _is_accessible

    def test_none_role_allows_all(self):
        chunk = {"allowed_roles": ["maintenance_engineer"]}
        assert self._check(chunk, user_role=None) is True

    def test_correct_role_allowed(self):
        chunk = {"allowed_roles": ["maintenance_engineer", "manager"]}
        assert self._check(chunk, user_role="maintenance_engineer") is True

    def test_wrong_role_denied(self):
        chunk = {"allowed_roles": ["manager"]}
        assert self._check(chunk, user_role="operator") is False

    def test_empty_roles_allows_all_authenticated(self):
        chunk = {"allowed_roles": []}
        assert self._check(chunk, user_role="operator") is True

    def test_missing_roles_key_allows_all_authenticated(self):
        chunk = {}
        assert self._check(chunk, user_role="operator") is True


# ─── search_documents integration test ────────────────────────────────────────

class TestSearchDocuments:
    """
    Integration test for search_documents().
    Builds a temporary vector store in-memory and patches the retriever's
    singleton to use it. Requires sentence-transformers.
    """

    @pytest.fixture(autouse=True)
    def setup_temp_store(self, tmp_path, monkeypatch):
        try:
            from rag.embeddings.embedder      import Embedder
            from rag.vector_store.faiss_store import FAISSVectorStore
        except ImportError:
            pytest.skip("sentence-transformers or faiss not installed")

        chunks = [
            {
                "chunk_id": "maint_p1_c0", "document_id": "maint_report_p101",
                "title": "Maintenance Report", "page": 1,
                "text": "Bearing temperature rose to 87°C on 28 May, exceeding the 85°C alarm threshold.",
                "equipment": "Pump P-101", "document_type": "maintenance",
                "classification": "internal", "source_file": "maintenance_report_p101.pdf",
                "allowed_roles": ["maintenance_engineer", "manager"], "total_pages": 10,
            },
            {
                "chunk_id": "manual_p3_c0", "document_id": "equip_manual_p101",
                "title": "Equipment Manual", "page": 3,
                "text": "Do not operate pump with bearing temperature above 85°C. Initiate shutdown.",
                "equipment": "Pump P-101", "document_type": "manual",
                "classification": "internal", "source_file": "equipment_manual_p101.pdf",
                "allowed_roles": ["operator", "maintenance_engineer"], "total_pages": 20,
            },
            {
                "chunk_id": "incident_p2_c0", "document_id": "incident_p101_2024",
                "title": "Incident Report", "page": 2,
                "text": "DCS trip bypass resulted in bearing seizure and crude oil fire.",
                "equipment": "Pump P-101", "document_type": "incident",
                "classification": "confidential", "source_file": "incident_report_p101.pdf",
                "allowed_roles": ["safety_officer", "manager"], "total_pages": 8,
            },
        ]

        embedder = Embedder()
        store    = FAISSVectorStore()
        texts    = [c["text"] for c in chunks]
        vecs     = embedder.embed_batch(texts, show_progress=False)
        store.add(vecs, chunks)

        # Patch the retriever module's singletons
        import rag.retrieval.retriever as ret_mod
        monkeypatch.setattr(ret_mod, "_store",    store)
        monkeypatch.setattr(ret_mod, "_embedder", embedder)

    def test_returns_evidence_list(self):
        from rag.retrieval.retriever import search_documents
        result = search_documents("bearing temperature", user_role="maintenance_engineer")
        assert "evidence" in result
        assert isinstance(result["evidence"], list)

    def test_evidence_has_required_fields(self):
        from rag.retrieval.retriever import search_documents
        result = search_documents("bearing alarm", user_role="maintenance_engineer")
        for ev in result["evidence"]:
            for field in ["source", "page", "text", "score"]:
                assert field in ev, f"Missing field '{field}' in evidence"

    def test_role_filter_maintenance_engineer(self):
        """maintenance_engineer should NOT see confidential incident report."""
        from rag.retrieval.retriever import search_documents
        result   = search_documents("bearing fire incident", user_role="maintenance_engineer")
        sources  = [e["source"] for e in result["evidence"]]
        assert "incident_report_p101.pdf" not in sources

    def test_role_filter_safety_officer(self):
        """safety_officer should see incident report."""
        from rag.retrieval.retriever import search_documents
        result   = search_documents("DCS trip bypass bearing fire", user_role="safety_officer")
        sources  = [e["source"] for e in result["evidence"]]
        assert "incident_report_p101.pdf" in sources

    def test_none_role_sees_all(self):
        """Passing role=None bypasses access control — backend trusted call."""
        from rag.retrieval.retriever import search_documents
        result  = search_documents("bearing fire DCS bypass", user_role=None)
        sources = [e["source"] for e in result["evidence"]]
        assert "incident_report_p101.pdf" in sources

    def test_top_k_respected(self):
        from rag.retrieval.retriever import search_documents
        result = search_documents("pump", user_role=None, top_k=1)
        assert len(result["evidence"]) <= 1

    def test_empty_query_returns_empty(self):
        from rag.retrieval.retriever import search_documents
        result = search_documents("", user_role=None)
        assert result["evidence"] == []

    def test_score_between_0_and_1(self):
        from rag.retrieval.retriever import search_documents
        result = search_documents("bearing temperature", user_role=None)
        for ev in result["evidence"]:
            assert 0.0 <= ev["score"] <= 1.0 + 1e-4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
