import os
from crewai import Agent, Task, Crew, LLM
from dotenv import load_dotenv

load_dotenv()

PROMPT = "What are the top 3 benefits of AI agents in enterprise?"

llm = LLM(
    model="anthropic/claude-sonnet-4-6",
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
)

analyst = Agent(
    role="Enterprise AI Analyst",
    goal="Provide clear, numbered analysis of enterprise AI benefits",
    backstory="You are a senior enterprise technology analyst with 10 years of AI experience.",
    llm=llm,
    verbose=False,
)


def run(prompt: str = PROMPT) -> str:
    try:
        task = Task(
            description=prompt,
            expected_output="A numbered list of exactly 3 enterprise benefits with brief explanations",
            agent=analyst,
        )
        crew = Crew(agents=[analyst], tasks=[task], verbose=False)
        result = crew.kickoff()
        return str(result)
    except Exception as e:
        raise RuntimeError(f"CrewAI agent failed: {e}") from e


if __name__ == "__main__":
    print(run())
