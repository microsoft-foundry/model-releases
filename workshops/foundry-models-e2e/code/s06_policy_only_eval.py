# =============================================================================
# s06_policy_only_eval.py — Isolated policy-QA evaluator (Step 6 payoff)
# =============================================================================
# NARRATIVE ROLE
# s05_run_eval.py scores the END-TO-END agent's JSON, which dilutes the
# improvement contributed by any single sub-model. To show the *real*
# lift from fine-tuning, we strip the planner out and evaluate the
# policy model directly against the policy doc.
#
# DETERMINISTIC EVALUATOR
# Each row in eval-policy-only.jsonl has expected_constraints:
#   must_cite_section: e.g. "4.2"
#   must_mention:      e.g. "$25/day"   (substring match, case-insensitive)
#   must_say:          e.g. "no"        (substring match, case-insensitive)
# A row passes (score=1.0) iff every present constraint is satisfied.
# No LLM judge needed → reproducible, zero judge cost.
#
# WHAT WE PRINT
# Side-by-side scorecards for policy-mini-base and policy-mini-ft on the
# same 35 rows, so the FT lift is impossible to misread.
# =============================================================================
import json
import time
from pathlib import Path

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.ai.projects import AIProjectClient
from openai import AzureOpenAI

from s02_config import (
    PROJECT_ENDPOINT, DEPLOY_POLICY_BASE, DEPLOY_POLICY_FT,
)
from s05_multi_model_agent import _AOAI_ENDPOINT  # reuse direct AOAI endpoint
from s02_scorecard import print_scorecard

EVAL_PATH = Path(__file__).parent.parent / "sample-data" / "eval-policy-only.jsonl"
POLICY_DOC = Path(__file__).parent.parent / "sample-data" / "travel-policy.md"

SYSTEM = (
    "You answer WWI policy questions. Be concise. "
    "Always cite the relevant policy section number (e.g. 'Section 4.2'). "
    "Quote specific amounts/limits where applicable."
)


def _check(answer: str, constraints: dict) -> tuple[bool, list[str]]:
    """Return (passed, failure_reasons)."""
    a = (answer or "").lower()
    fails = []
    if (sec := constraints.get("must_cite_section")):
        if sec.lower() not in a:
            fails.append(f"missing section {sec}")
    if (mention := constraints.get("must_mention")):
        if str(mention).lower() not in a:
            fails.append(f"missing '{mention}'")
    if (say := constraints.get("must_say")):
        if str(say).lower() not in a:
            fails.append(f"missing '{say}'")
    return (len(fails) == 0, fails)


def _eval_one(client, model: str, rows: list[dict]) -> dict:
    """Run all rows through one model; return aggregated metrics."""
    print(f"\n--- {model} ---")
    scores, lats, fail_samples = [], [], []
    tin_total, tout_total = 0, 0

    for i, row in enumerate(rows, 1):
        t0 = time.time()
        try:
            r = client.chat.completions.create(
                model=model,
                temperature=0,
                messages=[
                    {"role": "system", "content": SYSTEM},
                    {"role": "user",   "content": row["input"]},
                ],
            )
            ans = r.choices[0].message.content or ""
            tin_total  += getattr(r.usage, "prompt_tokens",     0)
            tout_total += getattr(r.usage, "completion_tokens", 0)
        except Exception as e:
            ans = ""
            print(f"  [{i}/{len(rows)}] {row['id']} ERROR: {e}")
        lat = time.time() - t0
        lats.append(lat)
        passed, fails = _check(ans, row.get("expected_constraints", {}))
        scores.append(1.0 if passed else 0.0)
        mark = "✅" if passed else "❌"
        print(f"  [{i}/{len(rows)}] {row['id']} {mark} lat={lat:.1f}s "
              f"{('  '+'; '.join(fails)) if fails else ''}")
        if not passed and len(fail_samples) < 3:
            fail_samples.append({"id": row["id"], "q": row["input"],
                                 "a": ans[:200], "fails": fails})

    n = len(rows)
    quality = sum(scores) / n if n else 0.0
    p50 = sorted(lats)[n // 2] if lats else 0.0
    # mini pricing: $0.0008/1K in, $0.0024/1K out  (per s02_config.PRICE)
    cost_per = (tin_total * 0.0008 + tout_total * 0.0024) / 1000 / n
    return {"model": model, "quality": quality, "cost": cost_per,
            "latency_p50": p50, "n": n, "fail_samples": fail_samples}


def main() -> None:
    rows = [json.loads(l) for l in open(EVAL_PATH)]
    print(f"Loaded {len(rows)} policy-only rows from {EVAL_PATH.name}")

    # Base client → project endpoint; FT client → direct AOAI endpoint
    project = AIProjectClient(
        endpoint=PROJECT_ENDPOINT, credential=DefaultAzureCredential())
    base_client = project.get_openai_client()

    ft_client = AzureOpenAI(
        azure_endpoint=_AOAI_ENDPOINT,
        azure_ad_token_provider=get_bearer_token_provider(
            DefaultAzureCredential(),
            "https://cognitiveservices.azure.com/.default"),
        api_version="2025-01-01-preview",
    )

    base = _eval_one(base_client, DEPLOY_POLICY_BASE, rows)
    ft   = _eval_one(ft_client,   DEPLOY_POLICY_FT,   rows)

    print("\n" + "=" * 60)
    print_scorecard(DEPLOY_POLICY_BASE, base["quality"], base["cost"], base["latency_p50"])
    print_scorecard(DEPLOY_POLICY_FT,   ft["quality"],   ft["cost"],   ft["latency_p50"],
                    baseline={"quality":  base["quality"],
                              "cost":     base["cost"],
                              "latency":  base["latency_p50"]})

    delta = ft["quality"] - base["quality"]
    rel   = (delta / base["quality"] * 100) if base["quality"] else float("inf")
    print(f"\n  ΔQuality:  {base['quality']:.2f} → {ft['quality']:.2f}  "
          f"(+{delta:.2f} abs, +{rel:.0f}% rel)")

    out = {"base": base, "ft": ft, "delta_abs": delta, "delta_rel_pct": rel}
    out_path = Path(__file__).parent / "generated" / "eval_results_policy-isolated.json"
    out_path.parent.mkdir(exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nResults saved to {out_path.name}")


if __name__ == "__main__":
    main()
