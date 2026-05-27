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


class InjectTransactionRequest(BaseModel):
    request_id: str
    requester: str
    amount: str
    request_type: str
    priority: str
    approver: str
    approver_status: str
    documentation_complete: str
    duplicate: str
    account_status: str
    employee_level: str
    previous_rejection_reason: str
    decision: str