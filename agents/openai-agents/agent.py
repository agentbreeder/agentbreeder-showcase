import os
from agents import Agent, Runner
from dotenv import load_dotenv

load_dotenv()

PROMPT = "What are the top 3 benefits of AI agents in enterprise?"

agent = Agent(
    name="demo-openai-agents",
    instructions="You are a helpful enterprise AI analyst. Answer concisely.",
    model="gpt-5.2",
)


def run(prompt: str = PROMPT) -> str:
    result = Runner.run_sync(agent, prompt)
    return result.final_output


if __name__ == "__main__":
    print(run())
