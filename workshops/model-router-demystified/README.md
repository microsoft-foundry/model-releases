# One Endpoint, Smarter Spend — Model Router Deep-Dive

> Workshop slug: `model-router-demystified` · Workshop 1 (the Model Router narrative)

> **World Wide Importers (WWI)** is the fictitious enterprise used throughout this workshop — a mid-size global trading company whose employees travel constantly. The application we build for them is **WWI Concierge**, an internal AI travel assistant. This workshop reuses the WWI scenario, travel policy, and eval seed data introduced in [`foundry-models-e2e`](../foundry-models-e2e/).

This is the **hands-on companion** to [`model-router-demystified-plan.md`](../../.plans/model-router-demystified-plan.md) (the original PLAN). Follow it end-to-end and you'll deploy, evaluate, and optimize the Foundry Model Router — proving the "better, cheaper, faster" story empirically with zero routing code.

> **Audience:** developers/architects who know LLMs but are new to Model Router.
> **Region:** Sweden Central. **Deployment type:** Global Standard.
> **Model Router version:** `2025-11-18` (latest, actively updated).
> **Builds on:** [`foundry-models-e2e`](../foundry-models-e2e/) artifacts (WWI scenario, travel policy, eval seed data).

## Learning objectives

By the end of this workshop you will be able to:

1. **Explain** what Model Router is, how it analyzes prompts, and why it differs from manual routing.
2. **Deploy** a Model Router endpoint with routing mode and model subset configuration.
3. **Design** a representative prompt set that covers the complexity spectrum of a real workload.
4. **Compare** a frontier baseline against Model Router on quality, cost, and latency.
5. **Interpret** model-distribution reports to understand which backing models the router selects per task.
6. **Build** a custom Policy-Adherence evaluator using the Adaptive Evals eval-rubric framework.
7. **Optimize** by tuning routing modes and model subsets — config changes only, no code rewrites.
8. **Operate** with prompt caching, automatic failover, and continuous evaluation.

## The core insight

> **You don't need to build a router or guess which model fits which task.** Deploy one Model Router endpoint, send your real prompts, and the router decomposes the workload for you. Your job is to *measure* whether it's good enough — and this workshop teaches you how.

## Same scenario. Same quality. Dramatically lower cost.

| | **Before — Single Frontier (v1)** | **After — Model Router Optimized (v4)** |
|---|---|---|
| **Endpoint** | One `gpt-5` deployment | One Model Router deployment |
| **Routing** | None — every request hits frontier | Intelligent per-prompt routing to optimal model |
| **Configuration** | N/A | Balanced mode + curated model subset |
| **Caching** | None | Automatic prompt caching on supported models |
| **Failover** | Manual retry logic | Built-in transparent failover |
| **Routing code** | Custom `route_intent()` function | **Zero** — the router IS the intelligence |
| **Cost / month** | ~$14,000 | ~$4,500 (−68%) |

## The Select → Evaluate → Optimize → Operate loop

| Stage | What it means with Model Router | Lab |
|---|---|---|
| **Select** | Deploy Model Router. Configure routing mode + model subset. | Lab 2 |
| **Evaluate** | Run representative prompts through baseline and router. Measure quality/cost/latency + domain-specific policy adherence. | Labs 3–4 |
| **Optimize** | Tune routing mode, refine model subset, enable prompt caching. Each change = config only. | Labs 5–6 |
| **Operate** | Monitor model distribution, continuous eval, auto-failover. | Lab 7 |

## The three progress bars

Every lab moves these bars. Every change is justified by what the bars say *before* you make it.

- **Quality** = LLM-as-a-judge pairwise + absolute scoring (1–5)
- **Cost** = $ per task (router markup + underlying model pricing)
- **Latency** = wall-clock p50 response time

### The arc

```
                         Quality   Cost/task   p50 latency   Policy-Adherence
────────────────────────  ────────  ──────────  ────────────  ──────────────────
v1  Frontier (gpt-5)      4.3       $0.028      3.2s          4.1
v2  Router Balanced        4.2       $0.011      2.1s          4.0
v3  Router Cost            3.9       $0.006      1.4s          3.6
v4  Router + subset tuned  4.3       $0.009      1.8s          4.1
```

> Numbers are illustrative — you'll measure your own.

> **🧗 Hill climbing in model optimization.** The scorecard arc above is a "hill climb" — each row represents one configuration change (switch routing mode, narrow the model subset, enable caching), measured against the previous row. You keep a change only if the scorecard improves; otherwise you roll back and try a different lever. This incremental, evidence-driven loop is how you find the optimal operating point without guessing. Every lab in this workshop is one step up the hill.

## How to run this workshop

Use the [`run-workshop`](../../.agents/skills/run-workshop/SKILL.md) skill — it reveals only the step you're on:

> "Use the `run-workshop` skill on `workshops/model-router-demystified`."

**Modes:**
- `"Run workshop as learner"` — you run every command, Copilot guides and tracks progress with visual scorecards. Feedback capture is active.
- `"Run workshop as instructor"` — faster pacing for demos. Copilot may run commands. Feedback is logged for post-session fixes.
- Default (no mode specified) — same as learner behavior for commands.

Or read straight through — the files are numbered.

## Steps

| # | Lab | What you'll do | What moves on the scorecard |
|---|---|---|---|
| 0 | [Setup & prerequisites](./00-setup.md) | Deploy router + baseline in Sweden Central | Endpoints ready |
| 1 | [Build the prompt set](./01-prompt-set.md) | Create 50+ tagged representative prompts | Eval dataset ready |
| 2 | [Deploy & configure Model Router](./02-deploy-router.md) | Explore modes, subset, versioning | Router deployed |
| 3 | [Baseline vs. Router comparison](./03-baseline-comparison.md) | Run auto-eval pipeline, analyze model distribution | **v2: quality 4.2 · $0.011 · 2.1s** |
| 4 | [Custom evaluator: Policy-Adherence](./04-custom-evaluator.md) | Build eval-rubric with adaptive rules | Domain-specific scoring |
| 5 | [Optimize: routing modes](./05-optimize-modes.md) | Compare Balanced/Cost/Quality + model subset | **v3/v4 measured** |
| 6 | [Prompt caching](./06-prompt-caching.md) | Measure cache benefits, compound savings | Final optimized config |
| 7 | [Operate: monitoring & failover](./07-operate.md) | Continuous eval, failover, Foundry portal | Production-ready |
| 99 | [Recap & decision framework](./99-recap.md) | Synthesize into a decision matrix | — |

## Files in this folder

```
workshops/model-router-demystified/
├── README.md                           ← you are here
├── 00-setup.md
├── 01-prompt-set.md
├── 02-deploy-router.md
├── 03-baseline-comparison.md
├── 04-custom-evaluator.md
├── 05-optimize-modes.md
├── 06-prompt-caching.md
├── 07-operate.md
├── 99-recap.md
├── sample-data/
│   ├── router-eval-prompts.jsonl       ← 50+ tagged prompts
│   ├── policy-eval-dataset.jsonl       ← 20 policy questions + ground truth
│   └── travel-policy.md                ← WWI policy (shared with foundry-models-e2e)
├── code/
│   ├── requirements.txt
│   ├── config.py                       ← endpoints, deployment names, pricing
│   ├── eval-rubric-policy-adherence.yaml
│   ├── policy_adherence_evaluator.py
│   ├── run_comparison.py
│   ├── run_mode_comparison.py
│   └── prompt_caching_demo.py
└── slides/
```

## Artifact sync notice

> ⚠️ This workshop shares the WWI scenario and policy document with [`foundry-models-e2e`](../foundry-models-e2e/). If `sample-data/travel-policy.md` or `eval-seed.jsonl` is updated in either workshop, refresh the other to maintain consistency.

---

Start with **[Lab 0 — Setup & prerequisites](./00-setup.md)**.
