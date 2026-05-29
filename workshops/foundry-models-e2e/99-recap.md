# 99 — Recap

> Workshop: Right Model, Right Job — WWI Concierge (`foundry-models-e2e`)

## What you built

- A reproducible **v1 baseline** in code with mocked tools and a measured quality number (0.61).
- A **per-task model selection** based on the Foundry catalog (router, mini, mini-vision, planner).
- A **synthetic eval dataset** grown from 20 seed rows to ~200, versioned in the portal.
- A **curated + batch eval pipeline** that runs the same evaluators across v1, v2, and v3.
- A **fine-tuned `gpt-4.1`** for policy QA (0.28 → ~0.94) at a fraction of asking the frontier for every answer.
- A **multi-model agent v3** that meets all three scorecard targets (≥ 0.92 quality, ≤ 3¢/task, ≤ 8 s p50).
- Portal artifacts — eval runs, red-team report, versioned agents — ready for stakeholder review.

## Final scorecard

```
Quality   █████████░  0.94  ✅  (target ≥ 0.92)
Cost      ██░░░░░░░░  2.8¢  ✅  (target ≤ 3¢ / task)
Latency   ███░░░░░░░  7.6s  ✅  (target ≤ 8s p50)
```

## Objectives revisited

1. **Explain why one frontier model is the wrong production answer** — Step 1's $0.11/12.3 s baseline.
2. **Decompose into tasks and pick a model per task** — Step 3's mapping with the Foundry Skill.
3. **Establish a per-task quality/cost/latency scorecard** — the three bars threaded through every step.
4. **Use curated, batch, and online evals** — Step 5's eval driver and the portal **Evaluation** tab.
5. **Apply synthetic data and fine-tuning to close a quality gap** — Steps 4 and 6.
6. **Assemble a multi-model agent and compare versions** — Steps 7 and 8.

## Where to go next

- **Compare models head-to-head** — use the `explore-model` skill on entries under `models/` to put your candidate models through their paces.
- **Continuous evaluation** — promote production traces back into the eval dataset and wire alerts on the same evaluators you used here.
- **Prompt optimizer** — re-run the planner with the optimizer to find a better prompt against the same evaluator suite.
- **A second workshop** — author one with `add-workshop` that focuses on a single Foundry capability (e.g. red team, dataset versioning).

## Tear down (optional)

```bash
# Drop the fine-tuned deployment if you no longer need it.
az ai deployment delete --name policy-mini-ft \
    --project wwi-concierge-demo --resource-group rg-wwi-concierge-demo
```

For the full project, delete the resource group:

```bash
az group delete --name rg-wwi-concierge-demo --yes
```

## How this maps to the original plan

The original design doc lives at
[`../../.plans/foundry-models-e2e-plan.md`](../../.plans/foundry-models-e2e-plan.md).
Use it to correlate **what was planned** (speaker script, 45-minute
beats, day-by-day build calendar) against **what was built** (this
workshop). If you discover gaps, the planning doc is the canonical
source — adjust the workshop to match, or file a note in the planning
doc explaining the deliberate deviation.
