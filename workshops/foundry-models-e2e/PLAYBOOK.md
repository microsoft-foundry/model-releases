# WWI Travel Concierge — Model Optimization Playbook

> *A retrospective + a reusable playbook, distilled from 6h 40m of live build
> time on May 29, 2026. Every pattern below has scars to prove it.*

> **📝 About these numbers.** The headline cells in the meta-table below
> and the scorecards the BRK230 demo agent renders are derived from
> [`.github/agents/brk230-demo/generated/narrative.json`](../../.github/agents/brk230-demo/generated/narrative.json),
> which in turn comes from the four `eval_results_*.json` files captured
> at the end of our May 29 run. **Two of those runs (`v1-demo` and
> `v2-demo`) are mildly throttled** — latency sits in the high-20s/low-30s
> instead of the sub-10s we measured pre-bump. We kept them anyway,
> because the smoking gun for **Pattern 4 — *Pre-warm provisioning*** is
> only visible if the audience can open the actual file and see
> `p50 ≈ p90 ≈ max`. *That's the lesson.*
>
> If you re-run the workshop and want the playbook to reflect *your*
> numbers, run [`code/s99_rebuild_playbook.sh`](./code/s99_rebuild_playbook.sh)
> — it regenerates the meta-table and the Hills Are Alive block from
> whatever `generated/narrative.json` currently says.

---

## Meta Moment: We Hill-Climbed Building This Demo!

Before you read the playbook, look at how *the workshop itself* hill-climbed.
We didn't write this in one shot. We wrote it the same way we tell you to
write production agents: **make a measurement, follow the signal, refuse to
ship until the number moves.**

| Phase | Wall-clock | What changed | The signal that moved | Lesson cashed in |
|---|---|---|---|---|
| **🌱 Setup**       | 08:04 → 08:10  | Bootstrap RG + Foundry project + 4 deployments via `s00_setup.sh` | 4/4 deployments Succeeded in 111s | "Name deployments by *job*, not by *model*." |
| **🎬 v1 Playground** | 08:15 → 08:20  | Carmen + receipt + planner-gpt41 in the portal | 7.4s wall-clock — *"it works on Carmen"* | Demos that "feel good" hide everything. |
| **🧱 v1 SDK**       | 08:23           | Same flow, in code | 16.5s · $0.0195 · **Quality unknown** | A demo without a number is a vibe. |
| **🧭 Router wired** | 08:29           | `gpt-4.1-nano` triages intent | 5/5 correct intents, warm p50 1.25s | Cheap models are great traffic cops. |
| **🧪 Eval set**     | 08:38 → 08:39  | 173 synthetic rows across 6 axes | We could finally *say* 0.49 | "Synthetic data + judge = reproducible truth." |
| **🩹 v1 curated**   | 08:48           | 20-row eval → 0.49 Q, 13.0s | **All 6 policy rows failed identically** | One drill-down beats a thousand vibes. |
| **🔥 Throttle crash** | 08:55 *(discarded)* | 173-row v2 eval at 10K TPM defaults | 162× 429s → Q=0.26, $0.000 (poisoned) | "Pre-warm provisioning — TPM is the silent dependency." |
| **⚖️ Right-size**    | 08:55           | `eval-demo.jsonl` (50 rows, balanced) + TPM bump | Cost / time per eval ÷4 | Match the eval set to the *cadence* you want, not the *ambition*. |
| **✅ v1-demo**       | 08:52           | 50-row clean run — *but TPM still tight* | Q **0.644** · $0.010 ✅ · **29.1s** 🚨 (throttled — see Pattern 4) | A clean *signal* unlocks the next move — even when one dial is still red. |
| **🐛 v2 zero bug**   | 08:54 *(discarded)* | `USE_FT_POLICY=True` before FT existed | All 50 rows empty — 404 DeploymentNotFound | "Flag defaults should match the *current* deployment reality." |
| **🪶 v2-demo**       | 08:57           | Multi-model split, FT off | Q **0.768** · **$0.0055** ✅ · **30.2s** 🚨 · 📜 0.28 🚨 | Cost halves and quality climbs — but the custom evaluator says policy *regressed*. |
| **🎨 Scorecard polish** | 09:18 → 09:28  | Δ column, baseline flag, helper extracted | v2's cost cut visibly half a bar in green | Pretty deltas are *operational*, not cosmetic. |
| **📜 Custom evaluator** | 09:38       | `s05_policy_adherence_evaluator.py` (5-axis rubric) | A new line appeared on every card | "If you can't see the failure, you can't fix it." |
| **🛠️ Fine-tune**     | 09:40 → 10:30  | 24 rows × 3 epochs on `gpt-4.1-mini` | `succeeded · trained_tokens=22962` | The model is the cheap part. The data is the work. |
| **🛰️ OTel pipeline** | 10:30 → 10:55  | Hosted Prompt Agent + `wwi.*` custom dims + App Insights | Patched a `NonRecordingSpan` SDK bug along the way | "Wire observability *before* you need it." |
| **🌊 2 h loadtester** | 11:00 →        | Sinusoidal · spikes · lulls vs `concierge-loadtest` | 405 ok / 1 err / 39 content_filtered at t+54m | Real dashboards need real traffic. |
| **💸 Developer SKU** | 11:46           | `06-finetune.md` §6.5 default flipped | Idle FT cost: $/day → ¢/day | "Default to the cheap tier in dev. Always." |
| **🚢 FT deployed**   | 14:35           | `policy-mini-ft` · DeveloperTier · 100 cap | Status: Succeeded | The whole story was waiting on one deployment. |
| **🎯 v3-demo**       | 14:42           | `USE_FT_POLICY=True` (one boolean) · TPM bumped between v2 and v3 | **📜 Policy 0.28 → 0.82 (+190%)** · Q 0.83 · $0.005 · **11.2s** (latency still > 8s target) | One flag flip clears policy + cost; latency is the *next* hill. |
| **🏁 Three-up card** | 14:44           | `render_scorecards.py v1 v2 v3` | The audience's eyes go to the green checks | Ship the *picture*, not the spreadsheet. |

> **The meta-punchline:** even *this README* hill-climbed. v1 was a script
> that crashed at 10K TPM. v3 is a 50-row deterministic eval with three
> evaluators and a custom rubric. **Same pattern. Three iterations.**

---

# MODEL OPTIMIZATION PLAYBOOK

## 🧰 The right model for the right job *(the analogy)*

> Think of a **kitchen brigade**, not a single celebrity chef.
>
> ```
>            🧑‍🍳 Executive Chef           ← planner-gpt41
>             (composes the dish,            big, expensive, only when
>              owns the experience)          the work *needs* a generalist
>
>     🥕 Prep cook        🧀 Garde-manger     ← router-nano · mini-vision
>     (fast triage)       (specialist plate)    cheap, fast, specialized
>
>            👨‍🎓 Sommelier in training         ← policy-mini-ft
>             (knows your wine list             small, fine-tuned, deep on
>              by heart — yours, not Bon          your domain — not the world's
>              Appétit's)
> ```
>
> One celebrity chef cooking every dish is **how a v1 baseline looks**: a
> 16.5-second, 2 700-token, $0.02 answer to *"what's the per-diem?"*
>
> A brigade is **how a v3 looks**: 6.7 s · $0.005 · 13 of 17 policy
> questions correct with citations. Same kitchen. Different staffing.
>
> **The Playbook below is how you hire your brigade.**

---

## Pattern 1 · Name deployments by job, not by model

```
❌ gpt-4.1-deployment-3        ✅ planner-gpt41
❌ openai-deployment-prod-eu   ✅ router-nano
❌ ft-policy-2026-may-v2       ✅ policy-mini-ft
```

| Why it matters | What it unlocks |
|---|---|
| Swapping `gpt-4.1` → `gpt-4.5` is a **one-line config change** | `DEPLOY_PLANNER = "planner-gpt45"` and your code, evals, traces all keep working |
| Routing logic stays declarative | The agent doesn't know — or care — what's behind `policy-mini-*` |
| **Step 6 → 7 v3 swap was one boolean** | `USE_FT_POLICY = True` — no refactor, no rename, no broken traces |

> 🔑 **Rule of thumb:** if you have to grep for a model name when a new one drops, your deployment names are wrong.

---

## Pattern 2 · A demo without a number is a vibe

| Vibe-only ("v1 playground") | Measured ("v1-demo") |
|---|---|
| *"7.4s, looks great!"*         | Q **0.42** · $0.010 · 9.1s — over 50 rows |
| Carmen says yes               | 6 of 6 policy questions say `<hallucinated number>` |
| Stakeholders nod              | Engineers know **exactly which axis to optimize next** |

```
   no eval        →   ░░░░░░░░░░    ?  ?  ?
   eval-curated   →   █████░░░░░    0.49  (you can see)
   eval-demo      →   ████░░░░░░    0.42  (you can compare)
```

> 🔑 **Rule of thumb:** before you optimize *anything*, run **eval-on-50-rows-with-a-baseline** at least once. If the bar fills, you haven't earned it back yet.

---

## Pattern 3 · Synthetic data is your eval set's flywheel

> 20 hand-curated rows → seed.
> + LLM-generated paraphrases / adversarials / edge cases → 173 rows.
> + Subset stratified across **class × kind** axes → 50 deterministic demo rows.

```
   seed (20)  ──synthetic──▶  full (173)  ──stratified──▶  demo (50)
       │                          │                            │
   instructor-built          coverage breadth          repeatable in CI
```

| Stage | Cost | Use |
|---|---|---|
| **Seed** (20 rows) | hours of thought | Truth source. Never auto-touch. |
| **Full** (173 rows) | 3m 20s + judge tokens | Quarterly regression. |
| **Demo** (50 rows) | ~30s + judge tokens | Per-PR / per-experiment. |

> 🔑 **Rule of thumb:** if your eval set is too big to run on every change, **it doesn't exist** — it just *aspires* to.

---

## Pattern 4 · Pre-warm provisioning *before* the eval

The single most painful 30 minutes of our build:

```
   v2 first attempt:  10K TPM defaults × 4 deployments
                            ↓
                     162× 429 throttles
                            ↓
            Q=0.26, $0.000, all 30s flat — signal poisoned
                            ↓
                     ENTIRE RUN DISCARDED
```

The fix is one `az` command per deployment. The lesson is everywhere.

| Phase | Recommended baseline |
|---|---|
| Per-row dev/eval     | planner ≥ 300K TPM, others ≥ 100K TPM |
| Loadtest / monitor   | + base × 5 for spike headroom |
| Fine-tune deployment | **DeveloperTier** in dev (¢/day idle); Standard only in prod |

> 🔑 **Rule of thumb:** TPM is a silent dependency. A throttled eval looks identical to a broken eval — until you look at the error budget.

---

## Pattern 5 · Custom evaluators are how you *see*

The headline judge said v2 → v3 moved Quality by +0.05.
The custom **Policy Adherence** evaluator said v2 → v3 moved policy by **+190%**.

```
   Without custom evaluator:           With it:

   v2 ████░░░░░░  0.42                v2 ████░░░░░░  0.42
   v3 █████░░░░░  0.47                v3 █████░░░░░  0.47
                                       📜 v2  ███░░░░░░░  0.28  ❌
   ¯\_(ツ)_/¯                          📜 v3  ████████░░  0.82  🎯
   "did it work?"                      "yes — by 190% on the slice we cared about"
```

| Hand-rolled (`s05_*`) | Managed Eval Rubric (portal) |
|---|---|
| Lives in git, reviewed in PR | First-class versions, pinned to runs |
| You author the prompt | **Foundry auto-generates** from labeled examples + source doc |
| Stale when policy changes | **Adaptive** — point it at the Tracing tab, mark pass/fail, rubric tightens |
| Travel team & Legal team write their own copy | Published in **Evaluator catalog**, shared across projects |

> 🔑 **Rule of thumb:** every step that moved a needle in this workshop *started* with adding a new way to measure. Hand-roll the first one in code to learn the shape, graduate it into a Managed Eval Rubric for everyone else.

---

## Pattern 6 · Wire observability *before* you need it

The hosted Prompt Agent + OTel pipeline took 25 minutes to wire (including
patching an SDK NonRecordingSpan bug) and delivered:

```
   Foundry portal:  Agents → concierge-loadtest → Tracing
                       ↓
   App Insights:    traces | where customDimensions["wwi.workload"] == "monitor-demo"
                          | summarize p95(wwi.run.latency_s) by wwi.prompt.kind
```

The `wwi.*` custom dimensions are the operational equivalent of the
**Policy Adherence evaluator**: a slice the headline metric can't see.

| Dimension | Pivot it enables |
|---|---|
| `wwi.prompt.class`         | normal / edge / adversarial mix shift |
| `wwi.prompt.kind`          | per-intent latency (policy vs plan vs vision) |
| `wwi.expected.is_policy`   | route policy QA without trial subscription |
| `wwi.run.content_filtered` | adversarial blocks as a *positive* signal |

> 🔑 **Rule of thumb:** if your first production incident is when you discover your tracing isn't wired, you've shipped two outages — the user's and yours.

---

## Pattern 7 · Defaults are policy. Choose them on purpose.

Three live bugs, all from defaults:

| Default | What broke | What we changed |
|---|---|---|
| `DEPLOY_POLICY_FT` ←(env) → `True` | v2 eval returned empty answers (FT didn't exist yet) | Default `USE_FT_POLICY = False` until Step 6 |
| Fine-tune deploy SKU `Standard` | $/day for an idle eval deployment | Default **DeveloperTier** in workshop/dev docs |
| 4 × 10K TPM at creation | 162 throttles, poisoned eval | Bump in `s00_setup.sh` + Best Practices recipe |

> 🔑 **Rule of thumb:** every default ships a value judgement. If you can't articulate why your default is what it is, somebody else's accident is.

---

## Pattern 8 · One boolean is the punchline

The entire v2 → v3 transition is *literally* this:

```python
# code/s05_multi_model_agent.py
- USE_FT_POLICY = False  # v2
+ USE_FT_POLICY = True   # v3
```

That's it. No code refactor. No new prompt. No new evaluator. No new dataset.

Because:
- Deployments are named by job (Pattern 1).
- The eval set is reproducible (Pattern 3).
- TPM was pre-warmed (Pattern 4).
- The Policy evaluator measured the right slice (Pattern 5).
- Tracing was already wired (Pattern 6).

When **all the other patterns are in place**, optimization collapses to
flipping a boolean and re-running the eval. **That is the goal.**

---

## 🎼 The Hills Are Alive with the Sound of … Metrics 🎶

```
                        🏔️  v3-demo
                      ╱  ┃  🎯 Q 0.83
                    ╱    ┃  📜 0.82  ✅
                  ╱      ┃  💸 $0.005 ✅
            🏔️ v2-demo   ┃  ⚡ 11.2s  (next hill)
         ╱  ┃  🎯 Q 0.77   ┃
       ╱    ┃  📜 0.28 🚨 ┃   ← one boolean flip
   🏔️ v1   ┃  💸 $0.006 ✅┃     fixed policy + held cost,
   ┃ Q 0.64  ┃  ⚡ 30.2s 🚨 ┃     and a TPM bump cleared
   ┃ 📜 0.36  ┃            ┃     half the latency hill.
   ┃ $0.010  ┃            ┃
   ┃ 29.1s 🚨┃            ┃
```

> *Climb every hill·climb every dial,*
> *measure every slice along the way…*
> *Each policy answer, each per-token charge,*
> *each P95 you log — they sing.* 🎵
>
> Because in the end the unit of progress isn't a model release.
> It's a **model decision**, made **per task**, against a **per-task scorecard** —
> and a brigade of small specialists, each humming the right note.
>
> So go forth, name your deployments, write that custom evaluator,
> wire that one extra trace attribute, and let your dashboards sing.
>
> 🎤 **The hills are alive. Pick up a metric and join the chorus.** 🎤

---

# 🧗 Bonus: How the `microsoft-foundry` Skill Could've Climbed Faster

We hand-rolled most of this workshop with `az`, the SDK, and a fair amount of
trial-and-error. The `microsoft-foundry` agent skill ships **15 specialized
sub-skills** that map almost 1:1 onto the hills we climbed. Here's how
they line up — load each one with the **read_file** tool when you want
Copilot to drive that part of the loop for you.

## 🧭 Discovery → Provisioning *(replace our manual `s00_setup.sh`)*

| Hill we climbed | Sub-skill | What it automates |
|---|---|---|
| "Which project, where?" | **`project/create`** | New Foundry project (public) with sane defaults |
| "VNet for the security team?" | **`resource/private-network`** | BYO / Managed / Hybrid VNet isolation with validation |
| Picking models, regions, SKUs, RAI policy | **`models/deploy-model`** | Routes to `preset` (quick), `customize` (full control), or `capacity` (region scan) |
| "10K TPM throttle disaster" (we lived this!) | **`quota`** | Pre-flight quota checks, capacity planning, increase requests |
| RBAC for CI/CD identity | **`rbac`** | Role assignments for managed identities + service principals |

> 💡 If we'd loaded **`quota`** before our 173-row v2 eval, we'd have caught
> the 10K TPM defaults and saved the discarded run (08:55 in the table above).

## 🛠️ Model Customization *(replace our manual `s06_finetune_policy.py`)*

| Hill we climbed | Sub-skill | What it automates |
|---|---|---|
| Hand-curate 24 training rows, paraphrase, format | **`finetuning`** | Dataset prep, **grader calibration**, large-file upload, training, **checkpoint selection**, deploy, evaluate |
| Pick SFT vs DPO vs RFT (we chose SFT blindly) | **`finetuning`** | Decision guide + technique-specific quickstarts |
| Catch overfit at epoch 2 vs 3 | **`finetuning`** | **Training-curve analysis** built into the workflow |
| Default to Standard SKU (the bug we fixed!) | **`finetuning`** + **`models/deploy-model`** | Tier-aware deployment with cost guidance |

> 💡 The skill bakes in *grader calibration* — exactly the
> "Policy Adherence" judge we hand-rolled in `s05_policy_adherence_evaluator.py`.

## 🏗️ Agent Building *(replace our `s08_agent_setup.py`)*

| Hill we climbed | Sub-skill | What it automates |
|---|---|---|
| Bootstrap `concierge-loadtest` Prompt Agent | **`create`** | Scaffolds hosted or prompt agents across MAF / LangGraph / custom Python or C# |
| Containerize + push to ACR + register version | **`deploy`** | Docker build, ACR push, agent create/update/clone — **with eval-suite setup baked in** |
| Single-turn smoke + multi-turn chat tests | **`invoke`** | Send messages, manage conversations, validate behavior |
| Voice / WebSocket agents (future Carmen demo?) | **`invocations-ws`** | Duplex `invocations_ws` protocol for real-time streams |

> 💡 If we'd loaded **`create` → `deploy` → `invoke`** for §8.PRE,
> the entire 25-minute "wire a Prompt Agent + patch NonRecordingSpan bug"
> detour would've been ~3 minutes of skill-driven scaffolding.

## 📊 Evaluation & Optimization *(replace our `s05_run_eval.py` loop)*

| Hill we climbed | Sub-skill | What it automates |
|---|---|---|
| 50-row deterministic eval + judge + custom evaluator | **`observe`** | Batch eval, failure analysis, **prompt optimization**, version comparison |
| Hand-rolled `s05_policy_adherence_evaluator.py` | **`observe`** | Drives the **`prompt_optimize`** MCP tool through the eval-driven workflow |
| "Make `policy-mini-ft` even better next quarter" | **`agent-optimizer`** | Scaffolds Python hosted agent for optimization, runs **Agent Optimizer jobs**, applies candidates locally, deploys via azd |
| Curate next eval set from production failures | **`eval-datasets`** | **Harvest production traces → eval dataset**, versioning, splits, regression detection, full trace→deployment lineage |
| Continuous eval on live traffic (Step 8.5!) | **`observe`** (Step 6: CI/CD & Monitoring) | Wires the **Continuous Evaluation** rule we manually pointed at the portal |

> 💡 **`eval-datasets`** is the loop-closing skill we *almost* wrote by hand
> in §8.6 — the "harvest the `pii_fishing` cluster from App Insights into
> the next eval-v2.jsonl" workflow.

## 🛰️ Observability *(complement our `wwi.*` OTel custom dimensions)*

| Hill we climbed | Sub-skill | What it automates |
|---|---|---|
| Auto-discover App Insights conn string | **`trace`** | Query traces via App Insights `customEvents`, **correlate eval results to specific responses** |
| Pivot by `wwi.prompt.class` / `wwi.run.content_filtered` | **`trace`** | KQL helpers + analyze latency / failure patterns |
| 405 ok / 1 err loadtester triage | **`troubleshoot`** | View hosted agent logs, query telemetry, diagnose failures |
| "Why did this Carmen run latency 12 s?" | **`trace`** + **`troubleshoot`** | Span-level drill-down from a single eval row → deployment logs |

> 💡 **`trace`** explicitly correlates eval rows ↔ App Insights `customEvents`.
> That's the connective tissue our hand-rolled `wwi.run.*` attributes
> *try* to provide via Logs queries.

## 🎼 The Optimized Hill-Climb — what it would've looked like

```
┌──────────────────── microsoft-foundry skill, end to end ────────────────────┐
│                                                                              │
│  project/create   ──▶  models/deploy-model  ──▶  quota (pre-flight)          │
│       │                       │                       │                      │
│       ▼                       ▼                       ▼                      │
│  create (agent)  ──▶  deploy (agent + eval-suite)  ──▶  invoke (smoke)       │
│       │                       │                       │                      │
│       ▼                       ▼                       ▼                      │
│  observe (eval + optimize)  ──▶  finetuning  ──▶  deploy (FT, Developer SKU) │
│       │                       │                       │                      │
│       ▼                       ▼                       ▼                      │
│  eval-datasets (harvest)  ──▶  observe (continuous)  ──▶  trace / troubleshoot
│                                                                              │
└─ Each box is one `read_file` call on the sub-skill. Copilot drives the rest. ┘
```

## 🪜 Mapping it back to our 6h 40m

| Workshop hill (from the meta table) | Sub-skill that would've shortened it |
|---|---|
| 0.x Setup (`s00_setup.sh`)             | **`project/create`** + **`models/deploy-model`** |
| 5.2a Throttle crash                    | **`quota`** (pre-flight) |
| 5.7 Custom Policy Adherence evaluator  | **`observe`** (with `prompt_optimize`) |
| 6.1–6.4 Fine-tune                      | **`finetuning`** (with grader calibration + curve analysis) |
| 6.5 Developer SKU realization          | **`finetuning`** + **`models/deploy-model`** customize path |
| 8.PRE Prompt Agent + OTel pipeline     | **`create`** → **`deploy`** + auto-wired trace/observe |
| 8.5 Continuous monitoring              | **`observe`** Step 6 (CI/CD & Monitoring) |
| 8.6 "Next eval set from production"    | **`eval-datasets`** (trace-to-dataset) |

> 🎯 **The TL;DR for next time:** the next workshop run can replace our
> "discover the right `az` command + patch the SDK bug + write the eval
> harness" loop with: *"read the sub-skill, let Copilot drive, review the
> diff, hit the green button."* The hill-climb stays the same — the
> *time-per-hill* drops by an order of magnitude.

