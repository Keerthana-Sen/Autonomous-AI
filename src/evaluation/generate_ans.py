import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.baseline_rag.rag_chain import build_rag_chain
from src.retrieval.retriever import get_retriever


def generate_rag_answers(qa_pairs: list):
    """
    For each QA pair, runs the question through the RAG chain.
    Returns a list of dicts with:
    - question       : original question
    - answer         : RAG generated answer
    - truth   : expected answer from dataset
    - contexts       : retrieved chunks used to generate the answer
    """

    chain = build_rag_chain()       # build RAG chain once, reuse for all questions
    retriever = get_retriever(k=3)  # same retriever used in chain

    results = []

    for i, pair in enumerate(qa_pairs):
        question = pair["question"]
        truth = pair["answer"]

        print(f"\nProcessing Q{i+1}/{len(qa_pairs)}: {question}")

        # Get generated answer from RAG chain
        generated_answer = chain.invoke(question)

        # Get retrieved context chunks separately for RAGAS evaluation
        # RAGAS needs to see what context was used to generate the answer
        retrieved_docs = retriever.invoke(question)
        contexts = [doc.page_content for doc in retrieved_docs]

        results.append({
            "question": question,
            "answer": generated_answer,        # what RAG said
            "truth": truth,                    # what it should have said
            "contexts": contexts               # chunks retrieved from ChromaDB
        })

        print(f"✓ Answer generated ({len(generated_answer)} chars)")

    print(f"\nGenerated answers for {len(results)} questions")
    return results