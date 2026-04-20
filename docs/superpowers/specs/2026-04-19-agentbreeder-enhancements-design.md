# AgentBreeder Showcase Enhancements — Design Spec

**Date:** 2026-04-19  
**Status:** Approved

---

## Goal

Enhance the 5 deployed AgentBreeder showcase agents (claude-sdk, openai-agents, crewai, google-adk, langgraph) with memory, RAG, A2A, tracing, and evals — using AgentBreeder's built-in declarative features exclusively. No custom framework code; all configuration is YAML.

---

## Guiding Constraint

> **Zero custom code.** Every feature must come from AgentBreeder's built-in platform capabilities. Agent `.py` files are not modified. All changes are YAML config, data files, and infrastructure.

---

## Architecture

### Baseline (all 5 agents)

Every agent gets:
- **Short-term memory**: Redis `buffer_window` store (10-turn window, 1-hour TTL)
- **Tracing**: `OPENTELEMETRY_ENDPOINT` in `deploy.env_vars` → Jaeger OTLP collector

### Per-Agent Unique Capability

| Agent | Unique Feature | Role in A2A |
|-------|---------------|-------------|
| `demo-claude-sdk` | PostgreSQL long-term **entity** memory | Orchestrator — Chain 1 |
| `demo-openai-agents` | PostgreSQL long-term **semantic** memory | Orchestrator — Chain 3 |
| `demo-crewai` | pgvector RAG (`enterprise_docs` collection) | Orchestrator — Chain 2 |
| `demo-google-adk` | pgvector RAG (`ai_use_cases` collection) | Sub-agent — Chains 1 & 3 |
| `demo-langgraph` | pgvector RAG (`technical_docs` collection) | Sub-agent — Chain 2 |

### A2A Demo Chains (3 independent scenarios)

- **Chain 1** — `claude-sdk` → `openai-agents` + `google-adk` *(research synthesis)*
- **Chain 2** — `crewai` → `langgraph` + `claude-sdk` *(analysis pipeline)*
- **Chain 3** — `openai-agents` → `crewai` + `google-adk` *(content generation)*

Each chain is an independent invocation; the same agent plays different roles in different chains. No circular call paths within a single invocation.

---

## Infrastructure

Three new Docker sidecars on the existing `agentbreeder-net` network:

| Service | Image | Purpose |
|---------|-------|---------|
| `redis` | `redis:7-alpine` | Short-term buffer memory for all agents |
| `postgres` | `pgvector/pgvector:pg16` | Long-term memory + pgvector RAG store |
| `jaeger` | `jaegertracing/all-in-one:latest` | OTLP trace collector + UI (`:16686`) |

Defined in `infra/docker-compose.yml`. Spun up before `agentbreeder deploy`.

---

## Files To Create or Modify

### New Files

| Path | Type | Description |
|------|------|-------------|
| `infra/docker-compose.yml` | Docker Compose | Redis, Postgres, Jaeger sidecars |
| `memory.yaml` | AgentBreeder config | Memory backends and stores |
| `rag.yaml` | AgentBreeder config | pgvector backend and 3 collections |
| `evals/dataset.jsonl` | JSONL data | Eval prompts + expected outputs for all agents |
| `evals/config.yaml` | AgentBreeder eval config | Eval run parameters |

### Modified Files (YAML only, no .py changes)

| Path | Change |
|------|--------|
| `agents/claude-sdk/agent.yaml` | Add `memory:`, `subagents:`, `deploy.env_vars.OPENTELEMETRY_ENDPOINT` |
| `agents/openai-agents/agent.yaml` | Add `memory:`, `subagents:`, `deploy.env_vars.OPENTELEMETRY_ENDPOINT` |
| `agents/crewai/agent.yaml` | Add `memory:`, `knowledge_bases:`, `subagents:`, `deploy.env_vars.OPENTELEMETRY_ENDPOINT` |
| `agents/google-adk/agent.yaml` | Add `memory:`, `knowledge_bases:`, `deploy.env_vars.OPENTELEMETRY_ENDPOINT` |
| `agents/langgraph/agent.yaml` | Add `memory:`, `knowledge_bases:`, `deploy.env_vars.OPENTELEMETRY_ENDPOINT` |

---

## memory.yaml

```yaml
backends:
  redis_short_term:
    type: redis
    config:
      url: redis://redis:6379
      ttl: 3600

  postgres_long_term:
    type: postgresql
    config:
      url: postgresql://agentbreeder:agentbreeder@postgres:5432/agentbreeder

stores:
  session_buffer:
    backend: redis_short_term
    memory_type: buffer_window
    window_size: 10

  entity_memory:
    backend: postgres_long_term
    memory_type: entity

  semantic_memory:
    backend: postgres_long_term
    memory_type: semantic
```

---

## rag.yaml

```yaml
backends:
  pgvector_store:
    type: pgvector
    config:
      url: postgresql://agentbreeder:agentbreeder@postgres:5432/agentbreeder
      embedding_model: text-embedding-3-small

collections:
  enterprise_docs:
    backend: pgvector_store
    description: "Enterprise AI benefits, ROI case studies, and adoption patterns"

  ai_use_cases:
    backend: pgvector_store
    description: "AI use cases across industries with implementation examples"

  technical_docs:
    backend: pgvector_store
    description: "Technical AI/ML implementation guides and best practices"
```

Seed documents (3–5 short markdown files per collection) stored in `rag/enterprise_docs/`, `rag/ai_use_cases/`, `rag/technical_docs/`.

---

## agent.yaml Changes (representative)

### claude-sdk (orchestrator, entity memory)
```yaml
memory:
  stores:
    - session_buffer   # short-term (baseline)
    - entity_memory    # long-term (unique)

subagents:
  - name: openai-agents
    endpoint: http://agentbreeder-demo-openai-agents:8080
  - name: google-adk
    endpoint: http://agentbreeder-demo-google-adk:8080

deploy:
  env_vars:
    ANTHROPIC_API_KEY: "secret://ANTHROPIC_API_KEY"
    OPENTELEMETRY_ENDPOINT: "http://jaeger:4317"
```

### crewai (rag + orchestrator)
```yaml
memory:
  stores:
    - session_buffer   # short-term (baseline)

knowledge_bases:
  - enterprise_docs    # pgvector RAG (unique)

subagents:
  - name: langgraph
    endpoint: http://agentbreeder-demo-langgraph:8080
  - name: claude-sdk
    endpoint: http://agentbreeder-demo-claude-sdk:8080

deploy:
  env_vars:
    ANTHROPIC_API_KEY: "secret://ANTHROPIC_API_KEY"
    OPENTELEMETRY_ENDPOINT: "http://jaeger:4317"
```

### google-adk / langgraph (rag sub-agents, no subagents block)
```yaml
memory:
  stores:
    - session_buffer

knowledge_bases:
  - ai_use_cases       # or technical_docs for langgraph

deploy:
  env_vars:
    OPENTELEMETRY_ENDPOINT: "http://jaeger:4317"
    # existing keys...
```

---

## Evals

`evals/dataset.jsonl` — 5 prompts per agent (25 total), covering:
- Direct capability (RAG retrieval quality)
- Memory recall (follow-up questions)
- A2A delegation (did orchestrator call sub-agents)
- Response quality (LLM-as-judge scoring)

```bash
agentbreeder eval run --dataset evals/dataset.jsonl --agent demo-claude-sdk
agentbreeder eval results --agent demo-claude-sdk
```

Results visible in AgentBreeder UI dashboard.

---

## Out of Scope (GitHub Issue)

**Neo4j Graph RAG backend** — AgentBreeder's `rag.yaml` only supports `pgvector` and `in_memory` backends. A GitHub issue will be filed requesting a `neo4j` backend type for graph-based retrieval (knowledge graphs, entity relationships, multi-hop queries).

Issue title: `feat: add neo4j backend for Graph RAG in rag.yaml`

---

## Success Criteria

1. All 5 agents respond to `/invoke` with memory context carried across calls
2. RAG agents return answers grounded in seed documents (verifiable by checking sources)
3. Each A2A chain produces traces showing cross-agent span propagation in Jaeger UI
4. `agentbreeder eval run` completes without errors; results appear in UI
5. No changes to any `agent.py` file
