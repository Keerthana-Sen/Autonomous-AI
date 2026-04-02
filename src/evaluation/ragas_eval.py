from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,         # is the answer faithful to the retrieved context?
    answer_relevancy,     # is the answer relevant to the question?
    context_precision,    # are retrieved chunks precise/relevant?
    context_recall        # did retrieval capture all needed info?
)


def run_ragas_evaluation(results: list):
    """
    Takes generated results and runs RAGAS evaluation.

    Metrics explained:
    - faithfulness     : Does the answer stick to the context? (hallucination check)
    - answer_relevancy : Is the answer actually addressing the question?
    - context_precision: Are the retrieved chunks relevant to the question?
    - context_recall   : Did we retrieve all the chunks needed to answer?

    Returns a dict of metric scores.
    """

    # RAGAS expects a HuggingFace Dataset with these exact column names
    ragas_data = {
        "question":     [r["question"] for r in results],
        "answer":       [r["answer"] for r in results],
        "truth":        [r["truth"] for r in results],
        "contexts":     [r["contexts"] for r in results],
    }

    dataset = Dataset.from_dict(ragas_data)
    print("\nRunning RAGAS evaluation...")

    # Run all 4 metrics at once
    scores = evaluate(
        dataset=dataset,
        metrics=[
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall
        ]
    )

    return scores


def print_scores(scores):
    """Prints RAGAS scores in a readable format."""

    print("\n" + "="*50)
    print("RAGAS EVALUATION RESULTS — BASELINE RAG")
    print("="*50)

    metrics = {
        "Faithfulness":      scores["faithfulness"],
        "Answer Relevancy":  scores["answer_relevancy"],
        "Context Precision": scores["context_precision"],
        "Context Recall":    scores["context_recall"],
    }

    for metric, score in metrics.items():
        bar = "█" * int(score * 20)  # visual progress bar
        print(f"{metric:<20} {score:.4f}  |{bar}")

    print("="*50)
    avg = sum(metrics.values()) / len(metrics)
    print(f"{'Average Score':<20} {avg:.4f}")
    print("="*50)

    return metrics