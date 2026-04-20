#!/usr/bin/env bash
set -euo pipefail

echo "=== AgentBreeder Showcase — Local Deploy ==="

# Load env
set -a && source .env && set +a

# Activate venv
source venv/bin/activate

# Validate all agents first
echo "→ Validating all agent configs..."
for agent_dir in agents/*/; do
  agentbreeder validate "$agent_dir/agent.yaml" && echo "  ✓ $(basename $agent_dir)"
done

# Deploy each agent
echo "→ Deploying agents..."
for agent_dir in agents/*/; do
  agent_name=$(grep '^name:' "$agent_dir/agent.yaml" | awk '{print $2}')
  agentbreeder deploy "$agent_dir/agent.yaml" --target local
  echo "  ✓ $agent_name deployed"
done

# Verify all running
echo "→ Verifying status..."
agentbreeder status

# List registry
echo "→ Registry:"
agentbreeder list

echo ""
echo "=== All agents deployed locally ==="
echo "Run the showcase: agentbreeder orchestration run showcase"
echo "Dashboard: http://localhost:3001"
