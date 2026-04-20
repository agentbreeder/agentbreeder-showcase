import os
import requests
from typing import TypedDict
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv

load_dotenv()

_PREFERRED_MODELS = ["gemma4", "gemma3", "llama3.3", "llama3.1", "llama3", "mistral"]
_OLLAMA_BASE = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")


def _pick_model() -> str:
    if env := os.environ.get("OLLAMA_MODEL"):
        return env
    try:
        available = {m["name"].split(":")[0] for m in requests.get(f"{_OLLAMA_BASE}/api/tags", timeout=3).json().get("models", [])}
        for candidate in _PREFERRED_MODELS:
            if candidate in available:
                return candidate
        if available:
            return next(iter(available))
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
    response: str


def answer(state: State) -> State:
    try:
        response = llm.invoke(state["prompt"])
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
    result = app.invoke({"prompt": prompt, "response": ""})
    return result["response"]


if __name__ == "__main__":
    print(run())
