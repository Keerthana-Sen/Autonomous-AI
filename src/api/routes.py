import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from fastapi import APIRouter, HTTPException
from src.api.models import QuestionRequest, AnswerResponse
from src.baseline_rag.rag_chain import build_rag_chain
from src.retrieval.retriever import get_retriever
from src.agent.agent_runner import run_agent

router = APIRouter()

# Build once at startup — avoids rebuilding on every request
rag_chain = build_rag_chain()
retriever = get_retriever(k=3)


@router.get("/health")
def health():
    """Quick check that the API is running."""
    return {"status": "ok"}


@router.post("/rag", response_model=AnswerResponse)
def rag_endpoint(request: QuestionRequest):
    """
    Baseline RAG endpoint.
    Retrieves policy chunks from ChromaDB, generates answer with Groq LLM.
    """
    try:
        answer = rag_chain.invoke(request.question)
        docs = retriever.invoke(request.question)
        contexts = [doc.page_content for doc in docs]

        return AnswerResponse(
            question=request.question,
            answer=answer,
            mode="rag",
            contexts=contexts
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agent", response_model=AnswerResponse)
def agent_endpoint(request: QuestionRequest):
    """
    Autonomous agent endpoint.
    Uses LangGraph agent with tools to reason and explain decisions.
    """
    try:
        result = run_agent(request.question)

        return AnswerResponse(
            question=request.question,
            answer=result["answer"],
            mode="agent"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    