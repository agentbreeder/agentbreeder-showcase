import os
from google.adk.agents import Agent
from dotenv import load_dotenv

load_dotenv()

PROMPT = "What are the top 3 benefits of AI agents in enterprise?"

agent = Agent(
    name="demo-google-adk",
    model="gemini-3.0-flash",
    instruction="You are a helpful enterprise AI analyst. Answer concisely.",
)


def run(prompt: str = PROMPT) -> str:
    try:
        response = agent.run(prompt)
        return response.text
    except Exception as e:
        raise RuntimeError(f"Google ADK agent failed: {e}") from e


if __name__ == "__main__":
    print(run())
