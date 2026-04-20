#!/usr/bin/env bash
set -euo pipefail

echo "=== AgentBreeder Showcase — AWS Deploy ==="
set -a && source .env && set +a
source venv/bin/activate

# Validate all agent configs before deploying
echo "→ Validating all agent configs..."
for agent_dir in agents/*/; do
  agentbreeder validate "$agent_dir/agent.yaml" && echo "  ✓ $(basename $agent_dir)"
done

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
