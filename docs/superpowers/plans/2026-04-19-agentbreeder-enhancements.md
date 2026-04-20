# AgentBreeder Showcase Enhancements Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enhance all 5 AgentBreeder showcase agents with tracing (all), A2A (crewai orchestrating langgraph + claude-sdk), memory/RAG registry declarations, and offline evals — using AgentBreeder's built-in features exclusively.

**Architecture:** Jaeger sidecar on `agentbreeder-net` receives OTLP traces from all 5 agents. CrewAI uses AgentBreeder's `subagents:` block + deployer injection of `AGENT_TOOLS_JSON` and `TOOL_ENDPOINT_*` to call langgraph and claude-sdk as sub-agents over HTTP. Memory and RAG are declared as AgentBreeder registry artifacts (memory.yaml, rag.yaml) and referenced from agent.yaml; runtime injection is a platform stub (issues filed). Evals run via the AgentBreeder eval service Python API in a single-process script.

**Tech Stack:** Docker Compose (Jaeger), AgentBreeder CLI + engine SDK, OpenTelemetry SDK (in agent containers), AgentBreeder eval service, Python YAML.

**What is NOT implemented (GitHub issues filed at end):**
- Memory runtime injection (no `memory:` field in agent.yaml schema)
- RAG runtime injection (knowledge_bases is a v0.1 stub in resolver)  
- A2A for claude_sdk / openai_agents templates (no tool-use loop)
- Eval CLI cross-process dataset persistence
- Neo4j Graph RAG backend

---

## File Map

**Create:**
- `infra/docker-compose.yml` — Jaeger on agentbreeder-net
- `memory/session-buffer.yaml` — Redis short-term memory declaration
- `memory/entity-store.yaml` — PostgreSQL entity memory declaration
- `memory/semantic-store.yaml` — PostgreSQL semantic memory declaration
- `rag/enterprise-docs.yaml` — pgvector RAG for crewai
- `rag/ai-use-cases.yaml` — pgvector RAG for google-adk
- `rag/technical-docs.yaml` — pgvector RAG for langgraph
- `rag/docs/enterprise/01-roi.md` — seed doc
- `rag/docs/enterprise/02-automation.md` — seed doc
- `rag/docs/ai-use-cases/01-industries.md` — seed doc
- `rag/docs/technical/01-patterns.md` — seed doc
- `evals/run_evals.py` — single-process eval runner using AgentBreeder eval service

**Modify (platform code only — no agent.py changes):**
- `venv/.../engine/deployers/docker_compose.py` — (a) all containers on agentbreeder-net, (b) inject AGENT_TOOLS_JSON, (c) inject TOOL_ENDPOINT_* for subagents
- `venv/.../engine/tool_bridge.py` — normalize dict inputs in `_resolve_endpoint`, `to_crewai_tools`, `to_claude_tools`
- `venv/.../engine/runtimes/templates/claude_sdk_server.py` — add `init_tracing()`
- `venv/.../engine/runtimes/templates/crewai_server.py` — add `init_tracing()`
- `venv/.../engine/runtimes/templates/openai_agents_server.py` — add `init_tracing()`
- `venv/.../engine/runtimes/templates/google_adk_server.py` — add `init_tracing()`
- `agents/*/agent.yaml` (all 5) — add OPENTELEMETRY_ENDPOINT to deploy.env_vars
- `agents/crewai/agent.yaml` — add `subagents:` block (Chain 2 orchestrator)
- `agents/claude-sdk/agent.yaml` — add `subagents:` block (Chain 1 orchestrator, for future use)
- `agents/openai-agents/agent.yaml` — add `subagents:` block (Chain 3 orchestrator, for future use)
- `agents/crewai/agent.yaml` — add `knowledge_bases:` ref
- `agents/google-adk/agent.yaml` — add `knowledge_bases:` ref
- `agents/langgraph/agent.yaml` — add `knowledge_bases:` ref
- `agents/*/requirements.txt` (all 5) — add opentelemetry packages

---

## Task 1: Infrastructure — Jaeger Sidecar

**Files:**
- Create: `infra/docker-compose.yml`

- [ ] **Step 1: Create the file**

```yaml
# infra/docker-compose.yml
services:
  jaeger:
    image: jaegertracing/all-in-one:latest
    container_name: agentbreeder-jaeger
    networks:
      - agentbreeder-net
    ports:
      - "16686:16686"   # Jaeger UI
      - "4317:4317"     # OTLP gRPC
      - "4318:4318"     # OTLP HTTP
    environment:
      COLLECTOR_OTLP_ENABLED: "true"

networks:
  agentbreeder-net:
    name: agentbreeder-net
    driver: bridge
```

- [ ] **Step 2: Start Jaeger**

Run: `DOCKER_HOST="unix:///Users/rajit/.docker/run/docker.sock" docker compose -f infra/docker-compose.yml up -d`

Expected: `Container agentbreeder-jaeger  Started`

- [ ] **Step 3: Verify Jaeger UI is reachable**

Run: `curl -s http://localhost:16686/ | head -5`

Expected: HTML response with `<title>Jaeger UI</title>`

- [ ] **Step 4: Commit**

```bash
git add infra/docker-compose.yml
git commit -m "infra: add Jaeger sidecar for OTLP tracing"
```

---

## Task 2: Memory Registry Declarations

**Files:**
- Create: `memory/session-buffer.yaml`, `memory/entity-store.yaml`, `memory/semantic-store.yaml`

- [ ] **Step 1: Create `memory/session-buffer.yaml`**

```yaml
name: session-buffer
version: 1.0.0
description: "Short-term conversation buffer for all showcase agents (Redis, 10-turn window, 1hr TTL)"
team: showcase
owner: saha.rajit@gmail.com
backend: redis
memory_type: buffer_window
config:
  max_messages: 10
  ttl_seconds: 3600
  namespace_pattern: "{agent_id}:{session_id}"
scope: agent
```

- [ ] **Step 2: Create `memory/entity-store.yaml`**

```yaml
name: entity-store
version: 1.0.0
description: "Long-term entity memory for claude-sdk agent (PostgreSQL)"
team: showcase
owner: saha.rajit@gmail.com
backend: postgresql
memory_type: entity
config:
  namespace_pattern: "{agent_id}:{session_id}"
scope: agent
```

- [ ] **Step 3: Create `memory/semantic-store.yaml`**

```yaml
name: semantic-store
version: 1.0.0
description: "Long-term semantic memory for openai-agents (PostgreSQL)"
team: showcase
owner: saha.rajit@gmail.com
backend: postgresql
memory_type: semantic
config:
  namespace_pattern: "{agent_id}:{session_id}"
scope: agent
```

- [ ] **Step 4: Validate YAML syntax**

Run:
```bash
python3 -c "
import yaml, sys
for f in ['memory/session-buffer.yaml','memory/entity-store.yaml','memory/semantic-store.yaml']:
    yaml.safe_load(open(f))
    print(f'OK: {f}')
"
```

Expected: `OK: memory/session-buffer.yaml` (3 lines)

- [ ] **Step 5: Commit**

```bash
git add memory/
git commit -m "feat: add AgentBreeder memory registry declarations"
```

---

## Task 3: RAG Registry Declarations

**Files:**
- Create: `rag/enterprise-docs.yaml`, `rag/ai-use-cases.yaml`, `rag/technical-docs.yaml`

- [ ] **Step 1: Create `rag/enterprise-docs.yaml`**

```yaml
name: enterprise-docs
version: 1.0.0
description: "Enterprise AI benefits, ROI case studies, and adoption patterns — for crewai agent"
team: showcase
owner: saha.rajit@gmail.com
backend: pgvector
embedding_model:
  provider: openai
  name: text-embedding-3-small
  dimensions: 1536
chunking:
  strategy: recursive
  chunk_size: 512
  chunk_overlap: 50
sources:
  - type: file
    path: "rag/docs/enterprise/*.md"
search:
  hybrid: false
  default_top_k: 5
```

- [ ] **Step 2: Create `rag/ai-use-cases.yaml`**

```yaml
name: ai-use-cases
version: 1.0.0
description: "AI use cases across industries with implementation examples — for google-adk agent"
team: showcase
owner: saha.rajit@gmail.com
backend: pgvector
embedding_model:
  provider: openai
  name: text-embedding-3-small
  dimensions: 1536
chunking:
  strategy: recursive
  chunk_size: 512
  chunk_overlap: 50
sources:
  - type: file
    path: "rag/docs/ai-use-cases/*.md"
search:
  hybrid: false
  default_top_k: 5
```

- [ ] **Step 3: Create `rag/technical-docs.yaml`**

```yaml
name: technical-docs
version: 1.0.0
description: "Technical AI/ML implementation guides and best practices — for langgraph agent"
team: showcase
owner: saha.rajit@gmail.com
backend: pgvector
embedding_model:
  provider: openai
  name: text-embedding-3-small
  dimensions: 1536
chunking:
  strategy: recursive
  chunk_size: 512
  chunk_overlap: 50
sources:
  - type: file
    path: "rag/docs/technical/*.md"
search:
  hybrid: false
  default_top_k: 5
```

- [ ] **Step 4: Create seed documents**

```bash
mkdir -p rag/docs/enterprise rag/docs/ai-use-cases rag/docs/technical
```

Create `rag/docs/enterprise/01-roi.md`:
```markdown
# Enterprise AI ROI: Key Metrics

Enterprise AI deployments deliver measurable ROI across three dimensions:

**Productivity**: Automation of repetitive tasks reduces manual labor by 40-60%.
Knowledge workers reclaim 2-3 hours per day through AI-assisted drafting, summarization, and research.

**Cost Reduction**: AI agents handle tier-1 support at 1/10th the cost of human agents.
Process automation cuts operational overhead by 20-35% within 18 months.

**Revenue Growth**: Personalization at scale increases conversion rates by 15-25%.
Faster time-to-market through AI-assisted development accelerates product cycles.
```

Create `rag/docs/enterprise/02-automation.md`:
```markdown
# Enterprise AI Automation Patterns

## Document Processing
AI agents extract, classify, and route documents with 95%+ accuracy.
Use cases: invoice processing, contract review, compliance monitoring.

## Customer Engagement
Conversational AI handles 70% of customer inquiries without human escalation.
Sentiment analysis enables proactive churn prevention.

## Decision Support
AI synthesizes data from multiple sources to surface actionable insights.
Reduces decision latency from days to minutes.
```

Create `rag/docs/ai-use-cases/01-industries.md`:
```markdown
# AI Use Cases by Industry

## Healthcare
- Clinical decision support: AI reviews patient records and flags risk factors
- Medical imaging analysis: 94% accuracy in radiology screening
- Drug discovery: Reduces candidate identification from years to months

## Financial Services
- Fraud detection: Real-time transaction scoring reduces false positives by 60%
- Algorithmic trading: Sub-millisecond execution with risk guardrails
- Credit underwriting: Alternative data expands access to 30M unbanked consumers

## Manufacturing
- Predictive maintenance: 40% reduction in unplanned downtime
- Quality control: Computer vision achieves 99.7% defect detection
- Supply chain optimization: Demand forecasting accuracy improved by 25%
```

Create `rag/docs/technical/01-patterns.md`:
```markdown
# AI Agent Implementation Patterns

## ReAct (Reasoning + Acting)
Agents alternate between reasoning about the problem and taking actions.
Best for: multi-step tasks requiring dynamic tool selection.

## Plan-and-Execute
Agent creates a plan upfront, then executes each step.
Best for: complex workflows with predictable structure.

## Multi-Agent Orchestration
Specialized agents collaborate — one orchestrator routes tasks to sub-agents.
Best for: tasks requiring diverse expertise (research + analysis + synthesis).

## Memory Integration
- Short-term: Buffer window (last N turns) — implemented via Redis
- Long-term: Entity extraction + semantic search — implemented via PostgreSQL + pgvector
```

- [ ] **Step 5: Validate YAML syntax**

Run:
```bash
python3 -c "
import yaml
for f in ['rag/enterprise-docs.yaml','rag/ai-use-cases.yaml','rag/technical-docs.yaml']:
    yaml.safe_load(open(f))
    print(f'OK: {f}')
"
```

Expected: 3 OK lines.

- [ ] **Step 6: Commit**

```bash
git add rag/
git commit -m "feat: add AgentBreeder RAG registry declarations and seed documents"
```

---

## Task 4: Add OpenTelemetry Packages to All requirements.txt

**Files:**
- Modify: `agents/claude-sdk/requirements.txt`, `agents/openai-agents/requirements.txt`, `agents/crewai/requirements.txt`, `agents/google-adk/requirements.txt`, `agents/langgraph/requirements.txt`

- [ ] **Step 1: Add OTel packages to claude-sdk**

Current `agents/claude-sdk/requirements.txt`:
```
anthropic>=0.49.0
python-dotenv>=1.0.0
```

New content:
```
anthropic>=0.49.0
python-dotenv>=1.0.0
opentelemetry-sdk>=1.20.0
opentelemetry-exporter-otlp-proto-grpc>=1.20.0
```

- [ ] **Step 2: Add OTel packages to openai-agents**

Current `agents/openai-agents/requirements.txt`:
```
openai-agents>=0.0.19
python-dotenv>=1.0.0
```

New content:
```
openai-agents>=0.0.19
python-dotenv>=1.0.0
opentelemetry-sdk>=1.20.0
opentelemetry-exporter-otlp-proto-grpc>=1.20.0
```

- [ ] **Step 3: Add OTel packages to crewai**

Current `agents/crewai/requirements.txt`:
```
crewai>=1.6.1
anthropic>=0.49.0
python-dotenv>=1.0.0
```

New content:
```
crewai>=1.6.1
anthropic>=0.49.0
python-dotenv>=1.0.0
opentelemetry-sdk>=1.20.0
opentelemetry-exporter-otlp-proto-grpc>=1.20.0
```

- [ ] **Step 4: Add OTel packages to google-adk**

Current `agents/google-adk/requirements.txt`:
```
google-adk>=1.31.0
google-genai>=1.0.0
python-dotenv>=1.0.0
```

New content:
```
google-adk>=1.31.0
google-genai>=1.0.0
python-dotenv>=1.0.0
opentelemetry-sdk>=1.20.0
opentelemetry-exporter-otlp-proto-grpc>=1.20.0
```

- [ ] **Step 5: Add OTel packages to langgraph (already has tracing but add grpc exporter)**

Current `agents/langgraph/requirements.txt`:
```
langgraph>=0.2.0
langchain-ollama>=0.1.0
requests>=2.31.0
python-dotenv>=1.0.0
```

New content:
```
langgraph>=0.2.0
langchain-ollama>=0.1.0
requests>=2.31.0
python-dotenv>=1.0.0
opentelemetry-sdk>=1.20.0
opentelemetry-exporter-otlp-proto-grpc>=1.20.0
```

- [ ] **Step 6: Commit**

```bash
git add agents/*/requirements.txt
git commit -m "feat: add OpenTelemetry packages to all agent requirements"
```

---

## Task 5: Patch Server Templates — Add init_tracing()

**Files:**
- Modify: `venv/lib/python3.12/site-packages/engine/runtimes/templates/claude_sdk_server.py`
- Modify: `venv/lib/python3.12/site-packages/engine/runtimes/templates/crewai_server.py`
- Modify: `venv/lib/python3.12/site-packages/engine/runtimes/templates/openai_agents_server.py`
- Modify: `venv/lib/python3.12/site-packages/engine/runtimes/templates/google_adk_server.py`

The langgraph template already calls `init_tracing()` — skip it.

- [ ] **Step 1: Patch claude_sdk_server.py**

Find the `startup()` function. It starts with:
```python
@app.on_event("startup")
async def startup() -> None:
    global _agent, _client, _tools  # noqa: PLW0603
```

Insert `init_tracing()` call at the beginning of `startup()`:
```python
@app.on_event("startup")
async def startup() -> None:
    global _agent, _client, _tools  # noqa: PLW0603

    # Initialise OTel tracing (no-op if OPENTELEMETRY_ENDPOINT not set)
    try:
        from _tracing import init_tracing
        init_tracing()
    except ImportError:
        pass
```

- [ ] **Step 2: Patch crewai_server.py**

Find the startup event handler in crewai_server.py. Add the same tracing init block at the start of the startup function (before the tools loading block):
```python
    # Initialise OTel tracing (no-op if OPENTELEMETRY_ENDPOINT not set)
    try:
        from _tracing import init_tracing
        init_tracing()
    except ImportError:
        pass
```

- [ ] **Step 3: Patch openai_agents_server.py**

Find the startup event handler in openai_agents_server.py. Add the same 5-line tracing init block at the start of the startup function.

- [ ] **Step 4: Patch google_adk_server.py**

Find the startup event handler in google_adk_server.py. Add the same 5-line tracing init block at the start of the startup function.

- [ ] **Step 5: Verify patches don't break existing imports**

Run:
```bash
cd /Users/rajit/agentbreeder-showcase/venv/lib/python3.12/site-packages/engine/runtimes/templates
python3 -c "import ast, sys
for f in ['claude_sdk_server.py','crewai_server.py','openai_agents_server.py','google_adk_server.py']:
    try:
        ast.parse(open(f).read())
        print(f'OK syntax: {f}')
    except SyntaxError as e:
        print(f'SYNTAX ERROR {f}: {e}')
        sys.exit(1)
"
```

Expected: 4 `OK syntax:` lines.

---

## Task 6: Patch tool_bridge.py — Dict Input Support

**Files:**
- Modify: `venv/lib/python3.12/site-packages/engine/tool_bridge.py`

The problem: `AGENT_TOOLS_JSON` contains JSON-deserialized dicts. `to_crewai_tools` and `_resolve_endpoint` access `.ref`, `.name` etc. via attribute access, which fails on dicts.

- [ ] **Step 1: Add `_normalize_tool_ref` helper**

After the `_ENV_PREFIX = "TOOL_ENDPOINT_"` line, add:

```python
def _normalize_tool_ref(tool: Any) -> Any:
    """Convert a plain dict to a SimpleNamespace so attribute access works on both."""
    if isinstance(tool, dict):
        from types import SimpleNamespace
        return SimpleNamespace(
            ref=tool.get("ref"),
            name=tool.get("name"),
            description=tool.get("description"),
            schema_=tool.get("schema"),
            type=tool.get("type"),
        )
    return tool
```

- [ ] **Step 2: Apply normalization in `to_claude_tools`**

Find the start of `to_claude_tools`:
```python
def to_claude_tools(tools: list[Any]) -> list[dict[str, Any]]:
    ...
    result: list[dict[str, Any]] = []
    for tool_ref in tools:
```

Change the loop line to normalize each tool:
```python
    result: list[dict[str, Any]] = []
    for tool_ref in [_normalize_tool_ref(t) for t in tools]:
```

- [ ] **Step 3: Apply normalization in `to_crewai_tools`**

Find the start of `to_crewai_tools`:
```python
    result: list[Any] = []

    for tool_ref in tools:
```

Change to:
```python
    result: list[Any] = []

    for tool_ref in [_normalize_tool_ref(t) for t in tools]:
```

- [ ] **Step 4: Verify syntax**

Run:
```bash
python3 -c "import ast; ast.parse(open('/Users/rajit/agentbreeder-showcase/venv/lib/python3.12/site-packages/engine/tool_bridge.py').read()); print('OK')"
```

Expected: `OK`

---

## Task 7: Patch docker_compose.py Deployer

**Files:**
- Modify: `venv/lib/python3.12/site-packages/engine/deployers/docker_compose.py`

Three changes:
1. Always put agent containers on `agentbreeder-net` (not just Ollama agents)
2. Inject `AGENT_TOOLS_JSON` env var from `config.tools`
3. Inject `TOOL_ENDPOINT_CALL_*` env vars from `config.subagents`

- [ ] **Step 1: Always ensure network + add all containers to agentbreeder-net**

Find the block near the end of `deploy()`:
```python
        if config.model.primary.startswith("ollama/") and "OLLAMA_BASE_URL" not in config.deploy.env_vars:
            await self._ensure_network(client)
            await self._ensure_ollama_sidecar(client)
            model_tag = config.model.primary.split("/", 1)[1]
            await self._pull_ollama_model(client, model_tag)
            container_env["OLLAMA_BASE_URL"] = f"http://{OLLAMA_CONTAINER_NAME}:11434"

        # Run the container
        logger.info("Starting container: %s on port %d", container_name, port)
        run_kwargs: dict = {
            "name": container_name,
            "ports": {"8080/tcp": port},
            "environment": container_env,
            "detach": True,
            "remove": False,
        }
        if config.model.primary.startswith("ollama/"):
            run_kwargs["network"] = OLLAMA_NETWORK_NAME
```

Replace with:
```python
        # Always ensure agentbreeder-net exists (for A2A + tracing)
        await self._ensure_network(client)

        if config.model.primary.startswith("ollama/") and "OLLAMA_BASE_URL" not in config.deploy.env_vars:
            await self._ensure_ollama_sidecar(client)
            model_tag = config.model.primary.split("/", 1)[1]
            await self._pull_ollama_model(client, model_tag)
            container_env["OLLAMA_BASE_URL"] = f"http://{OLLAMA_CONTAINER_NAME}:11434"

        # Run the container
        logger.info("Starting container: %s on port %d", container_name, port)
        run_kwargs: dict = {
            "name": container_name,
            "ports": {"8080/tcp": port},
            "environment": container_env,
            "detach": True,
            "remove": False,
            "network": OLLAMA_NETWORK_NAME,
        }
```

- [ ] **Step 2: Inject AGENT_TOOLS_JSON and TOOL_ENDPOINT_* for subagents**

Find the `# For ollama/ models:` comment block (just before the "Run the container" section). After the env_vars resolution loop and before that block, add:

```python
        # Inject subagent tools as AGENT_TOOLS_JSON so server templates can wire them
        if config.tools:
            import json as _json
            tools_payload = [
                {k: v for k, v in t.model_dump(by_alias=True).items() if v is not None}
                for t in config.tools
            ]
            container_env["AGENT_TOOLS_JSON"] = _json.dumps(tools_payload)

        # Inject TOOL_ENDPOINT_CALL_* for each subagent so tool_bridge can route calls
        for sub in config.subagents:
            slug = sub.slug  # e.g. "demo-openai-agents"
            container_name_sub = f"agentbreeder-{slug}"
            # tool_name matches generate_subagent_tools: call_{slug.replace('-', '_')}
            tool_name = f"call_{slug.replace('-', '_')}"
            # env key: TOOL_ENDPOINT_ + slug uppercased and non-alphanum replaced with _
            import re as _re
            env_key = "TOOL_ENDPOINT_" + _re.sub(r"[^a-zA-Z0-9]", "_", tool_name).upper()
            container_env[env_key] = f"http://{container_name_sub}:8080"
            logger.info("Injecting subagent endpoint: %s=%s", env_key, container_env[env_key])
```

- [ ] **Step 3: Verify syntax**

Run:
```bash
python3 -c "import ast; ast.parse(open('/Users/rajit/agentbreeder-showcase/venv/lib/python3.12/site-packages/engine/deployers/docker_compose.py').read()); print('OK')"
```

Expected: `OK`

---

## Task 8: Update agent.yaml Files — Tracing Baseline (All 5)

**Files:**
- Modify: all 5 `agents/*/agent.yaml`

Add `OPENTELEMETRY_ENDPOINT: "http://agentbreeder-jaeger:4317"` to the `deploy.env_vars` section of all 5 agent.yaml files.

- [ ] **Step 1: Update agents/claude-sdk/agent.yaml**

Replace the current file content with:
```yaml
# agents/claude-sdk/agent.yaml
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
  env_vars:
    ANTHROPIC_API_KEY: "secret://ANTHROPIC_API_KEY"
    OPENTELEMETRY_ENDPOINT: "http://agentbreeder-jaeger:4317"
```

- [ ] **Step 2: Update agents/openai-agents/agent.yaml**

```yaml
# agents/openai-agents/agent.yaml
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
  env_vars:
    OPENAI_API_KEY: "secret://OPENAI_API_KEY"
    OPENTELEMETRY_ENDPOINT: "http://agentbreeder-jaeger:4317"
```

- [ ] **Step 3: Update agents/crewai/agent.yaml**

```yaml
# agents/crewai/agent.yaml
name: demo-crewai
version: 1.0.0
team: showcase
owner: saha.rajit@gmail.com

framework: crewai
model:
  primary: claude-sonnet-4-6
  fallback: claude-sonnet-4-6

knowledge_bases:
  - ref: enterprise-docs

subagents:
  - ref: agents/demo-langgraph
    name: demo-langgraph
    description: "LangGraph agent for technical research and pattern analysis"
  - ref: agents/demo-claude-sdk
    name: demo-claude-sdk
    description: "Claude SDK agent for enterprise benefit synthesis"

deploy:
  cloud: local
  scaling:
    min: 1
    max: 3
  env_vars:
    ANTHROPIC_API_KEY: "secret://ANTHROPIC_API_KEY"
    OPENTELEMETRY_ENDPOINT: "http://agentbreeder-jaeger:4317"
```

- [ ] **Step 4: Update agents/google-adk/agent.yaml**

```yaml
# agents/google-adk/agent.yaml
name: demo-google-adk
version: 1.0.0
team: showcase
owner: saha.rajit@gmail.com

framework: google_adk
model:
  primary: gemini-2.5-flash
  fallback: gemini-2.0-flash-001

knowledge_bases:
  - ref: ai-use-cases

deploy:
  cloud: local
  scaling:
    min: 1
    max: 3
  env_vars:
    GOOGLE_API_KEY: "secret://GOOGLE_API_KEY"
    OPENTELEMETRY_ENDPOINT: "http://agentbreeder-jaeger:4317"
```

- [ ] **Step 5: Update agents/langgraph/agent.yaml**

```yaml
# agents/langgraph/agent.yaml
name: demo-langgraph
version: 1.0.0
team: showcase
owner: saha.rajit@gmail.com

framework: langgraph
model:
  primary: ollama/llama3.2
  fallback: ollama/llama3.1

knowledge_bases:
  - ref: technical-docs

deploy:
  cloud: local
  scaling:
    min: 1
    max: 3
  env_vars:
    OLLAMA_BASE_URL: "http://host.docker.internal:11434"
    OPENTELEMETRY_ENDPOINT: "http://agentbreeder-jaeger:4317"
```

- [ ] **Step 6: Validate all 5 agent.yaml files**

Run:
```bash
source venv/bin/activate
for f in agents/*/agent.yaml; do
    agentbreeder validate "$f" && echo "OK: $f" || echo "FAIL: $f"
done
```

Expected: 5 `OK:` lines

- [ ] **Step 7: Commit**

```bash
git add agents/*/agent.yaml
git commit -m "feat: add tracing, RAG refs, and A2A subagents to all agent.yaml configs"
```

---

## Task 9: Redeploy All 5 Agents

**Files:** None — deploy pipeline only

Before deploying: ensure Jaeger is running (`docker compose -f infra/docker-compose.yml ps`).

- [ ] **Step 1: Set Docker host**

```bash
export DOCKER_HOST="unix:///Users/rajit/.docker/run/docker.sock"
```

- [ ] **Step 2: Deploy claude-sdk**

Run: `source venv/bin/activate && agentbreeder deploy agents/claude-sdk/agent.yaml --target local`

Expected: `[8/8] Auto-register — done` with no errors

- [ ] **Step 3: Deploy openai-agents**

Run: `agentbreeder deploy agents/openai-agents/agent.yaml --target local`

Expected: `[8/8] Auto-register — done`

- [ ] **Step 4: Deploy crewai**

Run: `agentbreeder deploy agents/crewai/agent.yaml --target local`

Expected: `[8/8] Auto-register — done`

Note: This agent has `subagents:` — the deploy should log "Injecting subagent endpoint: TOOL_ENDPOINT_CALL_DEMO_LANGGRAPH=http://agentbreeder-demo-langgraph:8080"

- [ ] **Step 5: Deploy google-adk**

Run: `agentbreeder deploy agents/google-adk/agent.yaml --target local`

Expected: `[8/8] Auto-register — done`

- [ ] **Step 6: Deploy langgraph**

Run: `agentbreeder deploy agents/langgraph/agent.yaml --target local`

Expected: `[8/8] Auto-register — done`

- [ ] **Step 7: Verify all 5 containers are running**

Run: `DOCKER_HOST="unix:///Users/rajit/.docker/run/docker.sock" docker ps --format "{{.Names}}\t{{.Status}}" | grep agentbreeder-demo`

Expected: 5 containers showing `Up`

---

## Task 10: Smoke Test — Tracing and A2A

- [ ] **Step 1: Invoke claude-sdk and verify span appears in Jaeger**

Run:
```bash
curl -s -X POST http://localhost:8123/invoke \
  -H "Content-Type: application/json" \
  -d '{"input": "What are the top 3 benefits of AI agents in enterprise?"}' | python3 -m json.tool
```

Expected: JSON response with `"output": "..."` containing a numbered list.

- [ ] **Step 2: Check Jaeger UI for claude-sdk trace**

Open: `http://localhost:16686`

Select service: `demo-claude-sdk` → click "Find Traces"

Expected: At least 1 trace with an `agent.invoke` span.

- [ ] **Step 3: Invoke crewai (A2A orchestrator) and verify sub-agent calls**

Run:
```bash
curl -s -X POST http://localhost:8133/invoke \
  -H "Content-Type: application/json" \
  -d '{"input": "Analyze enterprise AI adoption barriers using your sub-agents"}' | python3 -m json.tool
```

Expected: JSON response showing crewai called its sub-agents (demo-langgraph and demo-claude-sdk).

- [ ] **Step 4: Check Jaeger for crewai trace showing cross-agent spans**

In Jaeger UI: select service `demo-crewai` → Find Traces.

Expected: Traces showing spans for `demo-crewai` AND child spans for `demo-langgraph` and/or `demo-claude-sdk`.

- [ ] **Step 5: Invoke remaining agents**

```bash
# google-adk
curl -s -X POST http://localhost:8127/invoke -H "Content-Type: application/json" \
  -d '{"input": "What AI use cases exist in healthcare?"}' | python3 -m json.tool

# langgraph
curl -s -X POST http://localhost:8145/invoke -H "Content-Type: application/json" \
  -d '{"input": "What AI implementation patterns exist?"}' | python3 -m json.tool

# openai-agents
curl -s -X POST http://localhost:8131/invoke -H "Content-Type: application/json" \
  -d '{"input": "What are the top 3 benefits of AI agents in enterprise?"}' | python3 -m json.tool
```

Expected: All 3 return JSON with `"output"` field containing relevant answers.

---

## Task 11: Create and Run Evals

**Files:**
- Create: `evals/run_evals.py`
- Create: `evals/dataset.jsonl`

The AgentBreeder eval store is in-memory per process. Dataset and run must be created in the same Python process.

- [ ] **Step 1: Create `evals/dataset.jsonl`** (reference data — not used directly by script, but documents the eval cases)

```jsonl
{"input": {"message": "What are the top 3 benefits of AI agents in enterprise?"}, "expected_output": "productivity, cost reduction, automation", "agent": "demo-claude-sdk", "tags": ["enterprise", "benefits"]}
{"input": {"message": "List 3 benefits of AI agents in enterprise"}, "expected_output": "1. productivity 2. cost 3. automation", "agent": "demo-openai-agents", "tags": ["enterprise", "benefits"]}
{"input": {"message": "What AI use cases exist in healthcare?"}, "expected_output": "clinical decision support, medical imaging, drug discovery", "agent": "demo-google-adk", "tags": ["healthcare", "use-cases"]}
{"input": {"message": "What AI implementation patterns exist?"}, "expected_output": "ReAct, Plan-and-Execute, multi-agent orchestration", "agent": "demo-langgraph", "tags": ["technical", "patterns"]}
{"input": {"message": "Analyze enterprise AI adoption barriers"}, "expected_output": "skills gap, data quality, integration complexity", "agent": "demo-crewai", "tags": ["enterprise", "adoption"]}
```

- [ ] **Step 2: Create `evals/run_evals.py`**

```python
"""Run AgentBreeder showcase evals using the eval service API.

The eval store is in-memory per process — dataset creation and eval run
must happen in the same process. This script does both.
"""
import sys
import json
sys.path.insert(0, "/Users/rajit/agentbreeder-showcase/venv/lib/python3.12/site-packages")

from api.services.eval_service import get_eval_store

AGENTS = [
    "demo-claude-sdk",
    "demo-openai-agents",
    "demo-google-adk",
    "demo-langgraph",
    "demo-crewai",
]

ROWS = [
    {
        "input": {"message": "What are the top 3 benefits of AI agents in enterprise?"},
        "expected_output": "Three enterprise AI benefits: productivity gains (40-60% automation), cost reduction (20-35% operational savings), and revenue growth through personalization.",
        "tags": ["enterprise", "benefits"],
    },
    {
        "input": {"message": "List 3 AI use cases in healthcare"},
        "expected_output": "Healthcare AI use cases: clinical decision support, medical imaging analysis (94% accuracy), and drug discovery acceleration.",
        "tags": ["healthcare", "use-cases"],
    },
    {
        "input": {"message": "What AI implementation patterns should I know?"},
        "expected_output": "Key AI agent patterns: ReAct (reasoning + acting), Plan-and-Execute (upfront planning), and Multi-Agent Orchestration (specialized sub-agents).",
        "tags": ["technical", "patterns"],
    },
]


def run_eval_for_agent(store, dataset_id: str, agent_name: str) -> dict:
    run = store.create_run(
        agent_name=agent_name,
        dataset_id=dataset_id,
        config={"judge_model": "claude-sonnet-4-6"},
    )
    result = store.execute_run(run["id"])
    return result


def main():
    store = get_eval_store()

    # Remove seeded demo dataset to avoid confusion
    for ds in store.list_datasets():
        if ds["name"] == "customer-support-qa":
            store.delete_dataset(ds["id"])

    # Create showcase dataset
    dataset = store.create_dataset(
        name="showcase-qa",
        description="Showcase agent evaluation — enterprise AI and technical questions",
        team="showcase",
        tags=["showcase", "demo", "enterprise"],
        version="1.0.0",
    )
    dataset_id = dataset["id"]
    store.add_rows(dataset_id, ROWS)
    print(f"Dataset created: {dataset_id}")

    # Run evals for all agents
    results = {}
    for agent_name in AGENTS:
        print(f"\nRunning eval for {agent_name}...")
        result = run_eval_for_agent(store, dataset_id, agent_name)
        summary = result.get("summary", {})
        metrics = summary.get("metrics", {})
        results[agent_name] = {
            "status": result["status"],
            "correctness": round(metrics.get("avg_correctness", 0), 3),
            "relevance": round(metrics.get("avg_relevance", 0), 3),
            "total_results": summary.get("total_results", 0),
        }
        print(f"  Status: {result['status']}")
        print(f"  Correctness: {results[agent_name]['correctness']}")
        print(f"  Relevance: {results[agent_name]['relevance']}")

    print("\n=== Eval Summary ===")
    print(json.dumps(results, indent=2))
    print(f"\nFull results available via store.list_runs()")


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Run the evals**

```bash
source venv/bin/activate && python3 evals/run_evals.py
```

Expected output:
```
Dataset created: <uuid>

Running eval for demo-claude-sdk...
  Status: completed
  Correctness: 0.7xx
  Relevance: 0.7xx
...

=== Eval Summary ===
{
  "demo-claude-sdk": {"status": "completed", ...},
  ...
}
```

- [ ] **Step 4: Commit**

```bash
git add evals/
git commit -m "feat: add showcase eval dataset and eval runner script"
```

---

## Task 12: File GitHub Issues for Unimplemented Features

For each issue below, file at the AgentBreeder repository. Based on the codebase, the likely repo is the one hosting the `engine` package.

- [ ] **Issue 1: Memory runtime integration**

Title: `feat: wire memory.yaml stores into agent.yaml and server templates`

Body:
```
## Problem
`memory.yaml` defines valid backend configurations (redis, postgresql) but:
1. `AgentConfig` (agent.yaml schema) has no `memory:` field to reference stores
2. Server templates do not inject memory context into agent invocations

## Expected Behavior
- Add `memory: {stores: [session-buffer, entity-store]}` to agent.yaml schema
- Server templates should load conversation history from the referenced store before invoking the agent, and persist the result after

## Use Case
Showcase agents using short-term Redis buffer + long-term PostgreSQL entity/semantic memory
```

- [ ] **Issue 2: RAG/knowledge_bases runtime injection**

Title: `feat: implement knowledge_bases runtime injection (currently stub)`

Body:
```
## Problem
`knowledge_bases:` is parsed in agent.yaml and `resolve_dependencies()` logs refs, but:
- The resolver comment says "refs are passed through unchanged" (v0.1 stub)
- No server template queries a rag.yaml index before agent invocation
- `rag.yaml` sources and pgvector backend are declared but never executed

## Expected Behavior
- On agent startup, index the rag.yaml sources into pgvector
- Before each invocation, perform vector search and inject top-k chunks as context

## Use Case
Showcase agents answering questions grounded in seed documents (enterprise docs, AI use cases, technical patterns)
```

- [ ] **Issue 3: A2A tool execution loop for claude_sdk and openai_agents**

Title: `feat: implement tool-use execution loop in claude_sdk and openai_agents server templates`

Body:
```
## Problem
`claude_sdk_server.py`'s `_run_agent()` calls `_extract_text(response)` which only reads text blocks. When Claude returns a `tool_use` block (e.g., calling a subagent), the tool call is silently dropped.

`openai_agents_server.py` uses the OpenAI Agents SDK handoff pattern, not the tool_bridge pattern.

`crewai_server.py` DOES work — it injects tools via `to_crewai_tools()` and CrewAI's native loop handles execution.

## Expected Behavior
- `claude_sdk_server.py`: implement agentic loop (tool_use block → execute via tool_bridge → tool_result → continue until text response)
- `openai_agents_server.py`: support subagent tools via tool_bridge in addition to SDK handoffs

## Use Case
All 3 A2A chains (claude-sdk orchestrating, openai-agents orchestrating, crewai orchestrating) should work identically
```

- [ ] **Issue 4: Neo4j Graph RAG backend**

Title: `feat: add neo4j backend for Graph RAG in rag.yaml`

Body:
```
## Problem
`rag.yaml` only supports `pgvector` and `in_memory` backends. Graph-based retrieval (entity relationships, multi-hop queries, knowledge graphs) requires a graph database.

## Proposed Schema Addition
```yaml
backend: neo4j
config:
  uri: bolt://neo4j:7687
  username: neo4j
  password: password
  database: neo4j
embedding_model:
  provider: openai
  name: text-embedding-3-small
```

## Use Case
Graph RAG over enterprise knowledge graphs: entity relationships between products, customers, and incidents with multi-hop traversal
```

- [ ] **Issue 5: Eval CLI cross-process dataset persistence**

Title: `bug: eval datasets are ephemeral per-process — eval run cannot reference datasets from eval datasets`

Body:
```
## Problem
`EvalStore` is a module-level singleton seeded with a random UUID on each process start. Running `agentbreeder eval datasets` and then `agentbreeder eval run --dataset <uuid>` fails with "Dataset not found" because each CLI command is a separate process with a fresh store.

## Root Cause
`get_eval_store()` calls `_seed_demo_data()` which uses `uuid.uuid4()` — different UUID per process.

## Expected Behavior
Datasets should persist to disk (SQLite or JSON file in `~/.agentbreeder/`) so they survive across CLI invocations.

## Workaround
Use `api.services.eval_service.get_eval_store()` directly in a Python script that creates the dataset and runs evals in the same process (see `evals/run_evals.py`).
```

---

## Success Criteria Check

- [ ] All 5 agents respond to `/invoke` POST requests
- [ ] Jaeger UI at `http://localhost:16686` shows traces for all 5 agents
- [ ] CrewAI `/invoke` with an orchestration prompt shows cross-agent spans in Jaeger
- [ ] `python3 evals/run_evals.py` completes with `status: completed` for all 5 agents
- [ ] `memory/*.yaml` and `rag/*.yaml` files validate as correct YAML
- [ ] 5 GitHub issues filed
- [ ] Zero changes to any `agents/*/agent.py` file
