from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """
    State maintained throughout the agent's reasoning loop.
    Each field is updated as the agent moves through nodes.
    """
    question: str                                                    # original user question
    messages: Annotated[list[BaseMessage], lambda x, y: x + y]     # full message history
    tool_calls: list[dict]                                           # last set of tool calls
    final_answer: str                                                # extracted clean answer
    iterations: int                                                  # loop counter