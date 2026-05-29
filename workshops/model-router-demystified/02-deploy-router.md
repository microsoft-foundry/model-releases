# Lab 2 — Deploy & Configure Model Router

> **Surface:** Portal + SDK · **Time:** ~15 min · **Outcome:** Model Router deployed with understood configuration options

## What you'll do

Explore Model Router's deployment and configuration options in depth. Understand routing modes, model subsets, versioning, and how to inspect which model handles each request.

## Key concepts

| Concept | Detail |
|---|---|
| **Quick deploy** | One-click deployment with defaults (Balanced mode, all models) |
| **Custom deploy** | Choose routing mode + model subset explicitly |
| **Routing modes** | **Balanced** (1–2% quality band, cost-optimized), **Cost** (5–6% band, aggressive savings), **Quality** (always picks highest-quality model) |
| **Model subset** | Restrict which underlying models the router can select. New models aren't auto-added to your subset. |
| **Versioning** | `2025-11-18` is the active version — updated in-place with new models. Older versions are frozen. |
| **Context window** | Effective limit = smallest underlying model's window. Use model subset to control this. |
| **Auto-failover** | If a model is throttled, router transparently redirects to next-best model in your subset. |

## Step-by-step

### 2.1 — Explore in the portal

1. Navigate to your Foundry project → Model Catalog
2. Search for "model-router"
3. Open the model card — note:
   - Supported models list (28+ models across OpenAI, Anthropic, xAI, DeepSeek, Meta)
   - Pricing (router markup on input tokens + underlying model's own pricing)
   - Region availability (Sweden Central ✓)

### 2.2 — Understand routing mode behavior

Think of routing modes as a "quality tolerance knob":

```
Quality mode:  "Always use the best model. Cost is irrelevant."
                ├── Picks highest-quality model for each prompt
                └── Effectively = using frontier for everything (but with failover)

Balanced mode: "Stay within ~2% of the best quality. Minimize cost within that band."
                ├── Most prompts route to capable-but-cheaper models
                ├── Complex prompts still escalate to frontier
                └── DEFAULT — best for most workloads

Cost mode:     "Stay within ~6% of the best quality. Maximize savings."
                ├── Aggressively routes to cheapest sufficient model
                ├── Only truly hard prompts hit frontier
                └── Best for high-volume, low-stakes tasks
```

### 2.3 — Inspect the response metadata

When Model Router handles a request, the response tells you which model was actually used. This is the key to understanding routing decisions:

```python
from openai import AzureOpenAI
import os

client = AzureOpenAI(
    azure_endpoint=os.environ["AZURE_MODEL_ROUTER_ENDPOINT"],
    api_key=os.environ["AZURE_MODEL_ROUTER_KEY"],
    api_version="2025-04-01-preview"
)

response = client.chat.completions.create(
    model=os.environ["AZURE_MODEL_ROUTER_DEPLOYMENT"],
    messages=[{"role": "user", "content": "What is the meal per-diem for domestic travel?"}],
    max_tokens=200
)

print(f"Response: {response.choices[0].message.content}")
print(f"Model used: {response.model}")  # Shows which underlying model was selected
print(f"Tokens: {response.usage.prompt_tokens} in / {response.usage.completion_tokens} out")
```

### 2.4 — Test routing behavior with different prompts

Send prompts of varying complexity and observe which models get selected:

```python
test_prompts = [
    ("easy", "What's the parking reimbursement limit per day?"),
    ("medium", "Can I book premium economy on a 6-hour flight to London?"),
    ("hard", "My trip is 18 days away (international requires 21). I need an exception. Walk me through the approval chain, who signs off, and what documentation I need. Also check if any budget cap implications apply given it's a 5-night trip."),
]

for difficulty, prompt in test_prompts:
    resp = client.chat.completions.create(
        model=os.environ["AZURE_MODEL_ROUTER_DEPLOYMENT"],
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300
    )
    print(f"[{difficulty}] Model selected: {resp.model}")
```

**Expected pattern:**
- Easy → routes to smaller model (gpt-4.1-nano, gpt-5-nano)
- Medium → routes to mid-tier (gpt-4.1-mini, gpt-5-mini)
- Hard → routes to frontier (gpt-5, o4-mini for reasoning)

### 2.5 — Configure a model subset (optional exploration)

If you want to restrict which models participate:

```python
# When deploying with custom configuration, you can specify model subset
# This is done at deployment time via the portal or ARM API
# Example: Only allow gpt-4.1 family + gpt-5 family
# This ensures predictable behavior and cost bounds
```

**When to use model subset:**
- Compliance: "Only use models we've security-reviewed"
- Cost capping: "Exclude expensive reasoning models for this workload"
- Predictability: "Limit to 3 models so we know exactly what to expect"
- Context window: "Only include models with 128K+ context"

### 2.6 — Prompt caching preview

Model Router supports prompt caching automatically. When the router selects a model that supports caching, overlapping prompt prefixes are cached:

```python
# Same system prompt sent repeatedly = cache hits
system_prompt = "You are the WWI assistant. [full policy document here...]"

# First call: full price
# Subsequent calls with same prefix to same model: cached token pricing
for i in range(3):
    resp = client.chat.completions.create(
        model=os.environ["AZURE_MODEL_ROUTER_DEPLOYMENT"],
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Question {i}: What's the per-diem?"}
        ]
    )
    print(f"Call {i}: model={resp.model}, cached_tokens={getattr(resp.usage, 'cached_tokens', 'N/A')}")
```

> **Note:** Cache benefits depend on the router selecting the *same* underlying model for consecutive requests. This is more likely with model subset enabled.

## Checkpoint

- [ ] Understand the three routing modes and when to use each
- [ ] Can send a prompt and see which underlying model was selected
- [ ] Observed different models selected for different complexity levels
- [ ] Understand model subset as a control/compliance lever
- [ ] Aware of prompt caching behavior (explored in depth in Lab 6)

---

**Next:** [Lab 3 — Baseline vs. Router comparison →](./03-baseline-comparison.md)
