"""
config.py — Central configuration for the MRPL RAG pipeline.
All tunable parameters live here so nothing is scattered across files.
"""

import os
from pathlib import Path



# ─── Paths ────────────────────────────────────────────────────────────────────
RAG_ROOT         = Path(__file__).parent.parent          # …/RAG/
VECTOR_STORE_DIR = RAG_ROOT / "rag" / "vector_store"
CHROMA_DB_DIR    = VECTOR_STORE_DIR / "chroma_db"    # ChromaDB persistent directory
FAISS_INDEX_PATH = VECTOR_STORE_DIR / "faiss.index"
METADATA_PATH    = VECTOR_STORE_DIR / "metadata.pkl"
DATA_RAW_DIR     = RAG_ROOT / "data" / "raw"
DATA_DEMO_DIR    = RAG_ROOT / "data" / "demo"

# ─── Embedding model ──────────────────────────────────────────────────────────
# all-MiniLM-L6-v2: 80 MB, CPU-friendly, strong retrieval quality.
# Downloaded automatically on first run from HuggingFace Hub (local cache only).
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIM        = 384        # Output dimension of all-MiniLM-L6-v2

# ─── Chunking ─────────────────────────────────────────────────────────────────
CHUNK_SIZE        = 400           # characters (not tokens) for simplicity
CHUNK_OVERLAP     = 80            # overlap between consecutive chunks (chars)
MIN_CHUNK_LENGTH  = 50            # discard chunks shorter than this

# ─── Retrieval ────────────────────────────────────────────────────────────────
DEFAULT_TOP_K = 5                 # default number of results returned

# ─── Vector Store ───────────────────────────────────────────────────────────
VECTOR_STORE_BACKEND = "chroma"   # options: "chroma" (default)

# ─── Logging ──────────────────────────────────────────────────────────────────
import logging
LOG_LEVEL = logging.INFO
