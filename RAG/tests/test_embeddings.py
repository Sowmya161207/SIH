"""
tests/test_embeddings.py
------------------------
Unit tests for the embedding module.
Requires sentence-transformers to be installed but NOT the vector store.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import numpy as np


class TestEmbedder:
    """Tests for the Embedder class."""

    @pytest.fixture(scope="class")
    @staticmethod
    def embedder():
        """Load the embedder once per test class (slow on first run — downloads model)."""
        try:
            from rag.embeddings.embedder import Embedder
            return Embedder()
        except ImportError:
            pytest.skip("sentence-transformers not installed")

    def test_embed_returns_numpy_array(self, embedder):
        vec = embedder.embed("bearing temperature exceeded")
        assert isinstance(vec, np.ndarray)

    def test_embed_correct_dimension(self, embedder):
        from rag.config import EMBEDDING_DIM
        vec = embedder.embed("pump maintenance report")
        assert vec.shape == (EMBEDDING_DIM,)

    def test_embed_is_unit_vector(self, embedder):
        vec = embedder.embed("this is a test sentence")
        norm = float(np.linalg.norm(vec))
        assert abs(norm - 1.0) < 1e-4, f"Expected unit vector, got norm={norm}"

    def test_embed_float32(self, embedder):
        vec = embedder.embed("crude oil feed pump")
        assert vec.dtype == np.float32

    def test_embed_batch_shape(self, embedder):
        texts = ["text one", "text two", "text three"]
        vecs = embedder.embed_batch(texts, show_progress=False)
        from rag.config import EMBEDDING_DIM
        assert vecs.shape == (3, EMBEDDING_DIM)

    def test_embed_batch_empty(self, embedder):
        from rag.config import EMBEDDING_DIM
        vecs = embedder.embed_batch([], show_progress=False)
        assert vecs.shape == (0, EMBEDDING_DIM)

    def test_similar_texts_close(self, embedder):
        """Semantically similar texts should have cosine similarity > 0.7."""
        v1 = embedder.embed("bearing temperature alarm")
        v2 = embedder.embed("bearing heat alarm exceeded")
        sim = float(np.dot(v1, v2))  # both are unit vectors → dot = cosine
        assert sim > 0.70, f"Expected similarity > 0.70, got {sim:.3f}"

    def test_dissimilar_texts_far(self, embedder):
        """Semantically unrelated texts should have lower similarity."""
        v1 = embedder.embed("crude oil pump bearing failure")
        v2 = embedder.embed("financial quarterly revenue report")
        sim = float(np.dot(v1, v2))
        assert sim < 0.80, f"Unexpected high similarity ({sim:.3f}) for unrelated texts"

    def test_same_text_identical_embedding(self, embedder):
        """Same text should always produce the same embedding."""
        text = "MRPL Pump P-101 maintenance"
        v1 = embedder.embed(text)
        v2 = embedder.embed(text)
        assert np.allclose(v1, v2, atol=1e-5)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
