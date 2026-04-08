import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.agent.agent_graph import agent_graph


def run_agent(question: str) -> dict:
    """
    Run the agent on a single question.

    Args:
        question: The input question

    Returns:
        Dict with question and final answer
    """
    print(f"\n{'='*70}")
    print(f"AGENT QUERY: {question}")
    print('='*70)

    # Initialize state
    initial_state = {
        "question": question,
        "messages": [],
        "tool_calls": [],
        "final_answer": ""
    }

    # Run the agent
    result = agent_graph.invoke(initial_state)

    answer = result.get("final_answer", "")
    print(f"\n[FINAL ANSWER]\n{answer}")
    print('='*70)

    return {
        "question": question,
        "answer": answer
    }


def run_agent_batch(qa_pairs: list) -> list:
    """
    Run agent on multiple questions.

    Args:
        qa_pairs: List of dicts with 'question' and optionally 'answer' (truth)

    Returns:
        List of results with question, agent answer, and truth (if available)
    """
    results = []

    for i, pair in enumerate(qa_pairs):
        question = pair["question"]
        truth = pair.get("answer", None)

        print(f"\n\n{'#'*70}")
        print(f"Processing Q{i+1}/{len(qa_pairs)}")
        print(f"{'#'*70}")

        result = run_agent(question)
        result["truth"] = truth
        results.append(result)

    print(f"\n\n{'*'*70}")
    print(f"Completed {len(results)} agent queries")
    print(f"{'*'*70}\n")

    return results


if __name__ == "__main__":
    # Example usage
    from src.evaluation.load_dataset import load_truth

    qa_pairs = load_truth()[:3]  # Test on first 3 questions

    results = run_agent_batch(qa_pairs)

    # Display results
    for i, result in enumerate(results):
        print(f"\nQ{i+1}: {result['question']}")
        print(f"Agent: {result['answer']}")
        if result.get("truth"):
            print(f"Truth: {result['truth']}")
