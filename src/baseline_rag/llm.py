from langchain_groq import ChatGroq

_MODEL = "llama-3.1-8b-instant"


def get_llm():
    llm = ChatGroq(
        model=_MODEL,
        temperature=0.0,
        max_tokens=1024,
    )
    print("LLM loaded: llama-3.1-8b-instant via Groq")
    return llm


def get_agent_llm():
    llm = ChatGroq(
        model=_MODEL,
        temperature=0.0,
        max_tokens=1024,
    )
    print("Agent LLM loaded: llama-3.1-8b-instant via Groq")
    return llm
