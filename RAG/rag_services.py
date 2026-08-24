"""
rag_services.py
---------------
MRPL RAG Pipeline — Public API Surface
======================================
This is the ONLY file Sharun (Backend) needs to import.

Usage
-----
    from rag_services import search_documents, ingest_pdf, get_store_stats

All heavy dependencies (FAISS, sentence-transformers) are loaded lazily on
the first call, so importing this module is lightweight.

Author:  Meenaloshini — RAG Engineer, SIH26117
Project: Sovereign On-Premise Agentic AI Workbench (MRPL)
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# ── Make sure the RAG package is importable regardless of CWD ─────────────────
_HERE = Path(__file__).parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

logging.basicConfig(
    level   = logging.INFO,
    format  = "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt = "%H:%M:%S",
)
logger = logging.getLogger("rag_services")


# ══════════════════════════════════════════════════════════════════════════════
# PUBLIC API
# ══════════════════════════════════════════════════════════════════════════════

def search_documents(
    query:     str,
    user_role: Optional[str] = None,
    top_k:     int = 5,
) -> Dict[str, Any]:
    """
    Search the RAG knowledge base.

    Parameters
    ----------
    query : str
        Natural-language question, e.g. "bearing temperature exceeded in P-101".
    user_role : str | None
        Role of the requesting user:
          - ``"maintenance_engineer"``
          - ``"operator"``
          - ``"safety_officer"``
          - ``"manager"``
          - ``None``  →  bypass access control (trusted backend call)
    top_k : int
        Maximum number of evidence chunks to return (default 5).

    Returns
    -------
    dict
        ::

            {
                "query":   "bearing temperature exceeded in P-101",
                "role":    "maintenance_engineer",
                "evidence": [
                    {
                        "source":        "maintenance_report_p101.pdf",
                        "page":          3,
                        "text":          "… bearing temp rose to 92°C …",
                        "score":         0.91,
                        "document_id":   "maint_report_p101",
                        "title":         "Pump P-101 Maintenance Report",
                        "equipment":     "Pump P-101",
                        "document_type": "maintenance",
                        "classification":"internal",
                    },
                    …
                ],
                "total_found":    12,
                "total_returned":  5,
            }

    Raises
    ------
    RuntimeError
        If the vector store hasn't been built yet. Run::

            python ingest_documents.py --pdf_dir data/demo/
    """
    from rag.retrieval.retriever import search_documents as _search
    return _search(query=query, user_role=user_role, top_k=top_k)


def ingest_pdf(
    pdf_path: str | Path,
    metadata: Dict[str, Any],
    reset_store: bool = False,
) -> Dict[str, Any]:
    """
    Ingest a single PDF into the vector store.

    Parameters
    ----------
    pdf_path : str | Path
        Path to the PDF file.
    metadata : dict
        Document-level metadata. Must include:
          - ``document_id``   (str, unique)
          - ``title``         (str)
          - ``equipment``     (str)
          - ``document_type`` (str)  e.g. "maintenance" | "sop" | "manual" | "incident"
          - ``classification``(str)  e.g. "internal" | "confidential"
          - ``allowed_roles`` (list) e.g. ["maintenance_engineer", "manager"]
    reset_store : bool
        If True, wipe the existing index before adding this document.
        Useful when re-ingesting from scratch.

    Returns
    -------
    dict
        ``{"status": "ok", "chunks_added": N, "document_id": "..."}``
    """
    from rag.ingestion.pdf_extractor import extract_pdf
    from rag.ingestion.cleaner       import clean_text, is_meaningful
    from rag.ingestion.chunker       import chunk_document
    from rag.embeddings.embedder     import Embedder
    from rag.vector_store.chroma_store import ChromaVectorStore

    pdf_path = Path(pdf_path)

    # 1. Load or reset store
    store = ChromaVectorStore()
    if reset_store:
        store.reset()

    # 2. Extract & clean
    raw_pages   = extract_pdf(pdf_path)
    clean_pages = []
    for p in raw_pages:
        ct = clean_text(p["text"])
        if is_meaningful(ct):
            clean_pages.append({**p, "text": ct})

    # 3. Build metadata per page
    doc_meta = {
        **metadata,
        "source_file": pdf_path.name,
    }

    # 4. Chunk
    chunks = chunk_document(clean_pages, doc_meta)

    if not chunks:
        logger.warning("No usable chunks extracted from %s", pdf_path.name)
        return {"status": "ok", "chunks_added": 0, "document_id": metadata.get("document_id")}

    # 5. Embed
    embedder = Embedder()
    texts    = [c["text"] for c in chunks]
    vecs     = embedder.embed_batch(texts)

    # 6. Add + save (ChromaDB auto-persists)
    store.add(vecs, chunks)

    logger.info(
        "Ingested '%s': %d chunks -> ChromaDB (%d total)",
        pdf_path.name, len(chunks), len(store),
    )

    # Invalidate the retriever's cached store handle
    from rag.retrieval.retriever import _reload_store
    _reload_store()

    return {
        "status":       "ok",
        "chunks_added": len(chunks),
        "document_id":  metadata.get("document_id"),
    }


def get_store_stats() -> Dict[str, Any]:
    """
    Return statistics about the current ChromaDB vector store.

    Returns
    -------
    dict
        ``{"total_vectors": N, "db_dir": "...", "backend": "chroma"}``
    """
    from rag.config import CHROMA_DB_DIR

    stats: Dict[str, Any] = {
        "backend":       "chroma",
        "db_dir":        str(CHROMA_DB_DIR),
        "db_exists":     CHROMA_DB_DIR.exists(),
        "total_vectors": 0,
    }

    if CHROMA_DB_DIR.exists():
        try:
            from rag.vector_store.chroma_store import ChromaVectorStore
            store = ChromaVectorStore()
            stats["total_vectors"] = len(store)
        except Exception as exc:
            stats["error"] = str(exc)

    return stats


# ══════════════════════════════════════════════════════════════════════════════
# Quick smoke-test when run directly
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import json
    print("-" * 60)
    print("RAG Services - smoke test")
    print("-" * 60)

    stats = get_store_stats()
    print(f"Store stats: {json.dumps(stats, indent=2)}")

    if stats["total_vectors"] == 0:
        print("\n[WARNING] Vector store is empty.")
        print("   Run:  python ingest_documents.py --pdf_dir data/demo/")
    else:
        result = search_documents(
            "bearing temperature exceeded",
            user_role="maintenance_engineer",
            top_k=3,
        )
        print(f"\nSearch result:\n{json.dumps(result, indent=2)}")
