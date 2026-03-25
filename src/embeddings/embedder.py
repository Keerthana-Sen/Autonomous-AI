import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load .env using absolute path relative to this file
dotenv_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=dotenv_path)

api_key = os.getenv("OPENAI_API_KEY")
print(f"API Key loaded: {api_key[:10] if api_key else 'NOT FOUND'}")

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from src.ingestion.ingest import load_documents, chunk_documents  #

CHROMA_DB = "data/chroma_db"


def create_vector_store(chunks):
    embedding_model = OpenAIEmbeddings(
        model="text-embedding-ada-002",
        openai_api_key=os.getenv("OPENAI_API_KEY")  #
    )

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=CHROMA_DB
    )

    print(f"Stored {len(chunks)} chunks in ChromaDB at {CHROMA_DB}")  
    return vector_store


def load_vector_store():
    embedding_model = OpenAIEmbeddings(
        model="text-embedding-ada-002",
        openai_api_key=os.getenv("OPENAI_API_KEY")  #key name
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