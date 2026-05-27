import os
from dotenv import load_dotenv
from pathlib import Path
from datasets import Dataset
from ragas import evaluate
from ragas import RunConfig
from ragas.metrics import faithfulness, context_precision, context_recall
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.globals import set_llm_cache
from langchain_community.cache import SQLiteCache

dotenv_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=dotenv_path)

# Cache LLM responses to disk — repeated eval runs with same data are instant
_CACHE_PATH = str(Path(__file__).resolve().parent.parent.parent / ".ragas_cache.db")
set_llm_cache(SQLiteCache(database_path=_CACHE_PATH))


def get_ragas_config():
    """
    RAGAS LLM + embeddings config using Groq and HuggingFace.
    No OpenAI needed — fully free.
    """

    # Groq LLM wrapped for RAGAS
    llm = ChatGroq(
        model_name="llama-3.1-8b-instant",
        groq_api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.0,
        max_tokens=2048
    )
    ragas_llm = LangchainLLMWrapper(llm)  # wrap for RAGAS compatibility

    # HuggingFace embeddings — free, local, no API needed
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    ragas_embeddings = LangchainEmbeddingsWrapper(embeddings)

    return ragas_llm, ragas_embeddings


def run_ragas_evaluation(results: list) -> dict:
    """
    Runs RAGAS on generated answers.
    Scores: faithfulness, context_precision, context_recall.
    """

    ragas_llm, ragas_embeddings = get_ragas_config()

    # RAGAS expects these exact column names
    dataset = Dataset.from_dict({
        "question":  [r["question"] for r in results],
        "answer":    [r["answer"] for r in results],
        "reference": [r.get("truth", r.get("ground_truth", "")) for r in results],
        "contexts":  [r["contexts"] for r in results],
    })

    print("\nRunning RAGAS evaluation...")

    scores = evaluate(
        dataset=dataset,
        metrics=[faithfulness, context_precision, context_recall],
        llm=ragas_llm,
        embeddings=ragas_embeddings,
        run_config=RunConfig(max_workers=8, timeout=120)
    )

    return scores


def print_scores(scores, title="RAGAS EVALUATION RESULTS"):
    """Prints RAGAS scores in a readable format."""

    print("\n" + "="*50)
    print(title)
    print("="*50)

    metrics = {}
    for key in ["faithfulness", "context_precision", "context_recall"]:
        raw = scores[key]

        # Handle list of per-sample scores — average them, skip NaN
        if isinstance(raw, list):
            valid = [x for x in raw if x is not None and x == x]
            avg = sum(valid) / len(valid) if valid else 0.0
        else:
            avg = raw if (raw is not None and raw == raw) else 0.0

        metrics[key.replace("_", " ").title()] = avg

    for name, score in metrics.items():
        bar = "█" * int(score * 20) + "░" * (20 - int(score * 20))
        print(f"{name:<20} {score:.4f}  |{bar}")

    print("="*50)
    avg = sum(metrics.values()) / len(metrics)
    print(f"{'Average Score':<20} {avg:.4f}")
    print("="*50)

    return metrics