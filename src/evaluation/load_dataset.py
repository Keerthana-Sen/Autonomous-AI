import json
import os
from pathlib import Path

# Path to your truth QA JSON file
TRUTH_PATH = "data/truth/qa_pairs.json"


def load_truth():
    """
    Loads the truth QA pairs from JSON.
    Returns a list of dicts with 'question' and 'answer' keys.
    """

    path = Path(TRUTH_PATH)

    if not path.exists():
        raise FileNotFoundError(f"truth file not found at {TRUTH_PATH}")

    with open(path, "r") as f:
        data = json.load(f)

    print(f"Loaded {len(data)} truth QA pairs")
    return data


if __name__ == "__main__":
    qa_pairs = load_truth()
    for i, pair in enumerate(qa_pairs):
        print(f"\nQ{i+1}: {pair['question']}")
        print(f"A{i+1}: {pair['answer']}")