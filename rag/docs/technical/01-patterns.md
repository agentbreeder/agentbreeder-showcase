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
