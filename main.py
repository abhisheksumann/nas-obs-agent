import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()

from tools import get_full_health_summary, query_prometheus
from llm import ask_llm

app = FastAPI(title="NAS Observability Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class Question(BaseModel):
    question: str


@app.get("/health")
def health():
    """Agent liveness check."""
    return {"status": "ok"}


@app.get("/metrics/summary")
def metrics_summary():
    """Return raw health summary without LLM processing."""
    return {"summary": get_full_health_summary()}


@app.post("/ask")
def ask(body: Question):
    """Ask a natural language question about the NAS."""
    context = get_full_health_summary()
    answer = ask_llm(body.question, context)
    return {
        "question": body.question,
        "answer": answer,
        "context": context
    }


@app.get("/query")
def query(promql: str):
    """Execute a raw PromQL query directly."""
    return query_prometheus(promql)


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("AGENT_PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
