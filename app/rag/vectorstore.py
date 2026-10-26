from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import CHROMA_DIR, DOCS_DIR, EMBEDDING_MODEL
from app.rag.loader import load_documents

COLLECTION = "helpdesk"


def get_vectorstore() -> Chroma:
    return Chroma(
        collection_name=COLLECTION,
        embedding_function=OpenAIEmbeddings(model=EMBEDDING_MODEL),
        persist_directory=str(CHROMA_DIR),
        collection_metadata={"hnsw:space": "cosine"},
    )


def build_index() -> tuple[int, int]:
    """(Re)build the vector index from everything in the docs folder."""
    docs = load_documents(DOCS_DIR)
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    chunks = splitter.split_documents(docs)

    store = get_vectorstore()
    store.delete_collection()
    store = get_vectorstore()
    if chunks:
        store.add_documents(chunks)
    return len(docs), len(chunks)
