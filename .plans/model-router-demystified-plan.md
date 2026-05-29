# Workshop Plan — "One Endpoint, Smarter Spend"

**Model Router Deep-Dive in Microsoft Foundry**

| Field | Content |
|---|---|
| **Format** | 45–60 minute hands-on workshop · lab-based, progressive |
| **Audience** | Developers/architects familiar with LLMs who want to understand and adopt Model Router for cost/quality optimization |
| **Goal** | Teach how to deploy, evaluate, and optimize the Foundry Model Router — making the "better, cheaper, faster" case empirically |
| **Scenario** | WWI Concierge — same toy scenario as `foundry-models-e2e`, extended with additional prompt types |
| **Platform** | Microsoft Foundry (portal + SDK + CLI) |
| **Region** | **Sweden Central** |
| **Model Router version** | `2025-11-18` (latest) |
| **Baseline model** | `gpt-5` (or current frontier at workshop time) |
| **Build budget** | Extends `foundry-models-e2e` artifacts; ~3–5 days incremental build |
| **Outcome** | Participants leave knowing when and how to adopt Model Router, with a custom evaluator they built themselves |

---

## Relationship to `foundry-models-e2e`

This workshop **builds on** artifacts from the original workshop:

- Reuses `sample-data/travel-policy.md` (the WWI policy document)
- Reuses `sample-data/eval-seed.jsonl` as a starting point for representative prompts
- Extends the prompt set with new categories (simple FAQ, complex reasoning, edge cases)
- References the scorecard concept (quality/cost/latency)

> **⚠️ Sync notice:** If artifacts in `foundry-models-e2e/sample-data/` are refreshed (policy updates, eval seed changes), the corresponding files in this workshop should be refreshed too. Both workshops share the WWI canon.

---

## Learning objectives

By the end of this workshop, participants will be able to:

1. **Explain** what Model Router is, how it analyzes prompts, and why it differs from manual routing.
2. **Deploy** a Model Router endpoint with routing mode and model subset configuration.
3. **Design** a representative prompt set that covers simple, moderate, and complex tasks for a real workload.
4. **Compare** a single frontier model baseline against Model Router on quality, cost, and latency.
5. **Interpret** model-distribution reports to understand which backing models the router selects per task type.
6. **Build** a custom Policy-Adherence evaluator using the Adaptive Evals eval-rubric framework.
7. **Optimize** by tuning routing modes (Balanced → Cost → Quality) and model subsets without code changes.
8. **Operate** with prompt caching, automatic failover, and continuous evaluation in production.

---

## The narrative arc — one endpoint, three modes, zero routing code

```
                    Quality (1-5)  Cost/task    p50 latency
─────────────────── ────────────── ─────────── ───────────
v1  Frontier only    4.3           $0.028      3.2s
v2  Router Balanced  4.2 (−2%)     $0.011      2.1s         ← Lab 3
v3  Router Cost      3.9 (−9%)     $0.006      1.4s         ← Lab 5
v4  Router Quality   4.4 (+2%)     $0.025      3.0s         ← Lab 5
    + subset tuned   4.3 (±0%)     $0.009      1.8s         ← Lab 6
```

> Numbers are illustrative — participants measure their own in the labs.

**Key insight:** The Model Router eliminates custom routing code. You deploy one endpoint, send all your prompts, and the router does the decomposition for you. Your job is to *measure* whether it's good enough for your workload — and that's what this workshop teaches.

---

## The "Select → Evaluate → Optimize → Operate" story (Model Router edition)

| Stage | What it means with Model Router | Lab |
|---|---|---|
| **Select** | Deploy Model Router instead of choosing individual models. Configure routing mode + model subset. | Lab 2 |
| **Evaluate** | Run representative prompts through both baseline and router. Use auto-eval pipeline + custom rubric evaluator. | Labs 3–4 |
| **Optimize** | Tune routing mode, refine model subset, enable prompt caching. Each change = config only, no code. | Labs 5–6 |
| **Operate** | Monitor model distribution, set up continuous eval, leverage auto-failover. | Lab 7 |

---

## Workshop structure — Labs

### Lab 0 — Setup & Prerequisites

**What:** Provision Foundry project, deploy Model Router (Global Standard, Sweden Central), deploy baseline frontier model.

**Key concepts introduced:**
- Model Router as a "trained language model" (not a rules engine)
- Single endpoint simplicity
- Routing modes overview (Balanced/Cost/Quality)
- Model subset concept
- Region + deployment type requirements

**Deliverables:**
- Foundry project in Sweden Central
- Model Router deployment (Balanced mode, default model set)
- Baseline model deployment (e.g., `gpt-5`)
- `.env` configured with both endpoints

---

### Lab 1 — Build the Representative Prompt Set

**What:** Create a diverse prompt dataset that exercises the full range of WWI tasks.

**Key concepts introduced:**
- Why prompt diversity matters for router evaluation
- Task complexity spectrum (trivial → frontier-hard)
- The JSONL format for eval datasets
- Categories: `simple_faq`, `policy_question`, `trip_planning`, `receipt_expense`, `edge_case`, `multi_step_reasoning`

**Approach:**
- Start from `foundry-models-e2e/sample-data/eval-seed.jsonl` (20 rows)
- Extend with 30+ new prompts covering the complexity spectrum
- Tag each prompt with `category` and `expected_difficulty` (easy/medium/hard)
- Include edge cases that test policy boundaries (the router should escalate these to stronger models)

**Deliverables:**
- `sample-data/router-eval-prompts.jsonl` — 50+ tagged prompts
- Documented rationale for prompt selection

---

### Lab 2 — Deploy and Configure Model Router

**What:** Deploy Model Router in Sweden Central, explore configuration options.

**Key concepts introduced:**
- Quick deploy vs Custom deploy
- Routing mode selection (start with Balanced)
- Model subset — which models to include/exclude
- Versioning (`2025-11-18` active, receives updates)
- Data Zone Standard vs Global Standard deployment types
- Context window considerations (smallest model = effective limit)

**Hands-on:**
1. Deploy Model Router via portal (Quick deploy)
2. Deploy Model Router via CLI/SDK (Custom deploy with explicit mode + subset)
3. Send a test prompt and inspect the response metadata (which model was selected)
4. Verify prompt caching behavior with repeated system prompts

**Deliverables:**
- Model Router deployment in Balanced mode
- Confirmed: can see which backing model handles each request
- Understanding of how to switch modes without redeployment

---

### Lab 3 — Baseline vs. Router: The First Comparison

**What:** Run the full prompt set against (a) the frontier baseline and (b) Model Router. Compare quality, cost, latency.

**Key concepts introduced:**
- The auto-eval pipeline (from `microsoft-foundry/Model-Router-Auto-Evaluation`)
- LLM-as-a-judge with anti-bias (dual-ordered pairwise scoring)
- Router-aware cost math (router markup + underlying model pricing)
- Model distribution — which models the router chose and how often
- Value & efficiency composites (quality-per-dollar, quality-per-second)

**Approach:**
1. Configure the auto-eval pipeline with WWI prompts
2. Run: frontier baseline (all prompts → `gpt-5`)
3. Run: Model Router Balanced (all prompts → router decides)
4. Generate dashboard — compare side-by-side
5. Analyze model distribution: "What did the router choose for simple FAQ vs. complex trip planning?"

**The revelation:**
- Simple policy questions → routed to smaller, cheaper models (nano/mini)
- Complex multi-step planning → routed to frontier
- Edge cases → routed to reasoning models
- **The router's choices ARE the workload decomposition** — no manual classification needed

**Deliverables:**
- `results/baseline-vs-router-balanced/dashboard.html`
- Model distribution chart showing per-category routing decisions
- Cost savings quantified (expect 40–60% on Balanced mode)

---

### Lab 4 — Custom Evaluator: Policy-Adherence with Adaptive Eval Rubric

**What:** Build a domain-specific evaluator using the Foundry Adaptive Evals framework with an eval-rubric.

**Key concepts introduced:**
- Why generic quality scores aren't enough (policy correctness ≠ general helpfulness)
- Eval-rubric structure: criteria, scales, weights, adaptive rules
- Prompt-based evaluators with rubric templates
- Adaptive rules that shift scoring emphasis based on input context
- The `{{response}}` and `{{ground_truth}}` template pattern

**The Policy-Adherence Evaluator:**

```yaml
name: "wwi_policy_adherence_eval"
description: "Evaluates whether AI responses correctly apply WWI policy rules."
version: 1.0

criteria:
  - id: rule_accuracy
    description: "Does the response cite the correct policy rule for the question asked?"
    scale: 1-5
    weight: 0.35
  - id: completeness
    description: "Are all relevant conditions, exceptions, and approval requirements mentioned?"
    scale: 1-5
    weight: 0.25
  - id: boundary_precision
    description: "Are dollar amounts, day counts, percentage thresholds, and approval levels exact?"
    scale: 1-5
    weight: 0.25
  - id: hallucination_absence
    description: "Does the response avoid inventing rules, limits, or exceptions not in the policy?"
    scale: 1-5
    weight: 0.15

adaptive_rules:
  # Rule 1: Budget/limit questions demand exact numbers
  - condition: "input.category == 'budget_cap' or input.category == 'reimbursement'"
    adjust_weights:
      rule_accuracy: 0.25
      completeness: 0.20
      boundary_precision: 0.40
      hallucination_absence: 0.15

  # Rule 2: Exception/approval-chain questions demand completeness
  - condition: "input.category == 'exception' or input.category == 'approval_chain'"
    adjust_weights:
      rule_accuracy: 0.30
      completeness: 0.40
      boundary_precision: 0.15
      hallucination_absence: 0.15

  # Rule 3: Edge cases (ambiguous scenarios) — hallucination risk is highest
  - condition: "input.category == 'edge_case'"
    adjust_weights:
      rule_accuracy: 0.25
      completeness: 0.20
      boundary_precision: 0.15
      hallucination_absence: 0.40

scoring:
  method: weighted_average
  pass_threshold: 3.5
```

**The Judge Prompt (prompt-based evaluator):**

```
You are evaluating an AI travel assistant's response against WWI's official policy.

## Policy Document (ground truth):
{{ground_truth}}

## User Question:
{{query}}

## AI Response to Evaluate:
{{response}}

## Scoring Rubric

Score each criterion from 1 (worst) to 5 (best):

### 1. Rule Accuracy (Does it cite the RIGHT rule?)
- 5: Cites the exact correct policy section and rule
- 4: Correct rule, minor section reference error
- 3: Partially correct — misses a related rule that applies
- 2: Cites a wrong rule or conflates two different rules
- 1: Completely wrong rule or no policy reference at all

### 2. Completeness (Are ALL conditions mentioned?)
- 5: All conditions, exceptions, and approval requirements included
- 4: Missing one minor condition that rarely applies
- 3: Missing a significant condition (e.g., approval threshold)
- 2: Only mentions the base rule, ignores exceptions entirely
- 1: Answer is a fragment with no useful policy detail

### 3. Boundary Precision (Are numbers EXACT?)
- 5: All dollar amounts, day counts, percentages match the policy exactly
- 4: One number is approximate but within 5% of correct
- 3: One number is wrong or a threshold is described vaguely ("a few days")
- 2: Multiple numbers are wrong or fabricated
- 1: No specific numbers given when the policy has them

### 4. Hallucination Absence (Does it AVOID making things up?)
- 5: Every claim is traceable to the policy document — nothing invented
- 4: One minor implication that's reasonable but not stated in policy
- 3: One fabricated rule or limit that sounds plausible but isn't in the policy
- 2: Multiple invented rules mixed with real ones
- 1: Largely fabricated response with minimal basis in the actual policy

Output Format (JSON):
{
  "rule_accuracy": <1-5>,
  "completeness": <1-5>,
  "boundary_precision": <1-5>,
  "hallucination_absence": <1-5>,
  "result": <weighted average as float>,
  "reason": "<2-3 sentence justification>"
}
```

**Hands-on:**
1. Define the eval-rubric YAML
2. Create the prompt-based evaluator using the Foundry SDK
3. Prepare a small policy-question dataset with ground truth (pull from travel-policy.md)
4. Run the evaluator against both baseline and router responses
5. Compare: Does the router maintain policy accuracy when routing policy questions to smaller models?

**Novel insight for learners:**
- The adaptive rules mean the evaluator automatically becomes stricter on boundary precision for budget questions and stricter on hallucination detection for edge cases
- This mirrors how a human reviewer would shift attention based on question type
- The evaluator adapts WITHOUT re-running — the rubric weights shift at scoring time

**Deliverables:**
- `code/eval-rubric-policy-adherence.yaml`
- `code/policy_adherence_evaluator.py` (SDK integration)
- `sample-data/policy-eval-dataset.jsonl` (20 policy questions with ground truth)
- Results comparing router vs baseline on policy-adherence specifically

---

### Lab 5 — Optimize: Routing Modes and Model Subset

**What:** Systematically compare Balanced vs. Cost vs. Quality modes. Then tune the model subset.

**Key concepts introduced:**
- How mode affects the quality band (1–2% for Balanced, 5–6% for Cost)
- Model subset as a compliance/control lever
- Comparing runs with the auto-eval `compare_results.py`
- Trade-off visualization: quality-per-dollar and quality-per-second

**Hands-on:**
1. Run eval with router in **Cost** mode → measure savings vs. quality drop
2. Run eval with router in **Quality** mode → measure quality gain vs. cost increase
3. Run eval with a **custom model subset** (e.g., exclude reasoning models, or limit to gpt-4.1 family only)
4. Compare all three runs side-by-side with the auto-eval compare tool
5. Make the decision: "For WWI, which mode gives the best trade-off?"

**The "aha" moment:**
- Balanced mode delivers ~60% of the cost savings with <2% quality loss
- Cost mode is aggressive — great for high-volume, low-stakes (e.g., inline summaries)
- Quality mode is almost identical to baseline — useful as a safety net
- Model subset lets you say "only use models I've vetted" — compliance without losing routing intelligence

**Deliverables:**
- Three eval runs (Balanced/Cost/Quality) compared
- One subset-constrained run
- Decision matrix: "which mode for which task category?"

---

### Lab 6 — Advanced: Prompt Caching + Combined Optimization

**What:** Enable and measure prompt caching benefits. Combine mode tuning + subset + caching for maximum optimization.

**Key concepts introduced:**
- How prompt caching works with Model Router (automatic when underlying model supports it)
- Cache hit conditions (same model handles consecutive requests with overlapping prefixes)
- System prompt design for cache-friendliness
- Combined optimization: mode + subset + caching = compounding savings

**Hands-on:**
1. Design a cacheable system prompt for WWI (policy document as prefix)
2. Send repeated policy questions → measure cache hit rate and latency reduction
3. Compare: cached vs. non-cached runs on the same prompts
4. Calculate compound savings: routing savings × caching savings

**Deliverables:**
- Measured prompt caching benefit (latency + cost reduction)
- Final optimized configuration (mode + subset + caching strategy)
- Updated scorecard: v1 (frontier) → v-final (router optimized)

---

### Lab 7 — Operate: Monitoring, Failover, and Continuous Eval

**What:** Set up production-grade operations with Model Router.

**Key concepts introduced:**
- Automatic failover — how it works, why model subset needs ≥2 models
- Model distribution monitoring over time (detect drift)
- Continuous evaluation with the policy-adherence evaluator
- When to re-evaluate (new models added to router, version updates)
- Submitting results to Foundry portal for governance (`run_foundry_eval.py`)

**Hands-on:**
1. Simulate failover: observe router behavior when primary model is throttled
2. Set up continuous eval: sample N% of production traffic, score with policy-adherence rubric
3. Push results to Foundry portal for cloud-graded visibility
4. Create an alert: "if policy-adherence drops below 3.5, notify the team"

**Deliverables:**
- Continuous eval pipeline configured
- Foundry portal showing eval results over time
- Failover behavior documented
- Production readiness checklist

---

### Lab 99 — Recap & Decision Framework

**What:** Synthesize learnings into a decision framework.

**Key takeaways:**
1. **Model Router vs. Manual routing** — use Router when you want zero routing code and your workload is diverse; use manual when you need deterministic control per-task.
2. **Mode selection** — Balanced is the default for most workloads; Cost for high-volume/low-stakes; Quality for safety-critical paths.
3. **Model subset** — use for compliance, cost capping, or when you need predictable model behavior.
4. **Custom evaluators** — always build a domain-specific evaluator; generic quality scores hide important failures.
5. **The loop** — Deploy → Measure → Tune mode/subset → Measure again → Operate.

**The final scorecard:**

```
                         Quality   Cost/task   p50 latency   Policy-Adherence
────────────────────────  ────────  ──────────  ────────────  ──────────────────
v1  Frontier (gpt-5)      4.3       $0.028      3.2s          4.1
v2  Router Balanced        4.2       $0.011      2.1s          4.0
v3  Router Cost            3.9       $0.006      1.4s          3.6
v4  Router + subset tuned  4.3       $0.009      1.8s          4.1
```

> **The story:** Same quality, 68% less cost, 44% less latency — and we wrote zero routing code.

---

## File structure (planned)

```
workshops/model-router-demystified/
├── README.md
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
│   └── travel-policy.md                ← symlink or copy from foundry-models-e2e
├── code/
│   ├── requirements.txt
│   ├── config.py                       ← endpoints, deployment names, pricing
│   ├── eval-rubric-policy-adherence.yaml  ← the adaptive eval rubric
│   ├── policy_adherence_evaluator.py   ← SDK integration for custom evaluator
│   ├── run_comparison.py               ← baseline vs router eval driver
│   ├── run_mode_comparison.py          ← Balanced vs Cost vs Quality
│   └── prompt_caching_demo.py          ← cache hit measurement
└── slides/                             ← (optional) MARP deck
```

---

## References

| Resource | URL |
|---|---|
| Model Router concept docs | https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/model-router |
| Model Router how-to | https://learn.microsoft.com/azure/foundry/openai/how-to/model-router |
| How Model Router works (deep dive) | https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/model-router-how-it-works |
| Auto-Evaluation repo | https://github.com/microsoft-foundry/Model-Router-Auto-Evaluation |
| Blog: How to run evals for Model Router | https://devblogs.microsoft.com/foundry/how-to-run-evals-for-model-router/ |
| Custom evaluators in Foundry | https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/custom-evaluators |
| Existing workshop (artifacts source) | `../workshops/foundry-models-e2e/` |

---

## Open questions / decisions

1. **Baseline model:** Use `gpt-5` or allow workshop to specify any frontier model? (Recommend: parametrize in config.py)
2. **Model subset for compliance lab:** Which models to exclude for the "compliance" scenario? (Recommend: exclude non-OpenAI models as a simple example)
3. **Prompt caching measurement:** Need to design prompts with overlapping prefixes for reliable cache hits. Policy document as system prompt is the natural choice.
4. **Foundry portal integration:** The `run_foundry_eval.py` step requires an active Foundry project with eval permissions. Mark as optional for self-paced learners without full access.

---

*Last updated: 2026-05-27*

---

## Addendum — Skill enhancements (2025-05-27)

### Workshop renamed

`model-router-workshop` → **`model-router-demystified`** (slug, folder, all references).

### `run-workshop` skill: modes added

| Mode | Trigger | Key behavior |
|---|---|---|
| Default | "Run workshop X" | Learner runs all commands, Copilot guides |
| **Learner** | "as learner" | + Feedback capture + granular `progress.<ts>.json` + visual scorecards |
| **Instructor** | "as instructor" | + Copilot may run commands + faster pacing + feedback → post-run fixes |

### Visual scorecards

The skill now displays ASCII-art scorecards at major step boundaries showing quality/cost/latency/custom metrics with progress bars and deltas. Scorecards are persisted in the progress file.

### Hill-climbing note

Both workshop READMEs now include a "Hill climbing in model optimization" callout explaining the incremental evidence-driven optimization loop.

### Artifact sync reminder

If `run-workshop` SKILL.md or the instructor-mode subskill is updated, verify both workshop READMEs reflect the same "How to run" section and mode descriptions.
