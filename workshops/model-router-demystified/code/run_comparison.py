# =============================================================================
# run_comparison.py — Baseline vs. Model Router evaluation driver
# =============================================================================
# Runs the full evaluation pipeline: baseline calls, router calls, judge
# scoring, and report generation.
#
# Usage:
#   python run_comparison.py --mode baseline --dataset ../sample-data/router-eval-prompts.jsonl
#   python run_comparison.py --mode router --dataset ../sample-data/router-eval-prompts.jsonl
#   python run_comparison.py --mode judge
#   python run_comparison.py --mode report --output results/baseline-vs-balanced/
# =============================================================================
import argparse
import json
import time
from pathlib import Path

from config import (
    get_router_client, get_baseline_client, get_judge_client,
    ROUTER_DEPLOYMENT, BASELINE_DEPLOYMENT, JUDGE_DEPLOYMENT,
    calculate_cost,
)

SYSTEM_PROMPT = """You are the WWI Concierge. Answer questions about travel policy 
accurately, citing specific section numbers. If something is not covered by the policy, 
say so explicitly. Be concise and precise with dollar amounts and thresholds."""

DEFAULT_OUTPUT = "results/baseline-vs-balanced"


def run_baseline(dataset_path: str, output_dir: str):
    """Send all prompts to the baseline frontier model."""
    client = get_baseline_client()
    dataset = _load_dataset(dataset_path)
    results = []

    print(f"Running baseline ({BASELINE_DEPLOYMENT}) on {len(dataset)} prompts...")
    for i, item in enumerate(dataset):
        start = time.time()
        response = client.chat.completions.create(
            model=BASELINE_DEPLOYMENT,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": item["prompt"]},
            ],
            max_tokens=500,
        )
        elapsed = time.time() - start

        result = {
            "id": item["id"],
            "prompt": item["prompt"],
            "category": item.get("category", "unknown"),
            "difficulty": item.get("difficulty", "unknown"),
            "response": response.choices[0].message.content,
            "model": response.model,
            "latency_s": round(elapsed, 3),
            "input_tokens": response.usage.prompt_tokens,
            "output_tokens": response.usage.completion_tokens,
            "cost": calculate_cost(
                BASELINE_DEPLOYMENT,
                response.usage.prompt_tokens,
                response.usage.completion_tokens,
            ),
        }
        results.append(result)
        print(f"  [{i+1}/{len(dataset)}] {item['id']} → {response.model} ({elapsed:.1f}s)")

    _save_results(results, output_dir, "baseline_responses.jsonl")
    _print_summary("Baseline", results)


def run_router(dataset_path: str, output_dir: str):
    """Send all prompts to Model Router."""
    client = get_router_client()
    dataset = _load_dataset(dataset_path)
    results = []

    print(f"Running router ({ROUTER_DEPLOYMENT}) on {len(dataset)} prompts...")
    for i, item in enumerate(dataset):
        start = time.time()
        response = client.chat.completions.create(
            model=ROUTER_DEPLOYMENT,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": item["prompt"]},
            ],
            max_tokens=500,
        )
        elapsed = time.time() - start

        # The response.model field shows which underlying model was selected
        selected_model = response.model

        result = {
            "id": item["id"],
            "prompt": item["prompt"],
            "category": item.get("category", "unknown"),
            "difficulty": item.get("difficulty", "unknown"),
            "response": response.choices[0].message.content,
            "model": selected_model,
            "latency_s": round(elapsed, 3),
            "input_tokens": response.usage.prompt_tokens,
            "output_tokens": response.usage.completion_tokens,
            "cost": calculate_cost(
                selected_model,
                response.usage.prompt_tokens,
                response.usage.completion_tokens,
            ),
        }
        results.append(result)
        print(f"  [{i+1}/{len(dataset)}] {item['id']} → {selected_model} ({elapsed:.1f}s)")

    _save_results(results, output_dir, "router_responses.jsonl")
    _print_summary("Router", results)
    _print_model_distribution(results)


def run_judge(output_dir: str):
    """Score baseline and router responses using LLM-as-a-judge."""
    client = get_judge_client()

    baseline_path = Path(output_dir) / "baseline_responses.jsonl"
    router_path = Path(output_dir) / "router_responses.jsonl"

    if not baseline_path.exists() or not router_path.exists():
        print("❌ Run baseline and router first.")
        return

    baseline = {r["id"]: r for r in _load_jsonl(baseline_path)}
    router = {r["id"]: r for r in _load_jsonl(router_path)}

    judge_prompt = """Compare these two AI responses to the same travel policy question.
Score each on a scale of 1-5 for: Accuracy, Completeness, Clarity, Helpfulness.

Question: {query}

Response A (Baseline):
{response_a}

Response B (Router):
{response_b}

Output JSON only:
{{
  "baseline": {{"accuracy": <1-5>, "completeness": <1-5>, "clarity": <1-5>, "helpfulness": <1-5>}},
  "router": {{"accuracy": <1-5>, "completeness": <1-5>, "clarity": <1-5>, "helpfulness": <1-5>}},
  "winner": "baseline" | "router" | "tie",
  "reason": "<brief justification>"
}}"""

    results = []
    ids = sorted(set(baseline.keys()) & set(router.keys()))
    print(f"Judging {len(ids)} prompt pairs...")

    for i, item_id in enumerate(ids):
        b = baseline[item_id]
        r = router[item_id]

        prompt = judge_prompt.format(
            query=b["prompt"],
            response_a=b["response"],
            response_b=r["response"],
        )

        resp = client.chat.completions.create(
            model=JUDGE_DEPLOYMENT,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            response_format={"type": "json_object"},
        )

        scores = json.loads(resp.choices[0].message.content)
        scores["id"] = item_id
        scores["category"] = b.get("category", "unknown")
        results.append(scores)
        print(f"  [{i+1}/{len(ids)}] {item_id} → winner: {scores.get('winner', '?')}")

    _save_results(results, output_dir, "judge_scores.jsonl")

    # Summary
    wins = {"baseline": 0, "router": 0, "tie": 0}
    for r in results:
        wins[r.get("winner", "tie")] += 1
    print(f"\nJudge results: Baseline={wins['baseline']}, "
          f"Router={wins['router']}, Tie={wins['tie']}")


def generate_report(output_dir: str):
    """Generate a summary report from all results."""
    baseline = _load_jsonl(Path(output_dir) / "baseline_responses.jsonl")
    router = _load_jsonl(Path(output_dir) / "router_responses.jsonl")
    judge = _load_jsonl(Path(output_dir) / "judge_scores.jsonl")

    report = {
        "baseline": {
            "avg_cost": sum(r["cost"] for r in baseline) / len(baseline),
            "avg_latency": sum(r["latency_s"] for r in baseline) / len(baseline),
            "total_prompts": len(baseline),
        },
        "router": {
            "avg_cost": sum(r["cost"] for r in router) / len(router),
            "avg_latency": sum(r["latency_s"] for r in router) / len(router),
            "total_prompts": len(router),
        },
        "comparison": {
            "cost_savings_pct": round(
                (1 - sum(r["cost"] for r in router) / sum(r["cost"] for r in baseline)) * 100, 1
            ),
            "latency_savings_pct": round(
                (1 - sum(r["latency_s"] for r in router) / sum(r["latency_s"] for r in baseline)) * 100, 1
            ),
        },
    }

    if judge:
        wins = {"baseline": 0, "router": 0, "tie": 0}
        for j in judge:
            wins[j.get("winner", "tie")] += 1
        report["judge"] = wins

    with open(Path(output_dir) / "report.json", "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n{'='*60}")
    print("COMPARISON REPORT: Baseline vs. Model Router")
    print(f"{'='*60}")
    print(f"Cost savings:    {report['comparison']['cost_savings_pct']}%")
    print(f"Latency savings: {report['comparison']['latency_savings_pct']}%")
    if judge:
        print(f"Judge results:   B={wins['baseline']} R={wins['router']} T={wins['tie']}")
    print(f"{'='*60}\n")


# --- Helpers ---

def _load_dataset(path: str) -> list:
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def _load_jsonl(path: Path) -> list:
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def _save_results(results: list, output_dir: str, filename: str):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    with open(Path(output_dir) / filename, "w") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")
    print(f"  → Saved {len(results)} results to {output_dir}/{filename}")


def _print_summary(label: str, results: list):
    avg_cost = sum(r["cost"] for r in results) / len(results)
    avg_latency = sum(r["latency_s"] for r in results) / len(results)
    print(f"\n  {label} summary:")
    print(f"    Avg cost/prompt: ${avg_cost:.4f}")
    print(f"    Avg latency:     {avg_latency:.2f}s")


def _print_model_distribution(results: list):
    """Show which models the router selected."""
    dist = {}
    for r in results:
        model = r["model"]
        dist[model] = dist.get(model, 0) + 1

    print("\n  Model distribution:")
    for model, count in sorted(dist.items(), key=lambda x: -x[1]):
        pct = count / len(results) * 100
        print(f"    {model}: {count} ({pct:.0f}%)")

    # By category
    cat_dist = {}
    for r in results:
        cat = r.get("category", "unknown")
        cat_dist.setdefault(cat, {})
        model = r["model"]
        cat_dist[cat][model] = cat_dist[cat].get(model, 0) + 1

    print("\n  Model distribution by category:")
    for cat, models in sorted(cat_dist.items()):
        top = sorted(models.items(), key=lambda x: -x[1])[:3]
        top_str = ", ".join(f"{m}={c}" for m, c in top)
        print(f"    {cat}: {top_str}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Baseline vs. Router Comparison")
    parser.add_argument("--mode", choices=["baseline", "router", "judge", "report"],
                        required=True)
    parser.add_argument("--dataset", default="../sample-data/router-eval-prompts.jsonl")
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    if args.mode == "baseline":
        run_baseline(args.dataset, args.output)
    elif args.mode == "router":
        run_router(args.dataset, args.output)
    elif args.mode == "judge":
        run_judge(args.output)
    elif args.mode == "report":
        generate_report(args.output)
