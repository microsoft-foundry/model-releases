---
marp: true
theme: default
paginate: true
size: 16:9
header: ''
footer: ''
style: |
  /* ─────────────────────────────────────────────────────────────────
     One Endpoint, Smarter Spend — Model Router Deep-Dive
     Microsoft Foundry training deck (shared theme)
     ───────────────────────────────────────────────────────────────── */
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;700&display=swap');

  :root {
    --ink:        #0f172a;
    --ink-soft:   #334155;
    --muted:      #64748b;
    --paper:      #ffffff;
    --paper-2:    #f8fafc;
    --line:       #e2e8f0;
    --accent:     #6366f1;
    --accent-2:   #06b6d4;
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

  .scorecard {
    font-family: 'JetBrains Mono', monospace;
    font-size: 24px;
    line-height: 1.7;
    background: #0f172a;
    color: #e2e8f0;
    padding: 24px 32px;
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
  section.divider h1 { color: white; font-size: 80px; font-weight: 900; max-width: 16ch; }
  section.divider p { color: #e0e7ff; font-size: 28px; max-width: 30ch; }
  section.divider::after { color: rgba(255,255,255,0.7); }

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

  section.hero {
    background: var(--paper);
    text-align: center;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
  }

  section.stage {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    color: #e2e8f0;
  }
  section.stage h1, section.stage h2 { color: white; }
  section.stage .note { color: #94a3b8; }
  section.stage::after { color: #64748b; }

  section.split { display: grid; grid-template-columns: 1fr 1fr; gap: 48px; align-items: start; }
  section.split h1, section.split h2 { grid-column: 1 / -1; }

  .grid-2x2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px 32px; margin-top: 20px; }
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
  One Endpoint, Smarter Spend — Model Router Deep-Dive
  Workshop: workshops/model-router-demystified
  ~35 slides · ~45 min · ~1 min/slide
═══════════════════════════════════════════════════════════════════════
-->

<!-- _class: lead -->
<!-- _paginate: false -->

<span class="pill">Microsoft Foundry · Model Router</span>

# One Endpoint, Smarter Spend

## A hands-on deep-dive into the Foundry Model Router

<br>

*Deploy. Evaluate. Optimize. Operate — with zero routing code.*

<!--
Opener. Frame the deck: this isn't a marketing pitch for Model Router,
it's an empirical workshop. We're going to *measure* whether the router
holds up on a real workload (WWI Concierge), and learn how to
optimize it with config alone.
-->

---

<!-- _class: quote -->

> "We're paying frontier prices for FAQ-grade questions.
> Can we route per request — without building our own classifier?"

<p class="note">— every team running an LLM in production, eventually</p>

<!--
The motivating problem. Most teams default to "one frontier model for
everything" because they don't want to maintain a custom routing layer.
That's exactly the gap Model Router fills.
-->

---

# What Model Router is

<div class="grid-2x2">
<div class="tile">
<p><strong>A trained router model</strong></p>
<p>Analyzes each prompt and selects the optimal backing model in real time.</p>
</div>
<div class="tile">
<p><strong>One deployment</strong></p>
<p>You call one endpoint. The router fans out to 28+ models across multiple providers.</p>
</div>
<div class="tile">
<p><strong>Config, not code</strong></p>
<p>Tune routing mode and model subset in the portal. No <code>route_intent()</code> to maintain.</p>
</div>
<div class="tile">
<p><strong>Built-in failover + caching</strong></p>
<p>Transparent retries on throttling. Automatic prompt caching on supported models.</p>
</div>
</div>

<!--
Four-corner overview. Each tile becomes a deeper slide later, so keep
this short. Emphasis: Model Router *is* the router — you don't build
one on top of it.
-->

---

# What you'll be able to do

1. **Explain** how Model Router analyzes prompts and selects backing models
2. **Deploy** a router endpoint with routing mode and model-subset configuration
3. **Design** a representative prompt set spanning the complexity spectrum
4. **Compare** a frontier baseline against Model Router on quality, cost, latency
5. **Build** a custom Policy-Adherence evaluator with the Adaptive Evals rubric
6. **Optimize** by tuning modes, subsets, and prompt caching — config only
7. **Operate** with failover, continuous eval, and Foundry portal visibility

<!--
The 7 learning objectives from README.md, condensed into action verbs.
This is the contract for the next 45 minutes.
-->

---

# The scenario: WWI Concierge

<div class="stat-row">
<div class="stat">
<div class="label">Workload</div>
<div class="val md">FAQ · policy · trip planning · expense · edge cases</div>
</div>
<div class="stat">
<div class="label">Today's cost</div>
<div class="val">~$14k/mo</div>
</div>
<div class="stat good">
<div class="label">Target after this workshop</div>
<div class="val">~$4.5k/mo</div>
</div>
</div>

<br>

<p class="note">One frontier model is handling every request — from "what's the per-diem?" to "compare 2 hops vs. 1 international flight". The mix is exactly what Model Router was built for.</p>

<!--
Anchor the workshop in a concrete scenario. The same WWI domain
is reused from foundry-models-e2e, so learners crossing over already
know the policy. The before/after numbers come from README.md.
-->

---

# The arc — four scorecard moves

<div class="scorecard">

```
                              Quality   Cost/task   p50 latency
────────────────────────────  ────────  ──────────  ────────────
v1  Frontier only (gpt-5)     4.3       $0.028      3.2s
v2  Router Balanced            4.2       $0.011      2.1s
v3  Router Cost                3.9       $0.006      1.4s
v4  Router + subset + cache    4.3       $0.009      1.8s  ← WIN
```

</div>

<p class="note sm">Numbers are illustrative — you'll measure your own. Every row is one config change, measured before kept.</p>

<!--
This is the spine of the workshop. Each lab moves one row. By the end
we want the audience to internalize: "Same quality. ~68% less cost.
~44% less latency. Zero code changes."
-->

---

<!-- _class: divider -->

<span class="pill">Stage 1</span>

# Select

A router endpoint, deployed in minutes.

<!--
Stage divider. The workshop uses the Select → Evaluate → Optimize →
Operate loop. We're entering Select.
-->

---

# Lab 0 — Setup

<div class="split">
<div>

**What we deploy**

- Foundry project in **Sweden Central**
- **Model Router** — Global Standard, Balanced mode
- **Baseline frontier model** (e.g. `gpt-5`)
- Credentials in `.env`

</div>
<div>

**Verify both endpoints**

```bash
az ai project create \
  --name "wwi-model-router" \
  --resource-group "rg-wwi" \
  --location "swedencentral"

# Then deploy model-router via portal or CLI
```

</div>
</div>

<!--
~15 min lab. The point is: deploying Model Router is the same workflow
as any other model. No special infrastructure.
-->

---

# Lab 1 — Build the prompt set

A workload's *distribution* is what gives Model Router its leverage.

| Category | Count | Difficulty |
|---|---|---|
| `simple_faq` | 15 | easy |
| `policy_question` | 10 | easy/medium |
| `trip_planning` | 10 | medium |
| `receipt_expense` | 5 | medium |
| `edge_case` | 5 | hard |
| `multi_step_reasoning` | 5 | hard |

<p class="note sm">If every prompt is equally complex, routing saves nothing. Real workloads have a long tail of easy queries — that's where the wins live.</p>

<!--
50+ prompts in router-eval-prompts.jsonl. The category column matters
later for adaptive evaluator rules. Spend a moment on why mirroring
your real distribution is the whole game for honest measurement.
-->

---

<!-- _class: divider -->

<span class="pill">Stage 1 · cont.</span>

# Deploy & configure

Two knobs: routing mode, model subset.

---

# Lab 2 — Routing modes are a tolerance knob

```
Quality mode:  "Always use the best model. Cost is irrelevant."
               → effectively frontier for everything (with failover)

Balanced mode: "Stay within ~2% of best quality. Minimize cost."
               → most prompts to capable-but-cheaper models
               → DEFAULT — best for most workloads

Cost mode:     "Stay within ~6% of best quality. Maximize savings."
               → aggressive routing to cheapest sufficient model
               → best for high-volume, low-stakes work
```

<!--
This is the conceptual pivot of the workshop. Mode = quality tolerance
band. Subset = which models the router can choose from. Together they
give you fine control without code.
-->

---

# Inspect the response metadata

```python
from openai import AzureOpenAI

client = AzureOpenAI(...)
resp = client.chat.completions.create(
    model="model-router",
    messages=[{"role": "user", "content": prompt}],
)

print(resp.model)        # ← which underlying model handled it
print(resp.usage)        # ← tokens for cost calculation
```

<p class="note">The router tells you, per request, which backing model it picked. That's the signal you'll graph in Lab 3.</p>

<!--
Demo this live if time. The response.model field is the most useful
single piece of telemetry in the entire workshop.
-->

---

<!-- _class: divider -->

<span class="pill">Stage 2</span>

# Evaluate

Does it actually hold up on *your* workload?

---

# Lab 3 — Baseline vs. Router

<div class="split">
<div>

**Three commands, three datasets**

```bash
# 1. Frontier baseline
python code/run_comparison.py \
  --mode baseline \
  --dataset sample-data/router-eval-prompts.jsonl

# 2. Router (Balanced)
python code/run_comparison.py \
  --mode router \
  --dataset sample-data/router-eval-prompts.jsonl

# 3. LLM-as-a-judge scoring
python code/run_comparison.py --mode judge
```

</div>
<div>

**What you measure**

- Response text + latency
- Tokens in / out (cost)
- Which backing model the router picked
- Pairwise quality (dual-ordered to cancel position bias)
- Value composites: quality-per-$, quality-per-second

</div>
</div>

<!--
~20 min lab. Pipeline is adapted from the public
Model-Router-Auto-Evaluation repo. Dual-ordered pairwise is the
non-obvious trick — without it, position bias contaminates results.
-->

---

# v2 — first scorecard move

<!-- _class: stage -->

<div class="scorecard">

```
                              Quality   Cost/task   p50 latency
────────────────────────────  ────────  ──────────  ────────────
v1  Frontier only (gpt-5)     4.3       $0.028      3.2s
v2  Router Balanced            4.2       $0.011      2.1s    ✓
```

</div>

<br>

<p class="note">Quality dipped 0.1 of a point. Cost dropped 60%. Latency dropped 34%. The router is doing what it claimed — and we have the receipts.</p>

<!--
Pause here. This is the "aha" moment for skeptics. The trade is real
and measurable, not theoretical. The next lab tightens the eval to
catch the domain-specific failures that generic scoring misses.
-->

---

# The model distribution chart

> "Which backing models did the router actually pick — and how often?"

This is the most revealing artifact of the entire workshop. For WWI on Balanced mode you'll typically see:

- ~40% of prompts to a small/fast model (`gpt-5-mini` class)
- ~35% to a mid-tier model
- ~25% escalating to the frontier

<p class="note">The distribution *is* your workload decomposition. You didn't have to design it — the router revealed it.</p>

<!--
Tie back to the core insight from README: "the router IS the
decomposition." If the distribution surprises you, that's data about
your workload, not a router bug.
-->

---

# Lab 4 — When generic quality isn't enough

> Quality 4.2 looks fine. But does the response cite the *right* reimbursement limit?

Generic LLM-as-a-judge scores (Accuracy, Completeness, Clarity, Helpfulness) answer **"is this a good response?"**

They do **not** answer **"does this correctly apply our travel policy?"**

A smaller model can be clear, complete, and helpful — and still confabulate a $400 per-diem that doesn't exist.

<!--
The pivot to domain-specific evaluation. This is the lesson that
generalizes far beyond Model Router: generic evals are necessary, not
sufficient.
-->

---

# The Policy-Adherence rubric

| Criterion | What it catches |
|---|---|
| **Rule accuracy** | Did it cite the *correct* section (hotels vs. flights)? |
| **Completeness** | Are all conditions and exceptions mentioned? |
| **Boundary precision** | Are dollar thresholds exact? ($300 vs. $325) |
| **Hallucination absence** | Did it invent rules not in the policy? |

<p class="note">YAML rubric · weighted average · runs through Foundry Adaptive Evals.</p>

<!--
Four criteria, all framed around failure modes we actually see with
smaller models. Boundary precision is the killer one — "reimbursable
vs. needs approval" hinges on $25.
-->

---

# Adaptive rules — context-aware weighting

```yaml
adaptive_rules:
  # Budget questions → boundary precision matters most
  - condition: "input.category in ['budget_cap','reimbursement']"
    adjust_weights:
      boundary_precision: 0.40   # up from 0.25

  # Exception/approval questions → completeness matters most
  - condition: "input.category in ['exception','approval_chain']"
    adjust_weights:
      completeness: 0.40

  # Edge cases → hallucination risk is highest
  - condition: "input.category == 'edge_case'"
    adjust_weights:
      hallucination_absence: 0.40
```

<!--
The rubric shifts weight based on the *kind* of question. Edge cases
penalize hallucination harder; budget questions penalize wrong
numbers harder. This is what makes the evaluator usable beyond a toy.
-->

---

<!-- _class: divider -->

<span class="pill">Stage 3</span>

# Optimize

Modes. Subset. Caching. Config only — no rewrites.

---

# Lab 5 — Compare all three modes

```bash
python code/run_mode_comparison.py --mode cost     --output results/router-cost/
python code/run_mode_comparison.py --mode balanced --output results/router-balanced/
python code/run_mode_comparison.py --mode quality  --output results/router-quality/
```

<div class="scorecard">

```
                              Quality   Cost/task   p50 latency
────────────────────────────  ────────  ──────────  ────────────
v2  Router Balanced            4.2       $0.011      2.1s
v3  Router Cost                3.9       $0.006      1.4s   ← too far
v4  Router Quality             4.4       $0.025      3.0s   ← like baseline
```

</div>

<p class="note">Cost mode saves more but drops a quality point. Quality mode regresses to baseline economics. Balanced is the sweet spot — for now.</p>

<!--
Three runs, three data points. The lesson: don't pick a mode by name,
pick it by what the scorecard says about *your* workload. For WWI
Travel, Balanced wins. For a tier-2 chatbot, Cost might.
-->

---

# Model subset — narrow the eligible set

```
Default subset:   28+ models across providers
Curated subset:   gpt-5-mini · gpt-5 · claude-3.5-sonnet · llama-3-70b
                  ↑ chosen because:
                    - 2+ models for failover
                    - tool-calling support across the set
                    - per-token cost ceiling
                    - cache compatibility for the system prompt
```

<p class="note">A smaller subset = more predictable distribution = higher cache hit rate = compound wins.</p>

<!--
This is where compliance, predictability, and caching all converge.
"Always include ≥2 models in your subset" is the one operational rule
to repeat twice.
-->

---

# Lab 6 — Prompt caching, automatically

```
Request 1:  system_prompt (2,000 tok) + user_A (50 tok)
            → Router picks gpt-5-mini
            → Full processing at standard rate

Request 2:  system_prompt (2,000 tok) + user_B (60 tok)
            → Router picks gpt-5-mini  (same model!)
            → 2,000 cached tokens at reduced rate
            → ~50% savings on the system prompt portion

Request 3:  system_prompt (2,000 tok) + user_C (40 tok)
            → Router picks gpt-5  (different model)
            → No cache hit — caches are per-model
```

<!--
Caching is automatic on supported models — you don't configure it,
you design *for* it: long stable system prompts + narrow subset =
high hit rate. This is why subset and caching combine multiplicatively.
-->

---

# v4 — compound optimization wins

<!-- _class: stage -->

<div class="scorecard">

```
                              Quality   Cost/task   p50 latency
────────────────────────────  ────────  ──────────  ────────────
v1  Frontier only (gpt-5)     4.3       $0.028      3.2s
v2  Router Balanced            4.2       $0.011      2.1s
v3  Router Cost                3.9       $0.006      1.4s   ✗ rolled back
v4  Router + subset + cache    4.3       $0.009      1.8s   ✓ WIN
```

</div>

<br>

<p class="note">Same quality as the frontier baseline. ~68% less cost. ~44% less latency. Zero application code changed.</p>

<!--
Land the closing scorecard. The v3 → v4 rollback is the
methodological lesson: hill-climbing means you keep a change only
if the scorecard supports it.
-->

---

<!-- _class: divider -->

<span class="pill">Stage 4</span>

# Operate

Failover. Continuous eval. Portal visibility.

---

# Lab 7 — Failover is built in

```
Normal flow:
  Prompt → Router → selects gpt-5-mini → response ✓

Failover flow (gpt-5-mini throttled):
  Prompt → Router → selects gpt-5-mini → 429 rate limit
                  → transparently retries
                  → selects gpt-5 → response ✓
```

**Operational rule:** your model subset *is* your fallback pool — never ship a subset of size 1.

<!--
Failover is the unsung feature. It also means you should think of the
subset as both an optimization tool AND a reliability tool.
-->

---

# Continuous evaluation in production

<div class="split">
<div>

**The loop**

1. Sample N% of production traffic
2. Score with the Policy-Adherence evaluator
3. Track model distribution week over week
4. Alert on quality regression or distribution drift

</div>
<div>

**Why it matters**

- Router version updates add models — your mix will shift
- Traffic patterns drift as the product grows
- Catch regressions before customers do

</div>
</div>

<!--
Move the workshop from "one-off comparison" to "ongoing practice."
Continuous eval is the bridge between Day-1 deployment and a
year-in production posture.
-->

---

<!-- _class: divider -->

<span class="pill">Recap</span>

# Three takeaways

---

# 1 — The router IS the decomposition

You don't have to guess which model fits which task.

Deploy Model Router, send representative prompts, **inspect the model distribution**. The router's choices empirically reveal your workload's structure.

<p class="note">The distribution chart is more valuable than the cost savings on the first run — it tells you what your workload actually looks like.</p>

---

# 2 — Evaluation is the whole game

Without evaluation, routing is a guess.<br>With evaluation, routing is a measured optimization.

<div class="grid-2x2">
<div class="tile"><p><strong>Generic quality</strong></p><p>LLM-as-a-judge pairwise + absolute</p></div>
<div class="tile"><p><strong>Domain quality</strong></p><p>Adaptive Policy-Adherence rubric</p></div>
<div class="tile"><p><strong>Cost</strong></p><p>Router markup + per-model token pricing</p></div>
<div class="tile"><p><strong>Latency</strong></p><p>Wall-clock p50 by category</p></div>
</div>

---

# 3 — Optimization is config, not code

Every improvement in this workshop was a configuration change:

- Routing mode: **Balanced → Cost → Quality**
- Model subset: **all models → curated set**
- Prompt caching: **system-prompt design + subset for hits**

No application code was rewritten. The loop is **measure → tune config → measure again**.

---

# When to use Model Router

<div class="split">
<div>

**Use it when**

- Workload has diverse prompt complexity
- You want zero routing code to maintain
- Cost optimization is a real priority
- New models should help you automatically

</div>
<div>

**Consider manual routing when**

- You need deterministic model-per-task
- Strict per-task latency SLOs
- Compliance needs a model audit trail
- Workload is homogeneous (no wins)

</div>
</div>

---

<!-- _class: lead -->

# Now you

**Run it on your workload.**

`workshops/model-router-demystified/` · runs in ~90 min

<br>

> "Use the `run-workshop` skill on `workshops/model-router-demystified`."

<br>

*One endpoint. Smarter spend. No routing code.*

<!--
Call to action. Point at the repo, the workshop folder, and the
run-workshop skill. Encourage measuring on their own prompts — the
methodology transfers even if the numbers don't.
-->
