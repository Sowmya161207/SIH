"""
vision_service.py
------------------
Multimodal Vision Model Service using local LLaVA / Ollama vision models.
Capable of inspecting and summarizing engineering drawings, P&IDs,
scanned inspection photos, and technical schematics.
"""

import base64
import logging
from pathlib import Path
from typing import Optional, Dict, Any

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

OLLAMA_GENERATE_URL = "http://127.0.0.1:11434/api/generate"


async def analyze_image_with_vision(
    image_bytes: bytes,
    prompt: Optional[str] = None,
    filename: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Analyzes an image using local Ollama vision model (llava:7b).
    Falls back gracefully if llava is not pulled.

    Returns:
    {
        "description": str,
        "model_used": str,
        "success": bool
    }
    """
    default_prompt = (
        "You are an industrial engineering AI inspector. "
        "Analyze this engineering drawing, photograph, or document image. "
        "Identify key components, labels, equipment IDs, safety warnings, "
        "anomalies, or measurements visible."
    )
    user_prompt = prompt or default_prompt

    # Encode image bytes to base64 string for Ollama API
    img_b64 = base64.b64encode(image_bytes).decode("utf-8")

    payload = {
        "model": settings.OLLAMA_VISION_MODEL,
        "prompt": user_prompt,
        "images": [img_b64],
        "stream": False,
        "options": {
            "temperature": 0.1
        }
    }

    try:
        logger.info(
            "Sending image to local vision model '%s' (%s bytes)",
            settings.OLLAMA_VISION_MODEL, len(image_bytes),
        )

        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(OLLAMA_GENERATE_URL, json=payload)

            if resp.status_code == 404:  # Model not found in Ollama
                logger.warning(
                    "Vision model '%s' not pulled in Ollama. Run: ollama pull %s",
                    settings.OLLAMA_VISION_MODEL, settings.OLLAMA_VISION_MODEL,
                )
                return {
                    "description": (
                        f"[Vision Model '{settings.OLLAMA_VISION_MODEL}' not initialized in Ollama. "
                        f"Please run 'ollama pull {settings.OLLAMA_VISION_MODEL}' for multimodal analysis.]"
                    ),
                    "model_used": "none",
                    "success": False,
                }

            resp.raise_for_status()
            data = resp.json()
            description = data.get("response", "").strip()

            return {
                "description": description,
                "model_used": settings.OLLAMA_VISION_MODEL,
                "success": True,
            }

    except Exception as exc:
        logger.error("Local Vision analysis error for %s: %s", filename or "image", exc)
        return {
            "description": f"[Multimodal vision error: {str(exc)}]",
            "model_used": settings.OLLAMA_VISION_MODEL,
            "success": False,
        }
