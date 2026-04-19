# AgentBreeder Multi-Framework Showcase Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a side-by-side comparison demo that fires 5 AI agents (one per framework) in parallel via AgentBreeder fan-out-fan-in orchestration, then deploys them to local, GCP, AWS, and Azure — each with a Playwright UI demo.

**Architecture:** 5 independent `agent.yaml` + `agent.py` files (one per framework), unified by `orchestration.yaml` using fan-out-fan-in strategy. Deploy scripts parameterize the `--cloud` flag. Playwright specs automate the no-code UI builder at `http://localhost:3001`.

**Tech Stack:** Python 3.11+, agentbreeder CLI, anthropic SDK, openai-agents SDK, google-adk, langgraph + langchain-ollama, crewai, Playwright (TypeScript), Docker, Ollama

---

## File Map

| File | Responsibility |
|------|---------------|
| `requirements.txt` | All Python deps |
| `package.json` | Playwright + TypeScript deps |
| `playwright.config.ts` | Playwright project config |
| `.env.example` | All required env vars documented |
| `agents/claude-sdk/agent.yaml` | Claude SDK agent config |
| `agents/claude-sdk/agent.py` | Claude SDK agent logic |
| `agents/openai-agents/agent.yaml` | OpenAI Agents SDK config |
| `agents/openai-agents/agent.py` | OpenAI Agents SDK logic |
| `agents/google-adk/agent.yaml` | Google ADK config |
| `agents/google-adk/agent.py` | Google ADK logic |
| `agents/langgraph/agent.yaml` | LangGraph config |
| `agents/langgraph/agent.py` | LangGraph + Ollama logic |
| `agents/crewai/agent.yaml` | CrewAI config |
| `agents/crewai/agent.py` | CrewAI logic |
| `orchestration.yaml` | Fan-out-fan-in orchestration |
| `deploy/local.sh` | Deploy all 5 agents locally |
| `deploy/gcp.sh` | Deploy all 5 to GCP Cloud Run |
| `deploy/aws.sh` | Deploy all 5 to AWS ECS Fargate |
| `deploy/azure.sh` | Deploy all 5 to Azure Container Apps |
| `demos/shared/helpers.ts` | Playwright screenshot + wait helpers |
| `demos/claude-sdk/demo.spec.ts` | Playwright UI demo: Claude SDK |
| `demos/openai-agents/demo.spec.ts` | Playwright UI demo: OpenAI Agents |
| `demos/google-adk/demo.spec.ts` | Playwright UI demo: Google ADK |
| `demos/langgraph/demo.spec.ts` | Playwright UI demo: LangGraph |
| `demos/crewai/demo.spec.ts` | Playwright UI demo: CrewAI |

---

## Task 1: Project Scaffolding

**Files:**
- Create: `requirements.txt`
- Create: `package.json`
- Create: `playwright.config.ts`
- Create: `.env.example`
- Create: `.gitignore`

- [ ] **Step 1: Create requirements.txt**

```
agentbreeder>=1.0.0
anthropic>=0.40.0
openai-agents>=0.1.0
google-adk>=1.0.0
langgraph>=0.2.0
langchain-ollama>=0.2.0
crewai>=0.80.0
python-dotenv>=1.0.0
rich>=13.0.0
```

- [ ] **Step 2: Create package.json**

```json
{
  "name": "agentbreeder-showcase",
  "version": "1.0.0",
  "scripts": {
    "demo": "npx playwright test demos/",
    "demo:report": "npx playwright show-report"
  },
  "devDependencies": {
    "@playwright/test": "^1.44.0",
    "typescript": "^5.4.0"
  }
}
```

- [ ] **Step 3: Create playwright.config.ts**

```typescript
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './demos',
  timeout: 120_000,
  retries: 1,
  workers: 5,
  use: {
    baseURL: 'http://localhost:3001',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  reporter: [['html', { outputFolder: 'playwright-report' }]],
});
```

- [ ] **Step 4: Create .env.example**

```bash
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
GOOGLE_API_KEY=
OLLAMA_BASE_URL=http://localhost:11434

# GCP
GOOGLE_CLOUD_PROJECT=
GOOGLE_CLOUD_REGION=us-central1

# AWS
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=

# Azure
AZURE_SUBSCRIPTION_ID=
AZURE_RESOURCE_GROUP=agentbreeder-showcase
AZURE_LOCATION=eastus
```

- [ ] **Step 5: Create .gitignore**

```
.env
__pycache__/
*.pyc
node_modules/
playwright-report/
demos/**/screenshots/*.png
.agentbreeder/
```

- [ ] **Step 6: Copy .env.example to .env and fill in your API keys**

```bash
cp .env.example .env
# Edit .env and add: ANTHROPIC_API_KEY, OPENAI_API_KEY, GOOGLE_API_KEY
```

- [ ] **Step 7: Install dependencies**

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
npm install
npx playwright install chromium
```

- [ ] **Step 8: Commit**

```bash
git add requirements.txt package.json playwright.config.ts .env.example .gitignore
git commit -m "feat: project scaffolding — deps, playwright config, env template"
```

---

## Task 2: AgentBreeder Platform Setup

**Files:** none (CLI operations only)

- [ ] **Step 1: Install AgentBreeder CLI**

```bash
pip install agentbreeder
agentbreeder --version
```
Expected output: `agentbreeder x.x.x`

- [ ] **Step 2: Start the local platform stack**

```bash
agentbreeder up
```
Expected: Dashboard available at `http://localhost:3001`, API at `http://localhost:8000`

- [ ] **Step 3: Verify dashboard is running**

```bash
curl -s http://localhost:8000/health | python -m json.tool
```
Expected: `{"status": "ok"}`

- [ ] **Step 4: Install and start Ollama, pull Gemma 4**

```bash
# macOS
brew install ollama
ollama serve &
ollama pull gemma4
```
Expected: `gemma4` appears in `ollama list`

- [ ] **Step 5: Verify Ollama**

```bash
curl http://localhost:11434/api/tags | python -m json.tool
```
Expected: JSON containing `"gemma4"` in models list

---

## Task 3: Claude SDK Agent

**Files:**
- Create: `agents/claude-sdk/agent.yaml`
- Create: `agents/claude-sdk/agent.py`

- [ ] **Step 1: Create agent.yaml**

```yaml
name: demo-claude-sdk
version: 1.0.0
team: showcase
owner: saha.rajit@gmail.com

framework: claude_sdk
model:
  primary: claude-sonnet-4-6
  fallback: claude-sonnet-4-6

deploy:
  cloud: local
  scaling:
    min: 1
    max: 3
```

- [ ] **Step 2: Create agent.py**

```python
import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

PROMPT = "What are the top 3 benefits of AI agents in enterprise?"


def run(prompt: str = PROMPT) -> str:
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


if __name__ == "__main__":
    print(run())
```

- [ ] **Step 3: Validate the agent.yaml**

```bash
cd agents/claude-sdk && agentbreeder validate
```
Expected: `✓ agent.yaml is valid`

- [ ] **Step 4: Smoke-test the agent locally**

```bash
python agents/claude-sdk/agent.py
```
Expected: A response listing 3 enterprise benefits (non-empty text)

- [ ] **Step 5: Commit**

```bash
git add agents/claude-sdk/
git commit -m "feat: claude-sdk agent — claude-sonnet-4-6"
```

---

## Task 4: OpenAI Agents SDK Agent

**Files:**
- Create: `agents/openai-agents/agent.yaml`
- Create: `agents/openai-agents/agent.py`

- [ ] **Step 1: Create agent.yaml**

```yaml
name: demo-openai-agents
version: 1.0.0
team: showcase
owner: saha.rajit@gmail.com

framework: openai_agents
model:
  primary: gpt-5.2
  fallback: gpt-4o

deploy:
  cloud: local
  scaling:
    min: 1
    max: 3
```

- [ ] **Step 2: Create agent.py**

```python
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
```

- [ ] **Step 3: Validate**

```bash
cd agents/openai-agents && agentbreeder validate
```
Expected: `✓ agent.yaml is valid`

- [ ] **Step 4: Smoke-test**

```bash
OPENAI_API_KEY=$(grep OPENAI_API_KEY .env | cut -d= -f2) python agents/openai-agents/agent.py
```
Expected: A response listing 3 enterprise benefits

- [ ] **Step 5: Commit**

```bash
git add agents/openai-agents/
git commit -m "feat: openai-agents agent — gpt-5.2"
```

---

## Task 5: Google ADK Agent

**Files:**
- Create: `agents/google-adk/agent.yaml`
- Create: `agents/google-adk/agent.py`

- [ ] **Step 1: Create agent.yaml**

```yaml
name: demo-google-adk
version: 1.0.0
team: showcase
owner: saha.rajit@gmail.com

framework: google_adk
model:
  primary: gemini-3.0-flash
  fallback: gemini-2.0-flash

deploy:
  cloud: local
  scaling:
    min: 1
    max: 3
```

- [ ] **Step 2: Create agent.py**

```python
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
    response = agent.run(prompt)
    return response.text


if __name__ == "__main__":
    print(run())
```

- [ ] **Step 3: Validate**

```bash
cd agents/google-adk && agentbreeder validate
```
Expected: `✓ agent.yaml is valid`

- [ ] **Step 4: Smoke-test**

```bash
GOOGLE_API_KEY=$(grep GOOGLE_API_KEY .env | cut -d= -f2) python agents/google-adk/agent.py
```
Expected: A response listing 3 enterprise benefits

- [ ] **Step 5: Commit**

```bash
git add agents/google-adk/
git commit -m "feat: google-adk agent — gemini-3.0-flash"
```

---

## Task 6: LangGraph + Ollama Agent

**Files:**
- Create: `agents/langgraph/agent.yaml`
- Create: `agents/langgraph/agent.py`

- [ ] **Step 1: Create agent.yaml**

```yaml
name: demo-langgraph
version: 1.0.0
team: showcase
owner: saha.rajit@gmail.com

framework: langgraph
model:
  primary: ollama/gemma4
  fallback: claude-sonnet-4-6

deploy:
  cloud: local
  scaling:
    min: 1
    max: 1
```

- [ ] **Step 2: Create agent.py**

```python
import os
from typing import TypedDict
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv

load_dotenv()

PROMPT = "What are the top 3 benefits of AI agents in enterprise?"

llm = ChatOllama(
    model="gemma4",
    base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
)


class State(TypedDict):
    prompt: str
    response: str


def answer(state: State) -> State:
    response = llm.invoke(state["prompt"])
    return {"response": response.content}


graph = StateGraph(State)
graph.add_node("answer", answer)
graph.set_entry_point("answer")
graph.add_edge("answer", END)
app = graph.compile()


def run(prompt: str = PROMPT) -> str:
    result = app.invoke({"prompt": prompt, "response": ""})
    return result["response"]


if __name__ == "__main__":
    print(run())
```

- [ ] **Step 3: Validate**

```bash
cd agents/langgraph && agentbreeder validate
```
Expected: `✓ agent.yaml is valid`

- [ ] **Step 4: Smoke-test (requires Ollama running with gemma4)**

```bash
python agents/langgraph/agent.py
```
Expected: A response listing 3 enterprise benefits (may take 10-30s for local model)

- [ ] **Step 5: Commit**

```bash
git add agents/langgraph/
git commit -m "feat: langgraph agent — ollama/gemma4"
```

---

## Task 7: CrewAI Agent

**Files:**
- Create: `agents/crewai/agent.yaml`
- Create: `agents/crewai/agent.py`

- [ ] **Step 1: Create agent.yaml**

```yaml
name: demo-crewai
version: 1.0.0
team: showcase
owner: saha.rajit@gmail.com

framework: crewai
model:
  primary: claude-sonnet-4-6
  fallback: claude-sonnet-4-6

deploy:
  cloud: local
  scaling:
    min: 1
    max: 3
```

- [ ] **Step 2: Create agent.py**

```python
import os
from crewai import Agent, Task, Crew, LLM
from dotenv import load_dotenv

load_dotenv()

PROMPT = "What are the top 3 benefits of AI agents in enterprise?"

llm = LLM(
    model="claude-sonnet-4-6",
    api_key=os.environ["ANTHROPIC_API_KEY"],
)

analyst = Agent(
    role="Enterprise AI Analyst",
    goal="Provide clear, numbered analysis of enterprise AI benefits",
    backstory="You are a senior enterprise technology analyst with 10 years of AI experience.",
    llm=llm,
    verbose=False,
)


def run(prompt: str = PROMPT) -> str:
    task = Task(
        description=prompt,
        expected_output="A numbered list of exactly 3 enterprise benefits with brief explanations",
        agent=analyst,
    )
    crew = Crew(agents=[analyst], tasks=[task], verbose=False)
    result = crew.kickoff()
    return str(result)


if __name__ == "__main__":
    print(run())
```

- [ ] **Step 3: Validate**

```bash
cd agents/crewai && agentbreeder validate
```
Expected: `✓ agent.yaml is valid`

- [ ] **Step 4: Smoke-test**

```bash
python agents/crewai/agent.py
```
Expected: A numbered list of 3 enterprise benefits

- [ ] **Step 5: Commit**

```bash
git add agents/crewai/
git commit -m "feat: crewai agent — claude-sonnet-4-6 via crewai framework"
```

---

## Task 8: Orchestration Config

**Files:**
- Create: `orchestration.yaml`

- [ ] **Step 1: Create orchestration.yaml**

```yaml
name: showcase
version: 1.0.0
team: showcase
strategy: fan-out-fan-in

agents:
  - demo-claude-sdk
  - demo-openai-agents
  - demo-google-adk
  - demo-langgraph
  - demo-crewai

input:
  prompt: "What are the top 3 benefits of AI agents in enterprise?"

output:
  format: table
  columns:
    - framework
    - model
    - latency_ms
    - response_preview
  truncate_response: 120

timeout_seconds: 60
on_agent_failure: continue
```

- [ ] **Step 2: Validate orchestration config**

```bash
agentbreeder orchestration validate showcase
```
Expected: `✓ orchestration.yaml is valid`

- [ ] **Step 3: Commit**

```bash
git add orchestration.yaml
git commit -m "feat: fan-out-fan-in orchestration config for 5-agent showcase"
```

---

## Task 9: Local Deploy Script

**Files:**
- Create: `deploy/local.sh`

- [ ] **Step 1: Create deploy/local.sh**

```bash
#!/usr/bin/env bash
set -euo pipefail

echo "=== AgentBreeder Showcase — Local Deploy ==="

# Load env
set -a && source .env && set +a

# Validate all agents first
echo "→ Validating all agent configs..."
for agent_dir in agents/*/; do
  (cd "$agent_dir" && agentbreeder validate && echo "  ✓ $(basename $agent_dir)")
done

# Deploy each agent
echo "→ Deploying agents..."
for agent_dir in agents/*/; do
  agent_name=$(grep '^name:' "$agent_dir/agent.yaml" | awk '{print $2}')
  (cd "$agent_dir" && agentbreeder deploy --cloud local)
  echo "  ✓ $agent_name deployed"
done

# Verify all running
echo "→ Verifying status..."
agentbreeder status

# List registry
echo "→ Registry:"
agentbreeder list

echo ""
echo "=== All agents deployed locally ==="
echo "Run the showcase: agentbreeder orchestration run showcase"
echo "Dashboard: http://localhost:3001"
```

- [ ] **Step 2: Make executable**

```bash
chmod +x deploy/local.sh
```

- [ ] **Step 3: Run local deployment**

```bash
./deploy/local.sh
```
Expected: All 5 agents show `running` status

- [ ] **Step 4: Run the showcase orchestration**

```bash
agentbreeder orchestration run showcase
```
Expected: Formatted table with 5 rows, one per framework, showing model, latency, and response preview

- [ ] **Step 5: Commit**

```bash
git add deploy/local.sh
git commit -m "feat: local deploy script — validates, deploys, and runs all 5 agents"
```

---

## Task 10: Cloud Deploy Scripts (GCP, AWS, Azure)

**Files:**
- Create: `deploy/gcp.sh`
- Create: `deploy/aws.sh`
- Create: `deploy/azure.sh`

- [ ] **Step 1: Create deploy/gcp.sh**

```bash
#!/usr/bin/env bash
set -euo pipefail

echo "=== AgentBreeder Showcase — GCP Deploy ==="
set -a && source .env && set +a

# Authenticate
gcloud auth application-default login

# Configure provider
agentbreeder provider add gcp \
  --project "$GOOGLE_CLOUD_PROJECT" \
  --region "$GOOGLE_CLOUD_REGION"

# Store secrets in GCP Secret Manager
agentbreeder secret set ANTHROPIC_API_KEY --backend gcp
agentbreeder secret set OPENAI_API_KEY --backend gcp
agentbreeder secret set GOOGLE_API_KEY --backend gcp

# Deploy all agents (langgraph uses fallback model on cloud)
for agent_dir in agents/*/; do
  agent_name=$(grep '^name:' "$agent_dir/agent.yaml" | awk '{print $2}')
  (cd "$agent_dir" && agentbreeder deploy --cloud gcp)
  echo "  ✓ $agent_name → GCP Cloud Run"
done

agentbreeder status
echo ""
echo "=== GCP deployment complete ==="
echo "Run evals: agentbreeder eval run --scorer semantic"
```

- [ ] **Step 2: Create deploy/aws.sh**

```bash
#!/usr/bin/env bash
set -euo pipefail

echo "=== AgentBreeder Showcase — AWS Deploy ==="
set -a && source .env && set +a

# Configure provider
agentbreeder provider add aws \
  --region "$AWS_REGION" \
  --account-id "$AWS_ACCOUNT_ID"

# Store secrets in AWS Secrets Manager
agentbreeder secret set ANTHROPIC_API_KEY --backend aws
agentbreeder secret set OPENAI_API_KEY --backend aws
agentbreeder secret set GOOGLE_API_KEY --backend aws

# Deploy all agents to ECS Fargate
for agent_dir in agents/*/; do
  agent_name=$(grep '^name:' "$agent_dir/agent.yaml" | awk '{print $2}')
  (cd "$agent_dir" && agentbreeder deploy --cloud aws)
  echo "  ✓ $agent_name → AWS ECS Fargate"
done

agentbreeder status
echo ""
echo "=== AWS deployment complete ==="
echo "Compare with GCP: agentbreeder eval compare"
```

- [ ] **Step 3: Create deploy/azure.sh**

```bash
#!/usr/bin/env bash
set -euo pipefail

echo "=== AgentBreeder Showcase — Azure Deploy ==="
set -a && source .env && set +a

# Authenticate
az login

# Configure provider
agentbreeder provider add azure \
  --subscription "$AZURE_SUBSCRIPTION_ID" \
  --resource-group "$AZURE_RESOURCE_GROUP" \
  --location "$AZURE_LOCATION"

# Store secrets in Azure Key Vault
agentbreeder secret set ANTHROPIC_API_KEY --backend azure
agentbreeder secret set OPENAI_API_KEY --backend azure
agentbreeder secret set GOOGLE_API_KEY --backend azure

# Deploy all agents to Azure Container Apps
for agent_dir in agents/*/; do
  agent_name=$(grep '^name:' "$agent_dir/agent.yaml" | awk '{print $2}')
  (cd "$agent_dir" && agentbreeder deploy --cloud azure)
  echo "  ✓ $agent_name → Azure Container Apps"
done

agentbreeder status
agentbreeder scan
echo ""
echo "=== Azure deployment complete ==="
```

- [ ] **Step 4: Make all executable**

```bash
chmod +x deploy/gcp.sh deploy/aws.sh deploy/azure.sh
```

- [ ] **Step 5: Commit**

```bash
git add deploy/gcp.sh deploy/aws.sh deploy/azure.sh
git commit -m "feat: cloud deploy scripts for GCP, AWS, and Azure"
```

---

## Task 11: Playwright Shared Helpers

**Files:**
- Create: `demos/shared/helpers.ts`
- Create screenshot dirs for all 5 agents

- [ ] **Step 1: Create screenshot directories with .gitkeep**

```bash
for f in claude-sdk openai-agents google-adk langgraph crewai; do
  mkdir -p "demos/$f/screenshots"
  touch "demos/$f/screenshots/.gitkeep"
done
```

- [ ] **Step 2: Create demos/shared/helpers.ts**

```typescript
import { Page } from '@playwright/test';
import path from 'path';

export async function waitForDashboard(page: Page): Promise<void> {
  await page.waitForSelector('text=AgentBreeder', { timeout: 15_000 });
}

export async function takeScreenshot(page: Page, filepath: string): Promise<void> {
  await page.screenshot({ path: filepath, fullPage: false });
}

export async function createAgentViaUI(
  page: Page,
  opts: {
    name: string;
    team: string;
    framework: string;
    model: string;
    screenshotDir: string;
  }
): Promise<void> {
  const { name, team, framework, model, screenshotDir } = opts;

  // Navigate to dashboard
  await page.goto('http://localhost:3001');
  await waitForDashboard(page);

  // Open new agent form
  await page.click('button:has-text("New Agent"), a:has-text("New Agent")');
  await page.waitForSelector('[name="agent-name"], [placeholder*="agent name"]', { timeout: 10_000 });

  // Fill identity fields
  const nameField = page.locator('[name="agent-name"], [placeholder*="agent name"]').first();
  await nameField.fill(name);

  const teamField = page.locator('[name="team"], [placeholder*="team"]').first();
  await teamField.fill(team);

  // Select framework
  const frameworkSelect = page.locator('select[name="framework"], [data-testid="framework-select"]').first();
  await frameworkSelect.selectOption(framework);

  // Select model
  const modelField = page.locator('[name="model"], [placeholder*="model"], [data-testid="model-input"]').first();
  await modelField.fill(model);

  await takeScreenshot(page, path.join(screenshotDir, 'builder-config.png'));

  // Preview YAML
  await page.click('button:has-text("Preview YAML"), [data-testid="preview-yaml"]');
  await page.waitForSelector('pre, code', { timeout: 5_000 });
  await takeScreenshot(page, path.join(screenshotDir, 'yaml-preview.png'));

  // Deploy
  await page.click('button:has-text("Deploy"), [data-testid="deploy-btn"]');
  await page.waitForSelector('text=running, text=deployed, [data-status="running"]', { timeout: 90_000 });
  await takeScreenshot(page, path.join(screenshotDir, 'deployed.png'));

  // Eject to SDK
  await page.click('button:has-text("Eject"), [data-testid="eject-btn"]');
  await page.click('button:has-text("SDK"), [data-testid="eject-sdk"]');
  await page.waitForSelector('pre, code', { timeout: 10_000 });
  await takeScreenshot(page, path.join(screenshotDir, 'ejected-sdk.png'));

  // Chat panel
  await page.click('button:has-text("Chat"), [data-testid="chat-btn"]');
  const chatInput = page.locator('[name="message"], [placeholder*="message"], textarea').first();
  await chatInput.fill('What are the top 3 benefits of AI agents in enterprise?');
  await page.keyboard.press('Enter');
  await page.waitForSelector('.agent-response, [data-testid="agent-response"], .message-content', { timeout: 60_000 });
  await takeScreenshot(page, path.join(screenshotDir, 'chat-response.png'));
}
```

- [ ] **Step 3: Commit**

```bash
git add demos/shared/ demos/*/screenshots/.gitkeep
git commit -m "feat: playwright shared helpers for UI demo automation"
```

---

## Task 12: Playwright Demo — Claude SDK

**Files:**
- Create: `demos/claude-sdk/demo.spec.ts`

- [ ] **Step 1: Create demo.spec.ts**

```typescript
import { test, expect } from '@playwright/test';
import { createAgentViaUI } from '../shared/helpers';
import path from 'path';

const SCREENSHOTS = path.join(__dirname, 'screenshots');

test('Claude SDK — create agent via UI, deploy, chat', async ({ page }) => {
  await createAgentViaUI(page, {
    name: 'demo-claude-sdk',
    team: 'showcase',
    framework: 'claude_sdk',
    model: 'claude-sonnet-4-6',
    screenshotDir: SCREENSHOTS,
  });

  // Verify all 5 screenshots were created
  const { existsSync } = await import('fs');
  for (const shot of ['builder-config', 'yaml-preview', 'deployed', 'ejected-sdk', 'chat-response']) {
    expect(existsSync(path.join(SCREENSHOTS, `${shot}.png`))).toBe(true);
  }
});
```

- [ ] **Step 2: Run just this spec (dashboard must be running)**

```bash
npx playwright test demos/claude-sdk/demo.spec.ts --headed
```
Expected: Test passes, 5 screenshots created in `demos/claude-sdk/screenshots/`

- [ ] **Step 3: Commit**

```bash
git add demos/claude-sdk/
git commit -m "feat: playwright UI demo for claude-sdk agent"
```

---

## Task 13: Playwright Demos — Remaining 4 Agents

**Files:**
- Create: `demos/openai-agents/demo.spec.ts`
- Create: `demos/google-adk/demo.spec.ts`
- Create: `demos/langgraph/demo.spec.ts`
- Create: `demos/crewai/demo.spec.ts`

- [ ] **Step 1: Create demos/openai-agents/demo.spec.ts**

```typescript
import { test, expect } from '@playwright/test';
import { createAgentViaUI } from '../shared/helpers';
import path from 'path';

const SCREENSHOTS = path.join(__dirname, 'screenshots');

test('OpenAI Agents SDK — create agent via UI, deploy, chat', async ({ page }) => {
  await createAgentViaUI(page, {
    name: 'demo-openai-agents',
    team: 'showcase',
    framework: 'openai_agents',
    model: 'gpt-5.2',
    screenshotDir: SCREENSHOTS,
  });

  const { existsSync } = await import('fs');
  for (const shot of ['builder-config', 'yaml-preview', 'deployed', 'ejected-sdk', 'chat-response']) {
    expect(existsSync(path.join(SCREENSHOTS, `${shot}.png`))).toBe(true);
  }
});
```

- [ ] **Step 2: Create demos/google-adk/demo.spec.ts**

```typescript
import { test, expect } from '@playwright/test';
import { createAgentViaUI } from '../shared/helpers';
import path from 'path';

const SCREENSHOTS = path.join(__dirname, 'screenshots');

test('Google ADK — create agent via UI, deploy, chat', async ({ page }) => {
  await createAgentViaUI(page, {
    name: 'demo-google-adk',
    team: 'showcase',
    framework: 'google_adk',
    model: 'gemini-3.0-flash',
    screenshotDir: SCREENSHOTS,
  });

  const { existsSync } = await import('fs');
  for (const shot of ['builder-config', 'yaml-preview', 'deployed', 'ejected-sdk', 'chat-response']) {
    expect(existsSync(path.join(SCREENSHOTS, `${shot}.png`))).toBe(true);
  }
});
```

- [ ] **Step 3: Create demos/langgraph/demo.spec.ts**

```typescript
import { test, expect } from '@playwright/test';
import { createAgentViaUI } from '../shared/helpers';
import path from 'path';

const SCREENSHOTS = path.join(__dirname, 'screenshots');

test('LangGraph + Ollama — create agent via UI, deploy, chat', async ({ page }) => {
  await createAgentViaUI(page, {
    name: 'demo-langgraph',
    team: 'showcase',
    framework: 'langgraph',
    model: 'ollama/gemma4',
    screenshotDir: SCREENSHOTS,
  });

  const { existsSync } = await import('fs');
  for (const shot of ['builder-config', 'yaml-preview', 'deployed', 'ejected-sdk', 'chat-response']) {
    expect(existsSync(path.join(SCREENSHOTS, `${shot}.png`))).toBe(true);
  }
});
```

- [ ] **Step 4: Create demos/crewai/demo.spec.ts**

```typescript
import { test, expect } from '@playwright/test';
import { createAgentViaUI } from '../shared/helpers';
import path from 'path';

const SCREENSHOTS = path.join(__dirname, 'screenshots');

test('CrewAI — create agent via UI, deploy, chat', async ({ page }) => {
  await createAgentViaUI(page, {
    name: 'demo-crewai',
    team: 'showcase',
    framework: 'crewai',
    model: 'claude-sonnet-4-6',
    screenshotDir: SCREENSHOTS,
  });

  const { existsSync } = await import('fs');
  for (const shot of ['builder-config', 'yaml-preview', 'deployed', 'ejected-sdk', 'chat-response']) {
    expect(existsSync(path.join(SCREENSHOTS, `${shot}.png`))).toBe(true);
  }
});
```

- [ ] **Step 5: Run all UI demos in parallel**

```bash
npx playwright test demos/ --headed
```
Expected: 5 tests pass, screenshots in each `demos/<framework>/screenshots/`

- [ ] **Step 6: View HTML report**

```bash
npx playwright show-report
```
Expected: Browser opens `playwright-report/index.html` showing all 5 passing tests with screenshots

- [ ] **Step 7: Commit**

```bash
git add demos/
git commit -m "feat: playwright UI demos for all 5 frameworks — openai, google-adk, langgraph, crewai"
```

---

## Task 14: End-to-End Validation

**Files:** none (validation steps only)

- [ ] **Step 1: Validate all 5 agent.yaml files**

```bash
for d in agents/*/; do echo "--- $(basename $d) ---" && (cd $d && agentbreeder validate); done
```
Expected: 5x `✓ agent.yaml is valid`

- [ ] **Step 2: Deploy all locally**

```bash
./deploy/local.sh
```
Expected: 5 agents `running`, table visible at end

- [ ] **Step 3: Run orchestration**

```bash
agentbreeder orchestration run showcase
```
Expected: Table with 5 rows, all with non-null latency and responses

- [ ] **Step 4: Check audit trail in dashboard**

Open `http://localhost:3001` → navigate to Audit Log
Expected: 5 deployment events, 1 orchestration run event

- [ ] **Step 5: Run evaluations**

```bash
agentbreeder eval run --scorer semantic --judge-model claude-sonnet-4-6
```
Expected: Semantic scores for all 5 agents, no failures

- [ ] **Step 6: Run all Playwright demos**

```bash
npm run demo
npm run demo:report
```
Expected: 5/5 passing, HTML report with screenshots

- [ ] **Step 7: Final commit**

```bash
git add -A
git commit -m "feat: complete agentbreeder showcase — 5 frameworks, local validated"
```

---

## Task 15: GCP Deployment

**Prerequisites:** `gcloud` CLI installed, `GOOGLE_CLOUD_PROJECT` set in `.env`

- [ ] **Step 1: Deploy to GCP**

```bash
./deploy/gcp.sh
```
Expected: 5 agents deployed to Cloud Run (langgraph uses claude-sonnet-4-6 fallback)

- [ ] **Step 2: Verify GCP deployment**

```bash
agentbreeder status --cloud gcp
```
Expected: 5 agents `running` on Cloud Run endpoints

- [ ] **Step 3: Run orchestration on GCP agents**

```bash
agentbreeder orchestration run showcase --cloud gcp
```
Expected: Same 5-row table, but with GCP endpoint URLs

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "feat: GCP Cloud Run deployment validated"
```

---

## Task 16: AWS Deployment

**Prerequisites:** `aws` CLI installed, `AWS_REGION` + `AWS_ACCOUNT_ID` set in `.env`

- [ ] **Step 1: Deploy to AWS**

```bash
./deploy/aws.sh
```
Expected: 5 agents deployed to ECS Fargate

- [ ] **Step 2: Verify AWS deployment**

```bash
agentbreeder status --cloud aws
```
Expected: 5 agents `running` on ECS Fargate

- [ ] **Step 3: Compare GCP vs AWS results**

```bash
agentbreeder eval compare --run-a gcp-showcase --run-b aws-showcase
```
Expected: Side-by-side comparison with regression detection output

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "feat: AWS ECS Fargate deployment validated"
```

---

## Task 17: Azure Deployment

**Prerequisites:** `az` CLI installed, `AZURE_SUBSCRIPTION_ID` + `AZURE_RESOURCE_GROUP` set in `.env`

- [ ] **Step 1: Deploy to Azure**

```bash
./deploy/azure.sh
```
Expected: 5 agents deployed to Azure Container Apps

- [ ] **Step 2: Verify Azure deployment**

```bash
agentbreeder status --cloud azure
```
Expected: 5 agents `running` on Azure Container Apps

- [ ] **Step 3: Scan for MCP servers**

```bash
agentbreeder scan
```
Expected: Discovery output (empty or listing any Azure-hosted MCP servers)

- [ ] **Step 4: Final teardown test (verify cleanup works)**

```bash
agentbreeder teardown demo-claude-sdk --cloud azure
agentbreeder status --cloud azure
```
Expected: `demo-claude-sdk` no longer listed, other 4 still running

- [ ] **Step 5: Final commit**

```bash
git add -A
git commit -m "feat: Azure Container Apps deployment validated — full multi-cloud showcase complete"
```
