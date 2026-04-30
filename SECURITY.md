# Security Policy

The showcase repository contains demonstration agents that consume external
APIs (LLM providers, MCP servers, RAG stores). It is intended for learning
and reference, not as production code.

## Reporting a vulnerability

If you discover a security issue in the showcase agents, configurations, or
deploy scripts, **do not open a public GitHub issue.**

Instead:

1. Use [GitHub's private vulnerability reporting](https://github.com/agentbreeder/agentbreeder-showcase/security/advisories/new), or
2. Email **security@agentbreeder.com** with subject `[SECURITY] showcase`

You will receive a response within 48 hours.

For vulnerabilities in the AgentBreeder platform itself, see the parent
repo's [`SECURITY.md`](https://github.com/agentbreeder/agentbreeder/blob/main/SECURITY.md).

## Scope

This policy covers:

- Hard-coded credentials, tokens, or other secrets accidentally committed
- Insecure deployment configurations in `deploy/` (e.g., over-privileged IAM)
- Vulnerabilities in dependencies declared in `requirements.txt` or `package.json`
- Demonstration agents that produce harmful output by design

This policy does **not** cover the AgentBreeder runtime, CLI, or engine —
those issues belong on the parent repo.

## Out of scope

- Generic advisories on third-party LLM providers
- Behavior of an agent that depends on the LLM provider's response
- Cost/spend-related issues from LLM API usage
