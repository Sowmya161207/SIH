"""
retriever.py
------------
Retrieval service supporting semantic similarity search and role-based access control (ACL).
"""

import logging
from typing import Any, Dict, List, Optional

from app.core.config import settings
from app.services.embeddings.embedder import Embedder
from app.services.retrieval.vector_store import VectorStore

logger = logging.getLogger(__name__)


def _is_accessible(chunk: Dict[str, Any], user_role: Optional[str]) -> bool:
    """Check role-based access control."""
    if user_role is None:
        return True

    allowed = chunk.get("allowed_roles")
    if not allowed:
        return True

    if isinstance(allowed, str):
        allowed = [allowed]

    return user_role in allowed or "manager" in [user_role]


class Retriever:
    """Retriever service executing embedding + similarity search + ACL filtering."""

    def __init__(self, store: Optional[VectorStore] = None, embedder: Optional[Embedder] = None):
        self.store = store or VectorStore()
        self.embedder = embedder or Embedder()

    def search(
        self,
        query: str,
        user_role: Optional[str] = None,
        top_k: int = settings.DEFAULT_TOP_K,
    ) -> Dict[str, Any]:
        """
        Execute semantic search for query string.

        Returns:
            {
                "query": str,
                "role": str | None,
                "evidence": [
                    {
                        "source": str,
                        "page": int,
                        "text": str,
                        "score": float,
                        "document_id": str,
                        "filename": str,
                        "title": str,
                        "equipment": str,
                        "document_type": str,
                        "classification": str,
                    }, ...
                ],
                "total_found": int,
                "total_returned": int
            }
        """
        if not query or not query.strip():
            return {"query": query, "role": user_role, "evidence": [], "total_found": 0, "total_returned": 0}

        query_vec = self.embedder.embed(query)
        candidates = self.store.search(query_vec, top_k=top_k * 3)

        accessible = [c for c in candidates if _is_accessible(c, user_role)]
        evidence_list = accessible[:top_k]

        formatted_evidence = []
        for c in evidence_list:
            formatted_evidence.append({
                "source": c.get("filename") or c.get("source_file", "unknown.pdf"),
                "filename": c.get("filename") or c.get("source_file", "unknown.pdf"),
                "page": c.get("page", 1),
                "text": c.get("text", ""),
                "score": c.get("score", 0.0),
                "document_id": c.get("document_id", ""),
                "title": c.get("title", ""),
                "equipment": c.get("equipment", "Unknown"),
                "document_type": c.get("document_type", "general"),
                "classification": c.get("classification", "internal"),
            })

        logger.info(
            "Query: '%s' | role=%s | found=%d | returned=%d",
            query, user_role, len(candidates), len(formatted_evidence),
        )

        return {
            "query": query,
            "role": user_role,
            "evidence": formatted_evidence,
            "total_found": len(candidates),
            "total_returned": len(formatted_evidence),
        }
