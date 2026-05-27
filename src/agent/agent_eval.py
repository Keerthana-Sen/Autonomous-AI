import sys
import os
import json
import math
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from dotenv import load_dotenv
from langchain_core.globals import set_llm_cache
from langchain_community.cache import SQLiteCache

from src.agent.agent_runner import run_agent_batch
from src.evaluation.load_dataset import load_truth
from src.retrieval.retriever import retrieve_multi_policy_context
from src.evaluation.ragas_eval import run_ragas_evaluation

# Load .env
load_dotenv()

_CACHE_PATH = str(Path(__file__).resolve().parent.parent.parent / ".ragas_cache.db")
set_llm_cache(SQLiteCache(database_path=_CACHE_PATH))


def generate_agent_answers(qa_pairs: list) -> list:
    """
    Run agent on QA pairs to generate answers.

    Args:
        qa_pairs: List of dicts with 'question' and 'answer' (truth)

    Returns:
        List of dicts with question, agent answer, truth, and contexts
    """
    print("\n" + "="*70)
    print("GENERATING AGENT ANSWERS")
    print("="*70)

    # Run agent on all questions
    agent_results = run_agent_batch(qa_pairs)

    # Add contexts for RAGAS — use multi-policy retrieval to match what the agent actually sees
    results = []
    for i, result in enumerate(agent_results):
        question = result["question"]
        try:
            combined = retrieve_multi_policy_context(question, k_per_policy=2)
            contexts = [s.strip() for s in combined.split("---") if s.strip()]
        except Exception as e:
            print(f"Warning: Could not retrieve contexts for Q{i+1}: {e}")
            contexts = []

        results.append({
            "question": question,
            "answer": result["answer"],
            "truth": result.get("truth", ""),
            "contexts": contexts
        })

    print(f"\n✓ Generated {len(results)} agent answers with contexts")
    return results


def evaluate_agent(agent_results: list) -> dict:
    """
    Run RAGAS evaluation on agent-generated answers.
    Uses run_ragas_evaluation from ragas_eval.py — single call, no duplication.
    """
    print("\n" + "="*70)
    print("EVALUATING AGENT WITH RAGAS")
    print("="*70)

    scores = run_ragas_evaluation([
        {
            "question": r["question"],
            "answer":   r["answer"],
            "truth":    r["truth"],      # ragas_eval.py maps this to "reference"
            "contexts": r["contexts"]
        }
        for r in agent_results
    ])

    print("\n✓ RAGAS evaluation complete")
    return scores


def print_agent_scores(scores: dict):
    """Print formatted agent evaluation scores."""
    print("\n" + "="*70)
    print("AGENT EVALUATION RESULTS")
    print("="*70)

    # Handle NaN values
    metrics = {}
    for key in ["faithfulness", "context_precision", "context_recall"]:
        valid_scores = [x for x in scores[key] if not math.isnan(x)]
        avg_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0.0
        metrics[key.replace("_", " ").title()] = avg_score

    for name, score in metrics.items():
        bar = "█" * int(score * 20) + "░" * (20 - int(score * 20))
        print(f"{name:20} | {bar} | {score:.4f}")

    print("="*70)
    return metrics


def compare_with_baseline(agent_metrics: dict) -> dict:
    """
    Compare agent metrics with baseline RAG metrics.

    Args:
        agent_metrics: Agent evaluation metrics

    Returns:
        Dict with comparison results
    """
    print("\n" + "="*70)
    print("AGENT vs BASELINE COMPARISON")
    print("="*70)

    # Load baseline scores
    baseline_path = "data/results/baseline_rag_scores.json"
    if not os.path.exists(baseline_path):
        print(f"Warning: Baseline scores not found at {baseline_path}")
        print("Skipping comparison")
        return {}

    with open(baseline_path, "r") as f:
        baseline_scores = json.load(f)

    # Compare
    comparison = {}
    for metric_key, baseline_val in baseline_scores.items():
        agent_val = agent_metrics.get(metric_key.replace("_", " ").title(), 0.0)
        diff = agent_val - baseline_val
        improvement = (diff / baseline_val * 100) if baseline_val != 0 else 0

        comparison[metric_key] = {
            "agent": agent_val,
            "baseline": baseline_val,
            "difference": diff,
            "improvement_percent": improvement
        }

        direction = "↑" if diff > 0 else "↓" if diff < 0 else "="
        print(
            f"{metric_key:20} | Agent: {agent_val:.4f} | Baseline: {baseline_val:.4f} | "
            f"Diff: {diff:+.4f} {direction}"
        )

    print("="*70)
    return comparison


def save_agent_results(agent_results: list, scores: dict, comparison: dict):
    """Save all agent results and evaluation scores."""
    results_dir = Path("data/results")
    results_dir.mkdir(exist_ok=True)

    # Save full results
    with open(results_dir / "agent_answers.json", "w") as f:
        json.dump(agent_results, f, indent=2)

    # Save aggregated scores
    score_dict = {}
    for key in ["faithfulness", "context_precision", "context_recall"]:
        valid_scores = [x for x in scores[key] if not math.isnan(x)]
        score_dict[key] = sum(valid_scores) / len(valid_scores) if valid_scores else 0.0

    with open(results_dir / "agent_scores.json", "w") as f:
        json.dump(score_dict, f, indent=2)

    # Save comparison
    if comparison:
        with open(results_dir / "agent_vs_baseline.json", "w") as f:
            json.dump(comparison, f, indent=2)

    print(f"\n✓ Results saved to {results_dir}/")


def run_agent_eval():
    """Main entry point: generate answers, evaluate, and compare."""
    # Load QA pairs
    qa_pairs = load_truth()

    # Generate agent answers
    agent_results = generate_agent_answers(qa_pairs)

    # Run RAGAS evaluation
    scores = evaluate_agent(agent_results)

    # Print scores
    agent_metrics = print_agent_scores(scores)

    # Compare with baseline
    comparison = compare_with_baseline(agent_metrics)

    # Save results
    save_agent_results(agent_results, scores, comparison)

    print("\n✓ Agent evaluation complete!")


if __name__ == "__main__":
    run_agent_eval()
