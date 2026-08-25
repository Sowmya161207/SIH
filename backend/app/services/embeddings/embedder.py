"""
embedder.py
-----------
Local embedding model wrapper using sentence-transformers.
Model: sentence-transformers/all-MiniLM-L6-v2 (384-dim)
Fully local, CPU-friendly, Apache 2.0.
"""

import logging
import numpy as np
from typing import List

from app.core.config import settings

logger = logging.getLogger(__name__)

_model = None


def _get_model():
    """Load (and cache) the sentence-transformer model."""
    global _model
    if _model is None:
        logger.info("Loading embedding model: %s", settings.EMBEDDING_MODEL_NAME)
        try:
            from sentence_transformers import SentenceTransformer
            try:
                # Try local cache load first (fast & immune to HF network drops)
                _model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME, local_files_only=True)
            except Exception:
                # Fallback to downloading if not cached locally
                _model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
            logger.info("Embedding model loaded ✓ (dim=%d)", settings.EMBEDDING_DIM)
        except ImportError as exc:
            raise ImportError(
                "sentence-transformers is not installed. Run: pip install sentence-transformers"
            ) from exc
    return _model


class Embedder:
    """Thin wrapper around SentenceTransformer model."""

    def __init__(self):
        self._model = _get_model()

    def embed(self, text: str) -> np.ndarray:
        """Embed a single string."""
        vec = self._model.encode(
            [text],
            normalize_embeddings=True,
            show_progress_bar=False,
            convert_to_numpy=True,
        )
        return vec[0].astype(np.float32)

    def embed_batch(
        self,
        texts: List[str],
        batch_size: int = 64,
        show_progress: bool = False,
    ) -> np.ndarray:
        """Embed a list of strings efficiently."""
        if not texts:
            return np.empty((0, settings.EMBEDDING_DIM), dtype=np.float32)

        vecs = self._model.encode(
            texts,
            batch_size=batch_size,
            normalize_embeddings=True,
            show_progress_bar=show_progress,
            convert_to_numpy=True,
        )
        return vecs.astype(np.float32)
