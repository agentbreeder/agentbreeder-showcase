#!/usr/bin/env bash
set -euo pipefail

echo "=== AgentBreeder Showcase — AWS Deploy ==="
set -a && source .env && set +a
source venv/bin/activate

# Docker socket fix for macOS Docker Desktop
export DOCKER_HOST=unix://"$HOME/.docker/run/docker.sock"

# Prerequisites check
: "${AWS_ACCESS_KEY_ID:?AWS_ACCESS_KEY_ID not set in .env}"
: "${AWS_SECRET_ACCESS_KEY:?AWS_SECRET_ACCESS_KEY not set in .env}"
: "${AWS_REGION:?AWS_REGION not set in .env}"
: "${AWS_ACCOUNT_ID:?AWS_ACCOUNT_ID not set in .env}"

# Validate all agent configs before deploying
echo "→ Validating all agent configs..."
for agent_dir in agents/*/; do
  agentbreeder validate "$agent_dir/agent.yaml" && echo "  ✓ $(basename $agent_dir)"
done

# Store secrets in AWS Secrets Manager (--prefix "" avoids path separator issues)
echo "→ Storing secrets in AWS Secrets Manager..."
agentbreeder secret set ANTHROPIC_API_KEY --value "$ANTHROPIC_API_KEY" --backend aws --prefix ""
agentbreeder secret set OPENAI_API_KEY --value "$OPENAI_API_KEY" --backend aws --prefix ""
agentbreeder secret set GOOGLE_API_KEY --value "$GOOGLE_API_KEY" --backend aws --prefix ""

# Deploy all agents to ECS Fargate
for agent_dir in agents/*/; do
  agent_name=$(grep '^name:' "$agent_dir/agent.yaml" | awk '{print $2}')
  echo "  → Deploying $agent_name..."
  agentbreeder deploy "$agent_dir/agent.yaml" --target aws
  echo "  ✓ $agent_name → AWS ECS Fargate"
done

agentbreeder status
echo ""
echo "=== AWS deployment complete ==="
echo "Compare with GCP: agentbreeder eval compare"
