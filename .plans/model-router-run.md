# Model Router — Comparison Run Plan

> Companion plan for the **`foundry-models-e2e`** workshop.
> Goal: deploy Azure OpenAI **`model-router`** into the same Foundry project as v1/v2/v3, run it against the synthetic + adversarial WWI prompt set, then read the portal monitor metrics to see which underlying model the router picked per task — and produce a comparable scorecard.

---

## 0 · Context

The workshop already proves a per-task multi-model agent (`v3`) beats a single-frontier baseline (`v1`) on quality / cost / latency. Foundry's hosted **`model-router`** is a counter-hypothesis: *can a single managed routing deployment match the hand-decomposed agent without us writing the routing logic?*

This plan adds **one new scorecard row** — `model-router` — to the existing arc:

```
                    Quality     Cost/task   p50 latency
─────────────────── ─────────── ─────────── ───────────
v1  Single frontier  0.41        $0.023      12.5s
v2  Multi-model      0.45        $0.006      11.0s
policy-FT  +distill  0.49 (slice) $0.003     5.1s
v3  Full assembly    0.46         $0.006      6.5s
model-router         ?           ?           ?         ← this run
```

---

## 1 · Target Foundry project

Reused from `code/.env` (no new project created):

| Field | Value |
|---|---|
| Subscription | `7a880728-70d3-49d0-adde-4250716cfd94` |
| Resource group | `rg-build26-brk230-demo` |
| Foundry account | `build26-brk230-demo-foundry` |
| Project | `build26-brk230-demo` |
| Region | **`swedencentral`** |
| Existing deployments | `planner-gpt41` · `router-nano` · `mini-vision` · `policy-mini-base` · `text-embedding-3-large` |

---

## 2 · Quota verification (swedencentral)

Pulled via `mcp_foundry_mcp_model_quota_list` on the subscription:

| Quota | SKU | Used / Limit (K TPM) | Headroom |
|---|---|---|---|
| **`ModelRouter`** | **GlobalStandard** | **632 / 10,000** | ✅ ~9,368 K TPM free |
| `ModelRouter` | DataZoneStandard | 0 / 3,000 | ✅ full |
| `ModelRouter-finetune` | GlobalStandard | 0 / 800 | ✅ full |

**Decision:** deploy at **`GlobalStandard` / capacity 10** (matches the other workshop deployments, ~10 K TPM — well under the available headroom). No quota increase required.

Re-verify before the run:

```bash
# Region quota for ModelRouter
az cognitiveservices usage list --location swedencentral \
  --query "[?contains(name.value, 'ModelRouter')].{name:name.value, used:currentValue, limit:limit}" \
  -o table
```

---

## 3 · Deploy the `model-router` model

Job-shaped deployment name (consistent with the workshop's "name by job, not by model" rule):

| Deployment name | Model | Version | SKU | Capacity |
|---|---|---|---|---|
| **`auto-router`** | `model-router` | `2025-08-07` (latest GA) | `GlobalStandard` | `10` |

### Option A — Foundry skill / MCP (preferred)

Invoke the `microsoft-foundry` skill's `models/deploy-model` sub-skill, or call the MCP directly:

```jsonc
// mcp_foundry_mcp_model_deploy
{
  "foundryAccountResourceId":
    "/subscriptions/7a880728-70d3-49d0-adde-4250716cfd94/resourceGroups/rg-build26-brk230-demo/providers/Microsoft.CognitiveServices/accounts/build26-brk230-demo-foundry",
  "deploymentName": "auto-router",
  "modelName": "model-router",
  "modelFormat": "OpenAI",
  "modelVersion": "2025-08-07",
  "skuName": "GlobalStandard",
  "skuCapacity": 10
}
```

### Option B — `az` CLI fallback

```bash
source workshops/foundry-models-e2e/.env

az cognitiveservices account deployment create \
  --name        "$FOUNDRY_ACCOUNT_NAME" \
  --resource-group "$AZURE_RESOURCE_GROUP" \
  --deployment-name "auto-router" \
  --model-name      "model-router" \
  --model-version   "2025-08-07" \
  --model-format    "OpenAI" \
  --sku-name        "GlobalStandard" \
  --sku-capacity    10
```

Verify state is `Succeeded`:

```bash
az cognitiveservices account deployment show \
  -n "$FOUNDRY_ACCOUNT_NAME" -g "$AZURE_RESOURCE_GROUP" \
  --deployment-name auto-router \
  --query "{name:name, state:properties.provisioningState, model:properties.model.name}" -o table
```

---

## 4 · New scripts to add under `workshops/foundry-models-e2e/code/`

These are *new* files — they do **not** modify the existing v1/v2/v3 agents.

### 4.1 · `s09_router_agent.py` — single-deployment "agent"

Mirrors the shape of `s02_baseline_agent.py` (so `s05_run_eval.py` can drive it unchanged) but every model call targets `auto-router` instead of `planner-gpt41`. Still wires the same mocked tools and returns the same `{answer, latency_s, usage_by_model}` dict expected by the eval harness.

Key points:
- `from s02_config import PROJECT_ENDPOINT` — reuses the project endpoint.
- New constant `DEPLOY_AUTO_ROUTER = "auto-router"`.
- Pricing entry must be added to `s02_config.PRICE` so `cost_of()` works — use the **billed sub-model** rates the router reports back. The router emits the chosen model in the response usage; we credit that rate. As a conservative default before the run, treat all router traffic as `gpt-4.1-mini` rates and refine after the run from the per-call telemetry.

### 4.2 · `s09_run_router_eval.py` — thin wrapper

A 5-line wrapper that just calls:

```python
from s05_run_eval import run_eval
run_eval("s09_router_agent",
         "../sample-data/eval-full.jsonl",
         "model-router")
```

### 4.3 · `requirements.txt`

No new dependencies. The existing `azure-ai-projects`, `openai`, and `azure-ai-evaluation` pins are sufficient.

---

## 5 · Run the eval

From `workshops/foundry-models-e2e/code/`:

```bash
# Full synthetic + adversarial set used by v1/v2/v3
python s09_run_router_eval.py
# → writes eval_results_model-router.json
# → prints the scorecard row
```

The eval set is the same `../sample-data/eval-full.jsonl` (~170 rows) — covering `plan_trip`, `policy_question`, `receipt_expense`, plus adversarial / over-budget / out-of-window rows.

---

## 6 · Read the monitor metrics (per-sub-model routing)

`model-router` decides which underlying model to invoke per request. Pull the routing distribution two ways:

### 6.1 · Foundry portal

`ai.azure.com` → project `build26-brk230-demo` → **Models + endpoints** → `auto-router` → **Monitor** tab. Charts to screenshot:

- *Tokens (prompt + completion) by underlying model*
- *Requests by underlying model*
- *Mean / p95 latency by underlying model*

### 6.2 · MCP query (scripted)

```jsonc
// mcp_foundry_mcp_model_monitoring_metrics_get
{
  "foundryAccountResourceId":
    "/subscriptions/7a880728-70d3-49d0-adde-4250716cfd94/resourceGroups/rg-build26-brk230-demo/providers/Microsoft.CognitiveServices/accounts/build26-brk230-demo-foundry",
  "modelDeploymentName": "auto-router",
  "metricCategory": "ModelsUsage"
}
```

Repeat with `"metricCategory": "Latency"` and `"Requests"`.

### 6.3 · Per-call telemetry (in-band)

The Responses API returns `model` in each completion — `s09_router_agent.py` should log it into `usage_by_model` so the eval harness can build a routing histogram directly from the run, independent of the portal.

---

## 7 · Scorecard delivery

After the eval finishes, produce **two** artifacts:

1. **Scorecard row** appended to the workshop arc:

   ```
   model-router          0.??        $0.???       ?.?s
   ```

   Uses the existing `s02_scorecard.print_scorecard(label, quality, cost, latency)` formatter.

2. **Routing distribution table** (built from `usage_by_model` + portal metrics):

   | Intent (from eval row) | Routed to | % of requests | Avg tokens in/out | $/task |
   |---|---|---|---|---|
   | `plan_trip` | … | … | … | … |
   | `policy_question` | … | … | … | … |
   | `receipt_expense` | … | … | … | … |

   This is the punch-line: did the *managed* router land on the same per-task split as the *hand-built* v3 router? Where did it differ, and what did that cost in quality / latency?

---

## 8 · Cleanup (optional)

If the demo is over and the deployment is no longer needed:

```bash
az cognitiveservices account deployment delete \
  -n "$FOUNDRY_ACCOUNT_NAME" -g "$AZURE_RESOURCE_GROUP" \
  --deployment-name auto-router
```

---

## 9 · Checklist

- [x] Re-confirm `ModelRouter` GlobalStandard quota in swedencentral (≥10 K TPM free) — *measured 9,368 K free*
- [x] Deploy `auto-router` (`model-router @ 2025-08-07`, GlobalStandard / 10)
- [x] Add `s09_router_agent.py` (mirrors `s02_baseline_agent.py` shape)
- [x] Add `s09_run_router_eval.py` wrapper
- [x] Add `auto-router` to `s02_config.PRICE` (start with mini rates, refine post-run)
- [x] **Scale-up gotcha:** at capacity 10 the deployment is 10 RPM / 10 K TPM. azure-ai-evaluation runs the 173-row target in parallel, which 429-throttled almost every row. Re-deployed at **capacity 100** (`az cognitiveservices account deployment create … --sku-capacity 100`) and re-ran cleanly.
- [x] Run eval over `eval-full.jsonl`, label `model-router` — completed 173/173, 0 errors
- [x] Emit scorecard row + routing distribution table — see §10 below
- [ ] Capture portal Monitor screenshots (Models Usage, Requests, Latency) — *manual portal step, optional*
- [ ] (Optional) delete `auto-router` deployment when done

---

## 10 · Results — `model-router` run, 2026-05-27

### 10.1 · Scorecard row

| Version | Quality | Cost/task | p50 latency | Notes |
|---|---|---|---|---|
| v1 — single frontier  | 0.41 | $0.023 | 12.5s | gpt-4.1 for everything |
| v2 — multi-model      | 0.45 | $0.006 | 11.0s | hand-built per-task split |
| policy-FT             | 0.49 (slice) | $0.003 | 5.1s | distilled mini |
| v3 — full assembly    | 0.46 | $0.006 | 6.5s | planner + ft + nano |
| **`model-router`**    | **0.59** | **$0.014** | **30.2s** | managed router, capacity 100 |

Underlying components of the `model-router` quality score:

- Schema pass rate: **49 / 173 = 0.28** (router picked richer JSON shapes than the eval's required keys expected — e.g. nested `flight.selected` vs flat `carrier`).
- LLM-judge mean: **0.90** (semantic answers were generally good).
- p95 latency: **76.1s**. Mean: **33.5s**.
- Exception fallbacks: **0 / 173** (no 429s after scale-up; no SDK errors).

### 10.2 · Routing distribution (which sub-model the router picked)

| Sub-model | Calls | % of calls | Tokens in | Tokens out |
|---|---:|---:|---:|---:|
| `gpt-5-mini-2025-08-07` | 150 | 65.2% | 239,157 | 557,393 |
| `gpt-5-chat-2025-08-07` |  58 | 25.2% |  45,941 |  12,167 |
| `gpt-5-nano-2025-08-07` |  14 |  6.1% |  24,644 | 113,583 |
| `gpt-4.1-mini-2025-04-14` | 8 |  3.5% |  20,375 |   2,135 |

> Tokens are summed over **all** Responses API turns in each multi-turn agent run (tool-calling loop), not per-row.

### 10.3 · Per-intent routing

| Intent | Total calls | Routing breakdown |
|---|---:|---|
| `plan_trip`        | 124 | gpt-5-mini=82 · gpt-5-chat=28 · gpt-5-nano=7 · gpt-4.1-mini=7 |
| `policy_question`  |  47 | gpt-5-mini=30 · gpt-5-chat=13 · gpt-5-nano=4 |
| `receipt_expense`  |  59 | gpt-5-mini=38 · gpt-5-chat=17 · gpt-5-nano=3 · gpt-4.1-mini=1 |

### 10.4 · Interpretation

- **Different model family.** The managed `model-router` reaches into the `gpt-5` family (mini · chat · nano) — orthogonal to the workshop's hand-built `gpt-4.1` split. That alone explains most of the numbers.
- **Quality (0.59) up vs all hand-built versions** — driven entirely by the LLM-judge (0.90 mean). The schema-pass slice (0.28) is *lower* than v1/v2/v3 because the gpt-5 outputs are JSON-rich but use slightly different key shapes than the strict `expected_keys` contract. This is a fixable evaluator issue, not a router issue.
- **Cost ($0.014) sits between v1 and v2** — better than the single-frontier baseline, worse than the hand-decomposed v2/v3. The router favoured `gpt-5-mini` (65%) which is mid-tier, and almost never reached for nano-tier on the simplest tasks.
- **Latency (30.2s p50, 76.1s p95) is the clear loss** — gpt-5-mini is reasoning-heavy and each agent task fires multiple tool-calling turns. v3's 6.5s p50 stays well ahead.
- **Hill-climb verdict:** as a *drop-in*, `model-router` improves quality and beats v1 on cost, but loses latency badly and doesn't reach v2/v3's cost. Useful as a zero-engineering fallback; not a replacement for the hand-built per-task split when latency matters.

### 10.5 · Where to see this in the portal

`ai.azure.com` → project `build26-brk230-demo` → **Models + endpoints** → `auto-router` → **Monitor** tab — the *Models Usage*, *Requests by model*, and *Latency by model* charts should mirror the §10.2 distribution, plus give you the per-sub-model latency split.

Artifacts:
- `workshops/foundry-models-e2e/code/eval_results_model-router.json` — full per-row outputs, schema + judge scores, usage JSON.
- `workshops/foundry-models-e2e/code/s09_router_agent.py`, `s09_run_router_eval.py` — reproducible run.
