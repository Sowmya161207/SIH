"""
rag_service.py
--------------
Unified RAG & Multimodal Document Intelligence Service.

Required Functions & Interfaces:
    ingest_document(document_id, file_path)
    process_document(document_id)
    retrieve(query, document_ids=None, top_k=5)
    build_evidence(claim, retrieved_chunk, confidence=None)
    get_store_stats()
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.core.config import settings
from app.services.embeddings.embedder import Embedder
from app.services.ingestion.file_detector import detect_file_type
from app.services.ingestion.pdf_extractor import extract_pdf
from app.services.ingestion.ocr_extractor import extract_scanned_pdf, extract_image_file
from app.services.ingestion.cleaner import clean_text, is_meaningful
from app.services.ingestion.chunker import chunk_document
from app.services.retrieval.vector_store import VectorStore
from app.services.retrieval.retriever import Retriever
from app.services.retrieval.evidence import build_evidence as _build_ev, attach_evidence_to_response

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
    Ingest a document (PDF, scanned PDF, image, or text) into the RAG vector store.

    Parameters:
        document_id: str - Safe unique identifier
        file_path: str | Path - Path to document file on disk
        metadata: dict (optional) - Additional document attributes
        reset_store: bool - Wipe index before adding (optional)

    Returns:
        {"status": "ok", "chunks_added": N, "document_id": document_id, "file_type": ftype}
    """
    store, _, embedder = _get_components()
    path = Path(file_path)

    if reset_store:
        store.reset()

    # 1. Detect file type
    ftype = detect_file_type(path)
    logger.info("Ingesting document %s (ID: %s, type: %s)", path.name, document_id, ftype)

    # 2. Extract pages based on detected type
    if ftype == "pdf_normal":
        raw_pages = extract_pdf(path)
    elif ftype == "pdf_scanned":
        raw_pages = extract_scanned_pdf(path)
    elif ftype == "image":
        raw_pages = extract_image_file(path)
    elif ftype == "text":
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                text_content = f.read()
            raw_pages = [{"page": 1, "text": text_content, "total_pages": 1}]
        except Exception:
            raw_pages = extract_pdf(path)
    else:
        raw_pages = extract_pdf(path)

    # 3. Clean text pages
    clean_pages = []
    for p in raw_pages:
        ct = clean_text(p["text"])
        if is_meaningful(ct) or len(p["text"].strip()) > 5:
            clean_pages.append({**p, "text": ct or p["text"].strip()})

    # 4. Assemble document metadata
    doc_meta = {
    **(metadata or {}),
    "document_id": document_id,
    "filename": (
        metadata.get("filename")
        if metadata and metadata.get("filename")
        else path.name
    ),
    "source_file": path.name,
    "file_type": ftype,
    "allowed_roles": (
        metadata.get("allowed_roles", [])
        if metadata
        else []
    ),
}
    # 5. Chunk
    chunks = chunk_document(clean_pages, doc_meta)

    if not chunks:
        logger.warning("No usable chunks extracted from %s", path.name)
        return {"status": "ok", "chunks_added": 0, "document_id": document_id, "file_type": ftype}

    # 6. Embed
    texts = [c["text"] for c in chunks]
    vecs = embedder.embed_batch(texts, show_progress=False)

    # 7. Store in ChromaDB
    store.add(vecs, chunks)
    logger.info("Ingested '%s' (ID: %s): %d chunks → VectorStore", path.name, document_id, len(chunks))

    return {
        "status": "ok",
        "chunks_added": len(chunks),
        "document_id": document_id,
        "file_type": ftype,
    }


def process_document(document_id: str) -> Dict[str, Any]:
    """
    Process document pipeline for a registered document ID.
    """
    logger.info("Processing document ID: %s", document_id)
    return {"status": "processed", "document_id": document_id}


def retrieve(
    query: str,
    document_ids: Optional[List[str]] = None,
    user_role: Optional[str] = None,
    top_k: int = settings.DEFAULT_TOP_K,
) -> List[Dict[str, Any]]:
    """
    Retrieve relevant evidence chunks.

    Returns:
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
    _, retriever, _ = _get_components()
    return retriever.search(
        query=query,
        document_ids=document_ids,
        user_role=user_role,
        top_k=top_k,
    )


def build_evidence(
    claim: str,
    retrieved_chunk: Dict[str, Any],
    confidence: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Construct a verified Evidence object for Santhosh's Orchestrator:
    {
      "claim": "...",
      "source_document": "...",
      "page": 1,
      "retrieved_text": "...",
      "confidence": 0.92
    }
    """
    return _build_ev(claim=claim, retrieved_chunk=retrieved_chunk, confidence=confidence)


def get_store_stats() -> Dict[str, Any]:
    """Return vector store statistics."""
    store, _, _ = _get_components()
    db_path = Path(settings.CHROMA_DB_DIR)
    return {
        "backend": "chroma",
        "db_dir": str(db_path),
        "db_exists": db_path.exists(),
        "total_vectors": len(store),
    }
