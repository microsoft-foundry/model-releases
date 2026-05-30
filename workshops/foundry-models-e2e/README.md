# Right Model, Right Job — WWI Concierge

> Workshop slug: `foundry-models-e2e` · Workshop 0 (the Foundry-Models-E2E narrative)

> **World Wide Importers (WWI)** is the fictitious enterprise used throughout this workshop — a mid-size global trading company whose employees travel constantly. The application we build for them is **WWI Concierge**, an internal AI travel assistant. Every persona, policy excerpt, evaluation row, and demo below is set in the WWI universe.

This is the **hands-on companion** to [`foundry-models-e2e-plan.md`](../../.plans/foundry-models-e2e-plan.md) (the original PLAN — speaker script + trainer guide). Follow it end-to-end and you'll have every demo in the 45-minute session built, recorded-ready, and explainable.

> **Audience:** professionals who know AI but are new to Microsoft Foundry.
> **Region:** Sweden Central. **Model family:** Azure Direct `gpt-4.1`, `gpt-4.1-mini`, `gpt-4.1-nano`.
> **Build budget:** ~7 days of evenings, toy-scale data.

## Learning objectives

By the end of this workshop you will be able to:

1. **Explain** when one frontier model behind one prompt is the wrong answer for a real workload.
2. **Decompose** an application into tasks and pick the right model per task from the Foundry catalog.
3. **Establish** a per-task quality/cost/latency scorecard and update it after every change.
4. **Use** Foundry evaluations — curated, batch, and online — to make model choice empirical.
5. **Apply** synthetic data generation and fine-tuning to close a specific quality gap.
6. **Assemble** a multi-model agent (v3) and compare versions in the portal.

## Five challenges this workshop tackles

Every AI team is hitting the same five walls. The eight steps are organized so each challenge gets answered once, with code:

| # | Challenge | What it really means | Where the workshop answers it |
|---|---|---|---|
| 1 | **Model choice is exploding** | More models, providers, modalities, and deployment options than ever. | Step 0 (catalog discovery in Sweden Central) · Step 3 (decompose the workload, pick a model **per task**) |
| 2 | **Benchmarks aren't enough** | Public benchmarks don't reflect *your* prompts, users, data, or business goals. | Step 4 (synthesize an eval grounded in your domain) · Step 5 (curated + batch evals with schema + LLM-as-judge evaluators you control) |
| 3 | **Cost is a system-level problem** | Routing, caching, batching, prompts, tiers, observability — not just model price. | Step 3 (router) · Step 7 (multi-model assembly) · scorecard tracks per-task `$/task` and p50 latency from Step 2 onward |
| 4 | **Production demands control** | Reliability, monitoring, safety, governance, versioning, rollback. | Step 6 (versioned fine-tune with train/val lineage) · Step 8 (portal review, red team, A/B compare v1 vs v2 vs v3, online tracing) |
| 5 | **The landscape keeps changing** | New models arrive constantly and your app must improve without being rebuilt. | Step 3 (name deployments **by job**, not by model) · Step 6 (swap to the fine-tune is a one-line `USE_FT_POLICY = True`) |

## The Foundry lifecycle — from model choice to a living AI system

Foundry isn't a one-shot picker; it's a **continuous loop**. Each step below tags which lifecycle stage it advances. By Step 8 you've completed one full turn of the loop — and the same pattern is what you'll repeat every time a new model lands in the catalog.

| Stage | What it means | Workshop steps |
|---|---|---|
| **01 · Select** | Match the model to the workload | Step 3 — *Model selection with the Foundry Skill* |
| **02 · Evaluate** | Test on **your own** data | Step 4 (synthesize a domain-grounded eval) · Step 5 (curated + batch evals with schema + LLM-judge) |
| **03 · Optimize** | Improve quality + latency + cost | Step 6 (fine-tune `gpt-4.1` for policy QA) · Step 7 (assemble the multi-model agent) |
| **04 · Operate** | Monitor, govern, roll back | Step 8 — *Portal review, red-team, online evaluation, agent versions* |
| **05 · Improve** | Adopt new models safely | Step 6 + Step 8 — *named-by-job deployments + one-line swap + A/B compare versions* |

> *Steps 0–2 are the prerequisite baseline (setup, v1 in the playground, v1 in code) — the lifecycle proper begins at Step 3.*

> **🎯 Plan before you build: evaluation-driven *development*, scorecard-driven *optimization*.**
> Before you write the agent, do two things in order:
>
> 1. **Define the optimization targets.** Pick a quality bar, a cost ceiling, and a latency budget — three concrete numbers your stakeholder would sign off on. These become `QUALITY_TARGET`, `COST_TARGET`, `LATENCY_TARGET` in [`code/s02_scorecard.py`](./code/s02_scorecard.py). No targets, no hill to climb.
> 2. **Identify the evaluators that will measure progress against each target.** A schema/constraint evaluator covers structural correctness, an LLM-as-judge covers generic semantic correctness, and a **custom prompt-based evaluator** covers the dimension your workload actually pays the bill for (here: **Policy Adherence** — does the answer stay inside the four corners of [`travel-policy.md`](./sample-data/travel-policy.md)?). All three are wired from Step 5 onward and run on every subsequent eval — so v1, v2, v3 are all measured against the same yardsticks. See [`code/s05_policy_adherence_evaluator.py`](./code/s05_policy_adherence_evaluator.py) and the rubric in [`sample-data/README.md`](./sample-data/README.md#evaluating-policy-adherence).
>
> Then — and only then — pick models and start changing things. Every architectural decision in Steps 3–7 is justified by what these evaluators say *before* the change, not after. Step 8 closes the loop by promoting the hand-rolled custom evaluator into a managed **adaptive Eval Rubric** that updates itself from production traces, so the *next* hill climb doesn't depend on a human noticing a gap.

## Same scenario. Same quality. Dramatically lower cost.

> *Numbers below are **representative, not measured** — they illustrate the shape of the win you'll reproduce at toy scale in the workshop. Imagine WWI has rolled the concierge to production: **~30,000 traveler interactions per day** across the customer base, three model roles (planner · policy · inline summarizer).*

| | **Before — Unoptimized (v1)** | **After — Foundry-Optimized (v3)** |
|---|---|---|
| **Model** | `gpt-4.1` for every call | `gpt-4.1` (planner) · `gpt-4.1-policy-ft` (policy) · `gpt-4.1-nano` (inline) |
| **Routing** | None. Every request hits the frontier model. | Foundry **Model Router** picks per task type (`route_intent → planner / policy / inline`). |
| **Caching** | None. Full processing every time. | System-prompt cache + semantic cache on policy Q&A (~35% hit rate). |
| **Outputs** | Free text, parsed manually downstream. | **Schema-validated JSON** — no parsing overhead, fewer retries. |
| **Customization** | Prompt-only. Policy answers drift on edge cases. | **Fine-tuned `gpt-4.1-mini`** on WWI refund / baggage / visa policy (knowledge-distilled from a `gpt-4.1` teacher). |
| **Deploy** | Serverless for all traffic — no headroom plan. | Serverless baseline **+ PTU + automatic spillover + priority processing** on the planner. |
| **Observability** | Print statements. | Built-in tracing, **online evaluations**, red team scans, version compare in the portal. |
| **Cost / month** | <span style="color:#d33">**~$14,000**</span> | <span style="color:#0a0">**~$3,200  (−77%)**</span> |

**Why it works:** none of these wins comes from picking a "better" single model. They come from treating the workload as a **system** — routing each task to the smallest model that meets its bar, fine-tuning where prompting plateaus, caching the repeatable parts, and putting a deployment tier under each call that matches its traffic shape. That is exactly the loop you'll run end-to-end in Steps 3 → 8.

## Speaker demo flows — how this workshop maps

The talk is structured as three short live demos (~4 / 4 / 5 minutes) that mirror the three audience challenges. The workshop is the **fully buildable version** of those same flows — every demo "step" lines up with a sub-section of one workshop step, so the speakers can rehearse from the workshop and the audience can re-run it later at their own pace.

### Demo 1 · Select the right model  *(~4 min · Step 3)*

| # | Demo beat | Workshop landing spot |
|---|---|---|
| 01 | **Catalog** — browse 11,000+ models across providers | Step 3 — *3.2 Ask the Foundry Skill to map jobs → models* (Skill enumerates catalog candidates per job) |
| 02 | **Filters** — narrow by capability, modality, cost, region | Step 3 — *3.2* (Skill prompt encodes capability + cost + Sweden Central region constraints) |
| 03 | **Model Cards** — review benchmarks, pricing, sample outputs | Step 3 — *3.2* output (model cards summarized) · Step 0 — *catalog discovery in the portal* |
| 04 | **Shortlist** — select candidates for evaluation and testing | Step 3 — *3.3 Deploy by job* + *3.4 Wire the router* (deployments named by job, ready for evaluation in Step 5) |

### Demo 2 · Validate with evidence  *(~4 min · Step 5, set up in Step 2 + Step 4)*

| # | Demo beat | Workshop landing spot |
|---|---|---|
| 01 | **Set criteria + identify evaluators** — define quality bar, latency budget, cost ceiling; pick the evaluators that will measure each one (including a custom evaluator for the dimension generic judges can't see) | Step 2 — *scorecard targets* (`QUALITY_TARGET=0.92`, `COST_TARGET=$0.03`, `LATENCY_TARGET=8.0s`) + Step 5 — *three evaluators registered together*: schema · generic LLM-judge · custom **Policy Adherence** rubric ([`s05_policy_adherence_evaluator.py`](./code/s05_policy_adherence_evaluator.py)) |
| 02 | **Load prompts** — a representative set of real production inputs | Step 4 — *synthetic eval set* (`eval-seed.jsonl`) + Step 5 — *5.3 The driver* loads it |
| 03 | **Run comparison** — execute the prompt set against Model A and Model B in parallel | Step 5 — *5.3* (v1 baseline) and *5.4 Build v2* (router + per-task models) over the same eval set |
| 04 | **Review results** — side-by-side outputs, scores, latency, cost — then decide | Step 5 — *5.5 Check it in the portal* (Foundry evaluations UI, side-by-side run compare) |

### Demo 3 · Optimize cost and performance  *(~5 min · Step 7, building on Steps 3 + 6)*

| # | Demo beat | Workshop landing spot |
|---|---|---|
| 01 | **Profile request** — classify incoming task by complexity, latency need, cost tolerance | Step 3 — *3.4 Wire the router* (`route_intent` returns `{planner, policy, inline}` per request) |
| 02 | **Apply routing** — route to the matched model tier (cheap for simple, capable for complex) | Step 7 — *7.1 What's already wired* + *7.2 Run Carmen's trip end-to-end* (router dispatches to nano / mini-FT / planner) |
| 03 | **Compare cost/quality** — same prompts through naive (single-model) and optimized (tiered) paths | Step 7 — *7.3 Run the full eval one more time* (v3 over the eval set, v1 numbers from Step 2 for the baseline column) |
| 04 | **Review savings** — side-by-side cost delta, latency delta, quality score; see the efficiency gain | Step 7 — *7.4 Side-by-side comparison* + *7.5 Save artifacts* · Step 8 — *portal version compare* for the screenshot |

> **Speaker note.** All three demos are designed to be **rehearseable from the workshop itself** — the workshop is the recording-ready long-form of what the speakers show live. Hooks to repeat in the room: *"Select"* → name your deployment by job, not by model · *"Validate"* → measure on **your** data, not a public benchmark · *"Optimize"* → the win is the **system**, not the single model.

## How to run this workshop

Use the [`run-workshop`](../../.agents/skills/run-workshop/SKILL.md) skill — it reveals only the step you're on and hides the rest. From the repo root, ask Copilot:

> "Use the `run-workshop` skill on `workshops/foundry-models-e2e`."

**Modes:**
- `"Run workshop as learner"` — you run every command, Copilot guides and tracks progress with visual scorecards. Feedback capture is active.
- `"Run workshop as instructor"` — faster pacing for demos. Copilot may run commands. Feedback is logged for post-session fixes.
- Default (no mode specified) — same as learner behavior for commands.

Need an explanation mid-step? Ask for `run-workshop/learn-more` on the term. Stuck? `run-workshop/troubleshoot` will pattern-match the Troubleshoot section of the current step. Want to know where you are? `run-workshop/check-status`.

If you'd rather read straight through, the files are numbered.

---

## The narrative device: three progress bars

Everything in this workshop moves three bars. Every step is justified by what the bars say *before* you make the change — not after.

- **Quality** = pass rate on the curated eval set (LLM-as-judge, schema-validated JSON output).
- **Cost** = $ per completed agent task (tokens × per-model rate, summed across all models used).
- **Latency** = wall-clock p50 for a single task end-to-end.

### The arc — measured in a live run on the gpt-4.1 model family

```
                    Quality     Cost/task   p50 latency
─────────────────── ─────────── ─────────── ───────────
v1  Single frontier  0.41        $0.023      12.5s
v2  Multi-model      0.45        $0.006      11.0s        ← Step 5
policy-FT  +distill  0.49 (slice) $0.003     5.1s         ← Step 6
| v3  Full assembly    0.46         $0.006      6.5s         ← Step 7
```

Each row reflects exactly one decision:
- **v1 → v2**: decompose the workload, route each task to the smallest model that meets its bar.
- **v2 → policy-FT**: fine-tune the policy model using knowledge distillation (gpt-4.1 teacher → gpt-4.1-mini student). Same quality, 3× cheaper, 2× faster.
- **v3**: assemble all three wins into the production agent and measure the compound effect.

> **On the gpt-4.1 model family:** These numbers reflect an actual live run on Azure Sweden Central with gpt-4.1, gpt-4.1-mini, and gpt-4.1-nano. The model family is noticeably stronger than the gpt-4o era the workshop was originally authored against — your baseline quality will be higher than older workshop recordings suggest, which makes the cost and latency wins the more compelling story.

The whole arc is: **one frontier model doing every task → the right model for each task, evaluated against a per-task scorecard.**

> **🧗 Hill climbing in model optimization.** Each row in the scorecard is one step up the hill. "Hill climbing" means making a single change (swap a model, add a route, enable caching), measuring whether it improves the scorecard, and keeping it only if it does. You never leap — you take one step, measure, and decide. If the scorecard gets worse, you roll back and try a different direction. This workshop is structured as a hill climb: v1 → v2 → v3, one decision at a time, each justified by the numbers that came before it.

---

## What you'll touch in Foundry

| Surface | What we use it for | When in the tutorial |
|---|---|---|
| **Foundry Portal** (low-code) | Provision project, browse the model catalog, try a prompt in the playground, review evals/red-team results, compare agent versions side-by-side | Steps 0, 1, and 8 |
| **Foundry SDK** (code-first, Python) | Build the agent, route between models, run evals, kick off fine-tuning, deploy versions | Steps 2–7 |
| **Foundry Skills** (AI-assisted code, e.g. Copilot CLI's `microsoft-foundry` skill) | Discover available models, deploy a model with one prompt, set up RBAC, scaffold evaluator code | Step 3 (model selection) and Step 6 (fine-tune) — but useful everywhere |

> **Two MCP tools you should know:** the Foundry MCP exposes `models_list`, `model_get`, `agent_get`, `evaluation_run`, and more. The `microsoft-foundry` skill in Copilot CLI wraps these. Anywhere this tutorial says *"ask the Foundry skill to…"* you can also call those MCP tools directly.

---

## Steps

| # | Step | Surface | What moves on the scorecard |
|---|---|---|---|
| 0 | [Prereqs & project](./00-setup.md) | Portal + CLI | Project provisioned · 5 deployments in `Succeeded` state |
| 1 | [Baseline in the playground](./01-baseline-portal.md) | Portal (low-code) | v1 intuition: ~5¢/task · 3.2s · tools not wired |
| 2 | [Baseline agent in VS Code](./02-baseline-sdk.md) | SDK | **v1 measured: quality 0.41 · $0.023/task · 12.5s p50** |
| 3 | [Model selection with the Foundry Skill](./03-model-selection.md) | AI-assisted | Router deployed · one model per task · nano at 180ms |
| 4 | [Synthetic dataset generation](./04-synthetic-data.md) | SDK | Eval set grown from 20 seed rows → 170 rows |
| 5 | [Evaluations: curated, batch, online](./05-evaluations.md) | SDK | **v2: quality 0.45 · $0.006/task · 11.0s** (+10% q, −74% cost) |
| 6 | [Fine-tune `gpt-4.1-mini` for policy (distillation)](./06-finetune.md) | SDK + Skill | **policy-FT: quality 0.49 · $0.003/task · 5.1s** (gpt-4.1 teacher → mini student) |
| 7 | [Assemble the multi-model agent (v3)](./07-multi-model-agent.md) | SDK | **v3-final: quality 0.46 · $0.006/task · 6.5s** (+12% quality, −74% cost, −48% latency vs v1) |
| 8 | [Back to the portal — evals, red team, versions](./08-portal-review.md) | Portal | Compare v1 vs. v2 vs. v3 side-by-side |

---

## Files in this folder

```
workshops/foundry-models-e2e/
├── README.md                      ← you are here
├── 00-setup.md
├── 01-baseline-portal.md
├── 02-baseline-sdk.md
├── 03-model-selection.md
├── 04-synthetic-data.md
├── 05-evaluations.md
├── 06-finetune.md
├── 07-multi-model-agent.md
├── 08-portal-review.md
├── 99-recap.md
├── sample-data/                   ← full asset map in [`sample-data/README.md`](./sample-data/README.md)
│   ├── README.md                  ← workload-intent map + per-file purpose + LLM-as-judge rubric
│   ├── travel-policy.md           ← the 2-page sample policy (text source-of-truth)
│   ├── wwi-travel-policy.html     ← glossy printable policy handbook → rendered to `assets/00-policy.png`
│   ├── carmen-parking-receipt.html ← branded receipt mock → rendered to `assets/00-receipt.png` (vision input)
│   ├── eval-seed.jsonl            ← 20 curated rows (ground truth)
│   ├── eval-full.jsonl            ← *(generated by Step 4)* ~200-row eval set
│   ├── eval-policy-only.jsonl     ← policy slice for Step 6 sanity checks
│   ├── synthetic-prompts.jsonl    ← seed prompts for §4 generation
│   ├── policy-ft-train.jsonl      ← 91 rows (84 distilled from gpt-4.1 + originals)
│   ├── policy-ft-val.jsonl        ← 23 held-out validation rows
│   └── carmen-trace.json          ← the on-stage demo input
├── slides/                        ← 45-minute training deck
└── code/
    ├── requirements.txt
    ├── s02_config.py             ← shared deployments + pricing
    ├── s02_tools_mock.py         ← mocked flight/hotel/booking tools
    ├── s02_scorecard.py          ← prints the progress bars
    ├── s02_baseline_agent.py     ← v1: gpt-4.1 does everything
    ├── s03_router.py             ← gpt-4.1-nano router
    ├── s04_generate_synthetic.py ← grow the eval set
    ├── s05_multi_model_agent.py  ← v2/v3: planner + router + mini + ft
    ├── s05_run_eval.py           ← curated + batch eval driver
    ├── s06_finetune_policy.py    ← fine-tune gpt-4.1-mini on policy QA
    ├── s06_expand_ft_data.py     ← distillation pipeline: gpt-4.1 teacher generates training labels
    ├── s06_policy_only_eval.py   ← isolated base-vs-FT scorecard (deterministic, no LLM judge)
    ├── s99_replay_demo.sh        ← interactive demo-replay driver (see DEMO.md)
    └── generated/                 ← all eval_results_*.json + traces (gitignored)
```

Start with **[Step 0 — Prereqs & project](./00-setup.md)**. When you finish Step 8, head to **[99 — Recap](./99-recap.md)**.

---

## Re-running for a clean recorded demo

Both replay paths below ultimately read **real eval JSON from real Azure
runs** — they differ only in *which* run, and how reproducible it is:

- **`session/`** — a frozen cache of the **original BRK230 session run**,
  hand-promoted into the agent tree. The BRK230 agent's *session*
  mode reads from here so rehearsals and recordings stay bit-for-bit
  reproducible forever. **Do not modify these files** — that's the
  reference build you'll always be able to fall back to.
- **`generated/`** — the run *you* want the agent to walk through. It
  starts out as a copy of the BRK230 run too, but **you're encouraged to
  replace it with your own numbers** any time you re-run the workshop.
  Nothing automatic touches this folder — you copy your eval JSONs in
  when *you* decide they're a good run, and they stay there until you
  choose to overwrite them.

### Option A — BRK230 demo replay (recommended for recordings)

A custom Copilot agent (**`@BRK230 Demo Replay`**) replays the entire
5-demo BRK230 flow end-to-end in chat, off whichever set of eval JSONs
you point it at — no Azure calls, no waiting on fine-tunes during the
recording itself. This is what we use for rehearsals and the recorded
session.

See **[DEMO.md](./DEMO.md)** for the full guide: how to invoke the agent,
the two modes (session vs live), how `narrative.json` drives every
scorecard, and how to refresh the live numbers from a fresh workshop
run.

### Option B — Re-run the code path against real Azure

Once you've completed the workshop once (resources provisioned, FT model
deployed, datasets generated), you can replay the **code-only path** in
~20 minutes against your live deployments to regenerate clean scorecards
— no setup, no fine-tuning, no portal clicks.

```bash
cd workshops/foundry-models-e2e/code
source ../.venv/bin/activate
./s99_replay_demo.sh           # interactive: ENTER to run each stage, s=skip, q=quit
```

This writes fresh `eval_results_*.json` files into
[code/generated/](./code/) (gitignored). To make those numbers visible
to the BRK230 demo agent, **manually copy them** over the matching files
in `.github/agents/brk230-demo/generated/`:

```bash
cp code/generated/eval_results_v1-curated.json \
   ../../.github/agents/brk230-demo/generated/
# ...repeat for v1-demo, v2-demo, v3-demo
```

The next time the agent loads in *live* mode it'll notice the new files,
rebuild `narrative.json`, and start citing your numbers instead. **The
`session/` folder is never touched** — it remains the original BRK230
cache for reproducible replays.

> **Set targets that match *your* SLA.** The four `targets` in
> `generated/narrative.json` (quality, cost, latency, policy) drive every
> ✅ / 🚨 in the scorecards. Defaults are tuned for the BRK230 demo
> (Quality ≥ 0.80 · Cost ≤ $0.008 · Latency ≤ 15.0s · Policy ≥ 0.80) so
> v1 lights up red across the board and v3 clears all four. Edit them in
> `generated/narrative.json` to match the SLA your stakeholders would
> sign off on — the scorecards re-render against your numbers on the
> next agent load. **`session/narrative.json` is locked** and should not
> be edited; it preserves the original BRK230 session targets so the
> recorded replay never drifts.

> **Regenerate the playbook from your run.** [PLAYBOOK.md](./PLAYBOOK.md)'s
> meta-table and headline numbers are derived from the same
> `generated/narrative.json` the agent reads. After you copy your eval
> JSONs into `generated/`, run
> [`code/s99_rebuild_playbook.sh`](./code/s99_rebuild_playbook.sh) and
> splice its output into PLAYBOOK — so the playbook always tells *your*
> story, not ours.

### Conventions used by the replay tooling

- **`code/generated/`** — every eval result, trace dump, and intermediate artifact lands here. The folder is `.gitignore`d so nothing committed gets dirty. Wipe with `rm -rf code/generated` for a full reset.
- **Timestamped result files** — the replay script names outputs `eval_results_<label>-<UTC-timestamp>.json` so prior runs are never clobbered and runs can be diffed.
- **`s06_expand_ft_data.py` is now idempotent.** Earlier versions read and wrote the same `policy-ft-{train,val}.jsonl` paths, which silently *doubled* the dataset on every re-run. The fixed version reads optional seeds from `policy-ft-seeds-{train,val}.jsonl` and always overwrites outputs fresh. Safe to re-run any number of times. See header of [`code/s06_expand_ft_data.py`](./code/s06_expand_ft_data.py).

---

## Best Practices

Hard-won lessons captured live as we ran this workshop on stage. Each one is a small lever that pays back many times over a recorded demo, a sales call, or an attendee's first hands-on. Apply these before you hit "go".

### Right-size the evaluation dataset for the venue

The same agent deserves different eval datasets at different moments. Don't run the 173-row `eval-full.jsonl` during a stage demo — it's noisy, slow, and the audience can't read the JSON anyway. Match dataset size to purpose:

| File | Rows | Purpose | Wall-clock (concurrency=10) | TPM needed |
|---|---|---|---|---|
| `eval-seed.jsonl` | 20 | Inner-loop smoke test while you iterate on a prompt | <30 s | planner ≤ 50K, others ≤ 10K |
| `eval-demo.jsonl` | **50** ⭐ | Stage default for v1 vs v2 vs v3 scorecard comparisons | ~60–90 s | planner ≤ 125K, others ≤ 30K |
| `eval-full.jsonl` | 173 | Offline / CI / overnight thoroughness | 3–5 min | planner ≥ 300K, others ≥ 100K |

**Why 50 is the sweet spot for a demo:**
- Detects a ~15% quality delta at 95% CI (enough to separate v1 / v2 / v3 cleanly)
- 5–8 examples per intent bucket → failure modes are *legible* when you open the JSON on stage
- Completes in under 90 s so the audience doesn't tab away
- Rerun variance is low enough that two consecutive runs won't swap your winners

`eval-demo.jsonl` is built deterministically (seed=42) from `eval-full.jsonl` — 20 seed rows verbatim plus 10/10/10 across plan_trip / policy_question / receipt_expense.

### Provision deployment TPM for parallel evaluation

The `azure-ai-evaluation` SDK runs ~10 evaluator workers concurrently, and the v2/v3 agents fan each row to up to four deployments with planner loops of 2–6 calls. If any deployment is provisioned at the default 10K TPM, you will see **every row return identical 30 s latency, $0.000 cost, and ~0.25 quality** — the OpenAI SDK silently absorbs the 429s with backoff and returns an empty `output_text`. That is a poisoned signal, not a model verdict.

Minimums for `eval-demo.jsonl` (50 rows, concurrency 10):

| Deployment | Minimum | Recommended for live demo |
|---|---|---|
| `planner-gpt41` | 125K | 200K (covers parallel v1+v2 runs + judge phase) |
| `router-nano` | 30K | 50K |
| `mini-vision` | 30K | 50K |
| `policy-mini-base` | 30K | 50K |
| `auto-router` *(optional, Step 8 stretch)* | 50K | 100K (also covers 173-row offline run) |

`s00_setup.sh` provisions everything at 10K by default — bump in the portal under **Build → Models → Deployments → Edit → Tokens per minute rate limit** before Step 5.

**Smoke-test for throttling** after any eval run:
```bash
jq -r '.rows[] | ."outputs.latency_s"' generated/eval_results_<label>.json \
  | sort -n | awk 'BEGIN{c=0} {a[c++]=$1; s+=$1}
                   END{print "p50="a[int(c*0.5)], "p90="a[int(c*0.9)], "max="a[c-1]}'
```
Healthy run: `p50 ≠ p90 ≠ max`. Throttle artifact: pathologically flat (e.g. `p50=30 p90=30 max=30`).

### Trust the local JSON as your inner-loop signal

Every `s05_run_eval.py` run prints a `📊 Portal:` URL. That URL is a stakeholder artifact — it appears in the portal after a delay and is the right view for **Step 8**'s version-compare narrative. It is **not** your dev inner loop.

The dev inner loop is the 40 KB file written next to the script: `code/generated/eval_results_<label>.json`. Three `jq` recipes get you everything you need without leaving VS Code:

```bash
# Headline
jq .metrics generated/eval_results_v1-curated.json

# What broke (schema failures)
jq -r '.rows[] | select(."outputs.schema.schema_score" < 1) | "\(."inputs.id") \(."inputs.intent")"' \
  generated/eval_results_v1-curated.json

# Why (judge reasoning on low scorers)
jq -r '.rows[] | select(."outputs.judge.judge_score" <= 0.4) | ."outputs.judge.reason"' \
  generated/eval_results_v1-curated.json
```

In our live run, the third recipe surfaced "every `policy_question` row failed for the same reason" in under five seconds — the exact motivation for Step 6's fine-tune, derived from local artifacts, no portal round-trip needed.

### Name deployments by job, not by model

`planner-gpt41`, `router-nano`, `mini-vision`, `policy-mini-base` — not `gpt-4.1-deployment-3`. When a new model lands in the catalog, swapping it in becomes a one-line config change (`DEPLOY_PLANNER = "planner-gpt45"`) and your code, evals, and traces all keep working. This is the operational backbone of Challenge #5 ("the landscape keeps changing") and the reason Step 6's fine-tune swap is `USE_FT_POLICY = True`, not a refactor.

### Pre-warm the Operate dashboards with realistic load

The portal monitoring tabs are uninteresting with no traffic. Set up a hosted **Prompt Agent** once and then drive it with the load tester an hour before the Step 8 walk-through:

```bash
# one-time: create the concierge-loadtest Prompt Agent in the project
../.venv/bin/python code/s08_agent_setup.py \
  --name concierge-loadtest --model planner-gpt41 --temperature 0.2

# 2 h continuous load against the hosted agent (attach App Insights first)
nohup ../.venv/bin/python -u code/s08_loadtest_agent.py \
  --duration 2h --base-rpm 5 --spikes 4 --lulls 2 --workers 4 \
  --label monitor-demo \
  > code/generated/loadtest_agent_monitor-demo.out 2>&1 &
```

The loadtester invokes the hosted agent through the Responses API (`agent_reference`) and wires `AIProjectInstrumentor` + Azure Monitor exporter, stamping every span with WWI custom dimensions (`wwi.prompt.class`, `wwi.prompt.kind`, `wwi.expected.is_policy`, `wwi.expected.is_adversarial`, `wwi.run.*`). By the time you're in [`08-portal-review.md`](./08-portal-review.md), **Agents → concierge-loadtest → Tracing** (and the attached App Insights Logs) has thousands of real spans to filter on — content-filter blocks, latency outliers, intent-distribution shifts — that motivate the closing "hand-rolled → managed Eval Rubric" narrative.


