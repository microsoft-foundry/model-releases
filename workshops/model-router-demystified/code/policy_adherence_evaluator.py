# =============================================================================
# policy_adherence_evaluator.py — Adaptive eval-rubric evaluator for WWI
# =============================================================================
# Implements the Policy-Adherence evaluator using Foundry's Adaptive Evals
# framework. Loads the eval-rubric YAML, applies adaptive weight rules based
# on question category, and scores responses via a prompt-based LLM judge.
#
# Usage:
#   python policy_adherence_evaluator.py --action create     # Register with Foundry
#   python policy_adherence_evaluator.py --action evaluate   # Run evaluation
#   python policy_adherence_evaluator.py --action report     # Generate report
# =============================================================================
import argparse
import json
import yaml
from pathlib import Path

from config import get_judge_client, JUDGE_DEPLOYMENT, PROJECT_ENDPOINT

RUBRIC_PATH = Path(__file__).parent / "eval-rubric-policy-adherence.yaml"
POLICY_PATH = Path(__file__).parent.parent / "sample-data" / "travel-policy.md"

# The judge prompt template — instructs an LLM to score each response
JUDGE_PROMPT_TEMPLATE = """You are evaluating an AI travel assistant's response against WWI's official policy.

## Policy Document (ground truth):
{ground_truth}

## User Question:
{query}

## AI Response to Evaluate:
{response}

## Scoring Rubric

Score each criterion from 1 (worst) to 5 (best):

### 1. Rule Accuracy (Does it cite the RIGHT rule?)
- 5: Cites the exact correct policy section and rule
- 4: Correct rule, minor section reference error
- 3: Partially correct — misses a related rule that applies
- 2: Cites a wrong rule or conflates two different rules
- 1: Completely wrong rule or no policy reference at all

### 2. Completeness (Are ALL conditions mentioned?)
- 5: All conditions, exceptions, and approval requirements included
- 4: Missing one minor condition that rarely applies
- 3: Missing a significant condition (e.g., approval threshold)
- 2: Only mentions the base rule, ignores exceptions entirely
- 1: Answer is a fragment with no useful policy detail

### 3. Boundary Precision (Are numbers EXACT?)
- 5: All dollar amounts, day counts, percentages match the policy exactly
- 4: One number is approximate but within 5% of correct
- 3: One number is wrong or a threshold is described vaguely ("a few days")
- 2: Multiple numbers are wrong or fabricated
- 1: No specific numbers given when the policy has them

### 4. Hallucination Absence (Does it AVOID making things up?)
- 5: Every claim is traceable to the policy document — nothing invented
- 4: One minor implication that's reasonable but not stated in policy
- 3: One fabricated rule or limit that sounds plausible but isn't in the policy
- 2: Multiple invented rules mixed with real ones
- 1: Largely fabricated response with minimal basis in the actual policy

Output Format (JSON only, no other text):
{{
  "rule_accuracy": <integer 1-5>,
  "completeness": <integer 1-5>,
  "boundary_precision": <integer 1-5>,
  "hallucination_absence": <integer 1-5>,
  "reason": "<2-3 sentence justification>"
}}"""


def load_rubric() -> dict:
    """Load the eval-rubric YAML."""
    with open(RUBRIC_PATH) as f:
        return yaml.safe_load(f)


def load_policy() -> str:
    """Load the WWI policy document."""
    with open(POLICY_PATH) as f:
        return f.read()


def get_adaptive_weights(rubric: dict, category: str) -> dict:
    """Apply adaptive rules to get context-specific weights."""
    # Start with default weights
    weights = {c["id"]: c["weight"] for c in rubric["criteria"]}

    # Apply adaptive rules
    for rule in rubric.get("adaptive_rules", []):
        condition = rule["condition"]
        # Safe evaluation of condition against input category
        if _eval_condition(condition, category):
            weights.update(rule["adjust_weights"])
            break  # First matching rule wins

    return weights


def _eval_condition(condition: str, category: str) -> bool:
    """Safely evaluate an adaptive rule condition."""
    # Replace input.category with the actual category value
    check = condition.replace("input.category", f"'{category}'")
    try:
        return eval(check, {"__builtins__": {}}, {})
    except Exception:
        return False


def score_response(query: str, response: str, ground_truth: str,
                   category: str, rubric: dict) -> dict:
    """Score a single response using the LLM judge + adaptive rubric."""
    client = get_judge_client()

    # Build the judge prompt
    prompt = JUDGE_PROMPT_TEMPLATE.format(
        ground_truth=ground_truth,
        query=query,
        response=response,
    )

    # Call the judge
    judge_response = client.chat.completions.create(
        model=JUDGE_DEPLOYMENT,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        response_format={"type": "json_object"},
    )

    # Parse scores
    scores = json.loads(judge_response.choices[0].message.content)

    # Apply adaptive weights
    weights = get_adaptive_weights(rubric, category)

    # Calculate weighted average
    weighted_sum = sum(
        scores.get(criterion_id, 3) * weight
        for criterion_id, weight in weights.items()
    )
    scores["result"] = round(weighted_sum, 2)
    scores["weights_applied"] = weights
    scores["category"] = category

    return scores


def evaluate_dataset(dataset_path: str, responses_path: str, rubric: dict) -> list:
    """Evaluate a full dataset of responses."""
    policy = load_policy()

    with open(dataset_path) as f:
        dataset = [json.loads(line) for line in f if line.strip()]

    with open(responses_path) as f:
        responses = [json.loads(line) for line in f if line.strip()]

    # Match by ID
    response_map = {r["id"]: r["response"] for r in responses}

    results = []
    for item in dataset:
        response_text = response_map.get(item["id"], "")
        if not response_text:
            continue

        score = score_response(
            query=item["prompt"],
            response=response_text,
            ground_truth=item.get("ground_truth", policy),
            category=item.get("category", "general"),
            rubric=rubric,
        )
        score["id"] = item["id"]
        results.append(score)
        print(f"  [{item['id']}] result={score['result']:.2f} "
              f"(rule={score.get('rule_accuracy')}, "
              f"complete={score.get('completeness')}, "
              f"precision={score.get('boundary_precision')}, "
              f"halluc={score.get('hallucination_absence')})")

    return results


def create_evaluator_in_foundry(rubric: dict):
    """Register the evaluator in Foundry's evaluator catalog via SDK."""
    from azure.identity import DefaultAzureCredential
    from azure.ai.projects import AIProjectClient

    client = AIProjectClient(
        endpoint=PROJECT_ENDPOINT,
        credential=DefaultAzureCredential(),
    )
    openai_client = client.get_openai_client()

    # Build the prompt text from our template
    prompt_text = JUDGE_PROMPT_TEMPLATE.replace("{ground_truth}", "{{ground_truth}}")
    prompt_text = prompt_text.replace("{query}", "{{query}}")
    prompt_text = prompt_text.replace("{response}", "{{response}}")

    evaluator = client.beta.evaluators.create_version(
        name="wwi_policy_adherence",
        evaluator_version={
            "name": "wwi_policy_adherence",
            "categories": ["quality"],
            "display_name": "WWI Policy Adherence (Adaptive Rubric)",
            "description": rubric["description"],
            "definition": {
                "type": "prompt",
                "prompt_text": prompt_text,
                "init_parameters": {
                    "type": "object",
                    "properties": {
                        "deployment_name": {"type": "string"},
                        "threshold": {"type": "number"},
                    },
                    "required": ["deployment_name", "threshold"],
                },
                "data_schema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "response": {"type": "string"},
                        "ground_truth": {"type": "string"},
                    },
                    "required": ["query", "response", "ground_truth"],
                },
                "metrics": {
                    "custom_prompt": {
                        "type": "ordinal",
                        "desirable_direction": "increase",
                        "min_value": 1,
                        "max_value": 5,
                    }
                },
            },
        },
    )
    print(f"✅ Evaluator registered: {evaluator}")


def generate_report(results: list, output_dir: str = "results/policy-adherence/"):
    """Generate a summary report from evaluation results."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Overall averages
    avg_result = sum(r["result"] for r in results) / len(results)
    avg_rule = sum(r.get("rule_accuracy", 0) for r in results) / len(results)
    avg_complete = sum(r.get("completeness", 0) for r in results) / len(results)
    avg_precision = sum(r.get("boundary_precision", 0) for r in results) / len(results)
    avg_halluc = sum(r.get("hallucination_absence", 0) for r in results) / len(results)

    # By category
    by_category = {}
    for r in results:
        cat = r.get("category", "unknown")
        by_category.setdefault(cat, []).append(r["result"])

    report = {
        "total_items": len(results),
        "overall": {
            "weighted_average": round(avg_result, 2),
            "rule_accuracy": round(avg_rule, 2),
            "completeness": round(avg_complete, 2),
            "boundary_precision": round(avg_precision, 2),
            "hallucination_absence": round(avg_halluc, 2),
        },
        "by_category": {
            cat: round(sum(scores) / len(scores), 2)
            for cat, scores in by_category.items()
        },
        "pass_rate": round(
            sum(1 for r in results if r["result"] >= 3.5) / len(results), 2
        ),
    }

    with open(Path(output_dir) / "report.json", "w") as f:
        json.dump(report, f, indent=2)

    # Print summary
    print(f"\n{'='*60}")
    print(f"POLICY-ADHERENCE EVALUATION REPORT")
    print(f"{'='*60}")
    print(f"Items evaluated:    {report['total_items']}")
    print(f"Overall score:      {report['overall']['weighted_average']}/5.0")
    print(f"Pass rate (≥3.5):   {report['pass_rate']*100:.0f}%")
    print(f"\nPer-criterion averages:")
    print(f"  Rule accuracy:       {report['overall']['rule_accuracy']}/5")
    print(f"  Completeness:        {report['overall']['completeness']}/5")
    print(f"  Boundary precision:  {report['overall']['boundary_precision']}/5")
    print(f"  Hallucination absence: {report['overall']['hallucination_absence']}/5")
    print(f"\nBy category:")
    for cat, score in sorted(report["by_category"].items()):
        print(f"  {cat}: {score}/5")
    print(f"{'='*60}\n")

    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Policy-Adherence Adaptive Evaluator")
    parser.add_argument("--action", choices=["create", "evaluate", "report"],
                        required=True, help="Action to perform")
    parser.add_argument("--dataset", default="sample-data/policy-eval-dataset.jsonl")
    parser.add_argument("--responses-baseline", default=None)
    parser.add_argument("--responses-router", default=None)
    parser.add_argument("--output-dir", default="results/policy-adherence/")
    args = parser.parse_args()

    rubric = load_rubric()

    if args.action == "create":
        create_evaluator_in_foundry(rubric)

    elif args.action == "evaluate":
        if args.responses_baseline:
            print("\n--- Evaluating BASELINE responses ---")
            baseline_results = evaluate_dataset(
                args.dataset, args.responses_baseline, rubric)
            with open(Path(args.output_dir) / "baseline_scores.jsonl", "w") as f:
                for r in baseline_results:
                    f.write(json.dumps(r) + "\n")

        if args.responses_router:
            print("\n--- Evaluating ROUTER responses ---")
            router_results = evaluate_dataset(
                args.dataset, args.responses_router, rubric)
            with open(Path(args.output_dir) / "router_scores.jsonl", "w") as f:
                for r in router_results:
                    f.write(json.dumps(r) + "\n")

    elif args.action == "report":
        # Load most recent results
        results_file = Path(args.output_dir) / "router_scores.jsonl"
        if not results_file.exists():
            results_file = Path(args.output_dir) / "baseline_scores.jsonl"
        with open(results_file) as f:
            results = [json.loads(line) for line in f if line.strip()]
        generate_report(results, args.output_dir)
