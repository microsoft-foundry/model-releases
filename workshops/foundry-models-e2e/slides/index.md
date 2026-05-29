---
marp: true
theme: default
paginate: true
size: 16:9
header: ''
footer: ''
style: |
  /* ─────────────────────────────────────────────────────────────────
     Right Model, Right Job — Microsoft Foundry training deck
     A modern dark/light theme with violet→cyan accent gradients,
     Inter for prose, JetBrains Mono for code.
     ───────────────────────────────────────────────────────────────── */
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;700&display=swap');

  :root {
    --ink:        #0f172a;
    --ink-soft:   #334155;
    --muted:      #64748b;
    --paper:      #ffffff;
    --paper-2:    #f8fafc;
    --line:       #e2e8f0;
    --accent:     #6366f1;   /* indigo */
    --accent-2:   #06b6d4;   /* cyan   */
    --violet:     #8b5cf6;
    --green:      #10b981;
    --amber:      #f59e0b;
    --red:        #ef4444;
    --grad:       linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #06b6d4 100%);
    --grad-dark:  linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #155e75 100%);
  }

  section {
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
    font-size: 26px;
    color: var(--ink);
    background: var(--paper);
    padding: 60px 80px;
    letter-spacing: -0.01em;
  }

  h1, h2, h3 { font-family: 'Inter', sans-serif; font-weight: 800; letter-spacing: -0.02em; color: var(--ink); }
  h1 { font-size: 44px; line-height: 1.1; margin: 0 0 24px; }
  h2 { font-size: 36px; line-height: 1.15; margin: 0 0 20px; }
  h3 { font-size: 28px; font-weight: 700; }

  p, li { line-height: 1.55; }
  strong { color: var(--ink); font-weight: 700; }
  em { color: var(--accent); font-style: normal; font-weight: 600; }

  blockquote {
    border: none;
    border-left: 6px solid var(--accent);
    padding: 16px 0 16px 28px;
    margin: 24px 0;
    color: var(--ink-soft);
    font-size: 28px;
    font-style: italic;
    background: linear-gradient(90deg, rgba(99,102,241,0.06), transparent);
  }

  code {
    font-family: 'JetBrains Mono', monospace;
    background: #eef2ff;
    color: #4338ca;
    padding: 2px 8px;
    border-radius: 6px;
    font-size: 0.9em;
  }
  pre {
    background: #0f172a;
    color: #e2e8f0;
    border-radius: 10px;
    padding: 22px 26px;
    font-size: 20px;
    line-height: 1.5;
    box-shadow: 0 8px 32px rgba(15,23,42,0.18);
  }
  pre code { background: transparent; color: inherit; padding: 0; }

  table {
    border-collapse: collapse;
    width: 100%;
    font-size: 22px;
    margin: 12px 0;
  }
  th {
    background: linear-gradient(135deg, #1e1b4b, #312e81);
    color: #fff;
    text-align: left;
    padding: 12px 16px;
    font-weight: 600;
    letter-spacing: 0.02em;
  }
  td { padding: 10px 16px; border-bottom: 1px solid var(--line); }
  tr:last-child td { border-bottom: none; }
  tr:nth-child(even) td { background: var(--paper-2); }

  ul, ol { padding-left: 28px; }
  li { margin: 8px 0; }
  li::marker { color: var(--accent); }

  header { color: var(--muted); font-size: 16px; padding: 24px 80px 0; }
  footer { color: var(--muted); font-size: 16px; padding: 0 80px 24px; }
  section::after {
    color: var(--muted);
    font-size: 14px;
    font-weight: 500;
  }

  /* ─── utility classes used by individual slides ─── */
  .scorecard {
    font-family: 'JetBrains Mono', monospace;
    font-size: 28px;
    line-height: 1.7;
    background: #0f172a;
    color: #e2e8f0;
    padding: 28px 36px;
    border-radius: 12px;
    box-shadow: 0 12px 40px rgba(15,23,42,0.25);
  }
  .scorecard .bar-red    { color: #fca5a5; }
  .scorecard .bar-amber  { color: #fcd34d; }
  .scorecard .bar-green  { color: #86efac; }
  .scorecard .check      { color: #10b981; font-weight: 700; }

  .pill {
    display: inline-block;
    padding: 6px 16px;
    background: var(--grad);
    color: white;
    border-radius: 999px;
    font-size: 18px;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
  }

  .hero-stat {
    font-size: 96px;
    font-weight: 900;
    background: var(--grad);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1;
    letter-spacing: -0.04em;
  }

  .stat-row { display: flex; gap: 32px; margin-top: 28px; }
  .stat {
    flex: 1;
    background: var(--paper-2);
    border: 1px solid var(--line);
    border-radius: 12px;
    padding: 24px;
    border-top: 4px solid var(--accent);
  }
  .stat .label { color: var(--muted); font-size: 16px; text-transform: uppercase; letter-spacing: 0.08em; }
  .stat .val { font-size: 44px; font-weight: 800; margin-top: 6px; }
  .stat .val.md { font-size: 28px; font-weight: 700; line-height: 1.3; }
  .stat .val.sm { font-size: 22px; font-weight: 700; line-height: 1.3; }
  .stat.good { border-top-color: var(--green); }
  .stat.bad  { border-top-color: var(--red); }

  .note { color: var(--muted); font-size: 22px; font-style: italic; }
  .note.sm { font-size: 18px; }
  .note.xs { font-size: 16px; }

  /* ─── slide variants via _class ─── */

  /* Title / closing slide */
  section.lead {
    background: var(--grad-dark);
    color: white;
    padding: 80px;
  }
  section.lead h1 { color: white; font-size: 72px; font-weight: 900; }
  section.lead h2 { color: #c7d2fe; font-weight: 500; font-size: 32px; }
  section.lead p, section.lead li { color: #e0e7ff; }
  section.lead em { color: #67e8f9; }
  section.lead strong { color: white; }
  section.lead::after { color: #c7d2fe; }

  /* Section dividers */
  section.divider {
    background: var(--grad);
    color: white;
    padding: 80px;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }
  section.divider .pill {
    background: rgba(255,255,255,0.18);
    color: white;
    border: 1px solid rgba(255,255,255,0.4);
    margin-bottom: 32px;
  }
  section.divider h1 { color: white; font-size: 88px; font-weight: 900; max-width: 14ch; }
  section.divider p { color: #e0e7ff; font-size: 28px; max-width: 30ch; }
  section.divider::after { color: rgba(255,255,255,0.7); }

  /* Quote / "the email" cold open */
  section.quote {
    background: var(--paper-2);
    padding: 80px 120px;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }
  section.quote blockquote {
    font-size: 36px;
    line-height: 1.4;
    color: var(--ink);
    border-left: 8px solid var(--accent);
    padding-left: 36px;
  }

  /* Hero stat slide */
  section.hero {
    background: var(--paper);
    text-align: center;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
  }

  /* Dark “stage” slide for scorecards */
  section.stage {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    color: #e2e8f0;
  }
  section.stage h1, section.stage h2 { color: white; }
  section.stage .note { color: #94a3b8; }
  section.stage::after { color: #64748b; }

  /* Two-column layout */
  section.split { display: grid; grid-template-columns: 1fr 1fr; gap: 48px; align-items: start; }
  section.split h1, section.split h2 { grid-column: 1 / -1; }

  /* Portrait layout — used with `![bg right:N%]`. Marp auto-reserves the
     right N% for the image, so we only need to tune typography here. */
  section.portrait p, section.portrait li { font-size: 24px; }
  section.portrait blockquote { font-size: 22px; padding: 12px 0 12px 20px; margin: 16px 0; }

  /* 2×2 tile grid — for slides with 4 short equal-weight ideas */
  .grid-2x2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px 32px; margin-top: 20px; }
  /* 1×N stacked tile list — for short, uniform enumerations (e.g. 5 challenges) */
  .list-5 { display: grid; grid-template-columns: 1fr; gap: 10px; margin-top: 14px; }
  .list-5 .tile { padding: 10px 18px; }
  .list-5 .tile p { font-size: 20px; margin: 2px 0; line-height: 1.35; }
  .tile {
    background: var(--paper-2);
    border: 1px solid var(--line);
    border-left: 4px solid var(--accent);
    border-radius: 10px;
    padding: 16px 20px;
  }
  .tile p { margin: 6px 0; font-size: 22px; line-height: 1.45; }
  .tile p:first-child { margin-top: 0; }
  .tile p:last-child { margin-bottom: 0; }
---

<!--
═══════════════════════════════════════════════════════════════════════
  Right Model, Right Job — End-to-End AI Development in Microsoft Foundry
  Two co-instructors: Naomi (dev) + Yina (decision maker)
  45 minutes · ~40 slides · ~1 min/slide

  BUILD:
    npm i -g @marp-team/marp-cli
    marp slides/index.md -o slides/index.html          # HTML deck
    marp slides/index.md --pdf -o slides/index.pdf     # PDF
    marp slides/index.md --pptx -o slides/index.pptx   # PowerPoint
    marp -s slides/                                    # live server :8080

  Speaker notes live inside HTML comment blocks like this one.
  Custom slide styles via the `_class: name` directive on a slide.
═══════════════════════════════════════════════════════════════════════
-->

<!-- _class: lead -->
<!-- _paginate: false -->

<span class="pill">Microsoft Foundry · 45 min</span>

# Right Model,<br>Right Job.

## End-to-End AI Development in Microsoft Foundry

<br>

**Naomi** — Developer    ·    **Yina** — Decision Maker
WWI Concierge

<!--
Yina opens. Warm welcome. Two co-instructors, two perspectives.
"By the end of 45 minutes we want you to be able to build a small version of this yourself, in 7 days, on Foundry."
-->

---

<!-- _class: divider -->

<span class="pill">Part 1</span>

# The problem.

Why most AI demos can't survive their first CFO email.

<!--
Quick pivot — Yina sets up the cold open.
-->

---

<!-- _class: quote -->

> *"Loved the demo. Two questions before we ship:*
> *1) How do you know it's right?*
> *2) At 8,000 trips/month, why is the bill $47K next quarter?"*

**— Email from the CFO, last Tuesday**

<!--
Yina reads slowly. Beat. "This talk is the answer to both."
-->

---

# The challenge going in

<br>

> ### **"One big frontier model.<br>Opaque quality."**

<br>

That's where most of us start.
It works. It's expensive. We can't defend it.

<!--
Naomi: "Show of hands — anyone shipped a feature this looks like? Both of mine did."
-->

---

# Five challenges every AI team is hitting

<div class="list-5">

<div class="tile">

**1 · Model choice is exploding** — more models, providers, modalities, and deployment options than ever.

</div>
<div class="tile">

**2 · Benchmarks aren't enough** — public scores don't reflect *your* prompts, users, data, or business goals.

</div>
<div class="tile">

**3 · Cost is a system-level problem** — routing, caching, batching, prompts, tiers, observability — not just model price.

</div>
<div class="tile">

**4 · Production demands control** — reliability, monitoring, safety, governance, versioning, rollback.

</div>
<div class="tile">

**5 · The landscape keeps changing** — new models arrive constantly, can you improve app without rebuilding it?

</div>

</div>

<!--
Yina: "Every CFO question we've fielded maps to one of these five.
This workshop's eight steps are organized so each challenge gets answered
once, on stage, with code."
-->

---

# The takeaway, coming out

<br>

> ### **"The unit of progress is the model decision —<br>made per task, against a per-task scorecard."**

<br>

<span class="note">If you remember one sentence from this session, this is it.<br>We'll come back to it on the closing slide.</span>

<!--
Yina says this slowly. Hold for a beat.
-->

---

<!-- _class: divider -->

<span class="pill">Part 2</span>

# Meet the workload.

One sentence from Carmen. Five jobs hiding inside it.

---

<!-- _class: portrait -->

# Carmen

![bg right:40%](https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=900&q=80)

**Senior engineer** · WWI San Diego office

Needs to be in **Berlin Tuesday morning** for an offsite that runs through Thursday. She messages the agent at 11 PM:

> *"Book flights + hotel near Alexanderplatz, under $2,500. Also — here's a parking receipt from SAN three days ago, can you expense it?"*

<!--
Naomi: "Carmen messages me at 11 PM every other week. This is what an enterprise AI task actually looks like — it's never one thing."

If image doesn't load (offline), the slide still works. Replace URL with a local image if needed.
-->

---

# Five jobs hiding in one sentence

| # | Job | What the model actually needs |
|---|---|---|
| 1 | **Route** the intent | Fast classifier · cheap · no creativity |
| 2 | **Read** the receipt image | Vision · structured extraction |
| 3 | **Answer** policy: *"expense parking?"* | Knowledge of *WWI* policy specifically |
| 4 | **Plan** the trip + call tools | Strong reasoning · longer context · tool use |
| 5 | **Translate** the German confirm email | Multilingual · short form |

<br>

<span class="note">There is **no single model** that's best for all five.</span>

<!--
Yina: "Hold this slide in your head. The rest of the talk is what happens when you take this seriously."
-->

---

<!-- _class: divider -->

<span class="pill">Part 3</span>

# The scorecard.

Three bars. Every step has to move at least one of them.

---

<!-- _class: stage -->

# Our narrative device

<br>

<div class="scorecard">

```
Quality   ░░░░░░░░░░    0%      ← target ≥ 0.92 on curated eval
Cost      ██████████   11¢      ← target ≤ 3¢ / task
Latency   ██████████  12.3s     ← target ≤ 8s p50
```

</div>

<br>

<span class="note">These are the only numbers that matter.<br>Quality, cost, latency — **per task**.</span>

<!--
Naomi: "We're going to walk a journey. Every step has to move at least one bar in the right direction. If a change doesn't show up here, it didn't happen."
-->

---

<!-- _class: divider -->

<span class="pill">Part 4</span>

# One model, all jobs.

The version of this we all ship first.

---

# Starting architecture — everything on `gpt-4.1`

```python
# This is the entire architecture
client.chat.completions.create(
    model="planner-gpt41",          # gpt-4.1
    messages=[system, user_message],
    tools=[search_flights, search_hotels, check_policy, submit_booking],
)
```

<br>

- ✅ Ships in a day
- ✅ Demos beautifully
- ❌ **No eval** — quality is *belief*, not measurement
- ❌ **No model choice** — one tool for every job

<!--
Naomi: "This is the first version of every AI feature I've ever shipped. Including the one in Yina's CFO email."
-->

---

<!-- _class: hero -->

<span class="pill">The CFO math</span>

<div class="hero-stat">$10,560</div>

### per year, just on travel planning

<br>

<div class="stat-row">
  <div class="stat bad"><div class="label">$/task</div><div class="val">$0.108</div></div>
  <div class="stat bad"><div class="label">Trips/month</div><div class="val">8,000</div></div>
  <div class="stat bad"><div class="label">Quality</div><div class="val">?</div></div>
</div>

<!--
Yina: "I can't take this to the CFO. Not because it's bad — because I can't tell her if it's bad."
-->

---

<!-- _class: stage -->

# Where we start — all red

<br>

<div class="scorecard">

```
Quality   ░░░░░░░░░░    ?       ← we don't even know
Cost      ██████████  $0.108
Latency   ██████████   12.3s
```

</div>

<br>

<span class="note">The bars **should** be red here. That's the point.<br>This is the gap the next 30 minutes close.</span>

<!--
Pause. Let the room sit with the red bars.
-->

---

<!-- _class: divider -->

<span class="pill">Part 5</span>

# Microsoft Foundry.

The surface where models, evaluations, and agents share a project.

---

# What is Microsoft Foundry, concretely?

<div class="stat-row">
  <div class="stat"><div class="label">Project</div><div class="val sm">Workspace that ties everything together</div></div>
  <div class="stat"><div class="label">Models + Endpoints</div><div class="val sm">What's deployed, where, at what SKU</div></div>
  <div class="stat"><div class="label">Playground</div><div class="val sm">Try a prompt against a deployment</div></div>
</div>
<div class="stat-row">
  <div class="stat"><div class="label">Evaluation</div><div class="val sm">Curated · batch · continuous · red team</div></div>
  <div class="stat"><div class="label">Fine-tuning</div><div class="val sm">Train, deploy, version, compare</div></div>
  <div class="stat"><div class="label">Tracing</div><div class="val sm">Per-call latency, tokens, errors</div></div>
</div>

<!--
Naomi: "This is what Foundry actually is. A coherent surface for the things we usually duct-tape together."
-->

---

# Three surfaces, one project

| Surface | Best for | Who uses it most |
|---|---|---|
| **Foundry Portal** (low-code) | Provision, browse catalog, review, govern | Decision makers · security · ops |
| **Foundry SDK** (`azure-ai-projects`) | Build the agent, run evals in code | Developers |
| **Foundry Skills** (AI-assisted, MCP) | Discover · deploy · scaffold by prompt | Anyone, fastest path |

<br>

**We'll use all three.** Same project. Same models. Same evals.

<!--
Yina: "Pick the surface that fits the user. The platform doesn't force you into one."
-->

---

<span class="pill">The Foundry lifecycle</span>

# From model choice to a living AI system

<div class="stat-row">
  <div class="stat"><div class="label">01</div><div class="val md">Select</div><div class="note sm">Match model to workload</div></div>
  <div class="stat"><div class="label">02</div><div class="val md">Evaluate</div><div class="note sm">Test on your own data</div></div>
  <div class="stat"><div class="label">03</div><div class="val md">Optimize</div><div class="note sm">Quality + latency + cost</div></div>
  <div class="stat"><div class="label">04</div><div class="val md">Operate</div><div class="note sm">Monitor · govern · roll back</div></div>
  <div class="stat"><div class="label">05</div><div class="val md">Improve</div><div class="note sm">Adopt new models safely</div></div>
</div>

<span class="note">Continuous loop — every cycle improves quality, cost, and trust.</span>

<!--
Naomi: "Each stage of this loop maps to a step we're about to run.
Select = Step 3. Evaluate = Steps 4–5. Optimize = Steps 6–7. Operate + Improve = Step 8.
By the end you've done one full turn — and the same pattern is what you repeat every time a new model lands."
-->

---

# Our dev journey today

<br>

<div class="stat-row">
  <div class="stat"><div class="label">Start</div><div class="val md">🌐 Portal</div><div class="note xs">create project · catalog · playground baseline</div></div>
  <div class="stat"><div class="label">Build</div><div class="val md">💻 VS Code + SDK</div><div class="note xs">agent · router · eval · fine-tune</div></div>
  <div class="stat"><div class="label">Close</div><div class="val md">🌐 Portal</div><div class="note xs">evals · red team · agent versions</div></div>
</div>

<br>

<span class="note">Portal → Code → Portal. The loop that's natural for both speakers in this room.</span>

---

<!-- _class: divider -->

<span class="pill">Part 6</span>

# Right model, right job.

Decompose the workload. Then go shopping.

---

# Step 1 — decompose, then shop in the catalog

<span class="note">Foundry catalog filter: *Sold directly by Azure · Sweden Central · Deployable*</span>

| # | Job | Pick | Why |
|---|---|---|---|
| Route | intent classify | **`gpt-4.1-nano`** | Sub-300ms · plenty smart for a 3-way classify |
| Vision | extract receipt | **`gpt-4.1-mini`** | Vision support · frontier overkill |
| Policy | *"can I expense X?"* | **`gpt-4.1`** → fine-tune | Cheap base + fine-tunable + supervised FT in Sweden Central |
| Plan | multi-step + tools | **`gpt-4.1`** | Frontier earns its keep here |
| Translate | EN ↔ DE | **`gpt-4.1-mini`** (reuse) | Same deployment as vision |

<br>

<span class="note">**4 of 5 jobs don't need a frontier model.** That insight is the whole talk.</span>

<!--
Naomi: "I asked the Foundry Skill — 'pick Azure Direct models for these five tasks in Sweden Central.' It returned this table in 8 seconds. I read it, agreed, deployed."
-->

---

# Demo — the Foundry Skill in action

```text
> List Azure Direct models in Sweden Central matching gpt-4.1*.
> For each: exact version · max tokens · supports fine-tuning ·
> input/output price per 1K.

> Now deploy:
>   router-nano        (gpt-4.1-nano,  TPM 10K)
>   mini-vision        (gpt-4.1-mini,  TPM 20K)
>   policy-mini-base   (gpt-4.1-mini,  TPM 20K)
```

<br>

<span class="note">Under the hood: `models_list` + `models/deploy-model` MCP tools.<br>Same calls a CI pipeline would make. Same calls the portal makes.</span>

<!--
Naomi: "Skills give you aspirational pseudocode that actually runs. Fastest path to a working configuration."
-->

---

# A naming convention that pays off later

<br>

```
planner-gpt41        ← gpt-4.1
router-nano          ← gpt-4.1-nano
mini-vision          ← gpt-4.1-mini
policy-mini-base     ← gpt-4.1-mini
policy-mini-ft       ← gpt-4.1 (fine-tuned, coming in Part 9)
```

<br>

**Deployments describe the *job*, not the model.**
When we swap in the fine-tune later, the app change is *one boolean*.

<!--
Yina: "This is the kind of small decision that pays off over a year of changes."
-->

---

# Route to the right model per task

```python
intent = route(user_msg)                  # router-nano   (~180ms)
if has_image:
    receipt = vision_extract(img)         # mini-vision   (~1.2s)
policy_note = policy_lookup(user_msg)     # policy-mini-base
itinerary = planner.run(user_msg, ...)    # planner-gpt41 + tools
```

<br>

<span class="note">Same app shape. Different model per call.<br>The router is the only piece of "agent" framework you actually need at this scale.</span>

---

<!-- _class: stage -->

# Scorecard — two bars move

<br>

<div class="scorecard">

```
Quality   ██░░░░░░░░    0.61   ← measured for the first time
Cost      ██████░░░░  $0.063   ⬇  from $0.108
Latency   █████████░    9.4s   ⬇  from 12.3s
```

</div>

<br>

<span class="note">Cost down 42%. Latency down 24%.<br>Quality measured — and it's not where we need it yet.</span>

<!--
Naomi: "Just from routing — half the bill, a third less latency. Now we have to face the quality number."
-->

---

<!-- _class: divider -->

<span class="pill">Part 7</span>

# Measure what you move.

Quality unmeasured ≠ quality is good.

---

# Before we move quality,<br>we have to see it

<div class="grid-2x2">

<div class="tile">

**20 curated rows** *hand-written, ground truth*
the smoke test on every commit

</div>
<div class="tile">

**~200 synthetic rows** *grown from the seed*
across 6 axes: geography · budget · language · policy traps · receipt categories · intent balance

</div>
<div class="tile">

**Two evaluators**
deterministic schema/constraint check + LLM-as-judge (semantic correctness)

</div>
<div class="tile">

**Dataset is versioned.**
*No version = no comparison = no story.*

</div>

</div>

<!--
Naomi: "First eval I ever ran, I cheated. I picked the rows the model passed. Don't do that. Hand-write the rows that scare you."
-->

---

# Demo — synthetic data generation

```python
# 20 seed rows → ~200 across axes:
#   intent · geography · budget edge · language · receipt category · policy traps
generate("eval-seed.jsonl",
         out_path="eval-full.jsonl",
         n_per_axis=25)

# → Wrote 198 rows (178 synthetic).
```

<br>

> **Then read the first 30 synthetic rows by hand.**
> A 150-row clean eval beats a 500-row noisy one.

<!--
Yina: "Synthetic data is a tool, not a magic wand. Every adversarial row I add, I read twice."
-->

---

# Three evals, three jobs

| Flavor | When you run it | What it answers |
|---|---|---|
| **Curated** (20 rows) | Every commit | *"Did I break a known case?"* |
| **Batch** (~200 rows) | Before each deploy | *"How does this version score overall?"* |
| **Online / continuous** | Production traffic, sampled | *"Is real-world quality drifting?"* |

<br>

<span class="note">All three live in the same Evaluation tab. Same dataset versions. Same evaluators.</span>

---

<!-- _class: divider -->

<span class="pill">Part 8</span>

# Customize.

Fine-tune the cheap model. Beat the frontier.

---

# When to fine-tune (and when not to)

<br>

| ✅ Use fine-tune when… | ❌ Skip fine-tune when… |
|---|---|
| A cheap base is **close** but not great | You haven't tried a better prompt + retrieval |
| Narrow, **stable** domain task | The task changes weekly |
| ≥30 high-quality labeled examples | Your eval doesn't isolate the task |
| The frontier is *too expensive* at scale | The base model already hits target |

<br>

**WWI policy QA: ✅ on all four.**

<!--
Yina: "Fine-tune is a commitment. Make it on purpose."
-->

---

# Demo — fine-tune `gpt-4.1` for policy

```python
job = client.fine_tuning.jobs.create(
    training_file=train.id,
    validation_file=val.id,
    model="gpt-4.1",
    hyperparameters={"n_epochs": 3},
    suffix="wwi-policy-v1",
)
```

<br>

**24 train rows · 6 val rows · ~2 hours.**

Then in the agent, **one line**:

```python
USE_FT_POLICY = True
```

<!--
Naomi: "This is the slide that lands hardest. One boolean — because we named the deployment by job, not by model."
-->

---

<!-- _class: hero -->

<span class="pill">Policy QA — before vs. after</span>

<div class="stat-row">
  <div class="stat bad">
    <div class="label">gpt-4.1 base</div>
    <div class="val">0.81</div>
    <div class="note sm">$0.0008 / answer</div>
  </div>
  <div class="stat good">
    <div class="label">policy-mini-ft</div>
    <div class="val">0.94</div>
    <div class="note sm">$0.0010 / answer</div>
  </div>
  <div class="stat bad">
    <div class="label">gpt-4.1 frontier</div>
    <div class="val">0.93</div>
    <div class="note sm">$0.045 / answer</div>
  </div>
</div>

<br>

### ~**50× cheaper than the frontier**, with **higher quality**.

<!--
Yina: "This is the slide for the CFO email."
-->

---

<!-- _class: divider -->

<span class="pill">Part 9</span>

# All green.

The end-of-talk slide.

---

<!-- _class: stage -->

# Final scorecard

<br>

<div class="scorecard">

```
Quality   █████████░    0.94   ✅
Cost      ██░░░░░░░░    2.8¢   ✅
Latency   ███░░░░░░░    7.6s   ✅
```

</div>

<br>

<span class="note">All three targets met. No heroics. Just the right model for each job, measured.</span>

<!--
Beat. Let the audience read it.
-->

---

# The journey, on one slide

| Version | Architecture | Quality | $/task | p50 latency |
|---|---|---|---|---|
| **v1** | `gpt-4.1` does everything | 0.61 | $0.108 | 12.3s |
| **v2** | Router + per-task models | 0.78 | $0.063 | 9.4s |
| **v3** | + fine-tuned policy | **0.94** ✅ | **$0.028** ✅ | **7.6s** ✅ |

<br>

<span class="note">Each row = **one decision**, justified by the scorecard *before* it was made.</span>

---

<!-- _class: hero -->

<span class="pill">The deltas, end to end</span>

<div class="stat-row">
  <div class="stat good">
    <div class="label">Quality</div>
    <div class="val">+54%</div>
    <div class="note sm">0.61 → 0.94</div>
  </div>
  <div class="stat good">
    <div class="label">Cost</div>
    <div class="val">–74%</div>
    <div class="note sm">$0.108 → $0.028</div>
  </div>
  <div class="stat good">
    <div class="label">Latency</div>
    <div class="val">–38%</div>
    <div class="note sm">12.3s → 7.6s</div>
  </div>
</div>

---

<!-- _class: divider -->

<span class="pill">Part 10</span>

# Govern.

Back to the portal — what your CFO, SecOps, and auditors see.

---

# Close the loop — back in the portal

<br>

- **Evaluation tab** — v1 vs v3 side-by-side · row-level diffs · dataset version pinned
- **Red team** — jailbreak · prompt injection · sensitive content (out of the box)
- **Agent versions** — v1.0 · v2.0 · v3.0, each with bound deployments and a pinned eval
- **Tracing** — the router → vision → policy(ft) → planner chain, per-call timing
- **Continuous evaluation** — sample 5% of prod traffic, catch regressions in days, not quarters

<br>

<span class="note">Everything you built in code is visible, governable, and comparable here.</span>

<!--
Yina: "This is the difference between 'we tested it on Carmen's trip' and 'we tested it against an adversary.' Both matter."
-->

---

# What we showcased today

✅ **Model selection** — per task, with a defensible reason
✅ **Synthetic dataset generation** — to grow a meaningful eval
✅ **Evaluations** — curated · batch · LLM-judge · red team · continuous
✅ **Customization** — fine-tune the cheap model, beat the frontier on cost *and* quality
✅ **Agent versioning** — v1 / v2 / v3 comparable side-by-side in the portal

<br>

**All on Microsoft Foundry. Sweden Central. 7-day build. Toy-scale data.**

<!--
Naomi: "Everything you saw fits in 7 days of evenings."
-->

---

<!-- _class: divider -->

<span class="pill">Part 11</span>

# The takeaway, again.

---

<!-- _class: stage -->

<br>

> ### **"The unit of progress is the model decision —<br>made per task, against a per-task scorecard."**

<br>

<div class="stat-row">
  <div class="stat" style="border-top-color:#67e8f9;background:#1e293b">
    <div class="label" style="color:#94a3b8">Quality</div>
    <div class="val" style="color:#86efac">0.61 → 0.94</div>
  </div>
  <div class="stat" style="border-top-color:#67e8f9;background:#1e293b">
    <div class="label" style="color:#94a3b8">Cost</div>
    <div class="val" style="color:#86efac">$0.108 → $0.028</div>
  </div>
  <div class="stat" style="border-top-color:#67e8f9;background:#1e293b">
    <div class="label" style="color:#94a3b8">Latency</div>
    <div class="val" style="color:#86efac">12.3s → 7.6s</div>
  </div>
</div>

<!--
Yina reads slowly. Hold the slide for 5 seconds before advancing.
-->

---

<!-- _class: lead -->
<!-- _paginate: false -->

<span class="pill">Build it yourself</span>

# Now you.

**Repo:** `nitya/model-releases-FORK` → `workshops/foundry-models-e2e/`
**Plan:** *.plans/foundry-models-e2e-plan.md* (full speaker script + trainer guide)
**Hands-on:** *workshops/foundry-models-e2e/README.md* (Steps 0–8, ~7 days of evenings)
**Code:** *workshops/foundry-models-e2e/code/* (`s02_…` through `s06_…`)

<br>

**Region:** Sweden Central  ·  **Models:** `gpt-4.1` family (Azure Direct)

<br>

### Questions?

<!--
QR code overlay on this slide before recording. Both speakers stay on stage for Q&A.
-->
