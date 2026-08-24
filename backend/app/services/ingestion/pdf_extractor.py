"""
pdf_extractor.py
----------------
Extracts text content page-by-page from PDF files using PyMuPDF (fitz).
Preserves page numbers, total pages, and raw text.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any

import fitz  # PyMuPDF

logger = logging.getLogger(__name__)


def extract_pdf(pdf_path: str | Path) -> List[Dict[str, Any]]:
    """
    Extract text from every page of a PDF file.

    Returns list of dicts:
        {"page": int, "text": str, "total_pages": int}
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    if pdf_path.stat().st_size == 0:
        logger.warning("PDF file '%s' is empty (0 bytes) — skipping extraction.", pdf_path.name)
        return []

    logger.info("Extracting PDF: %s", pdf_path.name)

    pages: List[Dict[str, Any]] = []
    try:
        doc = fitz.open(str(pdf_path))
    except Exception as exc:
        logger.warning("Cannot open PDF '%s' (%s) — skipping extraction.", pdf_path.name, exc)
        return []

    total_pages = len(doc)
    for page_num, page in enumerate(doc, start=1):
        try:
            raw_text = page.get_text("text")  # type: ignore
        except Exception as exc:
            logger.warning("Failed to extract page %d: %s", page_num, exc)
            raw_text = ""

        pages.append({
            "page": page_num,
            "text": raw_text,
            "total_pages": total_pages,
        })

    doc.close()
    logger.info("Extracted %d pages from '%s'", total_pages, pdf_path.name)
    return pages
