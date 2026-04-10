import os
import requests

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

SYSTEM_PROMPT = """You are an observability assistant for a home NAS running OpenMediaVault.
You have access to real-time metrics from Prometheus. When given a health summary,
answer the user's question concisely and in plain English. Flag anything concerning.
Rules:
- If disk usage is above 80%, warn the user
- If swap usage is above 90%, flag it as critical
- If any disk SMART status is FAILING, treat it as urgent
- If a container shows DOWN, mention it by name
Keep responses under 200 words."""


def ask_llm(question: str, context: str) -> str:
    """Send a question and metrics context to Ollama, return plain English response."""
    prompt = f"""Here is the current state of the NAS:

{context}

User question: {question}"""

    try:
        r = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "system": SYSTEM_PROMPT,
                "stream": False
            },
            timeout=60
        )
        r.raise_for_status()
        return r.json().get("response", "No response from LLM")
    except Exception as e:
        return f"LLM error: {e}"
