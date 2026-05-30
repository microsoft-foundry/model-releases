#!/usr/bin/env python3
"""
analyze_eval_run.py — turn a directory of eval_results_*.json files into a
narrative.json manifest the demo-replay agent can read deterministically.

USAGE
    python analyze_eval_run.py <data_dir>

INPUTS expected in <data_dir>:
    eval_results_v1-curated.json   (DEMO 1, 20-row baseline)
    eval_results_v1-demo.json      (DEMO 2, 50-row baseline)
    eval_results_v2-demo.json      (DEMO 2/3, multi-model)
    eval_results_v3-demo.json      (DEMO 4, after fine-tune)

OUTPUT
    <data_dir>/narrative.json — dict keyed by run label with computed
    quality / cost / latency / policy + Δ vs v1-demo + target flags +
    a content hash so the agent knows when to re-render.

The numbers come from the JSONs only. No invented values.
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

# Per-1K-token prices (mirrors workshops/foundry-models-e2e/code/s02_config.py PRICE)
PRICE = {
    "planner-gpt41":     {"in": 0.0050, "out": 0.0150},
    "router-nano":       {"in": 0.0002, "out": 0.0006},
    "mini-vision":       {"in": 0.0008, "out": 0.0024},
    "policy-mini-base":  {"in": 0.0008, "out": 0.0024},
    "policy-mini-ft":    {"in": 0.0010, "out": 0.0030},
    "auto-router":       {"in": 0.0008, "out": 0.0024},
}

# Default targets — overridden by `targets` in an existing narrative.json
# in the same data_dir, so learner edits to the manifest persist across re-runs.
DEFAULT_TARGETS = {"quality": 0.80, "cost": 0.008, "latency": 15.0, "policy": 0.80}
TARGETS = dict(DEFAULT_TARGETS)  # mutated in main() if existing manifest found

# Files we know about and the slot they fill in the narrative
RUN_FILES = {
    "v1-curated": "eval_results_v1-curated.json",  # 20-row baseline
    "v1-demo":    "eval_results_v1-demo.json",     # 50-row baseline
    "v2-demo":    "eval_results_v2-demo.json",     # 50-row multi-model
    "v3-demo":    "eval_results_v3-demo.json",     # 50-row after FT
}


def _safe_mean(values: list[float]) -> float | None:
    nums = [v for v in values if v is not None and not (isinstance(v, float) and math.isnan(v))]
    if not nums:
        return None
    return sum(nums) / len(nums)


def _row_cost_usd(usage_json: str) -> float | None:
    """outputs.usage_json looks like '{"planner-gpt41": [1847, 624]}'."""
    if not usage_json:
        return None
    try:
        usage = json.loads(usage_json)
    except (TypeError, ValueError):
        return None
    if not isinstance(usage, dict) or not usage:
        return None
    total = 0.0
    for deploy, tokens in usage.items():
        if not isinstance(tokens, (list, tuple)) or len(tokens) != 2:
            continue
        in_tok, out_tok = tokens
        price = PRICE.get(deploy)
        if not price:
            continue
        total += (in_tok / 1000.0) * price["in"] + (out_tok / 1000.0) * price["out"]
    return total if total > 0 else None


def _analyze_run(path: Path) -> dict[str, Any]:
    raw = json.loads(path.read_text())
    rows = raw.get("rows", [])
    metrics = raw.get("metrics", {}) or {}

    judge_score = metrics.get("judge.judge_score")
    schema_score = metrics.get("schema.schema_score")
    policy_score = metrics.get("policy.policy_adherence_score")
    policy_applicable = metrics.get("policy.applicable")

    latencies = [r.get("outputs.latency_s") for r in rows]
    avg_latency = _safe_mean([float(x) for x in latencies if x is not None])

    costs = [_row_cost_usd(r.get("outputs.usage_json", "")) for r in rows]
    avg_cost = _safe_mean([c for c in costs if c is not None])

    return {
        "source_file": path.name,
        "n_rows": len(rows),
        "judge_score": judge_score,
        "schema_score": schema_score,
        "quality": judge_score,  # primary headline metric = LLM judge
        "latency_s": avg_latency,
        "cost_usd": avg_cost,
        "policy_score": policy_score,
        "policy_applicable_frac": policy_applicable,
        "studio_url": raw.get("studio_url"),
    }


def _delta(curr: float | None, base: float | None) -> dict[str, Any] | None:
    if curr is None or base is None:
        return None
    abs_d = curr - base
    pct = (abs_d / base * 100.0) if base else None
    return {"abs": abs_d, "pct": pct}


def _flags(run: dict[str, Any]) -> dict[str, str]:
    """Return target_status per metric: 'green' | 'amber' | 'red' | 'na'."""
    out: dict[str, str] = {}
    q = run.get("quality")
    out["quality"] = (
        "na" if q is None
        else "green" if q >= TARGETS["quality"]
        else "amber" if q >= 0.75
        else "red"
    )
    c = run.get("cost_usd")
    out["cost"] = (
        "na" if c is None
        else "green" if c <= TARGETS["cost"]
        else "amber" if c <= TARGETS["cost"] * 1.25
        else "red"
    )
    lat = run.get("latency_s")
    out["latency"] = (
        "na" if lat is None
        else "green" if lat <= TARGETS["latency"]
        else "amber" if lat <= TARGETS["latency"] * 1.25
        else "red"
    )
    p = run.get("policy_score")
    out["policy"] = (
        "na" if p is None
        else "green" if p >= TARGETS["policy"]
        else "amber" if p >= 0.50
        else "red"
    )
    return out


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    data_dir = Path(sys.argv[1]).resolve()
    if not data_dir.is_dir():
        print(f"ERROR: not a directory: {data_dir}", file=sys.stderr)
        return 1

    # Preserve user-edited targets from a prior narrative.json if present.
    existing_path = data_dir / "narrative.json"
    if existing_path.exists():
        try:
            existing = json.loads(existing_path.read_text())
            prior = existing.get("targets") or {}
            for k in TARGETS:
                if k in prior and isinstance(prior[k], (int, float)):
                    TARGETS[k] = float(prior[k])
        except (ValueError, OSError):
            pass

    runs: dict[str, Any] = {}
    hasher = hashlib.sha256()
    for label, fname in RUN_FILES.items():
        path = data_dir / fname
        if not path.exists():
            runs[label] = {"missing": True, "source_file": fname}
            continue
        runs[label] = _analyze_run(path)
        hasher.update(path.read_bytes())

    # Δ vs v1-demo (50-row baseline) — the main comparison axis
    base = runs.get("v1-demo")
    for label, run in runs.items():
        if run.get("missing"):
            continue
        if label == "v1-demo" or base is None or base.get("missing"):
            run["delta_vs_v1"] = None
        else:
            run["delta_vs_v1"] = {
                "quality":   _delta(run.get("quality"),      base.get("quality")),
                "cost":      _delta(run.get("cost_usd"),     base.get("cost_usd")),
                "latency":   _delta(run.get("latency_s"),    base.get("latency_s")),
                "policy":    _delta(run.get("policy_score"), base.get("policy_score")),
            }
        run["target_status"] = _flags(run)

    manifest = {
        "version": 1,
        "data_dir": str(data_dir),
        "content_hash": hasher.hexdigest(),
        "targets": TARGETS,
        "price_table": PRICE,
        "runs": runs,
    }
    out_path = data_dir / "narrative.json"
    out_path.write_text(json.dumps(manifest, indent=2))
    print(f"Wrote {out_path}")

    # Brief summary to stdout — easy to eyeball
    print("\nSummary:")
    print(f"  {'label':12s}  {'n':>3s}  {'quality':>7s}  {'cost':>8s}  {'latency':>8s}  {'policy':>7s}")
    for label, run in runs.items():
        if run.get("missing"):
            print(f"  {label:12s}  MISSING ({run['source_file']})")
            continue
        q   = run.get("quality")
        c   = run.get("cost_usd")
        lat = run.get("latency_s")
        p   = run.get("policy_score")
        q_s = f"{q:.3f}"   if q   is not None else "   na  "
        c_s = f"${c:.4f}"  if c   is not None else "    na  "
        l_s = f"{lat:5.2f}s" if lat is not None else "    na  "
        p_s = f"{p:.3f}"   if p   is not None else "   na  "
        print(f"  {label:12s}  {run['n_rows']:>3d}  {q_s:>7s}  {c_s:>8s}  {l_s:>8s}  {p_s:>7s}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
