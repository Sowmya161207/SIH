"""
embedder.py
-----------
Local embedding model wrapper using sentence-transformers.

Model: all-MiniLM-L6-v2
  - Dimension:  384
  - Size:       ~80 MB
  - Runs on:    CPU (no GPU required)
  - License:    Apache 2.0
  - Source:     https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2

First call downloads the model weights to ~/.cache/huggingface/hub/
(or the HF_HOME env var) — subsequent calls use the cached version.
No internet access required after the initial download.
"""

import logging
import numpy as np
from typing import List, Union

from rag.config import EMBEDDING_MODEL_NAME, EMBEDDING_DIM

logger = logging.getLogger(__name__)

# ─── Lazy singleton ───────────────────────────────────────────────────────────
_model = None


def _get_model():
    """Load (and cache) the sentence-transformer model."""
    global _model
    if _model is None:
        logger.info("Loading embedding model: %s", EMBEDDING_MODEL_NAME)
        try:
            from sentence_transformers import SentenceTransformer
            try:
                # Try offline local load first (fast & immune to HF network drops)
                _model = SentenceTransformer(EMBEDDING_MODEL_NAME, local_files_only=True)
            except Exception:
                # Fallback to downloading if not cached locally
                _model = SentenceTransformer(EMBEDDING_MODEL_NAME)
            logger.info("Embedding model loaded ✓  (dim=%d)", EMBEDDING_DIM)
        except ImportError as exc:
            raise ImportError(
                "sentence-transformers is not installed. "
                "Run: pip install sentence-transformers"
            ) from exc
    return _model


class Embedder:
    """
    Thin wrapper around a SentenceTransformer model.

    Usage
    -----
    embedder = Embedder()
    vec  = embedder.embed("bearing temperature exceeded 85°C")  # shape (384,)
    vecs = embedder.embed_batch(["text1", "text2"])             # shape (N, 384)
    """

    def __init__(self):
        self._model = _get_model()

    # ── Single text ──────────────────────────────────────────────────────────

    def embed(self, text: str) -> np.ndarray:
        """
        Embed a single string.

        Returns
        -------
        np.ndarray
            Shape ``(384,)``, float32, L2-normalised.
        """
        vec = self._model.encode(
            [text],
            normalize_embeddings=True,
            show_progress_bar=False,
            convert_to_numpy=True,
        )
        return vec[0].astype(np.float32)

    # ── Batch ────────────────────────────────────────────────────────────────

    def embed_batch(
        self,
        texts: List[str],
        batch_size: int = 64,
        show_progress: bool = True,
    ) -> np.ndarray:
        """
        Embed a list of strings efficiently.

        Parameters
        ----------
        texts : List[str]
            Input texts.
        batch_size : int
            How many texts to encode per forward pass.
        show_progress : bool
            Print a tqdm progress bar (useful during ingestion).

        Returns
        -------
        np.ndarray
            Shape ``(len(texts), 384)``, float32, L2-normalised.
        """
        if not texts:
            return np.empty((0, EMBEDDING_DIM), dtype=np.float32)

        logger.info("Embedding %d texts …", len(texts))
        vecs = self._model.encode(
            texts,
            batch_size           = batch_size,
            normalize_embeddings = True,
            show_progress_bar    = show_progress,
            convert_to_numpy     = True,
        )
        return vecs.astype(np.float32)
