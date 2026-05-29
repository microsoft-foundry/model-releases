# Lab 5 — Optimize: Routing Modes & Model Subset

> **Surface:** SDK · **Time:** ~20 min · **Outcome:** Systematic comparison of Balanced/Cost/Quality modes + model subset tuning

## What you'll do

Run evaluations across all three routing modes and a custom model subset. Compare results side-by-side to find the optimal configuration for WWI.

## Key concepts

| Concept | Detail |
|---|---|
| **Mode switching** | Change routing behavior without code changes — config only |
| **Quality band** | Balanced ≈ 1–2% from best; Cost ≈ 5–6% from best; Quality = always best |
| **Model subset** | Restrict eligible models for compliance, cost capping, or predictability |
| **Compare runs** | Side-by-side diff of multiple eval runs |
| **Decision matrix** | Map each mode to the task categories where it's appropriate |

## Step-by-step

### 5.1 — Deploy router variants (or reconfigure)

You need to evaluate three modes. Options:

**Option A: Three deployments** (recommended for parallel comparison)
```bash
# Already have: model-router (Balanced)
# Add:
az cognitiveservices account deployment create \
  --deployment-name "model-router-cost" \
  --model-name "model-router" \
  --model-version "2025-11-18" \
  --sku-name "GlobalStandard" \
  --sku-capacity 100
  # Set routing_mode: "cost" via portal or ARM properties

az cognitiveservices account deployment create \
  --deployment-name "model-router-quality" \
  --model-name "model-router" \
  --model-version "2025-11-18" \
  --sku-name "GlobalStandard" \
  --sku-capacity 100
  # Set routing_mode: "quality" via portal or ARM properties
```

**Option B: Single deployment, reconfigure between runs** (saves quota)

### 5.2 — Run evaluation: Cost mode

```bash
python code/run_mode_comparison.py \
  --mode cost \
  --dataset sample-data/router-eval-prompts.jsonl \
  --output results/router-cost/
```

### 5.3 — Run evaluation: Quality mode

```bash
python code/run_mode_comparison.py \
  --mode quality \
  --dataset sample-data/router-eval-prompts.jsonl \
  --output results/router-quality/
```

### 5.4 — Run evaluation: Custom model subset

Create a subset-constrained deployment (e.g., only gpt-4.1 family + gpt-5):

```bash
python code/run_mode_comparison.py \
  --mode balanced \
  --subset "gpt-4.1,gpt-4.1-mini,gpt-4.1-nano,gpt-5,gpt-5-mini,gpt-5-nano" \
  --dataset sample-data/router-eval-prompts.jsonl \
  --output results/router-subset/
```

### 5.5 — Compare all runs side-by-side

```bash
python code/run_mode_comparison.py --compare \
  results/baseline-vs-balanced/ \
  results/router-cost/ \
  results/router-quality/ \
  results/router-subset/
```

### 5.6 — Analyze the trade-offs

**Expected results matrix:**

| Config | Quality (1–5) | Cost/prompt | p50 Latency | Policy-Adherence | Best for |
|---|---|---|---|---|---|
| Baseline (gpt-5) | 4.3 | $0.028 | 3.2s | 4.1 | Maximum quality guarantee |
| Router Balanced | 4.2 | $0.011 | 2.1s | 4.0 | **General purpose (default)** |
| Router Cost | 3.9 | $0.006 | 1.4s | 3.6 | High-volume, low-stakes |
| Router Quality | 4.4 | $0.025 | 3.0s | 4.2 | Safety-critical paths |
| Router Subset (gpt-4.1+5) | 4.3 | $0.009 | 1.8s | 4.1 | **Compliance + savings** |

### 5.7 — Build the decision matrix

Map modes to task categories:

| Task category | Recommended mode | Rationale |
|---|---|---|
| `simple_faq` | Cost | Low stakes, savings are large, quality drop is acceptable |
| `policy_question` | Balanced | Needs accuracy but most are straightforward |
| `trip_planning` | Balanced | Multi-step but router handles well |
| `receipt_expense` | Balanced or Subset | Numbers matter — don't let it route to weakest models |
| `edge_case` | Quality or Subset | High hallucination risk — need strongest models |
| `multi_step_reasoning` | Quality | Requires frontier reasoning capability |

### 5.8 — The "aha" moment

> **You can't use different modes for different prompts in a single deployment.** But you CAN:
> 1. Use **model subset** to exclude models that fail on your domain (achieves most of the benefit)
> 2. Deploy **two router endpoints** — one Balanced for general traffic, one Quality for critical paths
> 3. Use your own lightweight classifier to route between router deployments (hybrid approach)

**The simplest winning strategy for most workloads:**
- Balanced mode + curated model subset = best trade-off
- Exclude models that scored poorly on your custom evaluator
- Review subset quarterly as new models arrive

## Model distribution comparison

Compare what the router selects across modes:

```
Balanced mode distribution:
  gpt-5-nano:  25%   ← simple queries
  gpt-5-mini:  35%   ← moderate queries
  gpt-5:       25%   ← complex queries
  o4-mini:     15%   ← reasoning tasks

Cost mode distribution:
  gpt-5-nano:  45%   ← much more aggressive on cheap models
  gpt-5-mini:  35%
  gpt-5:       15%
  o4-mini:      5%

Quality mode distribution:
  gpt-5:       65%   ← heavily favors frontier
  o4-mini:     25%
  gpt-5-mini:  10%
  gpt-5-nano:   0%   ← never picks cheapest
```

## Checkpoint

- [ ] Ran evaluations for all three routing modes
- [ ] Ran at least one model-subset-constrained evaluation
- [ ] Generated comparison report across all runs
- [ ] Built a decision matrix (which mode for which task type)
- [ ] Identified optimal configuration for WWI (likely: Balanced + subset)
- [ ] Understand the model distribution differences between modes

---

**Next:** [Lab 6 — Prompt caching →](./06-prompt-caching.md)
