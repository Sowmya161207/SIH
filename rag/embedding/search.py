import os
from pathlib import Path
from sentence_transformers import SentenceTransformer
import chromadb

# Configuration
SCRIPT_DIR = Path(__file__).resolve().parent
CHROMA_DB_PATH = SCRIPT_DIR.parent / "chroma_db"
MODEL_NAME = "all-MiniLM-L6-v2"

def search():
    """Interactive search using local ChromaDB and SentenceTransformer."""
    if not CHROMA_DB_PATH.exists():
        print(f"Error: Vector database not found at {CHROMA_DB_PATH}")
        print("Please run create_embeddings.py first.")
        return

    print("Loading local embedding model...")
    model = SentenceTransformer(MODEL_NAME)
    
    print("Connecting to local ChromaDB...")
    chroma_client = chromadb.PersistentClient(path=str(CHROMA_DB_PATH))
    try:
        collection = chroma_client.get_collection(name="sih_documents")
    except Exception as e:
        print(f"Error: Could not find 'sih_documents' collection. Details: {e}")
        return

    print("\n--- Local RAG Search ---")
    print("Type 'exit' or 'quit' to stop.")
    
    while True:
        query = input("\nEnter your search query: ").strip()
        if not query:
            continue
        if query.lower() in ['exit', 'quit']:
            print("Exiting search. Goodbye!")
            break
            
        print(f"\nSearching for: '{query}'...")
        # 1. Embed query
        query_embedding = model.encode(query).tolist()
        
        # 2. Query vector DB
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=5,
            include=['documents', 'metadatas', 'distances']
        )
        
        if not results['documents'] or not results['documents'][0]:
            print("No results found.")
            continue
            
        print("\n--- Top 5 Relevant Chunks ---")
        # 3. Display results
        documents = results['documents'][0]
        metadatas = results['metadatas'][0]
        distances = results['distances'][0]
        
        for idx, (doc, meta, dist) in enumerate(zip(documents, metadatas, distances), 1):
            # Chroma returns cosine distance by default if configured, where distance = 1 - similarity
            # We assume cosine distance is used here as configured in create_embeddings.py
            similarity = max(0.0, 1.0 - dist)
            
            print(f"\nResult {idx} (Similarity: {similarity:.4f})")
            print(f"Source: {meta.get('source', 'Unknown')}")
            print(f"Chunk ID: {meta.get('chunk_id', 'Unknown')}")
            print(f"Text: {doc}")
            print("-" * 40)

if __name__ == "__main__":
    search()
