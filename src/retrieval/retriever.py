import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add project root to Python path so imports like src.embeddings work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

# Load .env from project root (needed later when we switch back to OpenAI)
dotenv_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=dotenv_path)

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

#reuses the same ChromaDB we already built
from src.embeddings.embedder import load_vector_store

# path what embedder.py used — same DB, same chunks
CHROMA_DB = "data/chroma_db"


def get_retriever(k: int = 3):
    """
    Loads the existing ChromaDB vector store and returns a retriever.
    
    k = number of chunks to retrieve per query.
    Higher k = more context but more noise. 3 is a safe default.
    """

    # Load the vector store that was created and persisted by embedder.py
    vector_store = load_vector_store()

    # Convert the vector store into a LangChain retriever object
    # search_type="similarity" uses cosine similarity to rank chunks
    # k controls how many top chunks are returned
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k}
    )

    print(f"Retriever ready — will fetch top {k} chunks per query")
    return retriever


def retrieve_chunks(query: str, k: int = 3):
    """
    Takes a natural language query and returns the top k most relevant chunks.
    
    This is what the RAG chain will call to get context before generating an answer.
    """

    # Build the retriever with desired k
    retriever = get_retriever(k=k)

    # .invoke() sends the query through the embedding model
    # then finds the k nearest chunks in ChromaDB by vector similarity
    results = retriever.invoke(query)

    # Each result is a LangChain Document object with:
    # - result.page_content → the actual text chunk
    # - result.metadata     → source file, chunk index, etc.
    return results

if __name__ == "__main__":

    # Test query that should match the approval policy chunks
    test_query = "Why was this request escalated to the director?"

    print(f"\nQuery: {test_query}")
    print("-" * 50)

    # Retrieve top 3 relevant chunks
    chunks = retrieve_chunks(test_query, k=3)

    # Print each retrieved chunk with its source metadata
    for i, chunk in enumerate(chunks):
        print(f"\nChunk {i+1}:")
        print(f"Source : {chunk.metadata.get('source', 'unknown')}")  # which policy file
        print(f"Content: {chunk.page_content}")
        print("-" * 50)
        