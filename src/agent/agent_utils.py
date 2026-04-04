from langchain_core.tools import StructuredTool
from src.agent.tools import check_transaction, lookup_policy, retrieve_policy_context


def get_tools_for_llm() -> list:
    """Returns LangChain StructuredTool list for LLM binding."""
    return [
        StructuredTool.from_function(
            check_transaction,
            name="check_transaction",
            description="Check details of a specific transaction by request_id"
        ),
        StructuredTool.from_function(
            lookup_policy,
            name="lookup_policy",
            description=(
                "Lookup a specific policy rule by name. "
                "Valid policy names are ONLY: "
                "'auto_approval_limit', 'manager_approval_limit', "
                "'duplicate_window_days', 'required_approvers'. "
                "Do not guess other names."
                )
        ),
        StructuredTool.from_function(
            retrieve_policy_context,
            name="retrieve_policy_context",
            description="Search policy documents for rules relevant to a query string"
        ),
    ]


# Tool name → function mapping used in tool execution node
TOOL_MAP = {
    "check_transaction": check_transaction,
    "lookup_policy": lookup_policy,
    "retrieve_policy_context": retrieve_policy_context,
}


def extract_clean_answer(raw: str) -> str:
    """
    Strips tool call syntax, Action/Observation traces, and
    leading labels like 'Final Answer:' from LLM output.
    Ensures RAGAS receives a clean answer string.
    """
    lines = raw.strip().split("\n")
    clean_lines = []

    for line in lines:
        # Skip reasoning trace lines
        if any(line.startswith(prefix) for prefix in [
            "Action:", "Action Input:", "Observation:",
            "Thought:", "Tool:", "```"
        ]):
            continue
        # Strip label if present
        if line.lower().startswith("final answer:"):
            line = line[len("final answer:"):].strip()
        clean_lines.append(line)

    return "\n".join(clean_lines).strip()