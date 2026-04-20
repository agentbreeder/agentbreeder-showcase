import asyncio
import os
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part
from dotenv import load_dotenv

load_dotenv()

PROMPT = "What are the top 3 benefits of AI agents in enterprise?"

_agent = Agent(
    name="demo_google_adk",
    model="gemini-2.5-flash",
    instruction="You are a helpful enterprise AI analyst. Answer concisely.",
)

# Export as root_agent for agentbreeder's google-adk server template
root_agent = _agent

_session_service = InMemorySessionService()
_runner = Runner(agent=_agent, app_name="showcase", session_service=_session_service)


async def _run_async(prompt: str) -> str:
    session = await _session_service.create_session(app_name="showcase", user_id="user")
    content = Content(role="user", parts=[Part(text=prompt)])
    result = ""
    async for event in _runner.run_async(user_id="user", session_id=session.id, new_message=content):
        if event.is_final_response() and event.content and event.content.parts:
            result = event.content.parts[0].text
    if not result:
        raise ValueError("Empty response from Google ADK agent")
    return result


def run(prompt: str = PROMPT) -> str:
    try:
        return asyncio.run(_run_async(prompt))
    except Exception as e:
        raise RuntimeError(f"Google ADK agent failed: {e}") from e


if __name__ == "__main__":
    print(run())
