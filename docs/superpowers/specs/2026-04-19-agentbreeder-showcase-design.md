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
```bash
pip install agentbreeder
ollama pull gemma4                          # pull local model
agentbreeder up                             # start full local platform stack
agentbreeder init                           # scaffold each agent (interactive wizard)
agentbreeder validate                       # validate all agent.yaml files before deploying
agentbreeder deploy                         # deploy each agent (cloud: local)
agentbreeder status                         # confirm all 5 agents running
agentbreeder list                           # verify registry entries
agentbreeder orchestration run showcase     # fan-out-fan-in across all 5
agentbreeder chat demo-claude-sdk           # interactive test of individual agent
agentbreeder logs demo-langgraph            # tail logs for debugging
```

### Phase 2 — GCP (Cloud Run)
```bash
gcloud auth application-default login
agentbreeder provider add gcp               # configure GCP provider
agentbreeder secret set ANTHROPIC_API_KEY   # store secrets in GCP Secret Manager
agentbreeder deploy --cloud gcp             # deploy all agents to Cloud Run
agentbreeder status                         # verify deployments
agentbreeder eval run --scorer semantic     # run evaluations on cloud agents
```

### Phase 3 — AWS (ECS Fargate)
```bash
aws configure                               # or use existing profile
agentbreeder provider add aws
agentbreeder secret set ANTHROPIC_API_KEY   # store in AWS Secrets Manager
agentbreeder deploy --cloud aws
agentbreeder status
agentbreeder eval compare                   # compare AWS vs GCP results
```

### Phase 4 — Azure (Container Apps)
```bash
az login
agentbreeder provider add azure
agentbreeder secret set ANTHROPIC_API_KEY   # store in Azure Key Vault
agentbreeder deploy --cloud azure
agentbreeder status
agentbreeder scan                           # discover any MCP servers in Azure env
```

### Teardown (any cloud)
```bash
agentbreeder teardown demo-claude-sdk       # remove individual agent + infra
agentbreeder down                           # stop local platform stack
```

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

## UI Demos (Playwright)

Each agent also has a Playwright-automated demo that walks through creation via the AgentBreeder no-code visual builder at `http://localhost:3001`. This showcases the full no-code → low-code → full-code tier progression.

### Demo Flow (per agent)

```
dashboard → New Agent → drag-and-drop builder → configure model/tools →
preview YAML → eject to SDK → save screenshots at each step
```

### Directory Structure

```
agentbreeder-showcase/
└── demos/
    ├── shared/
    │   └── helpers.ts          # reusable Playwright helpers
    ├── claude-sdk/
    │   ├── demo.spec.ts        # Playwright test
    │   └── screenshots/        # auto-captured at each step
    ├── openai-agents/
    │   ├── demo.spec.ts
    │   └── screenshots/
    ├── google-adk/
    │   ├── demo.spec.ts
    │   └── screenshots/
    ├── langgraph/
    │   ├── demo.spec.ts
    │   └── screenshots/
    └── crewai/
        ├── demo.spec.ts
        └── screenshots/
```

### Playwright Demo Steps (each `demo.spec.ts`)

1. Navigate to `http://localhost:3001`
2. Click **New Agent** → enter name + team
3. Select framework from dropdown (LangGraph / CrewAI / Claude SDK / etc.)
4. Set model via provider selector
5. Screenshot: **"builder-config.png"**
6. Click **Preview YAML** tab → screenshot: **"yaml-preview.png"**
7. Click **Deploy** → wait for status `running` → screenshot: **"deployed.png"**
8. Click **Eject → SDK** (`agentbreeder eject --to sdk`) → screenshot: **"ejected-sdk.png"**
9. Open **Chat** panel → send demo prompt → screenshot: **"chat-response.png"**

### Running All UI Demos

```bash
agentbreeder up                             # ensure dashboard is running
npx playwright install chromium
npx playwright test demos/                  # run all 5 demo specs in parallel
npx playwright show-report                  # view HTML report with screenshots
```

### Output

Each agent produces 5 screenshots + a Playwright HTML report showing the full no-code → deploy → eject journey.

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
- [ ] All 5 Playwright UI demos run and produce screenshots
- [ ] YAML preview and SDK eject demonstrated for each agent
- [ ] Playwright HTML report generated at `playwright-report/index.html`
