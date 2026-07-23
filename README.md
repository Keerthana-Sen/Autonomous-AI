# XFLOW — Explainable Workflow Decisions

An autonomous agent system that explains *why* workflow requests were approved, rejected, or escalated — using Retrieval-Augmented Generation and multi-step LangGraph reasoning.

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | Groq — `llama-3.1-8b-instant` |
| Agent framework | LangGraph |
| RAG pipeline | LangChain |
| Vector DB | ChromaDB (local) |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` (HuggingFace) |
| Evaluation | RAGAS |
| Backend | FastAPI |
| Frontend | Streamlit |

## Project Structure

```
Autonomous-AI/
├── data/
│   ├── raw/policies/          # Source policy text files
│   ├── chroma_db/             # Local vector store (auto-generated, git-ignored)
│   ├── transactions.csv       # Transaction dataset
│   └── results/               # RAGAS evaluation outputs
├── src/
│   ├── api/                   # FastAPI backend (main.py, routes.py)
│   ├── agent/                 # LangGraph agent (graph, nodes, prompts)
│   ├── baseline_rag/          # Baseline RAG chain for comparison
│   ├── embeddings/            # ChromaDB ingestion
│   ├── ingestion/             # Document loading and chunking
│   ├── retrieval/             # Vector store retriever
│   └── ui/                    # Streamlit frontend
└── requirements.txt
```

## Setup

### 1. Clone and create a virtual environment

```bash
git clone <repo-url>
cd Autonomous-AI
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Get a free Groq API key at [console.groq.com](https://console.groq.com).

### 3. Build the vector store

Run once to ingest policy documents into ChromaDB:

```bash
python3 -m src.embeddings.embedder
```

This reads the three policy files from `data/raw/policies/` and writes the local vector store to `data/chroma_db/`.

## Running the Application

### Start the backend (FastAPI)

```bash
source venv/bin/activate
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

### Start the frontend (Streamlit)

Open a second terminal:

```bash
source venv/bin/activate
streamlit run src/ui/app.py
```

The UI will open at `http://localhost:8501`.

## How It Works

1. A transaction (e.g. REQ007) is selected in the UI.
2. A natural-language question is sent to the FastAPI backend.
3. Two systems answer in parallel:
   - **Baseline RAG** — retrieves relevant policy chunks and generates a single-step answer.
   - **Agent (LangGraph)** — uses a multi-step reasoning loop: retrieves policy context, looks up transaction data, computes the approval tier, and synthesises an explanation.
4. Both answers are displayed side-by-side with decision badges and confidence scores.

## Evaluation

To run the RAGAS evaluation comparing agent vs baseline:

```bash
python3 -m src.evaluation.evaluate
```

Results are saved to `data/results/`.
