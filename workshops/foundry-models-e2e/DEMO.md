# Speaker Demo Guide — Right Model, Right Job

<!--
PURPOSE:
This file is the speaker + recording guide for the three demo segments
that accompany the foundry-models-e2e workshop. It is meant to be used
*while running the workshop end-to-end* against the WWI Concierge
scenario — you run each workshop step, verify it works, and capture
the relevant demo segment as a short video at the points called out
below. There is no automation skill driving the demos; pacing and
framing live in this file.
-->


> Three short demo videos to capture while running the workshop
> end-to-end. Target lengths: **~4 / 4 / 5 minutes**.
> Source material: [README.md](./README.md) · Workshop steps 2–8.
> Scenario: **WWI Concierge** — Carmen needs to book a business trip to Berlin.

---

## Table of Contents

- [How to use this guide](#how-to-use-this-guide)
- [Setup checklist (do this before you record)](#setup-checklist)
- [Recording workflow](#recording-workflow)
- [Demo 1 — Select the right model (~4 min)](#demo-1--select-the-right-model-4-min)
- [Demo 2 — Validate with evidence (~4 min)](#demo-2--validate-with-evidence-4-min)
- [Demo 3 — Optimize cost and performance (~5 min)](#demo-3--optimize-cost-and-performance-5-min)
- [Recovery notes](#recovery-notes)

---

## How to use this guide

The workflow this file assumes:

1. **Run the workshop end-to-end first.** Walk through
   [`00-setup.md`](./00-setup.md) through [`08-portal-review.md`](./08-portal-review.md)
   on the WWI brand and confirm every step works for you in isolation.
   The setup checklist below is the *exit state* of that run.
2. **Pre-stage the eval runs** so the v1 / v2 / v3 scorecards are real
   numbers from your environment, not placeholders.
3. **Record each demo as a separate video** — do not try to capture all
   three in one take. Each demo is anchored to specific workshop steps
   (called out in its header) so you can re-run just that slice to
   capture clean footage.
4. **Use the transcript as a narration script, not a teleprompter.** The
   cue-sheet table under each demo is the timing contract; aim for the
   time markers, not the exact wording.

If a demo segment goes long, trim from the narrative scaffolding
("a lot of teams skip this step…") before trimming the technical beats.
The technical beats are the proof; the narrative is the wrapper.

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
  - `mini-vision` (gpt-4.1-mini)
  - `policy-mini-base` (gpt-4.1-mini)
  - `policy-mini-ft` (fine-tuned gpt-4.1-mini, from Step 6)

### Eval runs pre-staged (needed for Demo 2 and 3 portal views)

Run these once before the session and keep the terminal output handy:

```bash
cd workshops/foundry-models-e2e/code

# v1 baseline — single model, no routing
python s05_run_eval.py --agent s02_baseline_agent \
    --eval ../sample-data/eval-seed.jsonl --label "v1-baseline"

# v2 — router + per-task models, no fine-tune
python s05_run_eval.py --agent s05_multi_model_agent \
    --eval ../sample-data/eval-full.jsonl --label "v2-batch"

# v3 — full assembly with fine-tuned policy model
# (set USE_FT_POLICY = True in s05_multi_model_agent.py first)
python s05_run_eval.py --agent s05_multi_model_agent \
    --eval ../sample-data/eval-full.jsonl --label "v3-final"
```

> [!NOTE]
> **All scorecard numbers in this file are placeholders.** The bars,
> quality scores, cost figures, latency values, and percentage deltas
> were drafted before the workshop was run end-to-end on the WWI brand.
> Replace them with the real output from your own eval runs as you
> work through Steps 2, 5, and 7. Look for the *Placeholder — replace*
> marker above each scorecard block.

*Placeholder — replace with the actual scorecard from your `v1-baseline` / `v2-batch` / `v3-final` runs.*

Expected terminal output to have visible during Demo 2:
```
=== v1-baseline scorecard ===
Quality   ██░░░░░░░░  0.61
Cost      ██░░░░░░░░  $0.108/task
Latency   ██████░░░░  12.3 s

=== v2-batch scorecard ===
Quality   ████░░░░░░  0.78
Cost      ░░░░░░░░░░  $0.063/task
Latency   █████░░░░░  9.4 s

=== v3-final scorecard ===
Quality   █████████░  0.94  ✅
Cost      ██░░░░░░░░  $0.028/task  ✅
Latency   ███░░░░░░░  7.6 s  ✅
```

### Portal tabs pre-loaded

Have these pages open and **logged in** before you start:

| Tab | URL path | Used in |
|---|---|---|
| **Tab 1** | Foundry Portal → project `wwi-concierge-demo` → **Models + endpoints** | Demo 1 |
| **Tab 2** | Foundry Portal → same project → **Evaluation** | Demo 2 |
| **Tab 3** | Foundry Portal → same project → **Evaluation → Compare** (v1 vs v3) | Demo 3 |
| **Tab 4** | Codespace — terminal open in `workshops/foundry-models-e2e/code/` | All demos |

> **Tip:** Use a browser profile with Foundry already authenticated to avoid login prompts mid-demo.

### Files to have open in the editor (Tab 4)

Open these in VS Code tabs before recording:

- `code/s02_config.py` — shows deployment names by job
- `code/s03_router.py` — shows the router
- `code/s05_multi_model_agent.py` — shows the full agent
- `code/s05_run_eval.py` — the eval driver

---

## Recording workflow

Each demo maps to a small slice of the workshop you have already run.
Capture them in workshop order so the Foundry project state moves
forward naturally between takes.

| Demo | Capture after running… | What you re-do on camera | Suggested take length |
|---|---|---|---|
| **Demo 1** | [Step 3 — Model selection](./03-model-selection.md) | Re-run the Copilot prompt against the model catalog; show the five deployments already in `Succeeded`. | ~4 min |
| **Demo 2** | [Step 5 — Evaluations](./05-evaluations.md) (after v1 + v2 eval rows exist) | Re-show the v1 vs v2 scorecard in the terminal, then the Evaluation tab in the portal. | ~4 min |
| **Demo 3** | [Step 7 — Multi-model agent](./07-multi-model-agent.md) + [Step 8 — Portal review](./08-portal-review.md) (after v3 eval row exists) | Re-run Carmen's trace end-to-end, then the v1 / v2 / v3 compare view in the portal. | ~5 min |

Capture tips:

- **Record at 1920×1080 minimum** so both the portal tab and the
  Codespace are legible side-by-side. If your display is narrower,
  record them as separate clips and rely on the **[SWITCH →]** cues in
  each transcript to mark the cut.
- **Pre-clear terminal history** (`clear`) before each take so the only
  output on screen is the one you're narrating.
- **Hide secrets.** Double-check `.env` is not visible in any file
  tab; close any browser tabs with subscription IDs in the URL.
- **Run each demo once unrecorded** as a dry run — the transcripts
  assume you know where each click lands.

---

## Demo 1 — Select the right model (~4 min)

**Message to land:** Decompose the workload first. Four of five jobs in this app do not need a frontier model — the catalog makes the right choice obvious once you ask the right question.

**Beats:** Catalog → Filters → Model cards → Shortlist  
**Workshop reference:** [Step 3 — Model selection](./03-model-selection.md)

### What to have visible at the start

- **Tab 1 (Portal)** showing `Models + endpoints` with the five deployments already in `Succeeded` state.
- **Tab 4 (Codespace)** with `s02_config.py` open and Copilot Chat visible.

---

### Transcript

> *(Start on Tab 1 — Models + endpoints page)*

"Let me show you where this all starts — and it's not in code.

WWI has an AI travel concierge that books trips for employees. The first version was simple: one prompt, one model — `gpt-4.1` for everything. Sounds fine. Costs about eleven cents per completed trip.

The question we're going to answer is: **do you actually need a frontier model for every part of this?**

Here in the Foundry portal I can see the model catalog. Over eleven thousand models, across providers, modalities, and tiers. This is useful but also overwhelming, so let's ask a better question.

**[SWITCH → Tab 4: Copilot Chat panel]**

I'm going to use the Foundry skill right here in Copilot. I'm going to describe the five actual jobs Carmen's trip requires — routing the request, reading a receipt image, answering a policy question, planning the multi-step itinerary, and translating a hotel email — and ask it to recommend a model and deployment for each one.

*(Type or paste the prompt into Copilot Chat)*

```
I need Azure Direct models from Sweden Central for these tasks:
  1. Fast intent classification (≤200 tokens in, ≤30 out, p50 ≤300ms)
  2. Vision: extract merchant, amount, date from a receipt image
  3. Domain QA grounded in a 2-page policy doc
  4. Multi-step planner with tool calls (≤4K tokens, p50 ≤6s)
  5. EN↔DE translation, short emails

Recommend a model from gpt-4.1, gpt-4.1-mini, gpt-4.1-nano for each,
with one-sentence justification and deployment names.
```

*(Let the response stream in — don't rush it)*

Look at what comes back. Routing: **nano** — sub-300ms, plenty capable for a three-class classifier. Receipt and translation: **mini** — vision support, no need for the frontier. Policy QA: **mini** — we'll fine-tune it on WWI's specific policy in Demo 3. Planning with tools: **gpt-4.1** — that's where frontier-level reasoning actually earns its keep.

Four of five jobs routed away from the most expensive model. The skill also generated deployment names like `router-nano`, `mini-vision`, `planner-gpt41`. Notice what those names *don't* contain — model version numbers. They describe the **job**, not the model underneath.

**[SWITCH → Tab 1: Models + endpoints]**

And those are exactly the deployments you see here, already in Succeeded state. I deployed these using the same Foundry skill — one prompt, one deployment. No portal clicks required, though you can always verify here.

This single decision — decomposing the workload and routing each job to the smallest model that meets its bar — drops the cost from eleven cents to about six cents before we've written a single line of agent code. And it's reversible: if a better nano drops next month, you swap the model behind the name and nothing else changes."

---

### Cue sheet (timing guide)

| Time | Beat | Action |
|---|---|---|
| 0:00 | Opening hook | Tab 1, models + endpoints visible |
| 0:30 | Describe the problem | Stay on Tab 1 |
| 1:00 | Switch to Copilot prompt | Tab 4, Copilot Chat |
| 1:30 | Paste prompt, let it run | Chat streaming in |
| 2:30 | Walk through the response | Highlight each row |
| 3:15 | Name-by-job insight | Point to deployment names |
| 3:30 | Switch back to portal | Tab 1 — show deployments |
| 3:50 | Land the cost message | Stay on Tab 1 |
| 4:00 | Hard stop |  |

---

## Demo 2 — Validate with evidence (~4 min)

**Message to land:** Public benchmarks measure what someone else cares about. The only number that matters for shipping is: does it meet *your* bar, on *your* prompts? Foundry makes that a first-class operation, not a side project.

**Beats:** Set criteria → Load prompts → Run comparison → Review results  
**Workshop reference:** [Step 2 — Baseline](./02-baseline-sdk.md), [Step 4 — Synthetic data](./04-synthetic-data.md), [Step 5 — Evaluations](./05-evaluations.md)

### What to have visible at the start

- **Tab 4 (Codespace)** terminal showing the pre-run scorecard output (v1 and v2 results scrolled to).
- **Tab 2 (Portal)** on Evaluation — three run rows visible (v1-baseline, v2-batch, v3-final).

---

### Transcript

> *(Start on Tab 4 — terminal, scorecard output visible)*

"A lot of teams skip this step — or they do it once, at the start, with someone else's benchmark. That's the part that bites them in production.

Here's what an honest starting point looks like. This is v1 of the WWI Concierge — `gpt-4.1` doing everything — measured against twenty representative traveler requests we wrote by hand. Policy questions, budget constraints, vision edge cases, translation.

*Placeholder — replace with the one-line summary your `v1-baseline` run actually prints.*

```
v1-baseline:  quality 0.61  ·  $0.108/task  ·  12.3s p50
```

Quality of 0.61. That means four in ten trips either fail a business constraint, misquote the policy, or produce malformed JSON that downstream code can't parse. Not good enough to ship — and we know that now, before it goes in front of a traveler.

Here's the other thing we did before running this. We set three explicit targets:

- Quality ≥ 0.92 — meaning at least 92% of trips pass all constraints and policy checks.
- Cost ≤ $0.03 per task.
- Latency ≤ 8 seconds p50.

These numbers are in `s02_config.py`. Every subsequent eval checks against them. The scorecard only goes green when all three hit.

*(Scroll down in terminal to show v2 output)*

After Step 3 — model selection, routing each job to a smaller model — here's v2:

*Placeholder — replace with the one-line summary your `v2-batch` run actually prints.*

```
v2-batch:     quality 0.78  ·  $0.063/task  ·  9.4s p50
```

Quality went up. Cost dropped significantly. But we're not green yet. Quality is still short, and we haven't applied the fine-tuned policy model. That's the key insight: **routing alone improved quality** because the planner isn't spending context budget on tasks nano handles better. And the eval set tells us that — we didn't have to guess.

**[SWITCH → Tab 2: Portal Evaluation]**

Everything that ran in the terminal is also visible here. Three eval runs, pinned to the dataset version they ran against. Click Compare — v1 and v3 side by side.

*(Click Compare → select v1-baseline and v3-final)*

This is what I want you to see. Row 14 — Carmen asks about parking reimbursement at SAN airport. V1 gives a plausible-sounding answer. V3 cites Section 4.2 verbatim. One of those answers you can show a compliance team. One you can't.

The dataset version is pinned right here at the top. These numbers are only meaningful because the dataset is fixed. If you change what you're measuring against, the numbers aren't comparable — and the portal enforces that discipline.

That's the message: benchmarks on someone else's data tell you what you paid for. Evals on your own prompts tell you whether you're ready to ship."

---

### Cue sheet

| Time | Beat | Action |
|---|---|---|
| 0:00 | Opening — the skip problem | Tab 4, terminal, v1 scorecard |
| 0:30 | Show v1 numbers | Point at 0.61 quality |
| 1:00 | Introduce the three targets | Point at config / scorecard |
| 1:45 | Show v2 numbers | Scroll terminal to v2 output |
| 2:30 | Quality-up insight | Stay on terminal |
| 3:00 | Switch to portal | Tab 2, Evaluation |
| 3:10 | Compare v1 vs v3, row 14 | Row-level diff visible |
| 3:40 | Dataset pinning insight | Point at dataset version header |
| 4:00 | Hard stop |  |

---

## Demo 3 — Optimize cost and performance (~5 min)

**Message to land:** The win isn't a better single model. It's treating the workload as a system — routing, fine-tuning, and tiering working together. Foundry gives you the infrastructure to make that systematic, not heroic.

**Beats:** Profile request → Apply routing → Compare cost/quality → Review savings  
**Workshop reference:** [Step 7 — Multi-model agent](./07-multi-model-agent.md), [Step 8 — Portal review](./08-portal-review.md)

### What to have visible at the start

- **Tab 4 (Codespace)** with `s05_multi_model_agent.py` open, terminal ready in `code/`.
- **Tab 3 (Portal)** pre-loaded on the version compare view (v1 vs v2 vs v3).

---

### Transcript

> *(Start on Tab 4 — s05_multi_model_agent.py open)*

"Alright. This is the part where the three decisions we made — model selection, evaluation, fine-tuning — get assembled into a single agent and we find out if the compound win is real.

Here's the v3 agent. It looks almost identical to v1 structurally. The core loop is the same. What changed is underneath: every task now routes to the model we picked for it, and the policy model is the fine-tuned version, not the base.

There's one flag in this file that tells you everything:

*(Scroll to `USE_FT_POLICY = True`)*

```python
USE_FT_POLICY = True  # flip to False to go back to v2 behavior
```

That one line is the entire fine-tune swap. The deployment name is `policy-mini-ft` — same job name from Demo 1, different model underneath. The planner code never changed.

Let me run Carmen's full trip end-to-end through this agent:

*(In terminal)*

```bash
python -c "
import json, s05_multi_model_agent as agent
with open('../sample-data/carmen-trace.json') as f:
    carmen = json.load(f)
out = agent.run(carmen['user_message'], image_url=carmen.get('image_url'))
print(json.dumps(out, indent=2, default=str))
"
```

*(Let it run — ~7-8 seconds)*

There it is. Flight under $1500, hotel near Alexanderplatz under $600 total, policy notes citing Section 4.2 and 7.1, booking confirmed. Seven and a half seconds wall clock.

Now let's run the full eval over the whole dataset and see the actual numbers:

*(In terminal — run pre-staged result or re-run live if time allows)*

*Placeholder — replace with the actual scorecard from your `v3-final` run.*

```
=== v3-final scorecard ===
Quality   █████████░  0.94  ✅
Cost      ██░░░░░░░░  $0.028/task  ✅
Latency   ███░░░░░░░  7.6 s  ✅
```

All green. Let me show you what that means in actual terms.

**[SWITCH → Tab 3: Portal version compare]**

Here are all three versions side by side. V1, V2, V3. Look at the cost column.

V1: `$0.108` per trip. V3: `$0.028` per trip. That's a **74% cost reduction** — not from switching to a cheaper model for the whole thing, but from routing each task to the right model, fine-tuning where prompting plateaued, and never spending frontier tokens on tasks that don't need them.

Quality went from 0.61 to 0.94 at the same time. Usually cost and quality trade off. Here they improved together — because v1's quality problem *was* a cost problem in disguise. The model was spending its context budget doing routing and translation when it should have been reasoning about the itinerary.

Now click into the architecture diff —

*(Click to show v1 vs v3 architecture in agent versions tab if available)*

V1: one model, one deployment. V3: four deployments, each named by the job it does. When `gpt-4.1-mini-v2` ships next quarter, we evaluate it against the same dataset, swap it behind `router-nano` if it wins, and nothing in the agent code changes.

That's the loop. Select. Evaluate. Optimize. Operate. You just watched one full turn of it.

And everything you saw here — the evals, the versions, the routing, the fine-tune — ran on a Foundry project any developer can provision in ten minutes. It's not a research project. It's how you build production AI today."

---

### Cue sheet

| Time | Beat | Action |
|---|---|---|
| 0:00 | Agent code walkthrough | Tab 4, s05_multi_model_agent.py |
| 0:30 | Flag `USE_FT_POLICY = True` | Scroll to that line |
| 1:00 | Run Carmen's trip end-to-end | Terminal command |
| 1:45 | Trip output — verify fields | Output JSON visible |
| 2:15 | Run full eval | Terminal — scorecard |
| 2:45 | All green — explain significance | Stay on terminal |
| 3:00 | Switch to portal | Tab 3, version compare |
| 3:15 | Cost column — v1 vs v3 | Point at numbers |
| 3:45 | Quality + cost both improved | The "not a tradeoff" insight |
| 4:15 | Architecture diff — name by job | Show v1 vs v3 topology |
| 4:40 | The loop — Select/Evaluate/Optimize | Closing hook |
| 5:00 | Hard stop |  |

---

## Recovery notes

Use these if a take goes sideways. With recording you can always cut
and retry, but these are the in-place fallbacks if you want to keep a
take rolling.

### Deployment not found / API error (any demo)

Switch to the portal, navigate to **Models + endpoints**, and show the five deployments visually. Say: *"While that reconnects, let me show you the same thing from the portal side."* The deployments are the story — the live call is supporting evidence.

### Eval run takes too long (Demo 2 or 3)

If re-running live isn't feasible in time, the pre-staged terminal output is sufficient. Say: *"I ran this before we started — here's the output"* and scroll to it. The numbers are real; they came from actual runs on the eval set.

### Copilot skill response is slow or truncated (Demo 1)

The skill response table is reproducible — you can read the key row aloud while it streams. If it fails entirely, flip to `s02_config.py` and say: *"This is the same recommendation the skill produced — five jobs, four deployment names, each named by the task not the model."* The message survives without the live call.

### Fine-tune deployment missing (Demo 3)

Set `USE_FT_POLICY = False` in `s05_multi_model_agent.py`, re-run the Carmen trace, and use the v2 scorecard numbers. Say: *"This is v2 — routing without fine-tuning. The quality gap between v2 at 0.78 and v3 at 0.94 is exactly the policy fine-tune's contribution. Step 6 of the workshop walks you through generating that."* The architecture story still lands.

---

## Three hooks to repeat in every demo

These phrases anchor each demo to the same through-line and work as natural transitions between demos:

- **Demo 1:** *"Name your deployment by job, not by model."* — Says it's the workload topology that matters, not the catalog choice.
- **Demo 2:** *"Measure on your data, not a public benchmark."* — Says evaluation is only meaningful when it reflects your actual usage.
- **Demo 3:** *"The win is the system, not the single model."* — Says optimization is a compounding set of decisions, each justified by the scorecard.
