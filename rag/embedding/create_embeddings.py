import os
import json
from pathlib import Path
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
import chromadb
from tqdm import tqdm

# Configuration
# Resolving paths relative to this script
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
DATA_PATH = PROJECT_ROOT / "documents" / "training" / "document_chunks.jsonl"
CHROMA_DB_PATH = SCRIPT_DIR.parent / "chroma_db"

MODEL_NAME = "all-MiniLM-L6-v2"
BATCH_SIZE = 64

def load_and_validate_chunks(filepath: Path) -> List[Dict[str, Any]]:
    """Reads JSONL, validates fields, and returns valid records."""
    valid_chunks = []
    skipped_count = 0
    seen_ids = set()
    
    if not filepath.exists():
        print(f"Error: Dataset not found at {filepath}")
        return []

    print(f"Reading chunks from {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
                
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                print(f"Warning: Invalid JSON at line {line_num}. Skipping.")
                skipped_count += 1
                continue
                
            source = data.get("source")
            chunk_id = data.get("chunk_id")
            text = data.get("text")
            
            # Validation
            if not source or not chunk_id or not text or not str(text).strip():
                skipped_count += 1
                continue
                
            # Deduplication
            if chunk_id in seen_ids:
                skipped_count += 1
                continue
                
            seen_ids.add(chunk_id)
            valid_chunks.append({
                "source": str(source),
                "chunk_id": str(chunk_id),
                "text": str(text).strip()
            })
            
    print(f"Found {len(valid_chunks)} valid chunks, skipped {skipped_count} chunks.")
    return valid_chunks

def create_embeddings():
    """Main pipeline for embedding and storing documents."""
    print("Starting local RAG embedding pipeline...")
    
    # 1. Load data
    chunks = load_and_validate_chunks(DATA_PATH)
    if not chunks:
        print("No valid chunks to process. Exiting.")
        return
        
    total_records = len(chunks)
    
    # 2. Initialize ChromaDB
    print(f"Initializing persistent ChromaDB at {CHROMA_DB_PATH}...")
    # Ensure directory exists
    os.makedirs(CHROMA_DB_PATH, exist_ok=True)
    chroma_client = chromadb.PersistentClient(path=str(CHROMA_DB_PATH))
    
    # Create or get the collection
    collection = chroma_client.get_or_create_collection(
        name="sih_documents",
        metadata={"hnsw:space": "cosine"}
    )
    
    # 3. Load embedding model
    print(f"Loading local embedding model: {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)
    
    # 4. Generate embeddings and store in batches
    print("Generating embeddings and storing in Vector DB...")
    
    for i in tqdm(range(0, total_records, BATCH_SIZE), desc="Processing Batches"):
        batch = chunks[i:i + BATCH_SIZE]
        
        texts = [item["text"] for item in batch]
        ids = [item["chunk_id"] for item in batch]
        metadatas = [{"source": item["source"], "chunk_id": item["chunk_id"]} for item in batch]
        
        # Generate embeddings
        embeddings = model.encode(texts, show_progress_bar=False).tolist()
        
        # Upsert into ChromaDB
        collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )
        
    # 5. Final Summary
    print("\n--- Pipeline Summary ---")
    print(f"Total chunks processed: {total_records}")
    print(f"Successfully embedded and stored: {total_records}")
    print(f"Vector Database Location: {CHROMA_DB_PATH}")
    print("------------------------\n")

if __name__ == "__main__":
    create_embeddings()
