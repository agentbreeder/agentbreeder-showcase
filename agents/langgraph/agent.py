import os
import requests
from typing import TypedDict
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv

load_dotenv()

_PREFERRED_MODELS = ["gemma4", "gemma3", "llama3.2:3b", "llama3.2", "llama3.3", "llama3.1", "llama3", "mistral", "phi3"]
_OLLAMA_BASE = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")


def _pick_model() -> str:
    if env := os.environ.get("OLLAMA_MODEL"):
        return env
    try:
        models = requests.get(f"{_OLLAMA_BASE}/api/tags", timeout=3).json().get("models", [])
        # Build both full names (with tag) and base names (without tag) for matching
        available_full = {m["name"] for m in models}
        available_base = {m["name"].split(":")[0] for m in models}
        for candidate in _PREFERRED_MODELS:
            if candidate in available_full or candidate in available_base:
                # Return full name with tag if available, to avoid "not found" errors
                for m in models:
                    if m["name"] == candidate or m["name"].split(":")[0] == candidate:
                        return m["name"]
        if available_full:
            return next(iter(available_full))
    except Exception:
        pass
    return "llama3.1"


_MODEL = _pick_model()

PROMPT = "What are the top 3 benefits of AI agents in enterprise?"

llm = ChatOllama(
    model=_MODEL,
    base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
)


class State(TypedDict):
    prompt: str
    message: str  # alias accepted by agentbreeder server template
    response: str


def answer(state: State) -> State:
    try:
        # Accept "message" as alias for "prompt" (agentbreeder server compatibility)
        prompt = state.get("prompt") or state.get("message", "")
        response = llm.invoke(prompt)
        if not response.content:
            raise ValueError("Empty response from Ollama model")
        return {"response": response.content}
    except Exception as e:
        raise RuntimeError(f"LangGraph/Ollama agent failed: {e}") from e


graph = StateGraph(State)
graph.add_node("answer", answer)
graph.set_entry_point("answer")
graph.add_edge("answer", END)
app = graph.compile()


def run(prompt: str = PROMPT) -> str:
    try:
        result = app.invoke({"prompt": prompt, "response": ""})
        return result["response"]
    except Exception as e:
        raise RuntimeError(f"LangGraph/Ollama agent failed: {e}") from e


if __name__ == "__main__":  # pragma: no cover
    print(run())
