import os
from crewai import Agent, Task, Crew, LLM
from dotenv import load_dotenv

load_dotenv()
os.environ.setdefault("CREWAI_TRACING_ENABLED", "false")

PROMPT = "What are the top 3 benefits of AI agents in enterprise?"

llm = LLM(
    model="anthropic/claude-sonnet-4-6",
    api_key=os.environ["ANTHROPIC_API_KEY"],
)

analyst = Agent(
    role="Enterprise AI Analyst",
    goal="Provide clear, numbered analysis of enterprise AI benefits",
    backstory="You are a senior enterprise technology analyst with 10 years of AI experience.",
    llm=llm,
    verbose=False,
)

_task = Task(
    description="{prompt}",
    expected_output="A numbered list of exactly 3 enterprise benefits with brief explanations",
    agent=analyst,
)

# Export crew at module level for agentbreeder's crewai server template
crew = Crew(agents=[analyst], tasks=[_task], verbose=False)


def run(prompt: str = PROMPT) -> str:
    try:
        result = crew.kickoff(inputs={"prompt": prompt})
        return str(result)
    except Exception as e:
        raise RuntimeError(f"CrewAI agent failed: {e}") from e


if __name__ == "__main__":  # pragma: no cover
    print(run())
