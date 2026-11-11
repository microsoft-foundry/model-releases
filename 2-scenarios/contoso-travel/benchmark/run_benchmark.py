#!/usr/bin/env python3
"""
run_benchmark.py — establish a baseline scorecard for the Contoso Travel
Concierge against a Foundry prompt agent or a Model Router deployment.

For each query it records the underlying model the router selected
(`response.model`), latency, and token usage, then applies a deterministic,
reproducible grade from the `expected` fields in queries.json. Use it to set a
baseline before hill climbing; use the Foundry custom rubric evaluator
(evaluators/policy-rubric.md) for the nuanced, optimizer-driven scoring.

Auth: `az login` (DefaultAzureCredential). No API key is read here.

Env:
  MICROSOFT_FOUNDRY_ENDPOINT      project endpoint
                                  (https://<res>.services.ai.azure.com/api/projects/<project>)
  AGENT_NAME                      a deployed prompt agent (preferred), OR
  AZURE_MODEL_ROUTER_DEPLOYMENT   a model-router deployment name (fallback)

Usage:
  python run_benchmark.py                    # run all queries, write results.json
  python run_benchmark.py --limit 5          # smoke test
  python run_benchmark.py --export-jsonl ds.jsonl   # emit optimizer dataset
"""
from __future__ import annotations

import argparse
import json
import os
import re
import statistics
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def norm(text: str) -> str:
    """Lowercase and strip thousands separators so '6,300' matches '6300'."""
    return re.sub(r"(?<=\d),(?=\d)", "", (text or "").lower())


def extract_json_block(text: str) -> dict | None:
    """Best-effort parse of the first {...} JSON object in the response."""
    for match in re.finditer(r"\{.*?\}", text or "", re.DOTALL):
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            continue
    return None


def grade(query: dict, response_text: str) -> tuple[bool, list[str]]:
    """Deterministic pass/fail against the query's expected fields.

    Returns (passed, reasons_for_failure). A missing signal fails closed so the
    baseline is honest about gaps.
    """
    exp = query.get("expected", {})
    text = norm(response_text)
    block = extract_json_block(response_text) or {}
    fails: list[str] = []

    for needle in exp.get("answer_contains", []):
        if norm(needle) not in text:
            fails.append(f"missing phrase '{needle}'")

    if "compliant" in exp:
        verdict = (block.get("compliance") or {}).get("compliant")
        if verdict is None:  # fall back to prose
            if "not compliant" in text or "non-compliant" in text or "isn't compliant" in text:
                verdict = False
            elif "compliant" in text:
                verdict = True
        if verdict is not exp["compliant"]:
            fails.append(f"compliance verdict {verdict} != {exp['compliant']}")

    for needle in exp.get("reason_contains", []):
        if norm(needle) not in text:
            fails.append(f"missing reason '{needle}'")

    if exp.get("must_refuse_booking"):
        if re.search(r"\b(booked|reserved|confirmed your|i have booked|approved)\b", text):
            fails.append("claimed to book/approve")

    if exp.get("should_decline"):
        if not re.search(r"\b(no|not|couldn't|cannot|no match|nothing)\b", text):
            fails.append("did not decline ungrounded request")

    for bad in exp.get("forbidden_ids", []):
        rec = block.get("recommendation") or {}
        if bad in rec.values():
            fails.append(f"recommended forbidden id {bad}")

    if exp.get("approver"):
        if norm(exp["approver"]) not in text:
            fails.append(f"missing approver {exp['approver']}")

    return (len(fails) == 0, fails)


def build_client():
    """Return (call_fn, mode). call_fn(text_or_turns) -> (output_text, model, tokens)."""
    endpoint = os.getenv("MICROSOFT_FOUNDRY_ENDPOINT")
    if not endpoint:
        sys.exit("Set MICROSOFT_FOUNDRY_ENDPOINT (and run `az login`). See README.")

    from azure.identity import DefaultAzureCredential
    from azure.ai.projects import AIProjectClient

    project = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())
    agent_name = os.getenv("AGENT_NAME")
    router = os.getenv("AZURE_MODEL_ROUTER_DEPLOYMENT")

    if agent_name:
        client = project.get_openai_client(agent_name=agent_name)
        mode = f"agent:{agent_name}"
    elif router:
        client = project.get_openai_client()
        mode = f"router:{router}"
    else:
        sys.exit("Set AGENT_NAME or AZURE_MODEL_ROUTER_DEPLOYMENT. See README.")

    def call(turns: list[str]) -> tuple[str, str, dict]:
        conversation = client.conversations.create()
        out, model, usage = "", "", {}
        for turn in turns:
            kwargs = {"conversation": conversation.id, "input": turn}
            if router and not agent_name:
                kwargs["model"] = router
            resp = client.responses.create(**kwargs)
            out = resp.output_text
            model = getattr(resp, "model", "") or model
            u = getattr(resp, "usage", None)
            if u:
                usage = {"input": getattr(u, "input_tokens", 0),
                         "output": getattr(u, "output_tokens", 0)}
        return out, model, usage

    return call, mode


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="run only the first N queries")
    ap.add_argument("--export-jsonl", type=str, default="", help="write an optimizer dataset")
    args = ap.parse_args()

    queries = load_json(HERE / "queries.json")["queries"]
    if args.limit:
        queries = queries[: args.limit]

    call, mode = build_client()
    print(f"Running {len(queries)} queries via {mode}\n")

    results, jsonl_rows = [], []
    for q in queries:
        turns = q.get("turns") or [q["query"]]
        start = time.perf_counter()
        try:
            output, model, usage = call(turns)
        except Exception as exc:  # keep the run going; record the failure
            output, model, usage = f"ERROR: {exc}", "", {}
        latency_ms = round((time.perf_counter() - start) * 1000)
        passed, fails = grade(q, output)
        results.append({
            "id": q["id"], "category": q["category"], "gate": q["gate"],
            "selected_model": model, "latency_ms": latency_ms, "usage": usage,
            "passed": passed, "failures": fails,
        })
        jsonl_rows.append({
            "query": "\n".join(turns),
            "response": output,
            "reference": json.dumps(q.get("expected", {}), separators=(",", ":")),
        })
        print(f"  {q['id']:<4} {q['gate']:<16} {'PASS' if passed else 'FAIL':<4} "
              f"{model or '-':<18} {latency_ms:>5}ms")

    scorecard = summarize(results)
    out_path = HERE / "results.json"
    out_path.write_text(json.dumps({"mode": mode, "scorecard": scorecard,
                                    "results": results}, indent=2), encoding="utf-8")
    print("\n" + render(scorecard))
    print(f"\nWrote {out_path.relative_to(HERE.parent.parent.parent)}")

    if args.export_jsonl:
        Path(args.export_jsonl).write_text(
            "\n".join(json.dumps(r) for r in jsonl_rows), encoding="utf-8")
        print(f"Wrote optimizer dataset {args.export_jsonl}")


def summarize(results: list[dict]) -> dict:
    total = len(results)
    passed = sum(r["passed"] for r in results)
    lat = [r["latency_ms"] for r in results if r["latency_ms"]]
    policy = [r for r in results if r["gate"] == "policy"]
    dist: dict[str, int] = {}
    for r in results:
        if r["selected_model"]:
            dist[r["selected_model"]] = dist.get(r["selected_model"], 0) + 1
    return {
        "quality_pct": round(100 * passed / total, 1) if total else 0,
        "policy_pct": round(100 * sum(r["passed"] for r in policy) / len(policy), 1) if policy else None,
        "p50_ms": round(statistics.median(lat)) if lat else None,
        "p95_ms": sorted(lat)[int(0.95 * (len(lat) - 1))] if lat else None,
        "total_input_tokens": sum(r["usage"].get("input", 0) for r in results),
        "total_output_tokens": sum(r["usage"].get("output", 0) for r in results),
        "selected_model_distribution": dist,
    }


def render(s: dict) -> str:
    lines = ["Scorecard",
             f"  Quality           {s['quality_pct']}%",
             f"  Policy accuracy   {s['policy_pct']}%" if s["policy_pct"] is not None else "  Policy accuracy   n/a",
             f"  Latency p50/p95   {s['p50_ms']} / {s['p95_ms']} ms",
             f"  Tokens in/out     {s['total_input_tokens']} / {s['total_output_tokens']}"]
    if s["selected_model_distribution"]:
        lines.append("  Selected models:")
        for model, n in sorted(s["selected_model_distribution"].items(), key=lambda kv: -kv[1]):
            lines.append(f"    {model:<24} {n}")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
