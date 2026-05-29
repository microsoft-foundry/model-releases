#!/usr/bin/env bash
# s00_setup.sh — one-shot Foundry workshop setup (CLI-only, idempotent).
#
# Reference: Quickstart — Setup Microsoft Foundry Resources
#   https://learn.microsoft.com/azure/ai-foundry/quickstarts/setup-resources
#
# ─── OPTIONAL: model-router deployment for the Step 8 stretch demo ──────────
# The Step 8 "managed routing" comparison (code/s09_router_agent.py) needs a
# `model-router` deployment in the same project, named exactly `auto-router`.
# It is NOT required for the core 8-step narrative — v1, v2, v3 all use our
# hand-rolled router-nano. Skip if you don't plan to show the stretch demo.
#
# TPM sizing: 100K is recommended.
#   - eval-demo.jsonl (50 rows) needs ~30K peak
#   - eval-full.jsonl (173 rows) needs ~120K peak
#   - 100K covers the demo comfortably and is usually within default quota for
#     model-router (a meta-deployment that bills at the chosen sub-model rate).
#
# To enable, in the Foundry portal:
#   Build → Models → Deployments → + Deploy → search "model-router"
#   → Deployment name: auto-router → TPM: 100 → Create
# Or via CLI after this script completes:
#   az cognitiveservices account deployment create \
#     -g "$AZURE_RESOURCE_GROUP" -n "$FOUNDRY_ACCOUNT_NAME" \
#     --deployment-name auto-router \
#     --model-name model-router --model-version 2025-05-19 \
#     --model-format OpenAI --sku-name Standard --sku-capacity 100
# ────────────────────────────────────────────────────────────────────────────

set -euo pipefail

TOTAL_STEPS=7
STEP_NUM=0
SCRIPT_T0=$SECONDS
STEP_T0=$SECONDS

# ─── colors / glyphs ──────────────────────────────────────────────────────
if [[ -t 1 ]] && command -v tput >/dev/null && [[ $(tput colors 2>/dev/null || echo 0) -ge 8 ]]; then
  BOLD=$(tput bold);      DIM=$(tput dim);        RESET=$(tput sgr0)
  RED=$(tput setaf 1);    GREEN=$(tput setaf 2);  YELLOW=$(tput setaf 3)
  BLUE=$(tput setaf 4);   MAGENTA=$(tput setaf 5); CYAN=$(tput setaf 6)
else
  BOLD=; DIM=; RESET=; RED=; GREEN=; YELLOW=; BLUE=; MAGENTA=; CYAN=
fi

WIDTH=$(tput cols 2>/dev/null || echo 72); WIDTH=$(( WIDTH > 78 ? 78 : WIDTH ))
repeat() { awk -v n="$1" -v c="$2" 'BEGIN{ for(i=0;i<n;i++) printf "%s", c; print "" }'; }
hr() { repeat "$WIDTH" "─"; }

banner() {
  echo
  echo "${CYAN}${BOLD}$(hr)${RESET}"
  echo "  ${BOLD}$1${RESET}"
  echo "  ${DIM}$2${RESET}"
  echo "${CYAN}${BOLD}$(hr)${RESET}"
  echo
}

step() {
  STEP_NUM=$((STEP_NUM + 1))
  STEP_T0=$SECONDS
  echo
  echo "${BLUE}${BOLD}[${STEP_NUM}/${TOTAL_STEPS}]${RESET} ${BOLD}$*${RESET}"
  echo "${DIM}$(hr)${RESET}"
}
ok()     { echo "  ${GREEN}✓${RESET} $*"; }
info()   { echo "  ${CYAN}·${RESET} $*"; }
warn()   { echo "  ${YELLOW}!${RESET} $*"; }
die()    { echo "  ${RED}✗${RESET} $*" >&2; exit 1; }
working(){ echo "  ${MAGENTA}…${RESET} ${DIM}$*${RESET}"; }
step_done() {
  local elapsed=$((SECONDS - STEP_T0))
  echo "  ${DIM}└─ done in ${elapsed}s${RESET}"
}

# ─── 0. banner ────────────────────────────────────────────────────────────
banner "Microsoft Foundry — workshop setup" \
       "Provisions RG → AIServices account → project → 3 deployments."

# ─── 1. prereqs ───────────────────────────────────────────────────────────
step "Checking prerequisites"
command -v az >/dev/null || die "Azure CLI not found. Install: https://aka.ms/azure-cli"
AZ_VER=$(az version --query '"azure-cli"' -o tsv 2>/dev/null || echo "?")
ok "az CLI ${AZ_VER}"
command -v jq >/dev/null && ok "jq present" || info "jq not installed (optional)"
step_done

# ─── 2. sign-in / subscription ────────────────────────────────────────────
step "Azure sign-in"
if ! az account show --only-show-errors >/dev/null 2>&1; then
  working "launching 'az login' (browser will open)..."
  az login --only-show-errors >/dev/null
fi
SUB_NAME=$(az account show --query name -o tsv)
SUB_ID=$(az account show --query id -o tsv)
TENANT=$(az account show --query tenantId -o tsv)
ok "subscription : ${BOLD}${SUB_NAME}${RESET}"
info "id           : ${DIM}${SUB_ID}${RESET}"
info "tenant       : ${DIM}${TENANT}${RESET}"
echo
read -r -p "  Use this subscription? [Y/n] " ans
if [[ "${ans:-Y}" =~ ^[Nn] ]]; then
  read -r -p "  Enter target subscription id or name: " new_sub
  az account set --subscription "$new_sub"
  ok "switched to: $(az account show --query name -o tsv)"
fi
step_done

# ─── 3. inputs & naming ───────────────────────────────────────────────────
step "Naming"
echo "  Project name controls every derived resource name."
read -r -p "  Project name [wwi-concierge-demo]: " PROJECT
PROJECT=${PROJECT:-wwi-concierge-demo}
read -r -p "  Azure region [swedencentral]: " LOCATION
LOCATION=${LOCATION:-swedencentral}
RG="rg-${PROJECT}"
FOUNDRY="${PROJECT}-foundry"

echo
echo "  ${BOLD}Will create:${RESET}"
printf "    %-18s %s\n" "resource group" "${BOLD}${RG}${RESET}"
printf "    %-18s %s\n" "foundry account" "${BOLD}${FOUNDRY}${RESET}"
printf "    %-18s %s\n" "project"         "${BOLD}${PROJECT}${RESET}"
printf "    %-18s %s\n" "region"          "${BOLD}${LOCATION}${RESET}"
printf "    %-18s %s\n" "deployments"     "planner-gpt41, router-nano, mini-vision, policy-mini-base"
  printf "    %-18s %s\n" "models"          "gpt-4.1, gpt-4.1-nano, gpt-4.1-mini, gpt-4.1-mini"
printf "    %-18s %s\n" "sku"             "GlobalStandard · 10 TPM each"
echo
read -r -p "  Proceed? [Y/n] " ans
[[ "${ans:-Y}" =~ ^[Nn] ]] && die "aborted by user."
step_done

# ─── 4. resource group ────────────────────────────────────────────────────
step "Resource group · ${RG}"
if az group show -n "$RG" >/dev/null 2>&1; then
  ok "already exists — reusing."
else
  working "creating in ${LOCATION}..."
  az group create -n "$RG" -l "$LOCATION" -o none
  ok "created."
fi
step_done

# ─── 5. Foundry (AIServices) account ──────────────────────────────────────
step "Foundry account · ${FOUNDRY}"
if az cognitiveservices account show -n "$FOUNDRY" -g "$RG" >/dev/null 2>&1; then
  ok "already exists — reusing."
else
  working "creating AIServices account with --allow-project-management..."
  az cognitiveservices account create \
    --name "$FOUNDRY" --resource-group "$RG" \
    --kind AIServices --sku s0 --location "$LOCATION" \
    --custom-domain "$FOUNDRY" \
    --allow-project-management true \
    --yes -o none
  ok "created."
fi
step_done

# ─── 6. project + deployments ─────────────────────────────────────────────
step "Project · ${PROJECT} (+ 3 model deployments)"
if az cognitiveservices account project show \
     --name "$FOUNDRY" --resource-group "$RG" \
     --project-name "$PROJECT" >/dev/null 2>&1; then
  ok "project already exists — reusing."
else
  working "creating project..."
  az cognitiveservices account project create \
    --name "$FOUNDRY" --resource-group "$RG" \
    --project-name "$PROJECT" --location "$LOCATION" -o none
  ok "project created."
fi
echo

deploy_model() {
  local deploy_name="$1" model_name="$2" version="$3"
  if az cognitiveservices account deployment show \
       -n "$FOUNDRY" -g "$RG" --deployment-name "$deploy_name" >/dev/null 2>&1; then
    ok "${deploy_name} ${DIM}(exists)${RESET}"
  else
    working "deploying ${deploy_name} (${model_name}@${version}) ..."
    az cognitiveservices account deployment create \
      --name "$FOUNDRY" --resource-group "$RG" \
      --deployment-name "$deploy_name" \
      --model-name "$model_name" --model-version "$version" \
      --model-format OpenAI \
      --sku-capacity 10 --sku-name GlobalStandard \
      -o none
    ok "${deploy_name} deployed."
  fi
}
# Job-shaped deployment names — each name describes the *role*, not the model.
# This lets Step 7 swap underlying models without touching any app code.
deploy_model "planner-gpt41"    "gpt-4.1"      "2025-04-14"
deploy_model "router-nano"      "gpt-4.1-nano" "2025-04-14"
deploy_model "mini-vision"      "gpt-4.1-mini" "2025-04-14"
deploy_model "policy-mini-base" "gpt-4.1-mini" "2025-04-14"
step_done

# ─── 7. .env + verify ─────────────────────────────────────────────────────
step "Capture endpoint → .env"
working "reading project endpoint..."
ENDPOINT=$(az cognitiveservices account project show \
  --name "$FOUNDRY" --resource-group "$RG" --project-name "$PROJECT" \
  --query 'properties.endpoints."AI Foundry API"' -o tsv)
[[ -z "$ENDPOINT" ]] && die "could not read project endpoint (try again in 30s)."

ENV_PATH="$(cd "$(dirname "$0")/.." && pwd)/.env"
SUBSCRIPTION=$(az account show --query id -o tsv)
cat > "$ENV_PATH" <<EOF
# Generated by s00_setup.sh on $(date -Iseconds)
FOUNDRY_PROJECT_ENDPOINT=${ENDPOINT}
FOUNDRY_PROJECT_NAME=${PROJECT}
AZURE_RESOURCE_GROUP=${RG}
AZURE_LOCATION=${LOCATION}
FOUNDRY_ACCOUNT_NAME=${FOUNDRY}
AZURE_SUBSCRIPTION_ID=${SUBSCRIPTION}
EOF
ok "wrote ${ENV_PATH}"
step_done

# ─── summary ──────────────────────────────────────────────────────────────
TOTAL_ELAPSED=$((SECONDS - SCRIPT_T0))
echo
echo "${GREEN}${BOLD}$(hr)${RESET}"
echo "  ${GREEN}${BOLD}✓ Setup complete in ${TOTAL_ELAPSED}s${RESET}"
echo "${GREEN}${BOLD}$(hr)${RESET}"
echo
echo "${BOLD}Project endpoint:${RESET}"
echo "  ${CYAN}${ENDPOINT}${RESET}"
echo
echo "${BOLD}Verify deployments (CLI):${RESET}"
cat <<EOF
  az cognitiveservices account deployment list \\
    -n ${FOUNDRY} -g ${RG} \\
    --query "[].{name:name, state:properties.provisioningState, model:properties.model.name, version:properties.model.version}" \\
    -o table
EOF
echo
echo "${BOLD}Verify in Portal (model catalog only):${RESET}"
echo "  https://ai.azure.com  →  project ${BOLD}${PROJECT}${RESET}  →  Models + endpoints"
echo "  expect 3 rows in state ${GREEN}Succeeded${RESET}."
echo
echo "${BOLD}Next:${RESET} Step 1 — Baseline in the playground"
echo
