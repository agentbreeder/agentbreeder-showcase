#!/usr/bin/env bash
set -euo pipefail

echo "=== AgentBreeder Showcase — Azure Deploy ==="
set -a && source .env && set +a
source venv/bin/activate

# Docker socket fix for macOS Docker Desktop
export DOCKER_HOST=unix://"$HOME/.docker/run/docker.sock"

# Prerequisites check
: "${AZURE_SUBSCRIPTION_ID:?AZURE_SUBSCRIPTION_ID not set in .env}"
: "${AZURE_RESOURCE_GROUP:?AZURE_RESOURCE_GROUP not set in .env}"
: "${AZURE_LOCATION:?AZURE_LOCATION not set in .env}"

# Validate all agent configs before deploying
echo "→ Validating all agent configs..."
for agent_dir in agents/*/; do
  agentbreeder validate "$agent_dir/agent.yaml" && echo "  ✓ $(basename $agent_dir)"
done

# Authenticate
az login

# Store secrets in Azure Key Vault (--prefix "" avoids path separator issues)
echo "→ Storing secrets in Azure Key Vault..."
agentbreeder secret set ANTHROPIC_API_KEY --value "$ANTHROPIC_API_KEY" --backend azure --prefix ""
agentbreeder secret set OPENAI_API_KEY --value "$OPENAI_API_KEY" --backend azure --prefix ""
agentbreeder secret set GOOGLE_API_KEY --value "$GOOGLE_API_KEY" --backend azure --prefix ""

# Deploy all agents to Azure Container Apps
for agent_dir in agents/*/; do
  agent_name=$(grep '^name:' "$agent_dir/agent.yaml" | awk '{print $2}')
  echo "  → Deploying $agent_name..."
  agentbreeder deploy "$agent_dir/agent.yaml" --target azure
  echo "  ✓ $agent_name → Azure Container Apps"
done

agentbreeder status
echo ""
echo "=== Azure deployment complete ==="
