import sys
import os
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

CHROMA_PATH = str(Path(__file__).resolve().parent.parent.parent / "data" / "chroma_db")

_vector_store = None


def _get_embedding_model():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        cache_folder=os.path.expanduser("~/.cache/huggingface/hub")
    )


def load_vector_store():
    global _vector_store
    if _vector_store is None:
        _vector_store = Chroma(
            persist_directory=CHROMA_PATH,
            embedding_function=_get_embedding_model()
        )
        print(f"Loaded ChromaDB from {CHROMA_PATH}")
    return _vector_store


def get_retriever(k: int = 3):
    """Returns a basic similarity retriever."""
    vector_store = load_vector_store()
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k}
    )
    print(f"Retriever ready — will fetch top {k} chunks per query")
    return retriever


def get_retrieval_confidence(query: str, k: int = 3) -> float:
    """
    Returns a 0-100 confidence score based on average similarity of top-k retrieved chunks.
    """
    try:
        vector_store = load_vector_store()
        results = vector_store.similarity_search_with_score(query, k=k)
        if not results:
            return 0.0
        scores = []
        for _, s in results:
            try:
                scores.append(float(s))
            except (TypeError, ValueError):
                pass
        if not scores:
            return round(len(results) / k * 65, 1)
        avg = sum(scores) / len(scores)
        if avg > 1.0:
            # L2 distance — invert to confidence
            confidence = max(1.0 - avg / 1.5, 0.0) * 100
        elif avg >= 0.0:
            # Cosine similarity [0, 1]
            confidence = avg * 100
        else:
            confidence = max((avg + 1) / 2 * 100, 10.0)
        return round(min(confidence, 100.0), 1)
    except Exception:
        return 0.0


def retrieve_multi_policy_context(query: str, k_per_policy: int = 3) -> str:
    """
    Retrieves policy context across all policy files.
    Fetches k_per_policy * 3 chunks so all three policy types are represented.
    Returns a single formatted string for the agent to consume.
    """
    try:
        vector_store = load_vector_store()
        results = vector_store.similarity_search(query, k=k_per_policy * 3)
        if not results:
            return "No relevant policy context found."
        parts = []
        for doc in results:
            source = doc.metadata.get("source", "policy")
            parts.append(f"[{source}]\n{doc.page_content}")
        return "\n\n".join(parts)
    except Exception as e:
        return f"Error retrieving policy context: {e}"


if __name__ == "__main__":
    test_queries = [
        "Why was REQ001 approved?",
        "Why was REQ004 rejected?",
        "Why was REQ007 escalated?"
    ]
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 50)
        docs = get_retriever(k=3).invoke(query)
        for doc in docs:
            print(doc.page_content[:300])
