import sys
import os
import json
import math

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.evaluation.load_dataset import load_truth
from src.evaluation.generate_ans import generate_rag_answers
from src.evaluation.ragas_eval import run_ragas_evaluation, print_scores


def save_results(results: list, scores: dict):
    """Saves raw answers and scores to data/results/ for later comparison with agent."""

    os.makedirs("data/results", exist_ok=True)

    # Save raw generated answers
    with open("data/results/baseline_rag_answers.json", "w") as f:
        json.dump(results, f, indent=2)

    # Save scores (compute mean of each metric returned as lists, filtering NaN values)
    score_dict = {}
    for key in ["faithfulness", "context_precision", "context_recall"]:
        valid_scores = [x for x in scores[key] if not math.isnan(x)]
        score_dict[key] = sum(valid_scores) / len(valid_scores) if valid_scores else 0.0

    with open("data/results/baseline_rag_scores.json", "w") as f:
        json.dump(score_dict, f, indent=2)

    print("\nResults saved to data/results/")


if __name__ == "__main__":

    # Step 1: Load ground truth QA pairs
    qa_pairs = load_truth()

    # Step 2: Run each question through RAG chain, collect answers + contexts
    results = generate_rag_answers(qa_pairs)

    # Step 3: Score with RAGAS
    scores = run_ragas_evaluation(results)

    # Step 4: Print scores
    metrics = print_scores(scores)

    # Step 5: Save everything to data/results/ — needed for agent comparison later
    save_results(results, scores)