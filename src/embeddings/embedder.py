import sys
import os
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from src.ingestion.ingest import load_documents, chunk_documents

CHROMA_PATH = str(Path(__file__).resolve().parent.parent.parent / "data" / "chroma_db")


def get_embedding_model():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        cache_folder=os.path.expanduser("~/.cache/huggingface/hub")
    )


def create_vector_store(chunks):
    """Builds and persists a ChromaDB from document chunks."""
    embedding_model = get_embedding_model()

    # Wipe existing store so re-ingestion starts clean
    import shutil
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)
        print(f"Removed existing ChromaDB at {CHROMA_PATH}")

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=CHROMA_PATH
    )
    print(f"Stored {len(chunks)} chunks in ChromaDB at {CHROMA_PATH}")
    return vector_store


def load_vector_store():
    embedding_model = get_embedding_model()
    vector_store = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embedding_model
    )
    print(f"Loaded ChromaDB from {CHROMA_PATH}")
    return vector_store


if __name__ == "__main__":
    docs = load_documents("data/raw/policies")
    chunks = chunk_documents(docs)
    vector_store = create_vector_store(chunks)

    test_query = "What happens when a request exceeds 10000 USD?"
    results = vector_store.similarity_search(test_query, k=2)

    print("\n--- Test Retrieval Results ---")
    for i, result in enumerate(results):
        print(f"\nResult {i+1}:")
        print(result.page_content)
