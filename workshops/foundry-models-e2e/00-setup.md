# Step 0 — Prereqs & project

> **Foundry lifecycle:** *prerequisite to entering the loop* — setup only.

## Goal

An empty Foundry project in Sweden Central + four model deployments + a local repo that can talk to it — all created from the command line in ~5 minutes.

**Time:** 5–10 min (script) or 15–20 min (manual CLI).

**Scorecard at end of step:**
```
Quality   ░░░░░░░░░░  —     (no agent yet)
Cost      ░░░░░░░░░░  —
Latency   ░░░░░░░░░░  —
```

## Prereqs

- Azure subscription with permission to create Microsoft Foundry resources in **Sweden Central**.
- Azure CLI (`az --version` ≥ 2.86), Python 3.11+, `pip`, `git`.
- VS Code with the Python extension.
- *(Optional)* GitHub Copilot CLI / Foundry MCP for "show me the catalog" queries.

> 📘 **Canonical reference:** [Quickstart: Setup Microsoft Foundry Resources](https://learn.microsoft.com/azure/ai-foundry/quickstarts/setup-resources). This workshop's `s00_setup.sh` is a thin wrapper around the exact `az` commands documented there, with workshop-specific defaults pre-filled.

> 🎯 **Optional stretch deployment — `model-router`.** The Step 8 "managed routing" comparison (`code/s09_router_agent.py`) compares our hand-rolled `router-nano` against Foundry's managed multi-model router. If you plan to show that stretch demo, deploy a **`model-router`** in this same project with the **deployment name exactly `auto-router`** (Build → Models → Deployments → + Deploy → search "model-router" → name `auto-router` → **TPM `100`**). The 100K capacity covers the 50-row demo set (~30K peak) and the 173-row offline set (~120K peak) with headroom; model-router quota is usually generous since it's a meta-deployment that bills at the chosen sub-model's rate. It is **not required** for the core v1/v2/v3 narrative — skip if you're sticking to the 8-step path.

## Steps

There are two paths. **Pick one.**

| Path | When to use | Subsections |
|---|---|---|
| **A — Scripted (recommended)** | You want a working environment in ≤10 minutes. | 0.1 → 0.2 → 0.4 → 0.5 |
| **B — Manual CLI** | You want to understand each `az` call. | 0.1 → 0.3 → 0.4 → 0.5 |

The portal appears only in §0.5 as a *verification* surface, not a creation surface.

---

## 0.1 — Clone the workshop repo and sign in

```bash
git clone <this-repo-url> wwi-concierge-demo
cd wwi-concierge-demo/workshops/foundry-models-e2e
python -m venv .venv && source .venv/bin/activate
pip install -r code/requirements.txt

az login
az account set --subscription "<your-sub-id-or-name>"
```

`code/requirements.txt` already pins the v2 SDKs:

```
azure-ai-projects>=2.1.0
azure-ai-evaluation>=1.16.0
azure-identity>=1.17.0
openai>=2.0.0
python-dotenv>=1.0.1
rich>=13.7.1
```

## 0.2 — Path A: run the setup script

The script provisions the resource group, Foundry account, project, and four model deployments — and writes `.env` with the project endpoint.

```bash
./code/s00_setup.sh
```

You'll be prompted for two things (defaults shown in brackets):

```
Project name [wwi-concierge-demo]:
Azure region [swedencentral]:
```

Everything else is derived from the project name:

| Resource | Naming pattern | Default |
|---|---|---|
| Resource group | `rg-<project>` | `rg-wwi-concierge-demo` |
| Foundry (AIServices) account | `<project>-foundry` | `wwi-concierge-demo-foundry` |
| Custom subdomain | same as account | `wwi-concierge-demo-foundry` |
| Project | `<project>` | `wwi-concierge-demo` |
| Deployment `planner-gpt41` | job-shaped name → `gpt-4.1` 2025-04-14 | GlobalStandard · 10 TPM |
| Deployment `router-nano` | job-shaped name → `gpt-4.1-nano` 2025-04-14 | GlobalStandard · 10 TPM |
| Deployment `mini-vision` | job-shaped name → `gpt-4.1-mini` 2025-04-14 | GlobalStandard · 10 TPM |
| Deployment `policy-mini-base` | job-shaped name → `gpt-4.1-mini` 2025-04-14 | GlobalStandard · 10 TPM |

The script is **idempotent** — re-run it safely if a step fails. Each resource is checked with `... show` before `... create`.

When it finishes you'll see:

```
✓ Wrote /…/foundry-models-e2e/.env
Setup complete.
```

Skip to **§0.4 (verify in the portal)**.

## 0.3 — Path B: run the `az` commands manually

If you want to see exactly what the script does, run these in order. Set variables once at the top:

```bash
PROJECT=wwi-concierge-demo
LOCATION=swedencentral
RG="rg-${PROJECT}"
FOUNDRY="${PROJECT}-foundry"
```

**1. Resource group.**

```bash
az group create -n "$RG" -l "$LOCATION"
```

**2. Foundry (AIServices) account with project management enabled.**

```bash
az cognitiveservices account create \
  --name "$FOUNDRY" --resource-group "$RG" \
  --kind AIServices --sku s0 --location "$LOCATION" \
  --custom-domain "$FOUNDRY" \
  --allow-project-management true \
  --yes
```

> 🔑 `--allow-project-management true` is the toggle that turns an AIServices account into a Foundry-capable account. Without it, project creation will fail.

**3. Project.**

```bash
az cognitiveservices account project create \
  --name "$FOUNDRY" --resource-group "$RG" \
  --project-name "$PROJECT" --location "$LOCATION"
```

**4. Four model deployments.**

```bash
for row in "planner-gpt41|gpt-4.1|2025-04-14" \
           "router-nano|gpt-4.1-nano|2025-04-14" \
           "mini-vision|gpt-4.1-mini|2025-04-14" \
           "policy-mini-base|gpt-4.1-mini|2025-04-14"; do
  DNAME=${row%%|*}; rest=${row#*|}; M=${rest%%|*}; V=${rest#*|}
  az cognitiveservices account deployment create \
    --name "$FOUNDRY" --resource-group "$RG" \
    --deployment-name "$DNAME" \
    --model-name "$M" --model-version "$V" \
    --model-format OpenAI \
    --sku-capacity 10 --sku-name GlobalStandard
done
```

**5. Capture the project endpoint into `.env`.**

```bash
ENDPOINT=$(az cognitiveservices account project show \
  --name "$FOUNDRY" --resource-group "$RG" --project-name "$PROJECT" \
  --query 'properties.endpoints."AI Foundry API"' -o tsv)

cat > .env <<EOF
FOUNDRY_PROJECT_ENDPOINT=${ENDPOINT}
FOUNDRY_PROJECT_NAME=${PROJECT}
AZURE_RESOURCE_GROUP=${RG}
AZURE_LOCATION=${LOCATION}
FOUNDRY_ACCOUNT_NAME=${FOUNDRY}
EOF
```

## 0.4 — Verify model catalog (Portal)

This is the **only** time we use the portal in Step 0 — to visually confirm the three deployments landed and to peek at the wider catalog before Step 3 model selection.

1. Open <https://ai.azure.com>.
2. Top-right region picker → **Sweden Central**.
3. Open your project (sidebar → **All projects** → `wwi-concierge-demo`).
4. Left nav → **Models + endpoints**. You should see four rows, each `Succeeded`:
   - `planner-gpt41` (gpt-4.1 · 2025-04-14)
   - `router-nano` (gpt-4.1-nano · 2025-04-14)
   - `mini-vision` (gpt-4.1-mini · 2025-04-14)
   - `policy-mini-base` (gpt-4.1-mini · 2025-04-14)
5. Left nav → **Model catalog** → filter **Collection = "Sold directly by Azure"**, **Region = Sweden Central**. Scan it once so you know what's available for Step 3.

> 🎓 `gpt-4.1` supports **Supervised** and **DPO** fine-tuning in Sweden Central — no cross-region workaround needed in Step 6.

## 0.5 — Sanity check (CLI)

```bash
az cognitiveservices account deployment list \
  -n "${FOUNDRY:-wwi-concierge-demo-foundry}" \
  -g "${RG:-rg-wwi-concierge-demo}" \
  --query "[].{name:name, state:properties.provisioningState, model:properties.model.name, version:properties.model.version}" \
  -o table
```

You should see all three deployments in state `Succeeded`. If you do, **you're done with Step 0**.

## Verify

- The `az ... deployment list` table above shows three rows in `Succeeded`.
- `.env` exists at the workshop root with `FOUNDRY_PROJECT_ENDPOINT` populated.
- The portal **Models + endpoints** view shows the same three deployments.

## Troubleshoot

| Symptom | Likely cause | Fix |
|---|---|---|
| `az cognitiveservices account create` fails with `SkuNotAvailable` | S0 not enabled in the region. | Try a different region (`eastus`, `swedencentral`) and rerun. |
| `account project create` returns `OperationNotAllowed` | The Foundry account was created without `--allow-project-management`. | Re-run §0.3 step 2 with the flag, or delete + recreate the account. |
| `deployment create` returns `QuotaExceeded` | Region quota for `GlobalStandard` is low. | Either request a quota increase, or use a different region for that one model. |
| `s00_setup.sh` exits at "Not signed in" | Token expired. | `az login` once, then re-run the script — it's idempotent. |
| `.env` has an empty endpoint | Project still provisioning. | Wait 60s, re-run §0.3 step 5 by itself. |

## Next

➡️ [Step 1 — Baseline in the playground](./01-baseline-portal.md)
