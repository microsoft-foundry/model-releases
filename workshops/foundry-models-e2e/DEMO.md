# Speaker Demo Guide — Right Model, Right Job

<!--
PURPOSE:
This file is the speaker + recording guide for the FIVE short demo
clips that get cut into the BRK230 deck. It is meant to be used
*while running the workshop end-to-end* against the WWI Concierge
scenario — you run each workshop step, verify it works, and capture
the relevant clip at the points called out below. There is no
automation skill driving the demos; pacing and framing live here.
Source of truth for the five-demo lineup: ../../.do-not-commit/Notes-v1.md.
-->


> Five short pre-recorded clips, all sourced from a single end-to-end
> run of this workshop so they share one scenario (WWI Concierge ·
> Carmen · Berlin trip · 170-row eval set) and one Foundry project.
> Total airtime ≈ **12 min** of the 45-min BRK230 session.
> Source material: [README.md](./README.md) · Workshop steps 2–6.
> Scenario: **WWI Concierge** — Carmen needs to book a business trip to Berlin.

---

## Table of Contents

- [How to use this guide](#how-to-use-this-guide)
- [The five clips at a glance](#the-five-clips-at-a-glance)
- [Setup checklist (do this before you record)](#setup-checklist)
- [Recording workflow](#recording-workflow)
- [D1 — Baseline with one frontier model (~1:30)](#d1--baseline-with-one-frontier-model-130)
- [D2 — Foundry catalog + leaderboard + benchmarks (~2:00)](#d2--foundry-catalog--leaderboard--benchmarks-200)
- [D3 — Multi-model decomposition (~2:30)](#d3--multi-model-decomposition-230)
- [D4 — Adaptive evaluation with a rubric (~3:00)](#d4--adaptive-evaluation-with-a-rubric-300)
- [D5 — Distillation + fine-tune + after-scorecard (~3:30)](#d5--distillation--fine-tune--after-scorecard-330)
- [Recovery notes](#recovery-notes)

---

## How to use this guide

The workflow this file assumes:

1. **Run the workshop end-to-end first.** Walk through
   [`00-setup.md`](./00-setup.md) through [`08-portal-review.md`](./08-portal-review.md)
   on the WWI brand and confirm every step works for you in isolation.
   The setup checklist below is the *exit state* of that run.
2. **Pre-stage the eval runs and the fine-tune** so every clip can be
   captured from a settled environment — no waiting on jobs mid-clip.
3. **Record each clip as a separate take.** Don't try to chain them.
   Each clip is anchored to specific workshop steps (called out in its
   header) so you can re-run just that slice for clean footage.
4. **Use the transcript as a narration script, not a teleprompter.**
   The cue sheet under each clip is the timing contract; aim for the
   time markers, not the exact wording.
5. **Keep every clip silent-cuttable.** Hold the final frame (scorecard
   or result card) for ~2 s so the speaker can cut at any beat. Mouse
   pointer enlarged, terminal font ≥ 18 pt, dark VS Code theme + light
   Foundry Portal theme for contrast, 1920×1080.

If a clip goes long, trim the narrative scaffolding before the
technical beats. The technical beats are the proof; the narrative is
the wrapper.

---

## The five clips at a glance

| ID | Stanza · slot | What it shows | Target | Source step(s) |
|---|---|---|---|---|
| **D1** | Stanza 2 — SELECT | Baseline strawman: one `gpt-4.1` answering every intent. The bar the rest of the talk knocks down. | ~1:30 | [`02-baseline-sdk.md`](./02-baseline-sdk.md) + [`code/s02_baseline_agent.py`](./code/s02_baseline_agent.py) |
| **D2** | Stanza 2 — SELECT | Foundry model catalog + leaderboard + benchmarks. Visual proof of breadth (frontier / small / domain / new entrants). | ~2:00 | [`03-model-selection.md`](./03-model-selection.md) |
| **D3** | Stanza 2 — SELECT | Multi-model decomposition: router-nano → policy-mini → planner-gpt-4.1, with a vision call. Cost/latency win, quality plateau on the policy slice. | ~2:30 | [`03-model-selection.md`](./03-model-selection.md) + [`code/s03_router.py`](./code/s03_router.py) + [`code/s05_multi_model_agent.py`](./code/s05_multi_model_agent.py) |
| **D4** | Stanza 3 — EVALUATE | Adaptive evaluation with a rubric (LLM-as-judge). Schema + rubric on the policy slice, failures clustered by axis. | ~3:00 | [`05-evaluations.md`](./05-evaluations.md) + [`code/s05_run_eval.py`](./code/s05_run_eval.py) + [`sample-data/eval-policy-only.jsonl`](./sample-data/eval-policy-only.jsonl) |
| **D5** | Stanza 4 — OPTIMIZE | Distillation + fine-tune of `gpt-4.1-mini` on the policy slice, hot-swap, re-run, before/after scorecard. | ~3:30 | [`06-finetune.md`](./06-finetune.md) + [`code/s06_expand_ft_data.py`](./code/s06_expand_ft_data.py) + [`code/s06_finetune_policy.py`](./code/s06_finetune_policy.py) |

---

## Setup checklist

The items here are the exit state of a full workshop run. If anything
below is not true, go back to the corresponding workshop step and
finish it before recording. Treat this as the recording-day pre-flight.

### Environment

- [ ] Codespace (or local dev container) open, repo cloned to `workshops/foundry-models-e2e`.
- [ ] Python venv active: `source .venv/bin/activate`
- [ ] `.env` present and loaded — contains `FOUNDRY_PROJECT_ENDPOINT`.
- [ ] `az login` current; `az account show` shows the right subscription.

### Foundry project

- [ ] Project `wwi-concierge-demo` exists in **Sweden Central**.
- [ ] All five deployments show `Succeeded` in the portal:
  - `planner-gpt41` (gpt-4.1)
  - `router-nano` (gpt-4.1-nano)
  - `vision-mini` (gpt-4.1-mini)
  - `policy-mini-base` (gpt-4.1-mini)
  - `policy-mini-ft` (fine-tuned gpt-4.1-mini, from Step 6 — needed for D5)

### Eval + fine-tune pre-staged

Run these once before recording and keep the outputs handy. D1 needs
the baseline scorecard; D3 needs the multi-model scorecard; D4 needs
the policy-only eval rows in the portal; D5 needs the FT job in
`Succeeded` state and the after-scorecard.

```bash
cd workshops/foundry-models-e2e/code

# D1 — single-model baseline scorecard
python s02_scorecard.py --agent s02_baseline_agent \
    --eval ../sample-data/eval-seed.jsonl --label "v1-baseline"

# D3 — multi-model (no FT) scorecard, full eval
python s05_run_eval.py --agent s05_multi_model_agent \
    --eval ../sample-data/eval-full.jsonl --label "v2-batch"

# D4 — policy-only eval against the base policy model
python s05_run_eval.py --agent s05_multi_model_agent \
    --eval ../sample-data/eval-policy-only.jsonl --label "policy-base"

# D5 — after the FT job has Succeeded, flip USE_FT_POLICY = True in
# s05_multi_model_agent.py, then:
python s05_run_eval.py --agent s05_multi_model_agent \
    --eval ../sample-data/eval-policy-only.jsonl --label "policy-ft"
python s05_run_eval.py --agent s05_multi_model_agent \
    --eval ../sample-data/eval-full.jsonl --label "v3-final"
```

> [!NOTE]
> **All scorecard numbers in this file are placeholders.** The bars,
> quality scores, cost figures, latency values, and percentage deltas
> were drafted from the BRK230 notes before the workshop was run
> end-to-end on the WWI brand. Replace them with the real output from
> your own eval runs as you work through Steps 2, 3, 5, and 6. Look
> for the *Placeholder — replace* marker above each scorecard block,
> and sweep the inline numeric callouts in the transcripts as well.

*Placeholder — replace with the actual scorecards from your runs (D1 baseline · D3 multi-model · D4 policy-base · D5 policy-ft + v3-final).*

```
=== v1-baseline scorecard (D1) ===
Quality   ████░░░░░░  0.41
Cost      ██░░░░░░░░  $0.023/req
Latency   ██████░░░░  12.5 s p50

=== v2-batch scorecard (D3) ===
Quality   █████░░░░░  0.55           ← cost & latency down, policy slice still 0.47
Cost      █░░░░░░░░░  $0.012/req
Latency   ████░░░░░░   7.9 s p50

=== policy-base scorecard (D4) ===
Quality (policy slice)  ████░░░░░░  0.47
Top failure axes        geography · language · policy_trap

=== policy-ft scorecard (D5) ===
Quality (policy slice)  ███████░░░  0.68  ✅ (+0.21)
Cost                    held
Latency                 held

=== v3-final scorecard (D5 closing frame) ===
Quality   ██████░░░░  0.53  → 0.65 across full eval  (+12% over D1)
Cost      █░░░░░░░░░  $0.006/req                     (−74% vs D1)
Latency   ███░░░░░░░  6.5 s p50                      (−48% vs D1)
```

### Portal tabs pre-loaded

Have these pages open and **logged in** before you start each clip:

| Tab | URL path | Used in |
|---|---|---|
| **Tab 1** | Foundry Portal → project `wwi-concierge-demo` → **Models + endpoints** | D1, D3 |
| **Tab 2** | Foundry Portal → same project → **Model catalog** (with leaderboard tab) | D2 |
| **Tab 3** | Foundry Portal → same project → **Evaluations** | D4 |
| **Tab 4** | Foundry Portal → same project → **Fine-tuning** (job `wwi-policy-v1` Succeeded) | D5 |
| **Tab 5** | Codespace — terminal in `workshops/foundry-models-e2e/code/` | All clips |

### Files to have open in the editor (Tab 5)

- `code/s02_baseline_agent.py` — D1
- `code/s02_scorecard.py` — D1
- `code/s03_router.py` — D3
- `code/s05_multi_model_agent.py` — D3, D5 (the `USE_FT_POLICY` flag)
- `code/s05_run_eval.py` — D4
- `code/s06_expand_ft_data.py` — D5
- `sample-data/eval-policy-only.jsonl` — D4
- `sample-data/policy-ft-train.jsonl` — D5

---

## Recording workflow

Capture clips in workshop order so the Foundry project state moves
forward naturally between takes.

| Clip | Capture after running… | What you re-do on camera | Take length |
|---|---|---|---|
| **D1** | [Step 2 — Baseline SDK](./02-baseline-sdk.md) | Open `s02_baseline_agent.py`, run Carmen's request, cut to the baseline scorecard. | ~1:30 |
| **D2** | [Step 3 — Model selection](./03-model-selection.md) intro | Tour the Foundry catalog: filters, leaderboard, model card, Model Router + announcement banners. | ~2:00 |
| **D3** | [Step 3 — Model selection](./03-model-selection.md) full | Open `s05_multi_model_agent.py`, run Carmen's request, cut to the multi-model scorecard with the policy plateau called out. | ~2:30 |
| **D4** | [Step 5 — Evaluations](./05-evaluations.md) | Show the policy-only dataset, kick off (or replay) the eval in the portal, drill into one failing row. | ~3:00 |
| **D5** | [Step 6 — Fine-tune](./06-finetune.md) | Show distillation expansion, the Succeeded FT job, the `USE_FT_POLICY` swap, and the before/after scorecard. | ~3:30 |

Capture tips:

- **Record at 1920×1080 minimum** so portal tab and Codespace are
  legible side by side. If your display is narrower, record each as a
  separate clip and rely on the **[SWITCH →]** cues in the transcripts
  to mark the cut.
- **Pre-clear terminal history** (`clear`) before each take so the
  only output on screen is the one you're narrating.
- **Hide secrets.** Double-check `.env` is not visible in any file
  tab; close browser tabs with subscription IDs in the URL.
- **Dry-run each clip once unrecorded** — the transcripts assume you
  know where each click lands.
- **Hold the final frame ~2 s** so the speaker has a clean cut point.

---

## D1 — Baseline with one frontier model (~1:30)

**Message to land:** Here is "the obvious thing" — one frontier model answering every intent. It works, but the cost/latency/quality numbers are the strawman the next four clips knock down.

**Beats:** Open baseline agent → Run Carmen's request → Cut to scorecard → Hold.
**Workshop reference:** [Step 2 — Baseline SDK](./02-baseline-sdk.md), [`code/s02_baseline_agent.py`](./code/s02_baseline_agent.py)

### What to have visible at the start

- **Tab 5 (Codespace)** with `s02_baseline_agent.py` open; terminal ready.
- **Tab 1 (Portal)** showing `planner-gpt41` deployment in the background.

### Transcript

> *(Start on Tab 5 — `s02_baseline_agent.py` in editor)*

"This is the simplest thing that could possibly work. One deployment — `gpt-4.1` — and one system prompt that has to handle everything Carmen throws at it: planning, policy questions, the parking receipt, all of it.

*(Highlight the single deployment name and the prompt block)*

Let me run it against Carmen's full request — Berlin trip, hotel near Alexanderplatz, parking from her SAN airport receipt, and a per-diem question.

*(Switch to terminal, run `python s02_baseline_agent.py --input ../sample-data/carmen-trace.json`)*

*(Let it run; ~12 s)*

Plausible-looking JSON comes back. Trip plan, policy notes, receipt fields. But plausible isn't shippable. Let's measure it.

*(Run `python s02_scorecard.py --label v1-baseline`)*

*Placeholder — replace with the real baseline scorecard from your run.*

```
=== v1-baseline scorecard ===
Quality   ████░░░░░░  0.41
Cost      ██░░░░░░░░  $0.023/req
Latency   ██████░░░░  12.5 s p50
```

Four out of ten requests fail a constraint, misquote the policy, or produce JSON the downstream code can't parse. That's the bar. Everything from here either beats it or doesn't earn its complexity."

### Cue sheet

| Time | Beat | Action |
|---|---|---|
| 0:00 | Open file, name the strawman | `s02_baseline_agent.py` visible |
| 0:20 | Highlight single deployment + prompt | Cursor on those lines |
| 0:35 | Switch to terminal, run agent | Watch JSON stream |
| 1:00 | Run scorecard | Scorecard renders |
| 1:15 | Land the "this is the bar" message | Hold on scorecard |
| 1:30 | Hard stop — hold scorecard frame | |

---

## D2 — Foundry catalog + leaderboard + benchmarks (~2:00)

**Message to land:** Foundry's value isn't a model — it's the catalog. Frontier, small, and domain models in one place, with leaderboards and benchmarks so you can pick by job, not by hype.

**Beats:** Catalog → Filters → Leaderboard sort → Model card → Model Router + announcement banners.
**Workshop reference:** [Step 3 — Model selection](./03-model-selection.md)

### What to have visible at the start

- **Tab 2 (Portal)** on the Model catalog page in `wwi-concierge-demo` (swedencentral).

### Transcript

> *(Start on Tab 2 — Model catalog landing)*

"This is the Foundry model catalog. Over eleven thousand models, every major provider, every modality, every size class.

The point isn't the number. The point is what you can do with the filters.

*(Filter by modality → text+vision. Then provider. Then 'fine-tunable')*

Watch the count drop as I narrow by what this workload actually needs — vision support on the receipt, and a small model I can fine-tune for the policy slice.

*(Open Leaderboard tab → sort by quality, then by cost)*

The leaderboard is where the picking happens. Sort by quality and the frontier models float to the top. Sort by cost and a very different shortlist emerges. Pin `gpt-4.1`, `gpt-4.1-mini`, and `gpt-4.1-nano` so I can compare them directly.

*(Click into one model card — `gpt-4.1-mini`)*

Each card carries the benchmark detail — quality scores, throughput, context window, region availability — so the decision is grounded in numbers, not vendor decks.

*(Click Model Router card; show announcement banners — Anthropic / MAI / Geospatial)*

And alongside the named models, you get **Model Router** for dynamic routing, and a steady flow of new entrants — Anthropic, MAI, Geospatial — landing in the same catalog. One place, one auth, one billing surface, every model you'd reasonably want to evaluate."

### Cue sheet

| Time | Beat | Action |
|---|---|---|
| 0:00 | Land on catalog | Catalog grid visible |
| 0:20 | Apply filters | Count visibly drops |
| 0:45 | Open leaderboard, sort | Quality then cost |
| 1:10 | Pin three GPT-4.1 variants | Compare view |
| 1:25 | Open one model card | Benchmark detail |
| 1:45 | Model Router + banners | New-entrants story |
| 2:00 | Hard stop — hold catalog frame | |

---

## D3 — Multi-model decomposition (~2:30)

**Message to land:** Decompose the workload and route each intent to the smallest model that meets its bar. Cost and latency drop together. Quality on the policy slice doesn't — and that's the cliffhanger into the eval clip.

**Beats:** Open multi-model agent → Run Carmen's request → Show trace fan-out → Cut to scorecard → Call out the policy plateau.
**Workshop reference:** [Step 3 — Model selection](./03-model-selection.md), [`code/s03_router.py`](./code/s03_router.py), [`code/s05_multi_model_agent.py`](./code/s05_multi_model_agent.py)

### What to have visible at the start

- **Tab 5 (Codespace)** with `s05_multi_model_agent.py` open; terminal ready.
- **Tab 1 (Portal)** with `Models + endpoints` showing the four named-by-job deployments in `Succeeded`.

### Transcript

> *(Start on Tab 5 — `s05_multi_model_agent.py` in editor)*

"Same Carmen request, different shape. Four deployments now, each named by the **job** it does — not by the model underneath.

*(Highlight `router-nano`, `policy-mini-base`, `vision-mini`, `planner-gpt41`)*

`router-nano` classifies intent. `vision-mini` reads the receipt. `policy-mini-base` answers policy questions. `planner-gpt41` does the multi-step itinerary reasoning where frontier capability actually earns its cost.

*(Switch to terminal — run the same Carmen prompt against the multi-model agent)*

```bash
python -c "
import json, s05_multi_model_agent as agent
with open('../sample-data/carmen-trace.json') as f: c = json.load(f)
out = agent.run(c['user_message'], image_url=c.get('image_url'))
print(json.dumps(out, indent=2, default=str))
"
```

*(Let the trace fan out — router → policy + planner — visible in the streamed output)*

Now the scorecard:

*Placeholder — replace with the real multi-model scorecard from your `v2-batch` run.*

```
=== v2-batch scorecard ===
Quality   █████░░░░░  0.55           ← policy slice still 0.47
Cost      █░░░░░░░░░  $0.012/req
Latency   ████░░░░░░   7.9 s p50
```

Cost is roughly halved. Latency is down nearly 40%. And quality went *up* — because the planner isn't burning context on intent classification or translation anymore.

But look at the annotation. The **policy slice is still 0.47**. Routing alone doesn't fix that. That's where the next two clips earn their keep."

### Cue sheet

| Time | Beat | Action |
|---|---|---|
| 0:00 | Open multi-model agent | Editor on `s05_multi_model_agent.py` |
| 0:25 | Highlight 4 named-by-job deployments | Cursor on each |
| 0:55 | Switch to terminal, run Carmen | Trace fan-out visible |
| 1:40 | Show scorecard | Cost & latency wins |
| 2:05 | Call out policy plateau | Annotation on 0.47 |
| 2:30 | Hard stop — hold scorecard with annotation | Cliffhanger for D4 |

---

## D4 — Adaptive evaluation with a rubric (~3:00)

**Message to land:** "Looks right" isn't measurable. Schema + rubric evaluators turn the policy slice into numbers — and the numbers cluster failures by axis, telling you exactly where to optimize.

**Beats:** Show dataset → Run eval in portal → Sort by judge score → Cluster by axis → Drill into one failing row → Land the takeaway.
**Workshop reference:** [Step 5 — Evaluations](./05-evaluations.md), [`code/s05_run_eval.py`](./code/s05_run_eval.py), [`sample-data/eval-policy-only.jsonl`](./sample-data/eval-policy-only.jsonl)

### What to have visible at the start

- **Tab 5 (Codespace)** with `eval-policy-only.jsonl` open.
- **Tab 3 (Portal)** on the Evaluations page, ready to start a run (or with the pre-staged `policy-base` run available).

### Transcript

> *(Start on Tab 5 — `eval-policy-only.jsonl`)*

"This is the policy slice — 35 rows of policy-only requests. Each row has the intent, the expected constraints, and an `axis_varied` field: geography, language, policy trap. That last column is the whole game.

*(Scroll a few rows; pause on one with `axis_varied: geography`)*

**[SWITCH → Tab 3: Portal Evaluations]**

Now I run the same dataset through Foundry's evaluation surface against `policy-mini-base`. Two judges: a schema validator and a rubric LLM-as-judge with the WWI policy in scope.

*(Trigger the run, or open the pre-staged `policy-base` run; let it complete)*

Sort results by `judge.judge_score`, ascending. The failures cluster at the top.

*(Group / filter by `axis_varied`)*

Look at this. Geography, language, and `policy_trap` are where it falls down. The model knows the US policy by default but stumbles on Tokyo per-diem and German VAT-inclusive rates.

*(Drill into one row — `seed-007` Tokyo per-diem)*

Here's the row. Carmen asked about the Tokyo per-diem cap. The model returned the US number. The judge caught it and quoted the rule it violated.

*Placeholder — replace with the actual scorecard from your `policy-base` run.*

```
=== policy-base scorecard ===
Quality (policy slice)  ████░░░░░░  0.47
Top failure axes        geography · language · policy_trap
```

So we know: it's not a *model* problem in general — it's a *coverage* problem on specific axes. That tells us exactly what to optimize. Targeted fine-tune, not a bigger model."

### Cue sheet

| Time | Beat | Action |
|---|---|---|
| 0:00 | Open policy dataset | Tab 5, `eval-policy-only.jsonl` |
| 0:25 | Call out `axis_varied` field | Scroll through 2-3 rows |
| 0:50 | Switch to portal Evaluations | Tab 3 |
| 1:10 | Run / open eval | Schema + rubric judges |
| 1:45 | Sort by score, cluster by axis | Failures grouped |
| 2:15 | Drill into one failing row | `seed-007` Tokyo |
| 2:40 | Land "targeted fine-tune" takeaway | Scorecard frame |
| 3:00 | Hard stop — hold the score + axes frame | |

---

## D5 — Distillation + fine-tune + after-scorecard (~3:30)

**Message to land:** Use the frontier as a teacher to expand the dataset, fine-tune the small model on the slice that matters, hot-swap behind the same job name. The compound win — quality up on the policy slice, cost and latency held — is the system-level optimization story.

**Beats:** Show seed FT data → Run distillation → Show Succeeded FT job → Flip `USE_FT_POLICY` → Re-run policy eval → Before/after scorecard → Full v1→v3 closing frame.
**Workshop reference:** [Step 6 — Fine-tune](./06-finetune.md), [`code/s06_expand_ft_data.py`](./code/s06_expand_ft_data.py), [`code/s06_finetune_policy.py`](./code/s06_finetune_policy.py)

### What to have visible at the start

- **Tab 5 (Codespace)** with `policy-ft-train.jsonl` and `s05_multi_model_agent.py` open.
- **Tab 4 (Portal)** on Fine-tuning, job `wwi-policy-v1` showing `Succeeded`.

### Transcript

> *(Start on Tab 5 — `policy-ft-train.jsonl`)*

"Here's our seed fine-tune dataset. Twenty-four hand-crafted pairs covering the policy axes we just saw fail.

Twenty-four isn't enough to fine-tune on. But it's enough to distill from.

*(Run `python s06_expand_ft_data.py`)*

This uses `gpt-4.1` as a teacher to fan each seed out across twelve axes — geography, language, policy trap, time of year, role, currency. Twenty-four becomes eighty-four.

*(Show the output count and a sample expanded row)*

**[SWITCH → Tab 4: Portal Fine-tuning]**

That dataset went into a fine-tune job for `gpt-4.1-mini`, suffixed `wwi-policy-v1`. Status: Succeeded. Here's the deployed FT model card — `policy-mini-ft`.

*(Show the job details and deployment)*

**[SWITCH → Tab 5: `s05_multi_model_agent.py`]*

Hot-swap is one line.

*(Scroll to `USE_FT_POLICY = True`)*

```python
USE_FT_POLICY = True  # flip to False to go back to v2 behavior
```

Same deployment **name** — `policy-mini-base` becomes `policy-mini-ft` — and the planner code never changed.

*(Switch to terminal, re-run the policy-only eval)*

```bash
python s05_run_eval.py --agent s05_multi_model_agent \
    --eval ../sample-data/eval-policy-only.jsonl --label "policy-ft"
```

*Placeholder — replace with the real before/after from your `policy-base` vs `policy-ft` runs.*

```
=== policy-ft scorecard ===
Quality (policy slice)  ███████░░░  0.68  ✅ (+0.21)
Cost                    held
Latency                 held
```

Policy quality went from 0.47 to 0.68. Cost and latency unchanged. That's the targeted optimization — we paid for fine-tuning capacity once and we keep the runtime cost.

Now the full system, end to end:

*Placeholder — replace with your full `v3-final` scorecard.*

```
=== v3-final scorecard ===
Quality   ██████░░░░  0.65   (+12% over D1)
Cost      █░░░░░░░░░  $0.006/req  (−74% vs D1)
Latency   ███░░░░░░░  6.5 s p50   (−48% vs D1)
```

That's the loop: select, evaluate, optimize, operate. Five clips, one workshop, one project — quality up, cost down, latency down, at the same time."

### Cue sheet

| Time | Beat | Action |
|---|---|---|
| 0:00 | Open FT seed data | Tab 5, `policy-ft-train.jsonl` |
| 0:25 | Run distillation expand | 24 → 84 visible |
| 0:55 | Switch to portal FT | Tab 4, Succeeded job |
| 1:20 | Show deployed FT model card | `policy-mini-ft` |
| 1:40 | Switch back to agent code | `USE_FT_POLICY = True` |
| 2:05 | Re-run policy eval in terminal | Output streaming |
| 2:35 | Show policy before/after | 0.47 → 0.68 |
| 3:00 | Show full v1→v3 scorecard | Three-metric win |
| 3:30 | Hard stop — hold v3 frame | Closing frame |

---

## Recovery notes

Use these if a take goes sideways. With recording you can always cut
and retry, but these are the in-place fallbacks if you want to keep a
take rolling.

### Deployment not found / API error (any clip)

Switch to the portal **Models + endpoints** tab and show the five
deployments visually. Say: *"While that reconnects, let me show you
the same thing from the portal side."* The deployments are the story;
the live call is supporting evidence.

### Eval run takes too long (D3, D4, D5)

Use the pre-staged scorecard output. Say: *"I ran this earlier — here's
the output"* and scroll to it. The numbers came from real runs on the
same eval set, so they're honest evidence either way.

### Distillation expand fails (D5)

Use the pre-generated [`policy-ft-train.jsonl`](./sample-data/policy-ft-train.jsonl)
+ [`policy-ft-val.jsonl`](./sample-data/policy-ft-val.jsonl) files in
`sample-data/`. Say: *"This expanded set is the input to the fine-tune
job — twelve axes, fanned out from twenty-four seeds."*

### Fine-tune deployment missing (D5)

Set `USE_FT_POLICY = False` in `s05_multi_model_agent.py`, re-run the
policy eval, and stop on the base scorecard (0.47). Say: *"This is the
state before fine-tuning. The gap to 0.68 is exactly what Step 6 of
the workshop closes — distillation expand, then fine-tune the policy
mini, then this one-line swap."* The architecture story still lands.

### Copilot skill response is slow or truncated (D2 / D3)

The catalog filter results are reproducible — narrate the row you
care about while it streams. If a panel fails entirely, fall back to
the README's model-selection table in [`03-model-selection.md`](./03-model-selection.md)
and say: *"This is the same recommendation we'd land on from the
catalog — five jobs, four deployment names, each named by the task,
not the model."* The message survives.

---
