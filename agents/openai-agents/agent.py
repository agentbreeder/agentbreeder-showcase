from agents import Agent, Runner
from dotenv import load_dotenv

load_dotenv()

PROMPT = "What are the top 3 benefits of AI agents in enterprise?"

agent = Agent(
    name="demo-openai-agents",
    instructions="You are a helpful enterprise AI analyst. Answer concisely.",
    model="gpt-4o",
)


def run(prompt: str = PROMPT) -> str:
    try:
        result = Runner.run_sync(agent, prompt)
        return result.final_output
    except Exception as e:
        raise RuntimeError(f"OpenAI Agents agent failed: {e}") from e


if __name__ == "__main__":  # pragma: no cover
    print(run())
