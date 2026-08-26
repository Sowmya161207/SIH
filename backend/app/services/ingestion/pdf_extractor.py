"""
pdf_extractor.py
----------------
Extracts text content page-by-page from PDF files using PyMuPDF (fitz).

Strategy:
  - For each page, attempt direct text extraction first (fast, lossless).
  - If a page yields fewer than 20 meaningful characters, fall back to OCR
    for that page only (handles mixed text+scanned PDFs correctly).
  - If the entire document has no text, delegate to extract_scanned_pdf().
"""

import logging
from pathlib import Path
from typing import List, Dict, Any

import fitz  # PyMuPDF
from app.services.ingestion.ocr_extractor import (
    extract_scanned_pdf,
    extract_text_from_image_bytes,
)

logger = logging.getLogger(__name__)

# Minimum character count for a page to be considered "has text"
_MIN_TEXT_CHARS = 20


def extract_pdf(pdf_path: str | Path) -> List[Dict[str, Any]]:
    """
    Extract text from every page of a PDF file.

    Per-page OCR fallback:
      - Pages with <20 chars are re-rendered at 200 DPI and passed through OCR.
      - This correctly handles partially-scanned PDFs (mixed text + image pages).
    Whole-document fallback:
      - If *no* page has extractable text, delegates entirely to OCR pipeline.
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    if pdf_path.stat().st_size == 0:
        logger.warning(
            "PDF file '%s' is empty (0 bytes) — skipping extraction.",
            pdf_path.name,
        )
        return []

    logger.info("Extracting PDF: %s", pdf_path.name)

    try:
        doc = fitz.open(str(pdf_path))
    except Exception as exc:
        logger.warning(
            "Cannot open PDF '%s' (%s) — using full OCR fallback.",
            pdf_path.name, exc,
        )
        return extract_scanned_pdf(pdf_path)

    total_pages = len(doc)
    pages: List[Dict[str, Any]] = []
    text_pages_found = 0

    for page_num, page in enumerate(doc, start=1):
        # ---- Direct text extraction ----
        try:
            raw_text = page.get_text("text").strip()  # type: ignore[attr-defined]
        except Exception as exc:
            logger.warning("Failed to extract text from page %d: %s", page_num, exc)
            raw_text = ""

        # ---- Per-page OCR fallback ----
        if len(raw_text) < _MIN_TEXT_CHARS:
            logger.debug(
                "Page %d of '%s' has only %d chars — attempting per-page OCR.",
                page_num, pdf_path.name, len(raw_text),
            )
            try:
                pix = page.get_pixmap(dpi=200)
                img_bytes = pix.tobytes("png")
                ocr_text = extract_text_from_image_bytes(
                    img_bytes,
                    page_label=f"page {page_num} of {pdf_path.name}",
                )
                if ocr_text:
                    logger.debug(
                        "Per-page OCR succeeded for page %d: %d chars.",
                        page_num, len(ocr_text),
                    )
                    raw_text = ocr_text
            except Exception as exc:
                logger.warning(
                    "Per-page OCR failed for page %d of '%s': %s",
                    page_num, pdf_path.name, exc,
                )

        if len(raw_text) >= _MIN_TEXT_CHARS:
            text_pages_found += 1

        pages.append({
            "page": page_num,
            "text": raw_text,
            "total_pages": total_pages,
        })

    doc.close()

    if text_pages_found == 0 and total_pages > 0:
        # No text found on any page even after per-page OCR — full OCR pass
        logger.info(
            "PDF '%s' has 0 usable text pages — switching to full OCR pipeline.",
            pdf_path.name,
        )
        return extract_scanned_pdf(pdf_path)

    logger.info(
        "Extracted %d/%d pages with text from '%s'.",
        text_pages_found, total_pages, pdf_path.name,
    )
    return pages
