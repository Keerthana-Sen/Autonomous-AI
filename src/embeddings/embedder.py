import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

# Load .env using absolute path relative to this file
dotenv_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=dotenv_path)

# HuggingFace runs locally — no API key needed
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from src.ingestion.ingest import load_documents, chunk_documents

CHROMA_DB = "data/chroma_db"


def create_vector_store(chunks):
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=CHROMA_DB
    )

    print(f"Stored {len(chunks)} chunks in ChromaDB at {CHROMA_DB}")
    return vector_store


def load_vector_store():
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vector_store = Chroma(
        persist_directory=CHROMA_DB,
        embedding_function=embedding_model
    )

    print(f"Loaded existing ChromaDB from {CHROMA_DB}")
    return vector_store


if __name__ == "__main__":

    docs = load_documents("data/raw/policies")       # Step 1: Load policy documents
    chunks = chunk_documents(docs)                   # Step 2: Chunk them

    vector_store = create_vector_store(chunks)       # Step 3: Embed and store in ChromaDB

    test_query = "What happens when a request exceeds 10000 USD?"
    results = vector_store.similarity_search(test_query, k=2)  # Step 4: Test retrieval

    print("\n--- Test Retrieval Results ---")
    for i, result in enumerate(results):
        print(f"\nResult {i+1}:")
        print(result.page_content)