"""
file_detector.py
----------------
Detects document and file types (Normal PDF, Scanned PDF, Images, Text)
for the multimodal ingestion pipeline.
"""

import os
import logging
from pathlib import Path
import fitz  # PyMuPDF

logger = logging.getLogger(__name__)

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp"}
TEXT_EXTENSIONS = {".txt", ".log", ".md", ".csv", ".json", ".docx", ".doc", ".pptx", ".ppt"}


def detect_file_type(file_path: str | Path) -> str:
    """
    Detect document file type.

    Returns:
        - "pdf_normal": Vector PDF with direct extractable text
        - "pdf_scanned": Scanned PDF containing image pages
        - "image": Raw image file (.png, .jpg, etc.)
        - "text": Plain text / markdown document
        - "unknown": Unrecognized extension
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = path.suffix.lower()

    if ext in IMAGE_EXTENSIONS:
        return "image"

    if ext in TEXT_EXTENSIONS:
        return "text"

    if ext == ".pdf":
        if path.stat().st_size == 0:
            return "pdf_scanned"

        try:
            doc = fitz.open(str(path))
            has_text = False
            for page in doc:
                text = page.get_text("text").strip()
                if len(text) > 20:
                    has_text = True
                    break
            doc.close()
            return "pdf_normal" if has_text else "pdf_scanned"
        except Exception as exc:
            logger.warning("Failed to analyze PDF structure for %s: %s", path.name, exc)
            return "pdf_scanned"

    return "unknown"
