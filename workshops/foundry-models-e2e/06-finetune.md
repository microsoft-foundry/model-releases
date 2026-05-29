# Step 6 — Fine-tune `gpt-4.1` for policy (SDK + Foundry Skill)

> **Foundry lifecycle:** **03 · Optimize** (quality) + **05 · Improve** (one-line FT swap shows the safe-adoption pattern).

## Goal

Close the policy-QA quality gap (0.28 → ~0.94) at ~1/50th the cost of asking `gpt-4.1` for every policy answer. This is the step that makes the whole architecture earn its keep.

**Model:** `gpt-4.1` — supports **Supervised** and **DPO** fine-tuning in Sweden Central. Use Supervised for this workshop (chat-format JSONL, standard Q&A pairs).

> **Fine-tuning support in Sweden Central (verified May 2026)**
> | Method | Models |
> |---|---|
> | Supervised | gpt-4.1, gpt-4.1-mini, gpt-4.1-nano, gpt-4o, gpt-4o-mini, Llama-3.3-70B, gpt-oss-20b, Ministral-3B, qwen3-32b |
> | DPO | gpt-4.1, gpt-4.1-mini, gpt-4.1-nano, gpt-4o |
> | Reinforcement | o4-mini |

**Surface:** Foundry SDK to prepare/upload data and kick off the job; Foundry Skill (`microsoft-foundry`) to monitor + deploy.

**Time:** 90 min of your time, plus ~2–4 hours of fine-tune training (do this **Day 4 morning** in your 7-day plan).

**Scorecard at end of step:**
```
Quality   █████████░  0.94   ⬆️  (policy bumps overall pass rate over 0.92)
Cost      ███░░░░░░░  $0.029 ⬇️  (frontier no longer answers policy)
Latency   ████░░░░░░  8.1 s  ⬇️  (skip frontier turn for policy)
```

## Prereqs

- Step 5 complete: v2 measured, policy QA confirmed as the laggard.
- `sample-data/travel-policy.md` available and a policy training file prepared from it.
- Fine-tuning quota for `gpt-4.1` in Sweden Central (confirmed available — see the fine-tune table in the Goal section above).

## Steps

The numbered subsections below (6.1 – 6.8) are the actions to perform in order.

All three bars are within striking distance of the targets. Step 7 ties the bow.

---

## 6.1 — When to fine-tune (and when not to)

Fine-tune **only** when:
- A cheap base model is *close* but not great on a narrow domain task.
- You have ≥30 high-quality labeled examples (more is better; 100–500 is the realistic sweet spot for narrow QA).
- The task is **stable** — you'd be embarrassed to re-train every week.

Don't fine-tune when:
- You haven't tried a good system prompt + retrieval yet.
- Your eval doesn't isolate the task you're trying to fix.
- The base model already hits your target.

For WWI policy QA: ✅ on all three.

## 6.2 — Prepare the training data

The training set is **already split** into chat-format JSONL files you can use directly:

- `sample-data/policy-ft-train.jsonl` — 24 hand-authored policy Q&A pairs
- `sample-data/policy-ft-val.jsonl`   — 6 held-out validation rows

Each row looks like:

```json
{"messages":[{"role":"system","content":"You answer WWI policy questions. Concise."},{"role":"user","content":"Can I expense airport parking at SAN for a business trip?"},{"role":"assistant","content":"Yes — airport parking is reimbursable up to $25/day under Section 4.2. Submit the receipt within 30 days."}]}
{"messages":[{"role":"system","content":"You answer WWI policy questions. Concise."},{"role":"user","content":"Am I allowed to fly business class on a 4-hour flight?"},{"role":"assistant","content":"No. Business class is only approved for flights over 6 hours (Section 7.1)."}]}
```

Keep them in `.foundry/datasets/` so the portal can show lineage.

> Want to author your own? Read `sample-data/travel-policy.md`, write 30 Q&A pairs grounded in it, then split 80/20 train/val.

## 6.3 — Sanity check the base model first

The **policy-only slice** of the eval — `sample-data/eval-policy-only.jsonl` — is generated from the eval-full dataset. Regenerate it from Step 4's output with:

```bash
grep '"intent": "policy_question"' ../sample-data/eval-full.jsonl \
  > ../sample-data/eval-policy-only.jsonl
```

Then sanity check the base model:

```bash
python s05_run_eval.py --agent s05_multi_model_agent \
                   --eval ../sample-data/eval-policy-only.jsonl \
                   --label "policy-base"
# → quality ≈ 0.28  (policy-mini-base without fine-tuning; this is the gap we're closing)
```

Make a note. We need this *before* number for the on-stage chart. The next run
(`policy-ft`) will pass `--baseline policy-base` so the Δ column shows the
fine-tune lift inline.

## 6.4 — Kick off the fine-tune via SDK

`code/s06_finetune_policy.py`:

```python
# s06_finetune_policy.py — upload data, create fine-tune job, poll
# Uses the Azure OpenAI resource endpoint directly (project /v1 endpoint does
# not support fine-tuning). Endpoint is derived from PROJECT_ENDPOINT automatically.
import re, time
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AzureOpenAI
from s02_config import PROJECT_ENDPOINT

BASE_MODEL = "gpt-4.1"        # supports Supervised FT in Sweden Central
TRAIN_FILE = "../sample-data/policy-ft-train.jsonl"
VAL_FILE   = "../sample-data/policy-ft-val.jsonl"

_m = re.match(r"https://([^.]+)\.services\.ai\.azure\.com", PROJECT_ENDPOINT)
AOAI_ENDPOINT = f"https://{_m.group(1)}.openai.azure.com/"
token_provider = get_bearer_token_provider(
    DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")
client = AzureOpenAI(azure_endpoint=AOAI_ENDPOINT,
                     azure_ad_token_provider=token_provider,
                     api_version="2025-01-01-preview")

train = client.files.create(file=open(TRAIN_FILE, "rb"), purpose="fine-tune")
val   = client.files.create(file=open(VAL_FILE,   "rb"), purpose="fine-tune")
print("uploaded:", train.id, val.id)

job = client.fine_tuning.jobs.create(
    training_file=train.id, validation_file=val.id,
    model=BASE_MODEL,
    hyperparameters={"n_epochs": 3},
    suffix="wwi-policy-v1")
print("job:", job.id, "status:", job.status)

while True:
    job = client.fine_tuning.jobs.retrieve(job.id)
    print(f"  {job.status}  trained_tokens={job.trained_tokens}")
    if job.status in ("succeeded", "failed", "cancelled"): break
    time.sleep(60)

print("fine-tuned model id:", job.fine_tuned_model)
```

Run it:

```bash
python s06_finetune_policy.py
```

Training takes anywhere from 30 min to a few hours for 24 rows × 3 epochs. **Start this Day 4 morning so you have Day 5 as a buffer.**

> **If fine-tune is not yet available in Sweden Central**, the job will fail at create time. Check the portal: **Fine-tuning** → **+ Create** → Customization Method: Supervised — if `gpt-4.1` appears in the model list you're good. The original plan (`.plans/foundry-models-e2e-plan.md` §9.7) accounts for cross-region fallback.

## 6.5 — Deploy the fine-tuned model (Foundry Skill)

Once the job reports `succeeded` with a `fine_tuned_model` id, deploy it. The Foundry Skill is the cleanest path:

```
Deploy fine-tuned model <fine_tuned_model id from job> to project
wwi-concierge-demo in region swedencentral,
deployment name = policy-mini-ft, sku=Developer, tpm=10000.
Verify status=Succeeded and return the endpoint.
```

Or in the portal: **Fine-tuning** → click your job → **Deploy** → name it `policy-mini-ft` → **Deployment type: Developer**.

> **Always use the Developer SKU for workshop / test fine-tune deployments.** It has no hourly hosting fee — you pay per-token only — so a fine-tune you only hit during evals costs cents instead of dollars/day. Switch to Standard or Provisioned only when the deployment is serving real production traffic.

## 6.6 — Flip the agent to use the fine-tune

In `code/s05_multi_model_agent.py`:

```python
USE_FT_POLICY = True   # was False
```

That's the entire app change. **One boolean.** Because we named deployments by job in Step 3, the agent doesn't care which underlying model is serving the policy job.

> **This is the slide that lands hardest.** Naomi says: *"This is the whole point of decomposing your agent by task and naming deployments by job. The fine-tune is a one-line swap — and we can A/B it in Step 8."*

## 6.7 — Re-run policy eval

```bash
python s05_run_eval.py --agent s05_multi_model_agent \
                   --eval ../sample-data/eval-policy-only.jsonl \
                   --label "policy-ft" \
                   --baseline "policy-base"
# → quality ≈ 0.94, rendered with ▲ green delta vs the policy-base run
```

Cost per policy answer:
- Base `gpt-4.1`:      ~$0.003
- Fine-tuned `gpt-4.1`: ~$0.004 *(slight surcharge per token)*
- All policy via `gpt-4.1` (no FT): ~$0.003 but quality stays at 0.28

**Higher quality, same cost tier, domain-specific knowledge baked in.** That's the headline.

## 6.8 — Version everything

In your repo:

```bash
git tag agent-v2.1-ftpolicy
```

In the portal, the fine-tuned deployment carries a version + lineage to the training file. Open it in **Models + endpoints** and screenshot — this becomes a slide in Step 8.

## Verify

- Fine-tune job reaches `succeeded` state in the portal's **Fine-tuning** tab.
- Fine-tuned deployment callable from the SDK using its deployment name.
- Re-running the policy slice of the eval yields ≈ 0.94.

## Troubleshoot

| Symptom | Likely cause | Fix |
|---|---|---|
| Job fails immediately with region/SKU error | `gpt-4.1` fine-tune not available. | Check portal: **Fine-tuning** → **+ Create** → verify `gpt-4.1` is listed under Supervised. |
| Training file rejected | Wrong format or unescaped JSON. | Validate JSONL line-by-line; ensure `{messages: [...]}` shape. |
| Fine-tuned model quality no better than base | Too few examples or too narrow. | Add more policy Q&A pairs, especially edge cases the base model fails on. |

## Next

➡️ [Step 7 — Assemble the multi-model agent (v3)](./07-multi-model-agent.md)
