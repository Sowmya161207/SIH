"""
model_router.py
---------------
Selects the optimal local Ollama model for a given task intent.

Model routing policy:
  - code / coding tasks  → codellama:7b  (code-specialized)
  - vision / image tasks → llava:7b       (multimodal vision)
  - document / RAG tasks → llama3.1:8b   (instruction-following)
  - general questions    → llama3.1:8b   (default)

The router is intentionally decoupled from config so it can be
changed independently. If a requested model is unavailable in Ollama,
it falls back to the default model gracefully.
"""

import logging
from typing import Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Intent → Model mapping
# ---------------------------------------------------------------------------

INTENT_MODEL_MAP: dict[str, str] = {
    # Code tasks
    "code":              settings.OLLAMA_CODE_MODEL,
    "coding_qa":         settings.OLLAMA_CODE_MODEL,
    "code_generation":   settings.OLLAMA_CODE_MODEL,
    "code_review":       settings.OLLAMA_CODE_MODEL,
    "debugging":         settings.OLLAMA_CODE_MODEL,

    # Vision / multimodal tasks
    "vision":            settings.OLLAMA_VISION_MODEL,
    "image_qa":          settings.OLLAMA_VISION_MODEL,
    "drawing_analysis":  settings.OLLAMA_VISION_MODEL,
    "ocr_understanding": settings.OLLAMA_VISION_MODEL,

    # Document / RAG tasks (default model)
    "document_qa":             settings.OLLAMA_MODEL,
    "document_summarization":  settings.OLLAMA_MODEL,
    "document_comparison":     settings.OLLAMA_MODEL,
    "rag":                     settings.OLLAMA_MODEL,
    "general_qa":              settings.OLLAMA_MODEL,
    "web_search_qa":           settings.OLLAMA_MODEL,
    "clarification":           settings.OLLAMA_MODEL,
}

# Keywords that signal a coding task when intent is not explicitly known
_CODE_KEYWORDS = {
    "code", "function", "script", "python", "java", "javascript",
    "typescript", "sql", "debug", "error", "bug", "implement",
    "algorithm", "program", "write a", "fix this", "refactor",
    "class", "def ", "lambda", "loop", "recursion", "api endpoint",
}

_VISION_KEYWORDS = {
    "drawing", "diagram", "image", "picture", "photo", "p&id",
    "piping", "schematic", "sketch", "figure", "chart", "graph",
    "engineering drawing", "inspect", "what is in this",
}


def detect_intent(message: str) -> str:
    """
    Lightweight intent classifier based on keyword matching.
    Used as a fast fallback when the planner doesn't provide intent.
    """
    lower = message.lower()

    for kw in _CODE_KEYWORDS:
        if kw in lower:
            return "code"

    for kw in _VISION_KEYWORDS:
        if kw in lower:
            return "vision"

    for kw in ("summarize", "summary", "tldr"):
        if kw in lower:
            return "document_summarization"

    for kw in ("compare", "difference between", "vs "):
        if kw in lower:
            return "document_comparison"

    for kw in ("document", "pdf", "report", "manual", "uploaded", "file"):
        if kw in lower:
            return "document_qa"

    return "general_qa"


def get_model_for_intent(intent: Optional[str], message: str = "") -> str:
    """
    Return the Ollama model name best suited for the given intent.
    Falls back to intent detection from the raw message if intent is None.

    Parameters
    ----------
    intent : str | None
        Intent string from the planner (e.g. 'code', 'document_qa').
    message : str
        Raw user message — used for fallback keyword detection.

    Returns
    -------
    str
        Ollama model name (e.g. 'codellama:7b', 'llava:7b', 'llama3.1:8b').
    """
    resolved_intent = intent or detect_intent(message)
    model = INTENT_MODEL_MAP.get(resolved_intent, settings.OLLAMA_MODEL)

    logger.info(
        "[ModelRouter] intent='%s' → model='%s'",
        resolved_intent, model,
    )
    return model


async def is_model_available(model_name: str) -> bool:
    """
    Check if a given model is pulled in Ollama.
    Returns True if available, False otherwise (caller should fallback).
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get("http://127.0.0.1:11434/api/tags")
            resp.raise_for_status()
            models = [m["name"] for m in resp.json().get("models", [])]
            # Match by prefix (e.g. "codellama:7b" matches "codellama:7b-instruct")
            base = model_name.split(":")[0]
            return any(base in m for m in models)
    except Exception:
        return False


async def get_available_model(intent: Optional[str], message: str = "") -> str:
    """
    Like get_model_for_intent() but verifies the model is pulled in Ollama.
    Falls back to the default model if the preferred one isn't available.
    """
    preferred = get_model_for_intent(intent, message)

    if preferred == settings.OLLAMA_MODEL:
        return preferred  # Default always assumed available

    if await is_model_available(preferred):
        return preferred

    logger.warning(
        "[ModelRouter] Model '%s' not found in Ollama — falling back to '%s'. "
        "Run: ollama pull %s",
        preferred, settings.OLLAMA_MODEL, preferred,
    )
    return settings.OLLAMA_MODEL
