"""Unit tests for all 5 showcase agents — all external API calls are mocked."""
import importlib.util
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock
import pytest

AGENTS_DIR = Path(__file__).parent.parent / "agents"


_TEST_ENV = {
    "ANTHROPIC_API_KEY": "test-key",
    "OPENAI_API_KEY": "test-key",
    "GOOGLE_API_KEY": "test-key",
}


def load_agent(name: str, extra_mocks: dict):
    """Load an agent module by path with sys.modules pre-populated with mocks."""
    path = AGENTS_DIR / name / "agent.py"
    module_name = f"agent_{name.replace('-', '_')}"
    saved_mods = {}
    for k, v in extra_mocks.items():
        saved_mods[k] = sys.modules.get(k)
        sys.modules[k] = v
    saved_env = {}
    for k, v in _TEST_ENV.items():
        saved_env[k] = os.environ.get(k)
        os.environ[k] = v
    try:
        spec = importlib.util.spec_from_file_location(module_name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    finally:
        for k, v in saved_mods.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v
        for k, v in saved_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


# ---------------------------------------------------------------------------
# Claude SDK
# ---------------------------------------------------------------------------

def _claude_mocks(response_text: str | None = "Enterprise AI: efficiency, cost, scale."):
    anthropic = MagicMock()
    if response_text is None:
        msg = MagicMock()
        msg.content = []
        anthropic.Anthropic.return_value.messages.create.return_value = msg
    else:
        msg = MagicMock()
        msg.content = [MagicMock(text=response_text)]
        anthropic.Anthropic.return_value.messages.create.return_value = msg
    return {"anthropic": anthropic, "dotenv": MagicMock()}


def test_claude_sdk_run_returns_string():
    mod = load_agent("claude-sdk", _claude_mocks())
    result = mod.run("test prompt")
    assert isinstance(result, str) and len(result) > 0


def test_claude_sdk_raises_on_empty_content():
    mod = load_agent("claude-sdk", _claude_mocks(response_text=None))
    with pytest.raises(RuntimeError, match="Claude SDK agent failed"):
        mod.run("test prompt")


def test_claude_sdk_wraps_api_error():
    anthropic = MagicMock()
    anthropic.Anthropic.return_value.messages.create.side_effect = Exception("API error")
    mod = load_agent("claude-sdk", {"anthropic": anthropic, "dotenv": MagicMock()})
    with pytest.raises(RuntimeError, match="Claude SDK agent failed"):
        mod.run("test prompt")


# ---------------------------------------------------------------------------
# OpenAI Agents
# ---------------------------------------------------------------------------

def _openai_mocks(output: str = "1. Productivity 2. Cost 3. Revenue"):
    agents_mod = MagicMock()
    result = MagicMock()
    result.final_output = output
    agents_mod.Runner.run_sync.return_value = result
    return {"agents": agents_mod, "dotenv": MagicMock()}


def test_openai_agents_run_returns_string():
    mod = load_agent("openai-agents", _openai_mocks())
    result = mod.run("test prompt")
    assert isinstance(result, str) and len(result) > 0


def test_openai_agents_wraps_error():
    agents_mod = MagicMock()
    agents_mod.Runner.run_sync.side_effect = Exception("OpenAI error")
    mod = load_agent("openai-agents", {"agents": agents_mod, "dotenv": MagicMock()})
    with pytest.raises(RuntimeError, match="OpenAI Agents agent failed"):
        mod.run("test prompt")


# ---------------------------------------------------------------------------
# LangGraph / Ollama
# ---------------------------------------------------------------------------

def _langgraph_mocks(response: str = "Ollama answer"):
    requests_mod = MagicMock()
    tag_resp = MagicMock()
    tag_resp.json.return_value = {"models": [{"name": "llama3.2"}]}
    requests_mod.get.return_value = tag_resp

    llm_resp = MagicMock()
    llm_resp.content = response
    lco = MagicMock()
    lco.ChatOllama.return_value.invoke.return_value = llm_resp

    compiled = MagicMock()
    compiled.invoke.return_value = {"response": response}

    lgg = MagicMock()
    lgg.StateGraph.return_value.compile.return_value = compiled
    lgg.END = "END"

    return {
        "langchain_ollama": lco,
        "langgraph": MagicMock(),
        "langgraph.graph": lgg,
        "requests": requests_mod,
        "dotenv": MagicMock(),
    }, compiled


def test_langgraph_run_returns_string():
    mocks, compiled = _langgraph_mocks()
    mod = load_agent("langgraph", mocks)
    mod.app = compiled
    result = mod.run("test prompt")
    assert isinstance(result, str) and len(result) > 0


def test_langgraph_wraps_error():
    mocks, _ = _langgraph_mocks()
    failing = MagicMock()
    failing.invoke.side_effect = Exception("Ollama down")
    mod = load_agent("langgraph", mocks)
    mod.app = failing
    with pytest.raises(RuntimeError, match="LangGraph/Ollama agent failed"):
        mod.run("test prompt")


def test_langgraph_pick_model_from_env():
    """_pick_model() returns OLLAMA_MODEL env var if set."""
    mocks, compiled = _langgraph_mocks()
    os.environ["OLLAMA_MODEL"] = "my-custom-model"
    try:
        mod = load_agent("langgraph", mocks)
        assert mod._MODEL == "my-custom-model"
    finally:
        del os.environ["OLLAMA_MODEL"]


def test_langgraph_pick_model_fallback_when_no_match():
    """_pick_model() falls back to 'llama3.1' when no preferred model is available."""
    requests_mod = MagicMock()
    tag_resp = MagicMock()
    tag_resp.json.return_value = {"models": [{"name": "unknown-model"}]}
    requests_mod.get.return_value = tag_resp

    lco = MagicMock()
    lgg = MagicMock()
    compiled = MagicMock()
    compiled.invoke.return_value = {"response": "ok"}
    lgg.StateGraph.return_value.compile.return_value = compiled
    lgg.END = "END"

    mocks = {
        "langchain_ollama": lco,
        "langgraph": MagicMock(),
        "langgraph.graph": lgg,
        "requests": requests_mod,
        "dotenv": MagicMock(),
    }
    mod = load_agent("langgraph", mocks)
    # No preferred model matched — should pick the only available model
    assert mod._MODEL == "unknown-model"


def test_langgraph_pick_model_fallback_on_request_error():
    """_pick_model() falls back to 'llama3.1' when Ollama API is unreachable."""
    requests_mod = MagicMock()
    requests_mod.get.side_effect = Exception("Connection refused")

    lco = MagicMock()
    lgg = MagicMock()
    compiled = MagicMock()
    compiled.invoke.return_value = {"response": "ok"}
    lgg.StateGraph.return_value.compile.return_value = compiled
    lgg.END = "END"

    mocks = {
        "langchain_ollama": lco,
        "langgraph": MagicMock(),
        "langgraph.graph": lgg,
        "requests": requests_mod,
        "dotenv": MagicMock(),
    }
    mod = load_agent("langgraph", mocks)
    assert mod._MODEL == "llama3.1"


def test_langgraph_answer_node_accepts_message_alias():
    """answer() accepts 'message' key as alias for 'prompt'."""
    mocks, _ = _langgraph_mocks()
    mod = load_agent("langgraph", mocks)
    llm_resp = MagicMock()
    llm_resp.content = "response via message alias"
    mod.llm = MagicMock()
    mod.llm.invoke.return_value = llm_resp
    result = mod.answer({"prompt": "", "message": "test via alias", "response": ""})
    assert result["response"] == "response via message alias"


def test_langgraph_answer_node_raises_on_empty_content():
    """answer() raises RuntimeError when LLM returns empty content."""
    mocks, _ = _langgraph_mocks()
    mod = load_agent("langgraph", mocks)
    llm_resp = MagicMock()
    llm_resp.content = ""
    mod.llm = MagicMock()
    mod.llm.invoke.return_value = llm_resp
    with pytest.raises(RuntimeError, match="LangGraph/Ollama agent failed"):
        mod.answer({"prompt": "test", "message": "", "response": ""})


# ---------------------------------------------------------------------------
# Google ADK
# ---------------------------------------------------------------------------

def _google_adk_mocks(response_text: str | None = "Google ADK answer"):
    part = MagicMock()
    part.text = response_text
    content = MagicMock()
    content.parts = [part] if response_text else []

    event = MagicMock()
    event.is_final_response.return_value = True
    event.content = content if response_text else None

    session = MagicMock()
    session.id = "sess-1"
    session_service = MagicMock()
    session_service.create_session = AsyncMock(return_value=session)

    runner = MagicMock()

    async def _gen(*a, **kw):
        yield event

    runner.run_async = _gen

    adk_agent = MagicMock()
    adk_runner = MagicMock()
    adk_runner.Runner.return_value = runner
    adk_session = MagicMock()
    adk_session.InMemorySessionService.return_value = session_service

    mocks = {
        "google": MagicMock(),
        "google.adk": MagicMock(),
        "google.adk.agents": adk_agent,
        "google.adk.runners": adk_runner,
        "google.adk.sessions": adk_session,
        "google.genai": MagicMock(),
        "google.genai.types": MagicMock(),
        "dotenv": MagicMock(),
    }
    return mocks, session_service, runner


def test_google_adk_run_returns_string():
    mocks, ss, runner = _google_adk_mocks()
    mod = load_agent("google-adk", mocks)
    mod._session_service = ss
    mod._runner = runner
    result = mod.run("test prompt")
    assert result == "Google ADK answer"


def test_google_adk_raises_on_empty_response():
    mocks, ss, runner = _google_adk_mocks(response_text=None)
    mod = load_agent("google-adk", mocks)
    mod._session_service = ss
    mod._runner = runner
    with pytest.raises(RuntimeError, match="Google ADK agent failed"):
        mod.run("test prompt")


# ---------------------------------------------------------------------------
# CrewAI
# ---------------------------------------------------------------------------

def _crewai_mocks(output: str = "CrewAI result"):
    crew_instance = MagicMock()
    crew_instance.kickoff.return_value = output
    crewai_mod = MagicMock()
    crewai_mod.Crew.return_value = crew_instance
    return {"crewai": crewai_mod, "dotenv": MagicMock()}, crew_instance


def test_crewai_run_returns_string():
    mocks, crew = _crewai_mocks()
    mod = load_agent("crewai", mocks)
    mod.crew = crew
    result = mod.run("test prompt")
    assert isinstance(result, str) and len(result) > 0


def test_crewai_wraps_error():
    mocks, _ = _crewai_mocks()
    failing_crew = MagicMock()
    failing_crew.kickoff.side_effect = Exception("LLM error")
    mod = load_agent("crewai", mocks)
    mod.crew = failing_crew
    with pytest.raises(RuntimeError, match="CrewAI agent failed"):
        mod.run("test prompt")
