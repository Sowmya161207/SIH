import argparse
from pathlib import Path
from sentence_transformers import SentenceTransformer
import chromadb
import ollama
import sys

# Automatically resolve paths
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
CHROMA_DB_PATH = PROJECT_ROOT / "rag" / "chroma_db"

def main():
    parser = argparse.ArgumentParser(description="Search the MRPL local RAG Vector DB and Generate Answer with LLaMA 3.")
    parser.add_argument("query", type=str, nargs='?', help="Your search query")
    args = parser.parse_args()
    
    query_text = args.query
    if not query_text:
        query_text = input("Enter your search query: ")

    if not query_text.strip():
        print("Empty query. Exiting.")
        return

    if not CHROMA_DB_PATH.exists():
        print(f"\n[ERROR] Database not found at {CHROMA_DB_PATH}")
        print("Please run create_embeddings.py first.")
        return

    # 1. RETRIEVAL STEP
    print("\n[1/2] Loading embedding model 'all-MiniLM-L6-v2' and connecting to ChromaDB...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    chroma_client = chromadb.PersistentClient(path=str(CHROMA_DB_PATH))
    collection = chroma_client.get_collection(name="mrpl_rag_collection")

    query_embedding = model.encode([query_text], convert_to_numpy=True).tolist()
    
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=5,
        include=['documents', 'metadatas', 'distances']
    )
    
    if not results['ids'][0]:
        print("No results found in ChromaDB.")
        return

    # Extract retrieved texts to form the context
    retrieved_texts = results['documents'][0]
    context = "\n\n".join([f"--- Chunk {i+1} ---\n{text}" for i, text in enumerate(retrieved_texts)])
    
    print("\n" + "="*60)
    print("                  TOP RETRIEVED CONTEXT")
    print("="*60)
    for i, (doc, dist) in enumerate(zip(results['documents'][0], results['distances'][0])):
        print(f"\nResult {i+1} (Distance: {dist:.4f}):\n{doc[:200]}...") # Print preview

    # 2. GENERATION STEP (LLaMA via Ollama)
    print("\n" + "="*60)
    print("             LLaMA 3 GENERATING ANSWER...")
    print("="*60 + "\n")
    
    prompt = f"""You are an expert AI assistant for MRPL (Mangalore Refinery and Petrochemicals Limited).
Use ONLY the following context to answer the user's question. If the context does not contain the answer, simply state "I don't have enough information to answer this based on the provided documents." Do not use outside knowledge.

Context:
{context}

Question: {query_text}

Answer:"""

    try:
        response = ollama.chat(
            model='llama3',
            messages=[{'role': 'user', 'content': prompt}],
            stream=True
        )
        
        # Stream the response to the terminal
        for chunk in response:
            sys.stdout.write(chunk['message']['content'])
            sys.stdout.flush()
            
        print("\n\n" + "="*60)
            
    except Exception as e:
        print(f"\n[ERROR] Failed to connect to Ollama: {e}")
        print("Please ensure you have installed Ollama and run 'ollama run llama3' in a separate terminal.")

if __name__ == "__main__":
    main()
