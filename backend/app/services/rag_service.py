"""
rag_service.py
--------------
Unified RAG service interface for the backend team.

Clean interfaces:
    ingest_document(document_id, file_path, metadata=None)
    retrieve(query, user_role=None, top_k=5)
    get_store_stats()
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from app.core.config import settings
from app.services.embeddings.embedder import Embedder
from app.services.ingestion.pdf_extractor import extract_pdf
from app.services.ingestion.cleaner import clean_text, is_meaningful
from app.services.ingestion.chunker import chunk_document
from app.services.retrieval.vector_store import VectorStore
from app.services.retrieval.retriever import Retriever

logger = logging.getLogger(__name__)

_store: Optional[VectorStore] = None
_retriever: Optional[Retriever] = None
_embedder: Optional[Embedder] = None


def _get_components():
    global _store, _retriever, _embedder
    if _store is None:
        _store = VectorStore()
    if _embedder is None:
        _embedder = Embedder()
    if _retriever is None:
        _retriever = Retriever(store=_store, embedder=_embedder)
    return _store, _retriever, _embedder


def ingest_document(
    document_id: str,
    file_path: str | Path,
    metadata: Optional[Dict[str, Any]] = None,
    reset_store: bool = False,
) -> Dict[str, Any]:
    """
    Ingest a PDF document into the RAG vector store.

    Parameters:
        document_id: str - Safe unique identifier
        file_path: str | Path - Path to saved PDF file on disk
        metadata: dict (optional) - Additional document attributes
        reset_store: bool - Wipe index before adding (optional)

    Returns:
        {"status": "ok", "chunks_added": N, "document_id": document_id}
    """
    store, _, embedder = _get_components()
    pdf_path = Path(file_path)

    if reset_store:
        store.reset()

    # 1. Extract raw pages
    raw_pages = extract_pdf(pdf_path)

    # 2. Clean pages
    clean_pages = []
    for p in raw_pages:
        ct = clean_text(p["text"])
        if is_meaningful(ct):
            clean_pages.append({**p, "text": ct})

    # 3. Assemble document metadata
    doc_meta = {
        **(metadata or {}),
        "document_id": document_id,
        "filename": metadata.get("filename") if metadata and metadata.get("filename") else pdf_path.name,
        "source_file": pdf_path.name,
    }

    # 4. Chunk
    chunks = chunk_document(clean_pages, doc_meta)

    if not chunks:
        logger.warning("No usable text chunks extracted from %s", pdf_path.name)
        return {"status": "ok", "chunks_added": 0, "document_id": document_id}

    # 5. Embed
    texts = [c["text"] for c in chunks]
    vecs = embedder.embed_batch(texts, show_progress=False)

    # 6. Store
    store.add(vecs, chunks)
    logger.info("Ingested '%s' (ID: %s): %d chunks → VectorStore", pdf_path.name, document_id, len(chunks))

    return {
        "status": "ok",
        "chunks_added": len(chunks),
        "document_id": document_id,
    }


def retrieve(
    query: str,
    user_role: Optional[str] = None,
    top_k: int = settings.DEFAULT_TOP_K,
) -> Dict[str, Any]:
    """
    Retrieve relevant permission-filtered chunks for a query string.
    """
    _, retriever, _ = _get_components()
    return retriever.search(query=query, user_role=user_role, top_k=top_k)


def get_store_stats() -> Dict[str, Any]:
    """Return vector store stats."""
    store, _, _ = _get_components()
    db_path = Path(settings.CHROMA_DB_DIR)
    return {
        "backend": "chroma",
        "db_dir": str(db_path),
        "db_exists": db_path.exists(),
        "total_vectors": len(store),
    }
