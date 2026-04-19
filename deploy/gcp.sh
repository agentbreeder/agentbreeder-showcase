#!/usr/bin/env bash
set -euo pipefail

echo "=== AgentBreeder Showcase — GCP Deploy ==="
set -a && source .env && set +a
source venv/bin/activate

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
