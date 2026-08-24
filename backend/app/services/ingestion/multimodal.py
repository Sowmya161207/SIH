"""
multimodal.py
-------------
Clean extension interfaces for Multimodal (Images, Diagrams, P&IDs, Scanned Pages) ingestion.
Designed for PS 26117 to cleanly plug in OCR / Vision-Language Models (VLM) without breaking text RAG.
"""

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class ImageExtractorInterface(ABC):
    """Abstract interface for extracting images, diagrams, and P&ID drawings from PDFs."""

    @abstractmethod
    def extract_images(self, pdf_path: str | Path) -> List[Dict[str, Any]]:
        """
        Extract embedded images / drawings.
        Returns list of dicts: {"page": int, "image_bytes": bytes, "format": str, "bbox": tuple}
        """
        pass


class MultimodalExtractor:
    """
    Multimodal Document Extractor.
    Combines text extraction with extension hooks for OCR / P&ID visual indexing.
    """

    def __init__(self, image_extractor: Optional[ImageExtractorInterface] = None):
        self.image_extractor = image_extractor

    def process(self, pdf_path: str | Path) -> Dict[str, Any]:
        """
        Extract text and (optionally) images/diagrams from a document.
        """
        from app.services.ingestion.pdf_extractor import extract_pdf
        pages = extract_pdf(pdf_path)

        images = []
        if self.image_extractor:
            try:
                images = self.image_extractor.extract_images(pdf_path)
            except Exception as exc:
                logger.warning("Multimodal image extraction skipped: %s", exc)

        return {
            "text_pages": pages,
            "images": images,
            "has_multimodal": len(images) > 0,
        }
