import sys
import os
from pathlib import Path
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

dotenv_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=dotenv_path)

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

CHROMA_DB = "data/chroma_db"


def load_vector_store():
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        cache_folder=os.path.expanduser("~/.cache/huggingface/hub")  # Use standard cache
    )
    vector_store = Chroma(
        persist_directory=CHROMA_DB,
        embedding_function=embedding_model
    )
    print(f"Loaded existing ChromaDB from {CHROMA_DB}")
    return vector_store


def get_retriever(k: int = 3):
    """Returns a basic similarity retriever."""
    vector_store = load_vector_store()
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k}
    )
    print(f"Retriever ready — will fetch top {k} chunks per query")
    return retriever


def get_smart_retriever(question: str, k: int = 3):
    """
    Picks the right policy file based on keywords in the question.
    Fixes the wrong-chunk retrieval problem — approval questions
    were pulling rejection/escalation chunks instead of approval chunks.
    """
    vector_store = load_vector_store()

    question_lower = question.lower()

    # Map keywords to the correct policy source file
    if any(w in question_lower for w in ["approved", "approval", "auto-approved", "auto approved"]):
        source_filter = "policy_approval_limits"
    elif any(w in question_lower for w in ["escalated", "escalation", "unavailable"]):
        source_filter = "policy_escalation_rules"
    elif any(w in question_lower for w in ["rejected", "rejection", "suspended", "duplicate", "incomplete"]):
        source_filter = "policy_rejection_rules"
    else:
        # No clear match — fall back to standard similarity search
        print("No keyword match — using standard retriever")
        return get_retriever(k=k)

    print(f"Smart retriever — filtering by: {source_filter}")

    # Filter ChromaDB by source metadata
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": k,
            "filter": {"source": {"$contains": source_filter}}
        }
    )
    return retriever


def retrieve_chunks(query: str, k: int = 3):
    """Retrieves top k chunks using smart routing."""
    retriever = get_smart_retriever(query, k=k)
    return retriever.invoke(query)


def retrieve_multi_policy_context(query: str, k_per_policy: int = 2) -> str:
    """
    Queries all three policy files separately and combines the results.
    A single similarity search can only pull chunks from one dominant policy file,
    missing the other policies needed for multi-rule decisions. This ensures
    coverage across rejection, escalation, and approval rules simultaneously.
    """
    vector_store = load_vector_store()

    policy_sources = [
        ("policy_rejection_rules",  "Rejection Rules"),
        ("policy_escalation_rules", "Escalation Rules"),
        ("policy_approval_limits",  "Approval Limits"),
    ]

    sections = []
    seen = set()

    for source_filter, label in policy_sources:
        retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={
                "k": k_per_policy,
                "filter": {"source": {"$contains": source_filter}}
            }
        )
        docs = retriever.invoke(query)
        chunks = [doc.page_content for doc in docs if doc.page_content not in seen]
        for chunk in chunks:
            seen.add(chunk)
        if chunks:
            sections.append(f"[{label}]\n" + "\n\n".join(chunks))

    return "\n\n---\n\n".join(sections) if sections else "No relevant policy context found."


if __name__ == "__main__":
    test_queries = [
        "Why was REQ001 approved?",
        "Why was REQ004 rejected?",
        "Why was REQ007 escalated?"
    ]

    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 50)
        chunks = retrieve_chunks(query, k=2)
        for i, chunk in enumerate(chunks):
            print(f"Chunk {i+1}: {chunk.page_content[:100]}...")