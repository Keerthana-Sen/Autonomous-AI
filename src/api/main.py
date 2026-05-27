import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from pathlib import Path
from fastapi import FastAPI
from src.api.routes import router
from dotenv import load_dotenv
from langchain_core.globals import set_llm_cache
from langchain_community.cache import SQLiteCache

load_dotenv()

_CACHE_PATH = str(Path(__file__).resolve().parent.parent.parent / ".ragas_cache.db")
set_llm_cache(SQLiteCache(database_path=_CACHE_PATH))

app = FastAPI(
    title="Autonomous AI — Workflow Decision Explainer",
    description="Compare baseline RAG vs autonomous agent for explaining workflow decisions",
    version="1.0.0"
)

app.include_router(router, prefix="/api")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)