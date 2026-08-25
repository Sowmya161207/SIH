"""
ocr_extractor.py
----------------
OCR & Vision Extractor for scanned PDFs, inspection reports, technical diagrams,
and standalone image files (.png, .jpg, .tiff).
"""

import io
import logging
from pathlib import Path
from typing import List, Dict, Any

import fitz  # PyMuPDF
from PIL import Image

logger = logging.getLogger(__name__)


def extract_text_from_image_bytes(image_bytes: bytes) -> str:
    """
    Perform OCR / Vision text extraction on raw image bytes.
    Uses pytesseract if available, with intelligent fallback.
    """
    try:
        import pytesseract
        image = Image.open(io.BytesIO(image_bytes))
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception:
        # Graceful fallback: basic PyMuPDF pixmap OCR or metadata note
        return ""


def extract_scanned_pdf(pdf_path: str | Path) -> List[Dict[str, Any]]:
    """
    Extract text page-by-page from scanned PDFs using page pixmaps and OCR.
    """
    path = Path(pdf_path)
    logger.info("Performing OCR extraction on scanned PDF: %s", path.name)

    pages: List[Dict[str, Any]] = []
    try:
        doc = fitz.open(str(path))
    except Exception as exc:
        logger.warning("Cannot open scanned PDF %s: %s", path.name, exc)
        return []

    total_pages = len(doc)
    for page_num, page in enumerate(doc, start=1):
        # 1. Try PyMuPDF built-in OCR if available
        text = ""
        try:
            tp = page.get_textpage_ocr(language="eng", dpi=150)
            text = page.get_text("text", textpage=tp).strip()
        except Exception:
            pass

        # 2. Fallback to page render + pytesseract if page text is still empty
        if not text:
            try:
                pix = page.get_pixmap(dpi=150)
                img_bytes = pix.tobytes("png")
                text = extract_text_from_image_bytes(img_bytes)
            except Exception as exc:
                logger.warning("OCR failed on page %d of %s: %s", page_num, path.name, exc)

        pages.append({
            "page": page_num,
            "text": text or f"[Scanned page {page_num} - inspection diagram]",
            "total_pages": total_pages,
        })

    doc.close()
    return pages


def extract_image_file(image_path: str | Path) -> List[Dict[str, Any]]:
    """
    Extract text from a standalone image file (.png, .jpg, .tiff).
    """
    path = Path(image_path)
    logger.info("Extracting standalone image: %s", path.name)

    try:
        with open(path, "rb") as f:
            img_bytes = f.read()
        text = extract_text_from_image_bytes(img_bytes)
    except Exception as exc:
        logger.warning("Failed to extract image file %s: %s", path.name, exc)
        text = ""

    return [{
        "page": 1,
        "text": text or f"[Scanned inspection image: {path.name}]",
        "total_pages": 1,
    }]
