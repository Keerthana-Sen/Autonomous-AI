from typing import TypedDict


class AgentState(TypedDict):
    question: str
    final_answer: str
    iterations: int
    retrieval_confidence: float