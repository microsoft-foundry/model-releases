# Lab 6 — Prompt Caching + Combined Optimization

> **Surface:** SDK · **Time:** ~15 min · **Outcome:** Measured caching benefits + final optimized configuration

## What you'll do

Enable and measure prompt caching benefits with Model Router. Then combine mode tuning + model subset + caching for maximum compound optimization.

## Key concepts

| Concept | Detail |
|---|---|
| **Prompt caching** | Automatic — when the router selects a model that supports caching, overlapping prompt prefixes are cached at reduced token pricing |
| **Cache hit conditions** | Same model handles consecutive requests + overlapping prompt prefix |
| **System prompt strategy** | A long, stable system prompt = high cache hit rate = compounding savings |
| **Model subset + caching** | Fewer eligible models = higher chance of consecutive cache hits |
| **Compound savings** | Routing savings × caching savings = multiplicative benefit |

## How prompt caching works with Model Router

```
Request 1:  system_prompt (2,000 tokens) + user_message_A (50 tokens)
            → Router picks gpt-5-mini
            → Full processing: 2,050 tokens at standard rate

Request 2:  system_prompt (2,000 tokens) + user_message_B (60 tokens)
            → Router picks gpt-5-mini (same model!)
            → Cached: 2,000 tokens at reduced rate + 60 new tokens at standard rate
            → Savings: ~50% on the system prompt portion

Request 3:  system_prompt (2,000 tokens) + user_message_C (40 tokens)
            → Router picks gpt-5 (different model)
            → NO cache hit — different model can't reuse cache
            → Full processing: 2,040 tokens at standard rate
```

**Key insight:** Model subset *improves* cache hit rate by constraining the router to fewer models. Fewer models = more likely consecutive requests hit the same model = more cache hits.

## Step-by-step

### 6.1 — Design a cache-friendly system prompt

The WWI policy document is the perfect cache candidate — it's long, stable, and sent with every request:

```python
# Load the full policy as the system prompt
with open("sample-data/travel-policy.md") as f:
    POLICY_DOCUMENT = f.read()

SYSTEM_PROMPT = f"""You are the WWI Concierge. Answer questions about travel policy accurately.
Always cite the specific section number from the policy when applicable.
If something is not covered by the policy, say so explicitly.

## WWI Policy (reference document):
{POLICY_DOCUMENT}
"""

# This system prompt is ~1,500 tokens — significant caching opportunity
```

### 6.2 — Measure cache behavior

```bash
python code/prompt_caching_demo.py --mode measure
```

This script:
1. Sends 20 policy questions with the same system prompt
2. Records which model was selected for each
3. Tracks `cached_tokens` in usage metadata
4. Reports: cache hit rate, latency reduction, cost reduction

### 6.3 — Compare: with vs. without model subset

```bash
# Without subset (all models eligible) — lower cache hit rate
python code/prompt_caching_demo.py --mode no-subset

# With subset (3 models only) — higher cache hit rate
python code/prompt_caching_demo.py --mode subset --models "gpt-5,gpt-5-mini,gpt-5-nano"
```

**Expected results:**

| Configuration | Cache hit rate | Avg latency | Avg cost/prompt |
|---|---|---|---|
| No subset (28 models) | ~15% | 2.1s | $0.011 |
| Subset (3 models) | ~55% | 1.6s | $0.008 |

### 6.4 — Calculate compound savings

```
Baseline (gpt-5, no routing, no caching):
  Cost per prompt: $0.028

Router Balanced + no caching:
  Cost per prompt: $0.011  (−61% from routing alone)

Router Balanced + subset + caching:
  Cost per prompt: $0.008  (−71% compound savings)

Total savings: $0.028 → $0.008 = 71% reduction
  └── Routing contributed: 61%
  └── Caching contributed: additional 10%
```

### 6.5 — System prompt design best practices for caching

| Practice | Why |
|---|---|
| Put stable content FIRST in system prompt | Prefix matching — longer stable prefix = more cacheable |
| Policy document before dynamic instructions | Policy rarely changes; per-request instructions vary |
| Use consistent formatting | Even whitespace changes break cache prefix matching |
| Keep model subset small | Increases probability of same-model consecutive routing |
| Batch similar queries together | If your app processes batches, group by category for better cache hits |

### 6.6 — Final optimized configuration

Combine all optimizations learned in Labs 3–6:

```yaml
# Final recommended config for WWI
deployment:
  model: model-router
  version: "2025-11-18"
  routing_mode: balanced
  model_subset:
    - gpt-5
    - gpt-5-mini
    - gpt-5-nano
    - gpt-4.1
    - gpt-4.1-mini
  sku: GlobalStandard
  region: swedencentral

system_prompt_strategy:
  # Stable policy document as prefix (cacheable)
  # Dynamic instructions appended after
  cache_prefix_tokens: ~1500

expected_performance:
  quality: 4.3  # matches baseline
  cost_per_prompt: $0.009
  p50_latency: 1.8s
  policy_adherence: 4.1
  cost_savings_vs_baseline: 68%
  latency_savings_vs_baseline: 44%
```

## The final scorecard update

```
                         Quality   Cost/task   p50 latency   Policy-Adherence
────────────────────────  ────────  ──────────  ────────────  ──────────────────
v1  Frontier (gpt-5)      4.3       $0.028      3.2s          4.1
v2  Router Balanced        4.2       $0.011      2.1s          4.0
v3  Router Cost            3.9       $0.006      1.4s          3.6
v4  Router + subset+cache  4.3       $0.009      1.8s          4.1   ← HERE
```

> **v4 matches v1 quality with 68% less cost and 44% less latency. Zero routing code written.**

## Checkpoint

- [ ] Measured prompt caching behavior with repeated system prompts
- [ ] Compared cache hit rates with and without model subset
- [ ] Calculated compound savings (routing + caching)
- [ ] Documented final optimized configuration
- [ ] Updated scorecard with v4 results

---

**Next:** [Lab 7 — Operate: monitoring & failover →](./07-operate.md)
