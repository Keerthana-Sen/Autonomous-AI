from pydantic import BaseModel


class QuestionRequest(BaseModel):
    """Input for both RAG and Agent endpoints."""
    question: str


class AnswerResponse(BaseModel):
    """Standard response for both endpoints."""
    question: str
    answer: str
    mode: str        # "rag" or "agent"
    contexts: list[str] = []   # retrieved chunks (empty for agent)