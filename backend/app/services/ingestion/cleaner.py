"""
cleaner.py
----------
Text normalization and cleaning utilities for the RAG ingestion pipeline.
"""

import re
import unicodedata


def clean_text(raw_text: str) -> str:
    """Normalize whitespace, remove control chars, fix broken line-end hyphens."""
    if not raw_text:
        return ""

    text = unicodedata.normalize("NFC", raw_text)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    text = re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def is_meaningful(text: str, min_chars: int = 15) -> bool:
    """True if text contains enough readable words to be worth indexing."""
    if not text or len(text.strip()) < min_chars:
        return False
    words = re.findall(r"[A-Za-z0-9]{2,}", text)
    return len(words) >= 3
