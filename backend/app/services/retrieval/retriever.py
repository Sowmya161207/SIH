"""
retriever.py
------------
Retrieval service supporting semantic similarity search, document_ids filtering,
role-based access control (ACL), and exact required output schemas.
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

    return user_role in allowed or user_role == "manager"


class Retriever:
    """Retriever service executing embedding + similarity search + ACL & document_ids filtering."""

    def __init__(self, store: Optional[VectorStore] = None, embedder: Optional[Embedder] = None):
        self.store = store or VectorStore()
        self.embedder = embedder or Embedder()

    def search(
        self,
        query: str,
        document_ids: Optional[List[str]] = None,
        user_role: Optional[str] = None,
        top_k: int = settings.DEFAULT_TOP_K,
    ) -> List[Dict[str, Any]]:
        """
        Execute semantic search.

        Returns list of dicts with exact required schema:
        [
          {
            "content": "...",
            "document_id": "...",
            "source": "...",
            "page": 1,
            "score": 0.92
          }
        ]
        """
        if not query or not query.strip():
            return []

        query_vec = self.embedder.embed(query)
        candidates = self.store.search(query_vec, top_k=top_k * 4)

        # 1. Document IDs filter
        if document_ids:
            doc_set = set(document_ids)
            candidates = [c for c in candidates if c.get("document_id") in doc_set]

        # 2. ACL Role filter
        accessible = [c for c in candidates if _is_accessible(c, user_role)]
        evidence_list = accessible[:top_k]

        results = []
        for c in evidence_list:
            results.append({
                "content": c.get("text", ""),
                "document_id": c.get("document_id", ""),
                "source": c.get("filename") or c.get("source_file", "unknown.pdf"),
                "page": c.get("page", 1),
                "score": float(round(c.get("score", 0.0), 4)),
            })

        logger.info(
            "Search query: '%s' | docs_filter=%s | role=%s | returned=%d",
            query, document_ids, user_role, len(results),
        )

        return results
