import os
from dotenv import load_dotenv
from pathlib import Path
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings

dotenv_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=dotenv_path)


def get_ragas_config():
    """
    RAGAS needs its own LLM + embeddings to score answers.
    We wrap LangChain's ChatGroq in LangchainLLMWrapper so RAGAS can use it.
    HuggingFace embeddings are used for answer_relevancy scoring — free, no API needed.
    """

    # Wrap Groq LLM for RAGAS — LangchainLLMWrapper is the correct interface
    llm = ChatGroq(
        model_name="llama-3.1-8b-instant",
        groq_api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.0,
        max_tokens=2048
    )
    ragas_llm = LangchainLLMWrapper(llm)          # ✅ fixed: llm not groq_llm

    # ✅ Keep only this embeddings block — delete the duplicate below it
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    ragas_embeddings = LangchainEmbeddingsWrapper(embeddings)

    return ragas_llm, ragas_embeddings


def run_ragas_evaluation(results: list) -> dict:
    """
    Runs RAGAS on generated answers.
    Scores: faithfulness, answer_relevancy, context_precision, context_recall.
    """

    ragas_llm, ragas_embeddings = get_ragas_config()

    # RAGAS expects these exact column names
    dataset = Dataset.from_dict({
        "question":     [r["question"] for r in results],
        "answer":       [r["answer"] for r in results],
        "reference":    [r["truth"] for r in results],
        "contexts":     [r["contexts"] for r in results],
    })

    print("\nRunning RAGAS evaluation...")

    scores = evaluate(
        dataset=dataset,
        metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
        llm=ragas_llm,
        embeddings=ragas_embeddings   # needed for answer_relevancy
    )

    return scores


def print_scores(scores):
    """Prints RAGAS scores in a readable format."""

    print("\n" + "="*50)
    print("RAGAS EVALUATION RESULTS — BASELINE RAG")
    print("="*50)

    metrics = {}
    for key in ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]:
        raw = scores[key]

        # RAGAS sometimes returns a list of per-sample scores — average them
        if isinstance(raw, list):
            valid = [x for x in raw if x is not None and not (isinstance(x, float) and x != x)]  # filter NaN
            avg = sum(valid) / len(valid) if valid else 0.0
        else:
            avg = raw if raw is not None else 0.0

        metrics[key.replace("_", " ").title()] = avg

    for name, score in metrics.items():
        bar = "█" * int(score * 20) + "░" * (20 - int(score * 20))
        print(f"{name:<20} {score:.4f}  |{bar}")

    print("="*50)
    avg = sum(metrics.values()) / len(metrics)
    print(f"{'Average Score':<20} {avg:.4f}")
    print("="*50)

    return metrics