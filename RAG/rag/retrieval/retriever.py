"""
retriever.py
------------
Permission-aware & evidence-grounded similarity search for the MRPL RAG pipeline.
Vector store backend: ChromaDB (persistent, cosine similarity).

Public API
----------
    search_documents(query, user_role=None, top_k=5, document_ids=None, min_score=0.35) -> dict
"""

import logging
from typing import Any, Dict, List, Optional

from rag.config import DEFAULT_TOP_K
from rag.embeddings.embedder import Embedder
from rag.vector_store.chroma_store import ChromaVectorStore

logger = logging.getLogger(__name__)

# ─── Singletons — loaded once per process ─────────────────────────────────────
_embedder: Optional[Embedder]          = None
_store:    Optional[ChromaVectorStore] = None


def _get_embedder() -> Embedder:
    global _embedder
    if _embedder is None:
        _embedder = Embedder()
    return _embedder


def _get_store() -> ChromaVectorStore:
    global _store
    if _store is None:
        _store = ChromaVectorStore()
        if len(_store) == 0:
            raise RuntimeError(
                "ChromaDB collection is empty. "
                "Run ingestion first:  python ingest_documents.py --pdf_dir data/demo/"
            )
    return _store


def _reload_store() -> None:
    """Force reload of the vector store (call after re-ingestion)."""
    global _store
    _store = None
    logger.info("ChromaDB store cache cleared — will reload on next query.")


# ─── Permission check ─────────────────────────────────────────────────────────

def _is_accessible(chunk: Dict[str, Any], user_role: Optional[str]) -> bool:
    """Check role-based access control."""
    if user_role is None:
        return True
    allowed: List[str] = chunk.get("allowed_roles", [])
    if not allowed:
        return True
    return user_role in allowed or user_role == "manager"


# ─── Main search function ─────────────────────────────────────────────────────

def search_documents(
    query:        str,
    user_role:    Optional[str] = None,
    top_k:        int = DEFAULT_TOP_K,
    document_ids: Optional[List[str]] = None,
    min_score:    float = 0.35,
) -> Dict[str, Any]:
    """
    Search the RAG knowledge base and return permission-filtered & evidence-grounded results.

    If top retrieval score < min_score, returns an explicit "insufficient_evidence" response.
    """
    if not query or not query.strip():
        return _empty_response(query, user_role)

    # 1. Embed query
    embedder  = _get_embedder()
    query_vec = embedder.embed(query.strip())

    # 2. Vector search
    fetch_k = top_k * 4
    try:
        store = _get_store()
    except RuntimeError as exc:
        raise RuntimeError(str(exc)) from exc

    raw_results: List[Dict[str, Any]] = store.search(query_vec, top_k=fetch_k)
    total_found = len(raw_results)

    # 3. Document IDs filter
    if document_ids:
        doc_set = set(document_ids)
        raw_results = [c for c in raw_results if c.get("document_id") in doc_set]

    # 4. Permission filter
    filtered: List[Dict[str, Any]] = [
        chunk for chunk in raw_results
        if _is_accessible(chunk, user_role)
    ]

    # 5. Evidence grounding check against min_score threshold
    strong_chunks = [c for c in filtered if c.get("score", 0.0) >= min_score]

    if not strong_chunks:
        logger.warning(
            "Query '%s' returned 0 chunks meeting min_score threshold %.2f",
            query[:50], min_score
        )
        return {
            "status":         "insufficient_evidence",
            "query":          query,
            "role":           user_role,
            "evidence":       [],
            "total_found":    total_found,
            "total_returned": 0,
            "message":        "Insufficient evidence found in knowledge base.",
        }

    # 6. Build evidence list up to top_k
    trimmed = strong_chunks[:top_k]
    evidence: List[Dict[str, Any]] = []
    for chunk in trimmed:
        evidence.append({
            "source":         chunk.get("source_file") or chunk.get("filename", ""),
            "page":           chunk.get("page", 1),
            "text":           chunk.get("text", ""),
            "score":          float(round(chunk.get("score", 0.0), 4)),
            "document_id":    chunk.get("document_id", ""),
            "title":          chunk.get("title", ""),
            "equipment":      chunk.get("equipment", ""),
            "document_type":  chunk.get("document_type", ""),
            "classification": chunk.get("classification", ""),
        })

    logger.info(
        "Query: '%s' | role=%s | found=%d | returned=%d",
        query[:60], user_role, total_found, len(evidence),
    )

    return {
        "status":         "success",
        "query":          query,
        "role":           user_role,
        "evidence":       evidence,
        "total_found":    total_found,
        "total_returned": len(evidence),
    }


def _empty_response(query: str, user_role: Optional[str]) -> Dict[str, Any]:
    return {
        "status":         "insufficient_evidence",
        "query":          query,
        "role":           user_role,
        "evidence":       [],
        "total_found":    0,
        "total_returned": 0,
        "message":        "Empty query provided.",
    }
