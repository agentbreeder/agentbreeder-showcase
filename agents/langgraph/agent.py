import os
from typing import TypedDict
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv

load_dotenv()

# Intended model: gemma4 (requires: brew upgrade ollama && ollama pull gemma4)
# Using llama3.1 until Ollama is upgraded
_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1")

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
