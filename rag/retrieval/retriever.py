"""
retriever.py
------------
Permission-aware similarity search for the MRPL RAG pipeline.
Vector store backend: ChromaDB (persistent, cosine similarity).

Public API
----------
    search_documents(query, workspace_id=None, user_role=None, top_k=5) -> dict

Return schema
-------------
    {
        "query":    str,
        "role":     str | None,
        "evidence": [
            {
                "source":        str,   # filename
                "page":          int,
                "text":          str,
                "score":         float, # cosine similarity 0-1
                "document_id":   str,
                "title":         str,
                "equipment":     str,
                "document_type": str,
                "classification":str,
                "has_images":    bool,
                "image_count":   int,
            },
            ...
        ],
        "total_found":    int,   # after ChromaDB query, before role filter
        "total_returned": int,   # after role filter, capped at top_k
    }

Permission model
----------------
If ``user_role`` is None  → all documents accessible (trusted backend call).
If ``user_role`` is a str → only chunks whose ``allowed_roles`` contains
that role are returned. Chunks with ``allowed_roles=[]`` are public to all
authenticated users.
"""

import logging
from typing import Any, Dict, List, Optional

from rag.config import DEFAULT_TOP_K
from rag.embeddings.embedder import Embedder
from rag.vector_store.chroma_store import ChromaVectorStore

logger = logging.getLogger(__name__)

# ─── Singletons — loaded once per process ─────────────────────────────────────
_embedder: Optional[Embedder]         = None
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
    """
    Return True if *user_role* can access this chunk.

    Rules
    -----
    - ``user_role`` is None  → open access (bypass all checks)
    - ``allowed_roles`` is [] → accessible by everyone
    - Otherwise, user_role must appear in allowed_roles
    """
    if user_role is None:
        return True
    allowed: List[str] = chunk.get("allowed_roles", [])
    if not allowed:
        return True
    return user_role in allowed


# ─── Main search function ─────────────────────────────────────────────────────

def search_documents(
    query:     str,
    workspace_id: Optional[str] = None,
    user_role: Optional[str] = None,
    top_k:     int = DEFAULT_TOP_K,
) -> Dict[str, Any]:
    """
    Search the RAG knowledge base and return permission-filtered evidence.

    Parameters
    ----------
    query : str
        Natural-language question or keyword string.
    workspace_id : str | None
        Optional workspace ID for strict boundary filtering.
    user_role : str | None
        The role of the requesting user (e.g. ``"maintenance_engineer"``).
        Pass ``None`` to bypass access control (useful in trusted back-end calls).
    top_k : int
        Maximum number of evidence chunks to return.

    Returns
    -------
    dict
        Schema described in the module docstring.

    Raises
    ------
    RuntimeError
        If the ChromaDB collection is empty (ingestion not yet run).
    """
    if not query or not query.strip():
        return _empty_response(query, user_role)

    # 1. Embed the query
    embedder  = _get_embedder()
    query_vec = embedder.embed(query.strip())

    # 2. ChromaDB search — over-fetch to absorb role-filter attrition
    fetch_k = top_k * 4
    try:
        store = _get_store()
    except RuntimeError as exc:
        raise RuntimeError(str(exc)) from exc

    where_filter = {}
    if workspace_id:
        where_filter["workspace_id"] = workspace_id

    raw_results: List[Dict[str, Any]] = store.search(
        query_vec, 
        top_k=fetch_k, 
        where_filter=where_filter if where_filter else None
    )
    total_found = len(raw_results)

    # 3. Permission filter
    filtered: List[Dict[str, Any]] = [
        chunk for chunk in raw_results
        if _is_accessible(chunk, user_role)
    ]

    # 4. Trim to top_k
    filtered = filtered[:top_k]

    # 5. Build safe evidence list
    evidence: List[Dict[str, Any]] = []
    for chunk in filtered:
        evidence.append({
            "source":         chunk.get("source_file", ""),
            "page":           chunk.get("page", 0),
            "text":           chunk.get("text", ""),
            "score":          chunk.get("score", 0.0),
            "document_id":    chunk.get("document_id", ""),
            "workspace_id":   chunk.get("workspace_id", ""),
            "title":          chunk.get("title", ""),
            "equipment":      chunk.get("equipment", ""),
            "document_type":  chunk.get("document_type", ""),
            "classification": chunk.get("classification", ""),
            "has_images":     chunk.get("has_images", False),
            "image_count":    chunk.get("image_count", 0),
        })

    logger.info(
        "Query: '%s' | role=%s | found=%d | after_filter=%d | returned=%d",
        query[:60], user_role, total_found, len(filtered), len(evidence),
    )

    return {
        "query":          query,
        "role":           user_role,
        "evidence":       evidence,
        "total_found":    total_found,
        "total_returned": len(evidence),
    }


def _empty_response(query: str, user_role: Optional[str]) -> Dict[str, Any]:
    return {
        "query":          query,
        "role":           user_role,
        "evidence":       [],
        "total_found":    0,
        "total_returned": 0,
    }
