"""
vector_store.py
---------------
Persistent ChromaDB vector store layer for backend RAG services.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

from app.core.config import settings

logger = logging.getLogger(__name__)

COLLECTION_NAME = "mrpl_rag"


class VectorStore:
    """Persistent ChromaDB vector database manager."""

    def __init__(self, db_dir: Optional[str | Path] = None):
        try:
            import chromadb
        except ImportError as exc:
            raise ImportError(
                "chromadb is not installed. Run: pip install chromadb"
            ) from exc

        db_path = Path(db_dir or settings.CHROMA_DB_DIR)
        db_path.mkdir(parents=True, exist_ok=True)

        self._client = chromadb.PersistentClient(path=str(db_path))
        self._collection = self._client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(
            "VectorStore opened at %s (vectors=%d)",
            db_path, self._collection.count(),
        )

    @staticmethod
    def _encode_meta(meta: Dict[str, Any]) -> Dict[str, Any]:
        """Encode list values into JSON strings for ChromaDB compatibility."""
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
        """Decode JSON strings back to lists."""
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

    def add(
        self,
        embeddings: np.ndarray,
        metadata_list: List[Dict[str, Any]],
    ) -> None:
        """Add embeddings and metadata to ChromaDB."""
        if len(embeddings) != len(metadata_list):
            raise ValueError("embeddings and metadata_list lengths must match.")
        if len(embeddings) == 0:
            return

        embeddings = np.array(embeddings, dtype=np.float32)
        ids = [m["chunk_id"] for m in metadata_list]
        documents = [m.get("text", "") for m in metadata_list]
        metadatas = [self._encode_meta(m) for m in metadata_list]

        self._collection.add(
            ids=ids,
            embeddings=embeddings.tolist(),
            documents=documents,
            metadatas=metadatas,
        )
        logger.info(
            "Added %d vectors. Total in store: %d",
            len(embeddings), self._collection.count(),
        )

    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = settings.DEFAULT_TOP_K,
    ) -> List[Dict[str, Any]]:
        """Search top-k most similar chunks by query vector."""
        if self._collection.count() == 0:
            logger.warning("VectorStore is empty — returning 0 results.")
            return []

        vec = np.array(query_vector, dtype=np.float32)
        if vec.ndim == 2:
            vec = vec[0]

        k = min(top_k, self._collection.count())
        raw = self._collection.query(
            query_embeddings=[vec.tolist()],
            n_results=k,
            include=["documents", "metadatas", "distances"],
        )

        results: List[Dict[str, Any]] = []
        for doc, meta, dist in zip(
            raw["documents"][0],
            raw["metadatas"][0],
            raw["distances"][0],
        ):
            entry = self._decode_meta(dict(meta))
            score = float(round(max(0.0, 1.0 - dist), 4))
            entry["text"] = doc
            entry["score"] = score
            results.append(entry)

        return results

    def reset(self) -> None:
        """Reset vector store."""
        self._client.delete_collection(COLLECTION_NAME)
        self._collection = self._client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info("VectorStore reset.")

    def __len__(self) -> int:
        return self._collection.count()
