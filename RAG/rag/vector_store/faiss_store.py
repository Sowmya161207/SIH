"""
faiss_store.py
--------------
FAISS-based vector store for the MRPL RAG pipeline.

Responsibilities
----------------
1. Build a FAISS FlatIP index from chunk embeddings
2. Persist index + metadata to disk
3. Load persisted index on startup
4. Search: given a query vector, return top-k matching chunks

Persistence layout
------------------
rag/vector_store/
    faiss.index   ← FAISS binary index
    metadata.pkl  ← list[dict] of chunk metadata (parallel to index rows)
"""

import os
import logging
import pickle
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

import numpy as np
import faiss

from rag.config import (
    FAISS_INDEX_PATH,
    METADATA_PATH,
    EMBEDDING_DIM,
    DEFAULT_TOP_K,
)

logger = logging.getLogger(__name__)


class FAISSVectorStore:
    """
    Persistent FAISS vector store.

    Usage
    -----
    store = FAISSVectorStore()
    store.add(embeddings, metadata_list)
    store.save()

    # Later / in another process:
    store = FAISSVectorStore.load()
    results = store.search(query_vec, top_k=5)
    """

    def __init__(self):
        # FlatIP = exact inner product search (cosine when vectors are L2-normalised)
        self.index: faiss.IndexFlatIP = faiss.IndexFlatIP(EMBEDDING_DIM)
        self.metadata: List[Dict[str, Any]] = []

    # ── Mutating ops ─────────────────────────────────────────────────────────

    def add(
        self,
        embeddings: np.ndarray,
        metadata_list: List[Dict[str, Any]],
    ) -> None:
        """
        Add embeddings and their metadata to the store.

        Parameters
        ----------
        embeddings : np.ndarray
            Shape ``(N, EMBEDDING_DIM)``, float32, L2-normalised.
        metadata_list : List[Dict]
            Length-N list of chunk metadata dicts.
        """
        if len(embeddings) != len(metadata_list):
            raise ValueError(
                f"embeddings ({len(embeddings)}) and metadata_list "
                f"({len(metadata_list)}) must have the same length."
            )
        if len(embeddings) == 0:
            return

        embeddings = np.array(embeddings, dtype=np.float32)
        faiss.normalize_L2(embeddings)  # ensure unit vectors
        self.index.add(embeddings)
        self.metadata.extend(metadata_list)
        logger.info(
            "Added %d vectors. Total in store: %d",
            len(embeddings),
            self.index.ntotal,
        )

    def reset(self) -> None:
        """Clear all vectors and metadata."""
        self.index.reset()
        self.metadata.clear()
        logger.info("Vector store reset.")

    # ── Persistence ──────────────────────────────────────────────────────────

    def save(
        self,
        index_path: Path = FAISS_INDEX_PATH,
        meta_path:  Path = METADATA_PATH,
    ) -> None:
        """Save FAISS index and metadata to disk."""
        index_path = Path(index_path)
        meta_path  = Path(meta_path)
        index_path.parent.mkdir(parents=True, exist_ok=True)

        faiss.write_index(self.index, str(index_path))
        with open(meta_path, "wb") as fh:
            pickle.dump(self.metadata, fh)

        logger.info(
            "Saved store: %d vectors → %s",
            self.index.ntotal,
            index_path.parent,
        )

    @classmethod
    def load(
        cls,
        index_path: Path = FAISS_INDEX_PATH,
        meta_path:  Path = METADATA_PATH,
    ) -> "FAISSVectorStore":
        """
        Load a previously saved store.

        Raises
        ------
        FileNotFoundError
            If the index or metadata files do not exist.
        """
        index_path = Path(index_path)
        meta_path  = Path(meta_path)

        if not index_path.exists():
            raise FileNotFoundError(
                f"FAISS index not found at {index_path}. "
                "Run the ingestion pipeline first: python ingest_documents.py"
            )
        if not meta_path.exists():
            raise FileNotFoundError(
                f"Metadata file not found at {meta_path}. "
                "Run the ingestion pipeline first: python ingest_documents.py"
            )

        store = cls()
        store.index    = faiss.read_index(str(index_path))
        with open(meta_path, "rb") as fh:
            store.metadata = pickle.load(fh)

        logger.info(
            "Loaded store: %d vectors from %s",
            store.index.ntotal,
            index_path.parent,
        )
        return store

    @property
    def is_persisted(self) -> bool:
        """True if a saved index exists on disk."""
        return FAISS_INDEX_PATH.exists() and METADATA_PATH.exists()

    # ── Search ───────────────────────────────────────────────────────────────

    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = DEFAULT_TOP_K,
    ) -> List[Dict[str, Any]]:
        """
        Find the *top_k* most similar chunks to *query_vector*.

        Parameters
        ----------
        query_vector : np.ndarray
            Shape ``(EMBEDDING_DIM,)`` or ``(1, EMBEDDING_DIM)``, float32.
        top_k : int
            Number of results to return.

        Returns
        -------
        List[Dict]
            Each dict is a copy of the chunk metadata with an added ``score``
            field (cosine similarity, 0–1).
        """
        if self.index.ntotal == 0:
            logger.warning("Vector store is empty — no results.")
            return []

        # Ensure shape (1, D) and float32
        vec = np.array(query_vector, dtype=np.float32)
        if vec.ndim == 1:
            vec = vec.reshape(1, -1)
        faiss.normalize_L2(vec)

        k = min(top_k, self.index.ntotal)
        scores, indices = self.index.search(vec, k)

        results: List[Dict[str, Any]] = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:          # FAISS returns -1 for padded slots
                continue
            entry = dict(self.metadata[idx])
            entry["score"] = float(round(float(score), 4))
            results.append(entry)

        return results

    # ── Stats ────────────────────────────────────────────────────────────────

    def __len__(self) -> int:
        return self.index.ntotal

    def __repr__(self) -> str:
        return f"FAISSVectorStore(vectors={self.index.ntotal})"
