import sys
import os
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

# ✅ Updated imports
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.output_parsers import StrOutputParser

from src.baseline_rag.prompt import prompt
from src.baseline_rag.llm import get_llm
from src.retrieval.retriever import get_smart_retriever
from langchain_core.runnables import RunnableLambda


def format_chunks(docs):
    """Joins retrieved chunks into a single context string for the prompt."""
    return "\n\n".join([doc.page_content for doc in docs])


def build_rag_chain():
    llm = get_llm()

    # Smart retriever picks correct policy file per question
    def smart_retrieve(question: str):
        retriever = get_smart_retriever(question, k=3)
        return retriever.invoke(question)

    chain = (
        {
            "context": RunnableLambda(smart_retrieve) | format_chunks,
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    print("RAG chain built successfully")
    return chain