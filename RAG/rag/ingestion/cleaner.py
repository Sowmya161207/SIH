"""
cleaner.py
----------
Text cleaning / normalization for extracted PDF text.

Handles common PDF artefacts:
  - Excessive whitespace and newlines
  - Hyphenated line-breaks (word-wrap artefacts)
  - Control characters and non-printable characters
  - Repeated header/footer lines (heuristic)
"""

import re
import unicodedata
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def clean_text(text: str) -> str:
    """
    Normalize raw text extracted from a PDF page.

    Parameters
    ----------
    text : str
        Raw text as returned by PyMuPDF ``page.get_text()``.

    Returns
    -------
    str
        Cleaned, normalized text ready for chunking.
    """
    if not text:
        return ""

    # 1. Unicode normalization (NFC)
    text = unicodedata.normalize("NFC", text)

    # 2. Replace non-breaking spaces and other Unicode spaces with regular space
    text = re.sub(r"[\u00a0\u200b\u200c\u200d\ufeff]", " ", text)

    # 3. Remove control characters (except newline and tab)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

    # 4. Fix hyphenated line breaks  (e.g. "main-\ntenance" → "maintenance")
    text = re.sub(r"-\s*\n\s*", "", text)

    # 5. Collapse multiple blank lines into a single blank line
    text = re.sub(r"\n{3,}", "\n\n", text)

    # 6. Remove lines that are purely whitespace
    lines = text.splitlines()
    lines = [line for line in lines if line.strip()]
    text = "\n".join(lines)

    # 7. Collapse multiple spaces into one
    text = re.sub(r"[ \t]{2,}", " ", text)

    # 8. Strip leading/trailing whitespace
    text = text.strip()

    return text


def is_meaningful(text: str, min_length: int = 20) -> bool:
    """
    Return True if the text contains enough meaningful content.

    Used to skip nearly-empty pages (e.g. blank pages, image-only pages).
    Requires at least some alphabetic characters (not just digits/punctuation).
    """
    stripped = text.strip()
    # Must have at least min_length characters and actual alphabetic word characters
    alpha_chars = len(re.findall(r"[a-zA-Z]", stripped))
    return len(stripped) >= min_length and alpha_chars >= 10
