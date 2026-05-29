# Lab 0 — Setup & Prerequisites

> **Surface:** Portal + CLI · **Time:** ~15 min · **Outcome:** Foundry project provisioned, Model Router + baseline deployed

## What you'll do

1. Provision (or reuse) a Foundry project in **Sweden Central**
2. Deploy the **Model Router** (Global Standard, Balanced mode)
3. Deploy a **baseline frontier model** (e.g., `gpt-5`)
4. Configure credentials in `.env`
5. Verify both endpoints respond

## Prerequisites

- Azure subscription with access to Azure AI Foundry
- Python 3.9+ with `pip`
- Azure CLI (`az`) installed and authenticated (`az login`)
- Access to Model Router in Sweden Central (Global Standard or Data Zone Standard)

## Key concepts

| Concept | What to know |
|---|---|
| **Model Router** | A trained language model that routes prompts to the optimal LLM in real time. Deploy it like any other model. |
| **Routing modes** | Balanced (default), Cost, Quality — controls the quality/cost trade-off band |
| **Model subset** | Choose which underlying models participate in routing decisions |
| **Supported regions** | East US 2, Sweden Central |
| **Deployment types** | Global Standard, Data Zone Standard |

## Step-by-step

### 0.1 — Create or reuse a Foundry project

If you completed the `foundry-models-e2e` workshop, you can reuse that project (it's already in Sweden Central).

Otherwise, create a new project:

```bash
# Via Azure CLI
az ai project create \
  --name "wwi-model-router" \
  --resource-group "rg-wwi" \
  --location "swedencentral"
```

Or use the Foundry portal: [https://ai.azure.com](https://ai.azure.com) → New Project → Sweden Central.

### 0.2 — Deploy Model Router

**Option A: Quick deploy (portal)**
1. Go to Model Catalog → search "model-router"
2. Click Deploy → Quick deploy
3. Deployment name: `model-router`
4. Region: Sweden Central
5. Deployment type: Global Standard

**Option B: Custom deploy (portal)**
1. Model Catalog → "model-router" → Deploy → Custom deploy
2. Set routing mode: **Balanced**
3. Model subset: leave default (all supported models) for now
4. Deployment name: `model-router-balanced`

**Option C: CLI**
```bash
az cognitiveservices account deployment create \
  --name "your-foundry-resource" \
  --resource-group "rg-wwi" \
  --deployment-name "model-router" \
  --model-name "model-router" \
  --model-version "2025-11-18" \
  --model-format "OpenAI" \
  --sku-capacity 100 \
  --sku-name "GlobalStandard"
```

### 0.3 — Deploy baseline frontier model

Deploy your comparison model (e.g., `gpt-5`):

```bash
az cognitiveservices account deployment create \
  --name "your-foundry-resource" \
  --resource-group "rg-wwi" \
  --deployment-name "gpt-5-baseline" \
  --model-name "gpt-5" \
  --model-version "2025-08-07" \
  --model-format "OpenAI" \
  --sku-capacity 100 \
  --sku-name "GlobalStandard"
```

### 0.4 — Configure credentials

```bash
cd workshops/model-router-demystified/code
cp .env.example .env
```

Fill in your `.env`:

```env
# Model Router
AZURE_MODEL_ROUTER_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_MODEL_ROUTER_KEY=your-key
AZURE_MODEL_ROUTER_DEPLOYMENT=model-router

# Baseline model
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_KEY=your-key
AZURE_BASELINE_DEPLOYMENT=gpt-5-baseline

# Judge model (for LLM-as-a-judge scoring)
AZURE_JUDGE_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_JUDGE_KEY=your-key
AZURE_JUDGE_DEPLOYMENT=gpt-5-baseline

# Foundry project (for portal integration)
AZURE_AI_PROJECT_ENDPOINT=https://your-account.services.ai.azure.com/api/projects/your-project
```

### 0.5 — Install dependencies

```bash
pip install -r requirements.txt
```

### 0.6 — Verify endpoints

```python
python -c "
from config import get_router_client, get_baseline_client
r = get_router_client()
b = get_baseline_client()
print('Router:', r.chat.completions.create(
    model='model-router', messages=[{'role':'user','content':'Hello'}],
    max_tokens=5).choices[0].message.content)
print('Baseline:', b.chat.completions.create(
    model='gpt-5-baseline', messages=[{'role':'user','content':'Hello'}],
    max_tokens=5).choices[0].message.content)
print('✅ Both endpoints responding')
"
```

## Checkpoint

- [ ] Foundry project exists in Sweden Central
- [ ] Model Router deployment in `Succeeded` state
- [ ] Baseline model deployment in `Succeeded` state
- [ ] `.env` configured with all endpoints/keys
- [ ] Both endpoints respond to a test prompt

## Troubleshooting

| Issue | Fix |
|---|---|
| Model Router deployment fails | Verify resource is in Sweden Central or East US 2 |
| "Model not found" | Ensure you're using model name `model-router` with version `2025-11-18` |
| Rate limit on first call | Global Standard starts at Tier 1 (1,000 RPM). Wait and retry. |

---

**Next:** [Lab 1 — Build the prompt set →](./01-prompt-set.md)
