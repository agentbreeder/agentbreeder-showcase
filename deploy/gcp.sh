#!/usr/bin/env bash
set -euo pipefail

echo "=== AgentBreeder Showcase — GCP Deploy ==="
set -a && source .env && set +a
source venv/bin/activate

# Docker socket fix for macOS Docker Desktop
export DOCKER_HOST=unix://"$HOME/.docker/run/docker.sock"

# Prerequisites check
: "${GOOGLE_CLOUD_PROJECT:?GOOGLE_CLOUD_PROJECT not set in .env}"
: "${GOOGLE_CLOUD_REGION:?GOOGLE_CLOUD_REGION not set in .env}"

# Validate all agent configs before deploying
echo "→ Validating all agent configs..."
for agent_dir in agents/*/; do
  agentbreeder validate "$agent_dir/agent.yaml" && echo "  ✓ $(basename $agent_dir)"
done

# Ensure Docker credential helper is available
if ! which docker-credential-gcloud &>/dev/null; then
  ln -sf "$(find ~/google-cloud-sdk /opt/homebrew -name docker-credential-gcloud 2>/dev/null | head -1)" /usr/local/bin/docker-credential-gcloud
fi
gcloud auth configure-docker "${GOOGLE_CLOUD_REGION}-docker.pkg.dev" --quiet

# Store secrets in GCP Secret Manager (--prefix "" avoids invalid name format)
echo "→ Storing secrets in GCP Secret Manager..."
agentbreeder secret set ANTHROPIC_API_KEY --value "$ANTHROPIC_API_KEY" --backend gcp --prefix ""
agentbreeder secret set OPENAI_API_KEY --value "$OPENAI_API_KEY" --backend gcp --prefix ""
agentbreeder secret set GOOGLE_API_KEY --value "$GOOGLE_API_KEY" --backend gcp --prefix ""

# Deploy all agents to Cloud Run
for agent_dir in agents/*/; do
  agent_name=$(grep '^name:' "$agent_dir/agent.yaml" | awk '{print $2}')
  echo "  → Deploying $agent_name..."
  agentbreeder deploy "$agent_dir/agent.yaml" --target gcp
  echo "  ✓ $agent_name → GCP Cloud Run"
done

agentbreeder status
echo ""
echo "=== GCP deployment complete ==="
echo "Run evals: agentbreeder eval run --scorer semantic"
