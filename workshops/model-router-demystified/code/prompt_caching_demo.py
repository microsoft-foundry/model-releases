# =============================================================================
# prompt_caching_demo.py — Measure prompt caching benefits with Model Router
# =============================================================================
# Demonstrates how prompt caching works with Model Router and measures
# the latency/cost benefits of a cache-friendly system prompt design.
#
# Usage:
#   python prompt_caching_demo.py --mode measure
#   python prompt_caching_demo.py --mode no-subset
#   python prompt_caching_demo.py --mode subset --models "gpt-5,gpt-5-mini,gpt-5-nano"
# =============================================================================
import argparse
import json
import time
from pathlib import Path

from config import get_router_client, ROUTER_DEPLOYMENT

POLICY_PATH = Path(__file__).parent.parent / "sample-data" / "travel-policy.md"

# Policy questions to send repeatedly (all use the same system prompt prefix)
CACHE_TEST_QUESTIONS = [
    "What is the daily meal per-diem for domestic travel?",
    "Is valet parking reimbursable?",
    "What's the max hotel rate in a Tier 2 city?",
    "Can I fly premium economy on a 5-hour flight?",
    "What's the receipt submission deadline?",
    "Is in-flight Wi-Fi reimbursable on a 1-hour flight?",
    "What's the per-trip budget cap for a 2-night domestic trip?",
    "Can I use a luxury rental car?",
    "Who approves expenses over 15% above cap?",
    "Is hotel Wi-Fi reimbursable?",
    "What's the alcohol reimbursement policy?",
    "Can I book first class for a 10-hour flight?",
    "What's the international per-diem?",
    "What counts as client entertainment?",
    "Is personal travel insurance reimbursable?",
    "What's the advance booking window for international trips?",
    "Can I submit a receipt after 45 days?",
    "What's the Tier 1 hotel nightly max?",
    "Is minibar reimbursable?",
    "What carrier selection rules apply?",
]


def load_system_prompt() -> str:
    """Load the cache-friendly system prompt with full policy document."""
    with open(POLICY_PATH) as f:
        policy = f.read()

    return f"""You are the WWI Concierge. Answer questions about travel policy accurately.
Always cite the specific section number from the policy when applicable.
If something is not covered by the policy, say so explicitly.
Be concise — answer in 2-3 sentences maximum.

## WWI Policy (reference document):
{policy}
"""


def measure_caching(questions: list = None, label: str = "default"):
    """Send repeated questions and measure caching behavior."""
    client = get_router_client()
    system_prompt = load_system_prompt()
    questions = questions or CACHE_TEST_QUESTIONS

    print(f"\n{'='*60}")
    print(f"PROMPT CACHING MEASUREMENT ({label})")
    print(f"{'='*60}")
    print(f"System prompt length: ~{len(system_prompt.split())} words")
    print(f"Questions to send: {len(questions)}")
    print(f"{'='*60}\n")

    results = []
    for i, question in enumerate(questions):
        start = time.time()
        response = client.chat.completions.create(
            model=ROUTER_DEPLOYMENT,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question},
            ],
            max_tokens=150,
        )
        elapsed = time.time() - start

        # Check for cached tokens in usage
        usage = response.usage
        cached = getattr(usage, "cached_tokens", None) or getattr(
            usage, "prompt_tokens_details", {}
        )
        if hasattr(cached, "cached_tokens"):
            cached_tokens = cached.cached_tokens
        elif isinstance(cached, dict):
            cached_tokens = cached.get("cached_tokens", 0)
        else:
            cached_tokens = 0

        result = {
            "question_idx": i,
            "question": question[:50],
            "model": response.model,
            "latency_s": round(elapsed, 3),
            "input_tokens": usage.prompt_tokens,
            "output_tokens": usage.completion_tokens,
            "cached_tokens": cached_tokens,
            "cache_hit": cached_tokens > 0,
        }
        results.append(result)

        cache_indicator = "🟢 CACHED" if result["cache_hit"] else "⚪ miss"
        print(f"  [{i+1:2d}] {cache_indicator} | model={response.model:<15} | "
              f"latency={elapsed:.2f}s | cached={cached_tokens}")

    # Summary
    cache_hits = sum(1 for r in results if r["cache_hit"])
    avg_latency_cached = (
        sum(r["latency_s"] for r in results if r["cache_hit"]) / max(cache_hits, 1)
    )
    avg_latency_miss = (
        sum(r["latency_s"] for r in results if not r["cache_hit"])
        / max(len(results) - cache_hits, 1)
    )

    # Model consistency (same model = more cache hits)
    models_used = set(r["model"] for r in results)

    print(f"\n{'='*60}")
    print(f"RESULTS SUMMARY ({label})")
    print(f"{'='*60}")
    print(f"Cache hit rate:     {cache_hits}/{len(results)} ({cache_hits/len(results)*100:.0f}%)")
    print(f"Avg latency (hit):  {avg_latency_cached:.2f}s")
    print(f"Avg latency (miss): {avg_latency_miss:.2f}s")
    print(f"Latency savings:    {(1 - avg_latency_cached/max(avg_latency_miss, 0.01))*100:.0f}% on cache hits")
    print(f"Unique models used: {len(models_used)} ({', '.join(sorted(models_used))})")
    print(f"{'='*60}\n")

    # Save results
    output_dir = Path("results") / f"caching-{label}"
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "results.jsonl", "w") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prompt Caching Demo")
    parser.add_argument("--mode", choices=["measure", "no-subset", "subset"],
                        default="measure")
    parser.add_argument("--models", default=None,
                        help="Comma-separated model subset for 'subset' mode")
    args = parser.parse_args()

    if args.mode == "measure":
        measure_caching(label="default")
    elif args.mode == "no-subset":
        print("Running WITHOUT model subset (all models eligible)...")
        print("NOTE: Lower cache hit rate expected — router may pick different models")
        measure_caching(label="no-subset")
    elif args.mode == "subset":
        models = args.models or "gpt-5,gpt-5-mini,gpt-5-nano"
        print(f"Running WITH model subset: {models}")
        print("NOTE: Higher cache hit rate expected — fewer models = more consistency")
        print(f"⚠️  Ensure your router deployment is configured with this subset")
        measure_caching(label=f"subset-{models.replace(',', '-')}")
