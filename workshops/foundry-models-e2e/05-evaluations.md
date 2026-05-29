# Step 5 — Evaluations: curated, batch, online (SDK)

> **Foundry lifecycle:** **02 · Evaluate** (run) — curated + batch evaluations turn belief into measurement.

## Goal

Turn "the answer sounds good" into a number, and run the same number across v1, v2, and v3 so we can *prove* the journey.

**Surface:** Foundry SDK (`azure-ai-evaluation`) + Foundry Portal review.

**Time:** 60 min.

**Scorecard at end of step:**
```
Quality   ████░░░░░░  0.52 (v1) → 0.43 (v2, flat — policy fine-tune comes in Step 6)
Cost      ░░░░░░░░░░  $0.004  ⬇️ from $0.007  ✅
Latency   ██████████  15.8s   ⬆️  (3 sequential hops — optimised in Step 7)
```

## Prereqs

- Step 4 complete: ~200-row eval dataset versioned and accessible.
- `azure-ai-evaluation` installed and the project endpoint exported.

## Steps

The numbered subsections below (5.1 – 5.5) are the actions to perform in order.

Quality moves for the first time — because we *measured* the v2 agent (model-per-task from Step 3) against our 198-row eval, not because we changed code.

---

## 5.1 — Three eval flavors, three jobs

| Flavor | When | What it answers |
|---|---|---|
| **Curated (20 rows)** | Every commit | "Did I break a known case?" Fast smoke test. |
| **Batch (~200 rows)** | Before deploy | "How does this version score overall?" |
| **Online (continuous)** | Production traffic | "Is real-world quality drifting?" |

This step builds curated + batch. Online is shown in the portal in Step 8.

## 5.2 — Evaluators

We use three:

1. **Schema/constraint evaluator** (deterministic): does the JSON parse, do `expected_keys` appear, is `total_estimated_cost_usd ≤ max_total`?
2. **LLM-as-judge — generic correctness** (uses `gpt-4.1`): scores semantic correctness 1–5, normalized to 0–1. Folded into the headline Quality score.
3. **LLM-as-judge — Policy Adherence** ⭐ *custom prompt-based evaluator*. Implements the five-axis rubric defined in [`sample-data/README.md`](./sample-data/README.md#evaluating-policy-adherence): Grounding (0.30) · Citation correctness (0.20) · Value & threshold accuracy (0.20) · Approval-path correctness (0.15) · Scope discipline (0.15). Code lives in [`code/s05_policy_adherence_evaluator.py`](./code/s05_policy_adherence_evaluator.py). Only fires for `intent == "policy_question"` rows so the slice metric reflects the gap fine-tuning is supposed to close.

> **Why a third evaluator?** Schema can't tell whether `"approval_required": "VP"` is the right approver. The generic judge gives polite credit for plausible-sounding answers — exactly the failure mode we're trying to catch on policy questions. The custom rubric is what lets v1 → v2 → v3 actually *show* the policy quality climb in a way the stakeholder cares about. We come back to this in **Step 8 (Operate)** when we discuss promoting it from a hand-rolled prompt into a managed **Foundry Eval Rubric** that auto-updates from production traces.

## 5.3 — The driver

`code/s05_run_eval.py`:

```python
# s05_run_eval.py — runs an agent factory over an eval set and scores it
import json, time, argparse
from statistics import mean
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.evaluation import evaluate, GroundednessEvaluator
from s02_config import PROJECT_ENDPOINT, DEPLOY_PLANNER
from s02_scorecard import print_scorecard, cost_of
# --- evaluators ---------------------------------------------------------

def schema_eval(row, response):
    try:
        obj = json.loads(response["answer"])
    except Exception:
        return {"score": 0.0, "reason": "non-json"}
    missing = [k for k in row["expected_keys"] if k not in obj]
    over = 0
    if "max_total" in row.get("expected_constraints", {}):
        if obj.get("total_estimated_cost_usd", 1e9) > row["expected_constraints"]["max_total"]:
            over = 1
    score = 1.0 if (not missing and not over) else 0.0
    return {"score": score, "missing": missing, "over_budget": bool(over)}

JUDGE_INSTRUCTIONS = """Score the agent's answer 1-5 for whether it correctly
satisfies the user's request and respects the stated constraints.
Return JSON: {"score": int, "reason": "..."}"""

def judge_eval(row, response, client):
    msg = (f"User asked: {row['input']}\n\nAgent answered:\n{response['answer']}")
    r = client.responses.create(
        model=DEPLOY_PLANNER, temperature=0,
        instructions=JUDGE_INSTRUCTIONS,
        input=msg,
        text={"format": {"type": "json_object"}},
    )
    return json.loads(r.output_text)

# --- driver -------------------------------------------------------------

def run_eval(agent_module: str, eval_path: str, label: str):
    mod = __import__(agent_module)
    rows = [json.loads(l) for l in open(eval_path)]

    project = AIProjectClient(endpoint=PROJECT_ENDPOINT,
                              credential=DefaultAzureCredential())
    judge_client = project.get_openai_client()

    schema_scores, judge_scores, latencies = [], [], []
    usage_by_model = {}

    for row in rows:
        resp = mod.run(row["input"])
        schema_scores.append(schema_eval(row, resp)["score"])
        judge_scores.append(judge_eval(row, resp, judge_client)["score"] / 5.0)
        latencies.append(resp["latency_s"])
        for m, (tin, tout) in resp.get("usage_by_model", {}).items():
            cur = usage_by_model.get(m, (0, 0))
            usage_by_model[m] = (cur[0] + tin, cur[1] + tout)

    quality = 0.5 * mean(schema_scores) + 0.5 * mean(judge_scores)
    cost    = cost_of(usage_by_model) / len(rows)
    latency = sorted(latencies)[len(latencies)//2]    # p50
    print_scorecard(label, quality, cost, latency)
    return {"quality": quality, "cost": cost, "latency": latency,
            "n": len(rows), "label": label}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", required=True,
                    help="python module: baseline_agent | multi_model_agent")
    ap.add_argument("--eval",  default="../sample-data/eval-full.jsonl")
    ap.add_argument("--label", required=True)
    a = ap.parse_args()
    run_eval(a.agent, a.eval, a.label)
```

Run the curated quick check first:

```bash
python s05_run_eval.py --agent s02_baseline_agent \
                   --eval ../sample-data/eval-seed.jsonl \
                   --label "v1-curated"
```

Then the full batch on v1:

```bash
python s05_run_eval.py --agent s02_baseline_agent \
                   --eval ../sample-data/eval-full.jsonl \
                   --label "v1-batch"
```

Expected (illustrative): **v1-batch quality ≈ 0.61.**

## 5.4 — Now build the v2 agent (router + per-task models, no fine-tune yet)

Drop in `code/s05_multi_model_agent.py` (we'll fill in fine-tune in Step 6; for v2 the policy step uses `DEPLOY_POLICY_BASE`):

```python
# s05_multi_model_agent.py — v2/v3 router-led agent (Responses API)
import json, time
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from s02_tools_mock import TOOL_SCHEMAS, DISPATCH
from s03_router import route
from s02_config import (PROJECT_ENDPOINT, DEPLOY_PLANNER, DEPLOY_ROUTER,
                       DEPLOY_MINI_VISION, DEPLOY_POLICY_BASE, DEPLOY_POLICY_FT)
USE_FT_POLICY = False   # flip to True after Step 6 deploys the fine-tune

_project = AIProjectClient(endpoint=PROJECT_ENDPOINT,
                           credential=DefaultAzureCredential())
_client  = _project.get_openai_client()

def run(user_message: str, image_url: str | None = None) -> dict:
    t0 = time.time()
    usage = {}
    def _bump(model, r):
        cur = usage.get(model, (0, 0))
        usage[model] = (cur[0] + r.usage.input_tokens,
                        cur[1] + r.usage.output_tokens)

    # 1. Route (uses the s03_router.route() helper; bill it conservatively)
    intent = route(user_message, has_image=bool(image_url))
    usage[DEPLOY_ROUTER] = (250, 35)

    # 2. Optional vision pre-step (Responses API: input_image content type)
    vision_facts = None
    if image_url:
        r = _client.responses.create(
            model=DEPLOY_MINI_VISION, temperature=0,
            instructions=("Extract receipt fields as JSON: "
                          "merchant, amount, date, category."),
            input=[{"role": "user", "content": [
                {"type": "input_text",  "text": "Extract."},
                {"type": "input_image", "image_url": image_url},
            ]}],
            text={"format": {"type": "json_object"}},
        )
        _bump(DEPLOY_MINI_VISION, r)
        vision_facts = json.loads(r.output_text)

    # 3. Pre-resolve policy (cheap model, optionally fine-tuned)
    policy_model = DEPLOY_POLICY_FT if USE_FT_POLICY else DEPLOY_POLICY_BASE
    pol = _client.responses.create(
        model=policy_model, temperature=0,
        instructions="You answer WWI policy questions. Concise.",
        input=user_message,
    )
    _bump(policy_model, pol)
    policy_note = pol.output_text

    # 4. Planner with tool calls — gets pre-resolved policy + vision facts
    planner_instructions = (
        "You are WWI planner. Use tools. Respect policy. "
        f"Pre-resolved policy: {policy_note}. "
        f"Receipt facts: {vision_facts}. "
        "Return final JSON: flight, hotel, policy_notes, "
        "total_estimated_cost_usd, booking_status."
    )
    input_items = [{"role": "user", "content": user_message}]
    final = None
    for _ in range(6):
        r = _client.responses.create(
            model=DEPLOY_PLANNER,
            instructions=planner_instructions,
            input=input_items,
            tools=TOOL_SCHEMAS, tool_choice="auto",
        )
        _bump(DEPLOY_PLANNER, r)
        final = r
        input_items += [it.model_dump(exclude_none=True) for it in r.output]
        function_calls = [it for it in r.output if it.type == "function_call"]
        if not function_calls:
            break
        for fc in function_calls:
            args = json.loads(fc.arguments)
            out = DISPATCH[fc.name](**args)
            input_items.append({
                "type": "function_call_output",
                "call_id": fc.call_id,
                "output": json.dumps(out),
            })

    return {"answer": final.output_text, "latency_s": time.time()-t0,
            "usage_by_model": usage,
            "intent": intent, "vision": vision_facts}
```

Run v2:

```bash
python s05_run_eval.py --agent s05_multi_model_agent \
                   --eval ../sample-data/eval-full.jsonl \
                   --label "v2-batch" \
                   --baseline "v1-batch"
```

> Passing `--baseline v1-batch` renders a colored Δ column next to each metric
> (▼ green when cost/latency drop, ▲ green when quality climbs), so the
> v1 → v2 delta is visible immediately, not just at the wrap-up.

Expected:
```
=== v2-batch scorecard ===
Quality   ████████░░  0.78
Cost      █████░░░░░  $0.063
Latency   ██████░░░░  9.4 s
```

Two rows of the on-stage scorecard turn green. Policy QA is still the blocker — that's Step 6.

## 5.5 — Check it in the portal

> **Note:** `azure-ai-evaluation.evaluate()` portal upload requires an Azure ML workspace. The new AI Foundry project type (`Microsoft.CognitiveServices`) is not yet supported by the `azure_ai_project` parameter. Eval results are saved locally as `eval_results_{label}.json`.
>
> To view results in the portal today, use **Tracing** — the Foundry SDK's `AIProjectClient` logs agent traces automatically when `AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED=true` is set.

Portal → **Tracing** → you'll see per-request spans for every model call. Click into a span to see input, output, latency, and token counts.

## Verify

- `python s05_run_eval.py` completes against v1 and v2 and writes results into the project's **Evaluation** tab.
- v2 overall quality lands around 0.78 (policy QA still the laggard at ~0.81).
- You can open a single failing row in the portal and explain why it failed.

## Troubleshoot

| Symptom | Likely cause | Fix |
|---|---|---|
| Eval run hangs at start | Dataset not registered in project. | Register via Foundry Skill or rerun with the local JSONL path. |
| Evaluator throws on a row | Output schema mismatch. | Add a `try/except` in the evaluator and log skipped rows; rerun on cleaned data. |
| Portal shows no results | Run wrote to a different project. | Verify `AZURE_AI_PROJECT_ENDPOINT` matches the portal project. |

## Next

➡️ [Step 6 — Fine-tune `gpt-4.1` for policy](./06-finetune.md)
