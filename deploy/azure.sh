#!/usr/bin/env bash
set -euo pipefail

echo "=== AgentBreeder Showcase — Azure Deploy ==="
set -a && source .env && set +a
source venv/bin/activate

# Validate all agent configs before deploying
echo "→ Validating all agent configs..."
for agent_dir in agents/*/; do
  (cd "$agent_dir" && agentbreeder validate && echo "  ✓ $(basename $agent_dir)")
done

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
