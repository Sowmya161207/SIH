"""
pdf_extractor.py
----------------
Extracts text content page-by-page from PDF files using PyMuPDF (fitz)
with OCR fallback for scanned pages and inspection drawings.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any

import fitz  # PyMuPDF
from app.services.ingestion.ocr_extractor import extract_scanned_pdf

logger = logging.getLogger(__name__)


def extract_pdf(pdf_path: str | Path) -> List[Dict[str, Any]]:
    """
    Extract text from every page of a PDF file.
    Falls back to OCR if pages are scanned or image-only.
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
        logger.warning("Cannot open PDF '%s' (%s) — using OCR fallback.", pdf_path.name, exc)
        return extract_scanned_pdf(pdf_path)

    total_pages = len(doc)
    has_any_text = False

    for page_num, page in enumerate(doc, start=1):
        try:
            raw_text = page.get_text("text").strip()  # type: ignore
        except Exception as exc:
            logger.warning("Failed to extract page %d text: %s", page_num, exc)
            raw_text = ""

        if len(raw_text) > 10:
            has_any_text = True

        pages.append({
            "page": page_num,
            "text": raw_text,
            "total_pages": total_pages,
        })

    doc.close()

    # If the PDF contains no extractable text across pages, fallback to OCR
    if not has_any_text and total_pages > 0:
        logger.info("PDF '%s' has 0 extractable text — switching to OCR.", pdf_path.name)
        return extract_scanned_pdf(pdf_path)

    logger.info("Extracted %d pages from '%s'", total_pages, pdf_path.name)
    return pages
