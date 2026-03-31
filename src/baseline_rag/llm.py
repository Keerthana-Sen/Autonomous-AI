import os
from dotenv import load_dotenv
from pathlib import Path
from langchain_groq import ChatGroq

# Load .env from project root
dotenv_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=dotenv_path)


def get_llm():
    """
    Returns a Groq LLM instance using llama-3.1-8b-instant.
    Free tier: 14,400 requests/day, 500,000 tokens/day.
    Swap model_name here when moving to agent phase.
    """

    groq_api_key = os.getenv("GROQ_API_KEY")

    llm = ChatGroq(
        model_name="llama-3.3-70b-versatile",  # free, fast, generous limits
        groq_api_key=groq_api_key,
        temperature=0.3,        # low = more factual answers
        max_tokens=512          # enough for policy explanations
    )

    print("LLM loaded: llama-3.1-8b-instant via Groq")
    return llm