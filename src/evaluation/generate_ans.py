import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.baseline_rag.rag_chain import build_rag_chain
from src.retrieval.retriever import get_retriever
from groq import RateLimitError


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

        # Retry up to 3 times if rate limited
        for attempt in range(3):
            try:
                generated_answer = chain.invoke(question)
                break  # success — exit retry loop
            except RateLimitError as e:
                wait_time = 90  # wait 90 seconds before retrying
                print(f"Rate limit hit. Waiting {wait_time}s before retry {attempt+1}/3...")
                time.sleep(wait_time)
                if attempt == 2:
                    raise e  # give up after 3 attempts

        # Retrieve contexts separately for RAGAS
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