"""
chunker.py
----------
Sliding-window character chunker.
Preserves page numbers, document_id, filename, chunk indices, and source metadata.
"""

import logging
from typing import List, Dict, Any

from app.core.config import settings

logger = logging.getLogger(__name__)


def chunk_document(
    pages: List[Dict[str, Any]],
    doc_metadata: Dict[str, Any],
    chunk_size: int = settings.CHUNK_SIZE,
    chunk_overlap: int = settings.CHUNK_OVERLAP,
    min_length: int = 40,
) -> List[Dict[str, Any]]:
    """
    Chunk extracted pages into overlapping text windows.

    Each returned chunk dict includes:
        - chunk_id: "{doc_id}_p{page}_c{idx}"
        - document_id: str
        - filename: str
        - page: int
        - text: str
        - equipment: str
        - document_type: str
        - classification: str
        - allowed_roles: list
    """
    doc_id = doc_metadata.get("document_id", "doc_unknown")
    filename = doc_metadata.get("filename", "")
    all_chunks: List[Dict[str, Any]] = []

    for page_data in pages:
        page_num = page_data["page"]
        text = page_data["text"]

        if not text or len(text.strip()) < min_length:
            continue

        step = chunk_size - chunk_overlap
        if step <= 0:
            step = chunk_size

        chunk_index = 0
        start = 0

        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk_text = text[start:end].strip()

            if len(chunk_text) >= min_length:
                chunk_id = f"{doc_id}_p{page_num}_c{chunk_index}"
                chunk_meta = {
                    "chunk_id": chunk_id,
                    "document_id": doc_id,
                    "filename": filename,
                    "page": page_num,
                    "text": chunk_text,
                    "title": doc_metadata.get("title", filename),
                    "equipment": doc_metadata.get("equipment", "Unknown"),
                    "document_type": doc_metadata.get("document_type", "general"),
                    "classification": doc_metadata.get("classification", "internal"),
                    "allowed_roles": doc_metadata.get("allowed_roles", []),
                    "source_file": filename,
                    "total_pages": page_data.get("total_pages", len(pages)),
                }
                all_chunks.append(chunk_meta)
                chunk_index += 1

            if end == len(text):
                break
            start += step

    logger.info(
        "Document '%s' → %d total chunks across %d pages",
        doc_id, len(all_chunks), len(pages),
    )
    return all_chunks
