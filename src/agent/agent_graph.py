import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from langgraph.graph import StateGraph, START, END
from src.agent.agent_state import AgentState
from src.agent.agent_nodes import reasoning_node, end_node


def create_agent_graph():
    """Assembles the agent graph from nodes defined in agent_nodes.py."""

    graph = StateGraph(AgentState)

    # Register nodes
    graph.add_node("reasoning_node", reasoning_node)
    graph.add_node("end_node", end_node)

    # Define edges
    graph.add_edge(START, "reasoning_node")
    graph.add_edge("end_node", END)

    return graph.compile()


# Single shared instance — imported by agent_runner and evaluator
agent_graph = create_agent_graph()
print("Agent graph created successfully")