import sys
import os
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from langchain_core.runnables import RunnablePassthrough

from src.baseline_rag.prompt import prompt
from src.baseline_rag.llm import get_llm
from src.retrieval.retriever import get_retriever


def format_chunks(docs):
    """Joins retrieved chunks into a single context string for the prompt."""
    return "\n\n".join([doc.page_content for doc in docs])


def _parse_llm_response(response) -> str:
    """StrOutputParser replacement that handles thinking-model empty content."""
    if hasattr(response, "content") and response.content:
        return response.content
    if hasattr(response, "additional_kwargs"):
        rc = response.additional_kwargs.get("reasoning_content", "")
        if rc:
            return rc
    return str(response)


def build_rag_chain():
    llm = get_llm()
    retriever = get_retriever(k=3)

    chain = (
        {
            "context": retriever | format_chunks,
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
        | _parse_llm_response
    )

    print("RAG chain built successfully")
    return chain