from langchain_core.prompts import PromptTemplate

PROMPT_TEMPLATE = """
You are an AI assistant that explains workflow automation decisions.
Use ONLY the context below to answer. If the answer isn't in the context, say "I don't know based on the available policies."

Context:
{context}

Question:
{question}

Think step by step:
1. Identify the exact amount or condition mentioned in the question
2. Find which range or rule it falls into from the context
3. State the required approval or action clearly

Explanation:
"""

# PromptTemplate makes this LangChain-compatible with {context} and {question} as inputs
prompt = PromptTemplate(
    input_variables=["context", "question"],
    template=PROMPT_TEMPLATE
)