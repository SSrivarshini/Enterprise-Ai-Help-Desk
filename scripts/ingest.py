"""Build the vector index from data/docs. Run: python -m scripts.ingest"""
from app.rag.vectorstore import build_index

if __name__ == "__main__":
    n_docs, n_chunks = build_index()
    print(f"Indexed {n_docs} document(s) as {n_chunks} chunk(s).")
