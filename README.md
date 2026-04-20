# AgentBreeder Multi-Framework Showcase

Side-by-side comparison of 5 AI agent frameworks (Claude SDK, OpenAI Agents, Google ADK, LangGraph, CrewAI) deployed via AgentBreeder to local, GCP, AWS, and Azure.

## Prerequisites

| Tool | Version | Install |
|---|---|---|
| Python | 3.11+ | `brew install python` |
| Node.js | 18+ | `brew install node` |
| Docker Desktop | latest | [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop) |
| Ollama | **latest** (required for gemma4) | `brew install ollama` then `brew upgrade ollama` |
| gcloud CLI | latest | `brew install --cask google-cloud-sdk` |
| AWS CLI | latest | `brew install awscli` |
| Azure CLI | latest | `brew install azure-cli` |

> **Important:** gemma4 requires the latest Ollama version. If `ollama pull gemma4` fails with a 412 error, run `brew upgrade ollama` first.

## Quick Start

```bash
# 1. Clone and install
git clone https://github.com/agentbreeder/agentbreeder-showcase
cd agentbreeder-showcase
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
npm install && npx playwright install chromium

# 2. Configure
cp .env.example .env
# Edit .env — add ANTHROPIC_API_KEY, OPENAI_API_KEY, GOOGLE_API_KEY

# 3. Pull local model
brew upgrade ollama
ollama pull gemma4

# 4. Start AgentBreeder platform
source venv/bin/activate
agentbreeder up

# 5. Deploy all 5 agents locally
./deploy/local.sh

# 6. Run the showcase
agentbreeder orchestration run showcase
```

## Agents

| Agent | Framework | Model |
|---|---|---|
| demo-claude-sdk | Claude SDK | claude-sonnet-4-6 |
| demo-openai-agents | OpenAI Agents SDK | gpt-4o |
| demo-google-adk | Google ADK | gemini-2.5-flash |
| demo-langgraph | LangGraph | ollama/gemma4 (local) |
| demo-crewai | CrewAI | claude-sonnet-4-6 |

## Cloud Deployment

```bash
./deploy/gcp.sh    # GCP Cloud Run
./deploy/aws.sh    # AWS ECS Fargate
./deploy/azure.sh  # Azure Container Apps
```

## Evals

```bash
source venv/bin/activate
agentbreeder up          # must be running
python evals/run_evals.py
```

Runs 3 QA prompts against all 5 agents and prints correctness + relevance scores.

## UI Demos (Playwright)

```bash
npm run demo         # run all 5 UI demos in parallel
npm run demo:report  # open HTML report with screenshots
```

Dashboard: http://localhost:3001 — log in with `admin@agentbreeder.local` / `plant`.

## Teardown

```bash
# Stop all local agent containers
agentbreeder teardown demo-claude-sdk
agentbreeder teardown demo-openai-agents
agentbreeder teardown demo-google-adk
agentbreeder teardown demo-langgraph
agentbreeder teardown demo-crewai

# GCP — delete Cloud Run services, Artifact Registry images, secrets
gcloud run services delete <name> --region $GOOGLE_CLOUD_REGION --quiet

# AWS — delete ECS services and task definitions
aws ecs delete-service --cluster $AWS_ECS_CLUSTER --service <name> --force

# Azure — delete Container Apps
az containerapp delete --name <name> --resource-group $AZURE_RESOURCE_GROUP
```
