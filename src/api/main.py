import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from fastapi import FastAPI
from src.api.routes import router
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Autonomous AI — Workflow Decision Explainer",
    description="Compare baseline RAG vs autonomous agent for explaining workflow decisions",
    version="1.0.0"
)

app.include_router(router, prefix="/api")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)