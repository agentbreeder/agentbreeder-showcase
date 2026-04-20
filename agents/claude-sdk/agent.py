import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

PROMPT = "What are the top 3 benefits of AI agents in enterprise?"


def run(prompt: str = PROMPT) -> str:
    try:
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        if not message.content:
            raise ValueError("Empty response from Anthropic API")
        return message.content[0].text
    except Exception as e:
        raise RuntimeError(f"Claude SDK agent failed: {e}") from e


if __name__ == "__main__":  # pragma: no cover
    print(run())
