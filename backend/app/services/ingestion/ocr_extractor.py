"""
ocr_extractor.py
----------------
OCR & Vision Extractor for scanned PDFs, inspection reports, technical diagrams,
and standalone image files (.png, .jpg, .tiff).

OCR engine priority:
  1. pytesseract (with auto-detected Tesseract path on Windows)
  2. easyocr (if installed)
  3. Placeholder text (graceful degradation)
"""

import io
import logging
import os
from pathlib import Path
from typing import List, Dict, Any

import fitz  # PyMuPDF
from PIL import Image

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tesseract path auto-detection for Windows
# ---------------------------------------------------------------------------

def _configure_tesseract() -> bool:
    """
    Try to configure pytesseract on Windows by finding the Tesseract binary
    and setting TESSDATA_PREFIX so language data files can be found.
    Returns True if pytesseract is usable, False otherwise.
    """
    try:
        import pytesseract

        # If already configured (e.g. in PATH), test it directly
        try:
            pytesseract.get_tesseract_version()
            return True
        except Exception:
            pass

        # Common Windows install locations
        candidate_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            r"C:\Users\{}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe".format(
                os.environ.get("USERNAME", "")
            ),
        ]

        for path in candidate_paths:
            if os.path.isfile(path):
                pytesseract.pytesseract.tesseract_cmd = path

                # Set TESSDATA_PREFIX so Tesseract can find language files.
                # Tesseract resolves: TESSDATA_PREFIX + "/eng.traineddata"
                # so the var must point to the tessdata/ directory itself.
                tessdata_dir = os.path.join(os.path.dirname(path), "tessdata")
                if os.path.isdir(tessdata_dir):
                    os.environ["TESSDATA_PREFIX"] = tessdata_dir
                    logger.info(
                        "TESSDATA_PREFIX set to: %s", tessdata_dir
                    )

                try:
                    pytesseract.get_tesseract_version()
                    logger.info("Tesseract found at: %s", path)
                    return True
                except Exception:
                    continue

        logger.warning(
            "Tesseract OCR binary not found. "
            "Install from: https://github.com/UB-Mannheim/tesseract/wiki "
            "and ensure it is in your PATH."
        )
        return False

    except ImportError:
        logger.warning("pytesseract not installed. Run: pip install pytesseract")
        return False


_TESSERACT_READY: bool | None = None  # cached result


def _tesseract_available() -> bool:
    """Lazily check and cache whether Tesseract is usable."""
    global _TESSERACT_READY
    if _TESSERACT_READY is None:
        _TESSERACT_READY = _configure_tesseract()
    return _TESSERACT_READY


# ---------------------------------------------------------------------------
# Core OCR function
# ---------------------------------------------------------------------------

def extract_text_from_image_bytes(image_bytes: bytes, page_label: str = "") -> str:
    """
    Perform OCR text extraction on raw image bytes.

    Engine priority:
      1. pytesseract (most accurate, requires Tesseract installed)
      2. easyocr (no system dependency, GPU-optional)
      3. Returns empty string (caller adds placeholder)

    Parameters
    ----------
    image_bytes : bytes
        Raw image data (PNG, JPEG, TIFF, etc.)
    page_label : str
        Human-readable label for log messages (e.g. "page 3 of report.pdf")
    """
    # ----- 1. Try pytesseract -----
    if _tesseract_available():
        try:
            import pytesseract
            image = Image.open(io.BytesIO(image_bytes))
            # Use LSTM engine with page segmentation mode 3 (auto)
            config = "--oem 1 --psm 3"
            text = pytesseract.image_to_string(image, config=config)
            text = text.strip()
            if text:
                logger.debug(
                    "pytesseract extracted %d chars from %s",
                    len(text), page_label or "image",
                )
                return text
        except Exception as exc:
            logger.warning("pytesseract OCR failed for %s: %s", page_label, exc)

    # ----- 2. Try easyocr -----
    try:
        import easyocr  # type: ignore
        reader = easyocr.Reader(["en"], gpu=False, verbose=False)
        image_array = Image.open(io.BytesIO(image_bytes))
        import numpy as np
        results = reader.readtext(np.array(image_array), detail=0)
        text = " ".join(results).strip()
        if text:
            logger.debug(
                "easyocr extracted %d chars from %s",
                len(text), page_label or "image",
            )
            return text
    except ImportError:
        pass  # easyocr not installed — skip silently
    except Exception as exc:
        logger.warning("easyocr failed for %s: %s", page_label, exc)

    logger.warning(
        "All OCR engines failed or unavailable for %s — returning empty.",
        page_label or "image",
    )
    return ""


# ---------------------------------------------------------------------------
# PDF-level OCR extractor
# ---------------------------------------------------------------------------

def extract_scanned_pdf(pdf_path: str | Path) -> List[Dict[str, Any]]:
    """
    Extract text page-by-page from scanned PDFs using page pixmaps and OCR.
    Uses 200 DPI for good accuracy without excessive memory usage.
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
        text = ""
        page_label = f"page {page_num} of {path.name}"

        # Render page at 200 DPI for good OCR accuracy
        try:
            pix = page.get_pixmap(dpi=200)
            img_bytes = pix.tobytes("png")
            text = extract_text_from_image_bytes(img_bytes, page_label=page_label)
        except Exception as exc:
            logger.warning("Failed to render %s for OCR: %s", page_label, exc)

        pages.append({
            "page": page_num,
            "text": text or f"[Scanned page {page_num} — OCR unavailable]",
            "total_pages": total_pages,
        })

    doc.close()
    logger.info(
        "OCR extraction complete for '%s': %d pages processed.",
        path.name, total_pages,
    )
    return pages


# ---------------------------------------------------------------------------
# Standalone image file extractor
# ---------------------------------------------------------------------------

def extract_image_file(image_path: str | Path) -> List[Dict[str, Any]]:
    """
    Extract text from a standalone image file (.png, .jpg, .tiff, etc.).
    """
    path = Path(image_path)
    logger.info("Extracting standalone image: %s", path.name)

    try:
        with open(path, "rb") as f:
            img_bytes = f.read()
        text = extract_text_from_image_bytes(img_bytes, page_label=path.name)
    except Exception as exc:
        logger.warning("Failed to read image file %s: %s", path.name, exc)
        text = ""

    return [{
        "page": 1,
        "text": text or f"[Scanned inspection image: {path.name} — OCR unavailable]",
        "total_pages": 1,
    }]
