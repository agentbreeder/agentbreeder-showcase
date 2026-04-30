# Contributing to AgentBreeder Showcase

This repository hosts the official AgentBreeder side-by-side showcase: five
agent frameworks (Claude SDK, OpenAI Agents, Google ADK, LangGraph, CrewAI)
deployed via AgentBreeder to local Docker, GCP, AWS, and Azure.

The showcase is a **reference catalog** for the parent project. The bar for
contributions is "this would help a new AgentBreeder user understand what's
possible," not "this is the cleanest code possible."

## Quick start

```bash
git clone https://github.com/agentbreeder/agentbreeder-showcase.git
cd agentbreeder-showcase
pip install -r requirements.txt
npm install

# Pick an agent and follow its README
cd agents/<framework>-<scenario>
```

Every agent directory has a `README.md` with the specific deploy steps.

## What to contribute

| Type | Example |
|---|---|
| New agent template | `agents/openai-agents-customer-support/` |
| Cloud deploy config | Add `deploy/azure.yaml` for an existing agent |
| Eval scenario | New offline eval set in `evals/` |
| RAG demo | New connector in `rag/` |
| End-to-end orchestration | Multi-agent flow in `orchestration.yaml` |

## Standards

- **Self-contained.** Each agent must run with the steps in its own README,
  no hidden dependencies.
- **No secrets.** Use `.env.example` placeholders. The repo is scanned by
  `gitleaks` on every PR.
- **Realistic, not toy.** A "customer support agent" must answer real-shaped
  questions, not just `print("Hello world")`.
- **Tested.** At minimum a `pytest tests/` smoke test that the agent
  initialises without errors.

## License

By contributing, you agree to license your contribution under
[Apache License 2.0](LICENSE).

## Code of Conduct

Same as the parent project — see [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## Contributor License Agreement

Same CLA as the parent project. The
[CLA Assistant](https://cla-assistant.io/) bot will prompt you on your first
PR. Full rationale in the parent repo's
[`CLA.md`](https://github.com/agentbreeder/agentbreeder/blob/main/CLA.md).

## Parent project

The AgentBreeder platform itself lives at
[`agentbreeder/agentbreeder`](https://github.com/agentbreeder/agentbreeder).
Open feature requests and bug reports for the platform there, not in this
showcase repo.
