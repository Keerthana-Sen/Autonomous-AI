import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.baseline_rag.rag_chain import build_rag_chain


def run_query(query: str):
    """Builds the chain and runs a single query. Returns the answer."""

    chain = build_rag_chain()

    print(f"\nQuery: {query}")
    print("-" * 50)

    # .invoke() triggers the full pipeline — retrieve → prompt → LLM → parse
    answer = chain.invoke(query)

    print(f"Answer:\n{answer}")
    print("-" * 50)
    return answer


if __name__ == "__main__":

    # Test queries that match your synthetic dataset
    test_queries = [
        "Why was this request escalated to the director?",
        "What is the approval process for a 7000 USD request?",
        "Can a manager approve a 500 USD request automatically?"
    ]

    for query in test_queries:
        run_query(query)