"""
chunker.py
----------
Sliding-window text chunker.

Splits a page's cleaned text into overlapping chunks so that:
  - Each chunk fits within the embedding model's context window
  - Context at chunk boundaries is preserved via overlap
  - Every chunk inherits its parent page's metadata

Chunk schema
------------
{
    "chunk_id":      str,   # "{document_id}_p{page}_c{chunk_index}"
    "document_id":   str,
    "title":         str,
    "page":          int,
    "chunk_index":   int,   # 0-indexed within the page
    "text":          str,
    "equipment":     str,
    "document_type": str,
    "classification":str,
    "allowed_roles": list[str],
    "source_file":   str,
    "total_pages":   int,
}
"""

import logging
from typing import List, Dict, Any

from rag.config import CHUNK_SIZE, CHUNK_OVERLAP, MIN_CHUNK_LENGTH

logger = logging.getLogger(__name__)


def chunk_text(
    text: str,
    page_metadata: Dict[str, Any],
    chunk_size:    int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> List[Dict[str, Any]]:
    """
    Split *text* into overlapping character-based chunks.

    Parameters
    ----------
    text : str
        Cleaned text for a single PDF page.
    page_metadata : dict
        Must contain at minimum:
          - ``document_id``, ``title``, ``page``, ``equipment``,
            ``document_type``, ``classification``, ``allowed_roles``,
            ``source_file``, ``total_pages``
    chunk_size : int
        Maximum character length of each chunk.
    chunk_overlap : int
        Number of characters to overlap between consecutive chunks.

    Returns
    -------
    List[Dict]
        List of chunk dicts, each with all metadata fields plus ``text``.
    """
    if not text or len(text.strip()) < MIN_CHUNK_LENGTH:
        return []

    chunks: List[Dict[str, Any]] = []
    start  = 0
    idx    = 0
    step   = max(1, chunk_size - chunk_overlap)  # guard against zero step

    while start < len(text):
        end       = start + chunk_size
        chunk_str = text[start:end].strip()

        if len(chunk_str) >= MIN_CHUNK_LENGTH:
            doc_id   = page_metadata.get("document_id", "unknown")
            page_num = page_metadata.get("page", 0)

            chunk = {
                "chunk_id":      f"{doc_id}_p{page_num}_c{idx}",
                "chunk_index":   idx,
                "text":          chunk_str,
                # ── carry all metadata fields forward ──
                "document_id":   doc_id,
                "title":         page_metadata.get("title", ""),
                "page":          page_num,
                "equipment":     page_metadata.get("equipment", ""),
                "document_type": page_metadata.get("document_type", ""),
                "classification":page_metadata.get("classification", "internal"),
                "allowed_roles": page_metadata.get("allowed_roles", []),
                "source_file":   page_metadata.get("source_file", ""),
                "total_pages":   page_metadata.get("total_pages", 0),
            }
            chunks.append(chunk)
            idx += 1

        start += step

    logger.debug(
        "Page %d → %d chunks",
        page_metadata.get("page", 0),
        len(chunks),
    )
    return chunks


def chunk_document(
    pages: List[Dict[str, Any]],
    doc_metadata: Dict[str, Any],
    chunk_size:   int = CHUNK_SIZE,
    chunk_overlap:int = CHUNK_OVERLAP,
) -> List[Dict[str, Any]]:
    """
    Convenience wrapper: chunk all pages of a document.

    Parameters
    ----------
    pages : List[Dict]
        As returned by ``pdf_extractor.extract_pdf`` (cleaned).
    doc_metadata : dict
        Document-level metadata (``document_id``, ``title``, etc.).
        Per-page fields (``page``, ``total_pages``) are merged per page.

    Returns
    -------
    List[Dict]
        Flat list of all chunks across all pages.
    """
    all_chunks: List[Dict[str, Any]] = []

    for page_data in pages:
        page_meta = {**doc_metadata, **page_data}
        # ``page_data`` contains ``page``, ``text``, ``total_pages``
        # We don't want ``text`` at the top level of meta — it's already the input
        page_text = page_meta.pop("text", "")

        page_chunks = chunk_text(
            text          = page_text,
            page_metadata = page_meta,
            chunk_size    = chunk_size,
            chunk_overlap = chunk_overlap,
        )
        all_chunks.extend(page_chunks)

    logger.info(
        "Document '%s' → %d total chunks across %d pages",
        doc_metadata.get("document_id", "?"),
        len(all_chunks),
        len(pages),
    )
    return all_chunks
