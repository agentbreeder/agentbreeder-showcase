"""Run AgentBreeder showcase evals using the eval service API.

The eval store is in-memory per process — dataset creation and eval run
must happen in the same process. This script does both.
"""
import sys
import json
sys.path.insert(0, "/Users/rajit/agentbreeder-showcase/venv/lib/python3.12/site-packages")

from api.services.eval_service import get_eval_store

AGENTS = [
    "demo-claude-sdk",
    "demo-openai-agents",
    "demo-google-adk",
    "demo-langgraph",
    "demo-crewai",
]

ROWS = [
    {
        "input": {"message": "What are the top 3 benefits of AI agents in enterprise?"},
        "expected_output": "Three enterprise AI benefits: productivity gains (40-60% automation), cost reduction (20-35% operational savings), and revenue growth through personalization.",
        "tags": ["enterprise", "benefits"],
    },
    {
        "input": {"message": "List 3 AI use cases in healthcare"},
        "expected_output": "Healthcare AI use cases: clinical decision support, medical imaging analysis (94% accuracy), and drug discovery acceleration.",
        "tags": ["healthcare", "use-cases"],
    },
    {
        "input": {"message": "What AI implementation patterns should I know?"},
        "expected_output": "Key AI agent patterns: ReAct (reasoning + acting), Plan-and-Execute (upfront planning), and Multi-Agent Orchestration (specialized sub-agents).",
        "tags": ["technical", "patterns"],
    },
]


def run_eval_for_agent(store, dataset_id: str, agent_name: str) -> dict:
    run = store.create_run(
        agent_name=agent_name,
        dataset_id=dataset_id,
        config={"judge_model": "claude-sonnet-4-6"},
    )
    result = store.execute_run(run["id"])
    return result


def main():
    store = get_eval_store()

    # Remove seeded demo dataset to avoid confusion
    for ds in store.list_datasets():
        if ds["name"] == "customer-support-qa":
            store.delete_dataset(ds["id"])

    # Create showcase dataset
    dataset = store.create_dataset(
        name="showcase-qa",
        description="Showcase agent evaluation — enterprise AI and technical questions",
        team="showcase",
        tags=["showcase", "demo", "enterprise"],
        version="1.0.0",
    )
    dataset_id = dataset["id"]
    store.add_rows(dataset_id, ROWS)
    print(f"Dataset created: {dataset_id}")
    print(f"Rows added: {len(ROWS)}")

    # Run evals for all agents
    results = {}
    for agent_name in AGENTS:
        print(f"\nRunning eval for {agent_name}...")
        result = run_eval_for_agent(store, dataset_id, agent_name)
        summary = result.get("summary", {})
        metrics = summary.get("metrics", {})
        correctness = round(metrics.get("correctness", {}).get("mean", 0), 3)
        relevance = round(metrics.get("relevance", {}).get("mean", 0), 3)
        results[agent_name] = {
            "status": result["status"],
            "correctness": correctness,
            "relevance": relevance,
            "total_results": summary.get("total_results", 0),
        }
        print(f"  Status: {result['status']}")
        print(f"  Correctness: {correctness}")
        print(f"  Relevance: {relevance}")

    print("\n=== Eval Summary ===")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
