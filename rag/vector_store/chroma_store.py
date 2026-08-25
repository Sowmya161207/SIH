"""
chroma_store.py
---------------
ChromaDB-backed vector store for the MRPL RAG pipeline.
Replaces faiss_store.py as the persistence layer.

ChromaDB advantages over FAISS for this use-case:
  - Stores documents + embeddings + metadata in one place (no separate .pkl)
  - Built-in persistent client — no manual save/load calls
  - Cosine similarity natively
  - Supports metadata filtering (used here for future role-filter push-down)

Persistence layout
------------------
rag/vector_store/chroma_db/   ← ChromaDB persistent directory
    chroma.sqlite3            (auto-created by ChromaDB)
    ...

Collection name: "mrpl_rag"

Note on allowed_roles
---------------------
ChromaDB metadata values must be str | int | float | bool — NOT lists.
We serialise ``allowed_roles`` as a JSON string on write and deserialise on read.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

from rag.config import CHROMA_DB_DIR, DEFAULT_TOP_K, EMBEDDING_DIM

logger = logging.getLogger(__name__)

COLLECTION_NAME = "mrpl_rag"


class ChromaVectorStore:
    """
    Persistent ChromaDB vector store.

    Usage
    -----
    store = ChromaVectorStore()          # creates / opens existing DB
    store.add(embeddings, metadata_list)
    store.reset()                        # wipe and start fresh

    # In another process / same process:
    store = ChromaVectorStore()
    results = store.search(query_vec, top_k=5)
    """

    def __init__(self, db_dir: Path = CHROMA_DB_DIR):
        try:
            import chromadb
        except ImportError as exc:
            raise ImportError(
                "chromadb is not installed. Run: pip install chromadb"
            ) from exc

        db_dir = Path(db_dir)
        db_dir.mkdir(parents=True, exist_ok=True)

        self._client = chromadb.PersistentClient(path=str(db_dir))
        self._collection = self._client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},   # cosine similarity
        )
        logger.info(
            "ChromaDB store opened at %s  (vectors=%d)",
            db_dir, self._collection.count(),
        )

    # ── Internal helpers ─────────────────────────────────────────────────────

    @staticmethod
    def _encode_meta(meta: Dict[str, Any]) -> Dict[str, Any]:
        """
        Flatten metadata for ChromaDB (values must be scalar).
        Lists are JSON-encoded to strings.
        """
        encoded = {}
        for k, v in meta.items():
            if isinstance(v, list):
                encoded[k] = json.dumps(v)
            elif isinstance(v, (str, int, float, bool)):
                encoded[k] = v
            else:
                encoded[k] = str(v)
        return encoded

    @staticmethod
    def _decode_meta(meta: Dict[str, Any]) -> Dict[str, Any]:
        """Reverse of _encode_meta — restore lists from JSON strings."""
        decoded = {}
        for k, v in meta.items():
            if isinstance(v, str):
                try:
                    parsed = json.loads(v)
                    if isinstance(parsed, list):
                        decoded[k] = parsed
                        continue
                except (json.JSONDecodeError, ValueError):
                    pass
            decoded[k] = v
        return decoded

    # ── Mutating ops ─────────────────────────────────────────────────────────

    def add(
        self,
        embeddings: np.ndarray,
        metadata_list: List[Dict[str, Any]],
    ) -> None:
        """
        Add embeddings and their associated chunk metadata to ChromaDB.

        Parameters
        ----------
        embeddings : np.ndarray
            Shape ``(N, EMBEDDING_DIM)``, float32.
        metadata_list : List[Dict]
            Length-N list of chunk metadata dicts. Each must have ``chunk_id``.
        """
        if len(embeddings) != len(metadata_list):
            raise ValueError(
                f"embeddings ({len(embeddings)}) and metadata_list "
                f"({len(metadata_list)}) must have the same length."
            )
        if len(embeddings) == 0:
            return

        embeddings = np.array(embeddings, dtype=np.float32)

        ids        = [m["chunk_id"] for m in metadata_list]
        documents  = [m.get("text", "") for m in metadata_list]
        metadatas  = [self._encode_meta(m) for m in metadata_list]

        self._collection.add(
            ids        = ids,
            embeddings = embeddings.tolist(),
            documents  = documents,
            metadatas  = metadatas,
        )
        logger.info(
            "Added %d vectors. Total in store: %d",
            len(embeddings), self._collection.count(),
        )

    def reset(self) -> None:
        """
        Delete and recreate the collection (wipe all data).
        """
        self._client.delete_collection(COLLECTION_NAME)
        self._collection = self._client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info("ChromaDB collection reset.")

    # ── Search ───────────────────────────────────────────────────────────────

    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = DEFAULT_TOP_K,
        where_filter: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Find the *top_k* most similar chunks to *query_vector*.

        Parameters
        ----------
        query_vector : np.ndarray
            Shape ``(EMBEDDING_DIM,)`` or ``(1, EMBEDDING_DIM)``.
        top_k : int
            Number of results to return.
        where_filter : dict, optional
            ChromaDB filter dict, e.g., {"workspace_id": "ws_123"}.

        Returns
        -------
        List[Dict]
            Each dict is chunk metadata with an added ``score`` field.
            ``score`` is cosine similarity (0–1), computed as 1 - distance.
        """
        if self._collection.count() == 0:
            logger.warning("ChromaDB collection is empty — no results.")
            return []

        vec = np.array(query_vector, dtype=np.float32)
        if vec.ndim == 2:
            vec = vec[0]

        k = min(top_k, self._collection.count())

        query_args = {
            "query_embeddings": [vec.tolist()],
            "n_results": k,
            "include": ["documents", "metadatas", "distances"],
        }
        if where_filter:
            query_args["where"] = where_filter

        raw = self._collection.query(**query_args)

        results: List[Dict[str, Any]] = []
        for doc, meta, dist in zip(
            raw["documents"][0],
            raw["metadatas"][0],
            raw["distances"][0],
        ):
            entry = self._decode_meta(dict(meta))
            # ChromaDB cosine distance ∈ [0, 2]; 0 = identical, 2 = opposite
            # Convert to similarity score ∈ [0, 1]
            score = float(round(max(0.0, 1.0 - dist), 4))
            entry["text"]  = doc
            entry["score"] = score
            results.append(entry)

        return results

    # ── Stats ────────────────────────────────────────────────────────────────

    def __len__(self) -> int:
        return self._collection.count()

    def __repr__(self) -> str:
        return f"ChromaVectorStore(vectors={self._collection.count()})"
