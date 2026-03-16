# Autonomous-AI
Autonomous AI for workflow automation and data-driven decisions

An autonomous agent-based system that explains why certain workflow automation 
decisions were made, such as approval rejections or escalation triggers, using 
Retrieval-Augmented Generation and multi-step reasoning.

## Tech-stack
LLM: GPT-40
Agent framework: LangGraph
RAG pipeline: LangChain
Vector DB: Chroma DB
Embeddings: text-embedding-ada-002
Evaluation: RAGAS
Backend: FastAPI
Frontend : Streamlit

## Project Structure
autonomous-ai/
├─ data/
├── docs/
├── src/
│   ├── ingestion/
│   ├── embeddings/
│   ├── retrieval/
│   ├── baseline_rag/
│   ├── agent/
│   └── evaluation/
├── notebooks/
├── app/
├── requirements.txt
└── .env.example

