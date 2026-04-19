# AgentBreeder Multi-Framework Showcase — Design Spec
**Date:** 2026-04-19

## Overview

A side-by-side comparison demo that sends a single prompt to 5 AI agents simultaneously, each built with a different AgentBreeder-supported framework, and displays results in a formatted table. Validates the full AgentBreeder deployment pipeline across local Docker, GCP, AWS, and Azure.

## Goal

Demonstrate that AgentBreeder's "define once, deploy anywhere" promise works across every supported framework and every cloud target, using real models from Anthropic, OpenAI, Google, and Ollama.

---

## Agents

| Agent Name | Framework | Model | Notes |
|---|---|---|---|
| `demo-claude-sdk` | Claude SDK | `claude-sonnet-4-6` | Anthropic native |
| `demo-openai-agents` | OpenAI Agents SDK | `openai-5.2` | OpenAI latest |
| `demo-google-adk` | Google ADK | `gemini-3.x` | Google latest |
| `demo-langgraph` | LangGraph | `ollama/gemma4` | Local Ollama only |
| `demo-crewai` | CrewAI | `claude-sonnet-4-6` | Same model as Claude SDK — shows framework effect |

**Demo prompt (fixed):** `"What are the top 3 benefits of AI agents in enterprise?"`

---

## Repository Structure

```
agentbreeder-showcase/
├── agents/
│   ├── claude-sdk/
│   │   ├── agent.yaml
│   │   └── agent.py
│   ├── openai-agents/
│   │   ├── agent.yaml
│   │   └── agent.py
│   ├── google-adk/
│   │   ├── agent.yaml
│   │   └── agent.py
│   ├── langgraph/
│   │   ├── agent.yaml
│   │   └── agent.py
│   └── crewai/
│       ├── agent.yaml
│       └── agent.py
├── orchestration.yaml
├── .env.example
├── requirements.txt
├── deploy/
│   ├── local.sh
│   ├── gcp.sh
│   ├── aws.sh
│   └── azure.sh
└── docs/
    └── superpowers/specs/
        └── 2026-04-19-agentbreeder-showcase-design.md
```

---

## Orchestration

**Strategy:** fan-out-fan-in (AgentBreeder native)

`orchestration.yaml` fires all 5 agents in parallel, collects responses with latency metadata, and renders a side-by-side comparison table:

```
Framework       Model              Latency   Response (truncated)
─────────────────────────────────────────────────────────────────
Claude SDK      claude-sonnet-4-6  1.2s      "1. Automation..."
OpenAI Agents   openai-5.2         1.8s      "1. Efficiency..."
Google ADK      gemini-3.x         1.4s      "1. Scale..."
LangGraph       ollama/gemma4      3.1s      "1. Cost savings..."
CrewAI          claude-sonnet-4-6  1.3s      "1. Productivity..."
```

---

## agent.yaml Pattern (per agent)

```yaml
name: demo-<framework>
version: 1.0.0
team: showcase
owner: saha.rajit@gmail.com

framework: <framework>
model:
  primary: <model>
  fallback: claude-sonnet-4-6

deploy:
  cloud: local        # overridden per deploy script
  scaling:
    min: 1
    max: 3
```

---

## Deployment Pipeline

### Phase 1 — Local (Docker Compose)
1. Install AgentBreeder: `pip install agentbreeder`
2. Install Ollama + pull Gemma 4: `ollama pull gemma4`
3. Start AgentBreeder platform: `docker compose up -d`
4. `agentbreeder deploy` for each agent (or `deploy/local.sh` runs all 5)
5. `agentbreeder chat orchestration` to run the showcase

### Phase 2 — GCP (Cloud Run)
- Set `deploy.cloud: gcp` in each agent.yaml (or override via `--cloud gcp`)
- Authenticate: `gcloud auth application-default login`
- Run `deploy/gcp.sh` — deploys all 5 agents to Cloud Run

### Phase 3 — AWS (ECS Fargate)
- Set `deploy.cloud: aws`
- Authenticate: `aws configure` or use existing profile
- Run `deploy/aws.sh`

### Phase 4 — Azure (Container Apps)
- Set `deploy.cloud: azure`
- Authenticate: `az login`
- Run `deploy/azure.sh`

**Note:** `demo-langgraph` (Ollama/gemma4) is local-only — cloud deployments use `claude-sonnet-4-6` as its fallback model automatically.

---

## Secrets / Environment Variables

```bash
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
GOOGLE_API_KEY=
OLLAMA_BASE_URL=http://localhost:11434   # local only

# GCP
GOOGLE_CLOUD_PROJECT=
GOOGLE_CLOUD_REGION=us-central1

# AWS
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=

# Azure
AZURE_SUBSCRIPTION_ID=
AZURE_RESOURCE_GROUP=
AZURE_LOCATION=eastus
```

---

## Error Handling

- Any agent that fails returns `{ error: "<message>", latency: null }` — other agents continue
- LangGraph/Ollama timeout set to 30s (local model is slower)
- AgentBreeder's 8-step pipeline auto-rolls back on infra provisioning failure

---

## Success Criteria

- [ ] All 5 agents deploy locally and return responses
- [ ] Comparison table renders correctly
- [ ] GCP deployment succeeds for 4 agents (LangGraph uses fallback)
- [ ] AWS deployment succeeds for 4 agents
- [ ] Azure deployment succeeds for 4 agents
- [ ] Audit trail visible in AgentBreeder dashboard (`http://localhost:3001`)
