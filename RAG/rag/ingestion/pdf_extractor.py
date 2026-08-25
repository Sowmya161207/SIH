"""
pdf_extractor.py
----------------
Extracts text content from PDF files page-by-page using PyMuPDF (fitz).

Returns a list of dicts, one per page:
    {
        "page": int,          # 1-indexed page number
        "text": str,          # raw text from that page
        "total_pages": int    # total page count in the document
    }
"""

import logging
from pathlib import Path
from typing import List, Dict, Any

import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io

logger = logging.getLogger(__name__)


def extract_pdf(pdf_path: str | Path) -> List[Dict[str, Any]]:
    """
    Extract text from every page of a PDF.

    Parameters
    ----------
    pdf_path : str | Path
        Absolute or relative path to the PDF file.

    Returns
    -------
    List[Dict]
        One dict per page with keys: ``page``, ``text``, ``total_pages``.

    Raises
    ------
    FileNotFoundError
        If the PDF does not exist at the given path.
    ValueError
        If the file cannot be opened as a valid PDF.
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
        image_list = page.get_images(full=True)
        has_images = len(image_list) > 0
        try:
            raw_text = page.get_text("text").strip()  # type: ignore[attr-defined]
            # Fallback to OCR if text is empty (scanned page)
            if not raw_text:
                logger.debug("Page %d has no extractable text, attempting OCR...", page_num)
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2)) # 2x resolution for better OCR
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                raw_text = pytesseract.image_to_string(img).strip()
                if raw_text:
                    logger.debug("Successfully extracted text via OCR for page %d.", page_num)
        except Exception as exc:
            logger.warning("Failed to extract page %d: %s", page_num, exc)
            raw_text = ""

        pages.append({
            "page":        page_num,
            "text":        raw_text,
            "total_pages": total_pages,
            "has_images":  has_images,
            "image_count": len(image_list),
        })

    doc.close()
    logger.info("Extracted %d pages from '%s'", total_pages, pdf_path.name)
    return pages
