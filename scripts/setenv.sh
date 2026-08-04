#!/usr/bin/env bash
# setenv.sh
# Purpose:    Bootstrap the repo-root .env from scripts/sample.env and
#             auto-populate Microsoft Foundry connection details using
#             the Azure CLI when a project is provided.
# Prereqs:    Azure CLI logged in (`az login`) for any mode beyond copy-only.
# Learn ref:  https://learn.microsoft.com/en-us/cli/azure/get-started-with-azure-cli
#             https://learn.microsoft.com/en-us/azure/foundry/how-to/create-projects
# Usage:
#   ./scripts/setenv.sh                                          # copy template only
#   ./scripts/setenv.sh --use <rg> <project> [--force]          # populate from existing project
#   ./scripts/setenv.sh --create <rg> <project> <location> [--force]  # create project + populate
#   ./scripts/setenv.sh <rg> <project> [--force]                # legacy alias for --use
#
# The .env file is git-ignored. Never commit real keys.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SAMPLE="${REPO_ROOT}/scripts/sample.env"
TARGET="${REPO_ROOT}/.env"

# ---------- argument parsing ----------

MODE=""
RG=""
PROJECT=""
LOCATION=""
FORCE=""

case "${1:-}" in
  --use)
    MODE="use"
    RG="${2:-}"
    PROJECT="${3:-}"
    FORCE="${4:-}"
    ;;
  --create)
    MODE="create"
    RG="${2:-}"
    PROJECT="${3:-}"
    LOCATION="${4:-}"
    FORCE="${5:-}"
    ;;
  --force)
    FORCE="--force"
    ;;
  "")
    MODE=""
    ;;
  *)
    # Legacy positional: setenv.sh <rg> <project> [--force]
    MODE="use"
    RG="${1:-}"
    PROJECT="${2:-}"
    FORCE="${3:-}"
    ;;
esac

# ---------- helpers ----------

require_az() {
  if ! command -v az >/dev/null 2>&1; then
    echo "✗ Azure CLI not found. Install: https://learn.microsoft.com/en-us/cli/azure/install-azure-cli" >&2
    exit 1
  fi
  if ! az account show >/dev/null 2>&1; then
    echo "✗ Not logged in. Run: az login" >&2
    exit 1
  fi
}

# Portable in-place .env key rewrite (macOS + Linux sed).
update_env() {
  local key="$1" value="$2"
  if [[ -z "$value" ]]; then return; fi
  local escaped="${value//\//\\/}"
  if grep -q "^${key}=" "$TARGET"; then
    if [[ "$OSTYPE" == "darwin"* ]]; then
      sed -i '' "s|^${key}=.*|${key}=\"${escaped}\"|" "$TARGET"
    else
      sed -i "s|^${key}=.*|${key}=\"${escaped}\"|" "$TARGET"
    fi
  else
    echo "${key}=\"${value}\"" >> "$TARGET"
  fi
}

populate_from_project() {
  local rg="$1" project="$2"
  echo "→ Reading project '${project}' in resource group '${rg}'..."
  local sub tenant resource_name endpoint apikey region
  sub="$(az account show --query id -o tsv)"
  tenant="$(az account show --query tenantId -o tsv)"

  # Discover the AIServices resource name in the RG — it may differ from the project name.
  # Reference: https://learn.microsoft.com/en-us/azure/foundry/how-to/create-projects
  resource_name="$(az cognitiveservices account list \
    --resource-group "$rg" \
    --query "[?kind=='AIServices'] | [0].name" -o tsv 2>/dev/null || true)"

  if [[ -z "$resource_name" ]]; then
    echo "⚠️  No AIServices resource found in '${rg}'. Skipping endpoint/key/region population." >&2
  else
    # Build the Foundry project endpoint from the resource hostname + project name.
    endpoint="https://${resource_name}.services.ai.azure.com/api/projects/${project}"
    apikey="$(az cognitiveservices account keys list \
      --name "$resource_name" --resource-group "$rg" \
      --query "key1" -o tsv 2>/dev/null || true)"
    region="$(az cognitiveservices account show \
      --name "$resource_name" --resource-group "$rg" \
      --query "location" -o tsv 2>/dev/null || true)"
  fi

  update_env "AZURE_SUBSCRIPTION_ID"      "$sub"
  update_env "AZURE_TENANT_ID"            "$tenant"
  update_env "AZURE_RESOURCE_GROUP"       "$rg"
  update_env "MICROSOFT_FOUNDRY_PROJECT_NAME" "$project"
  update_env "MICROSOFT_FOUNDRY_ENDPOINT"     "$endpoint"
  update_env "MICROSOFT_FOUNDRY_API_KEY"      "$apikey"
  update_env "MICROSOFT_FOUNDRY_REGION"       "$region"
  echo "✅ Populated .env from Azure CLI."
  echo "→ Next: add deployment names (e.g. CHAT_DEPLOYMENT=my-gpt4o) as each capsule requires them."
}

# ---------- guard: sample.env must exist ----------

if [[ ! -f "$SAMPLE" ]]; then
  echo "✗ scripts/sample.env missing — cannot continue." >&2
  exit 1
fi

# ---------- step 1: copy template ----------

if [[ -f "$TARGET" && "$FORCE" != "--force" ]]; then
  echo "ℹ️  .env already exists — leaving it alone."
  echo "   Pass --force (last arg) to overwrite."
else
  cp "$SAMPLE" "$TARGET"
  echo "✅ Copied scripts/sample.env → .env"
fi

# ---------- step 2: branch on mode ----------

case "$MODE" in

  "")  # copy-only
    echo "ℹ️  No mode given — .env is ready to edit by hand."
    echo "   To populate from an existing project:"
    echo "     ./scripts/setenv.sh --use <rg> <project>"
    echo "   To create a new project and populate:"
    echo "     ./scripts/setenv.sh --create <rg> <project> <location>"
    exit 0
    ;;

  use)
    if [[ -z "$RG" || -z "$PROJECT" ]]; then
      echo "✗ --use requires <rg> and <project>." >&2
      echo "  Usage: ./scripts/setenv.sh --use <rg> <project> [--force]" >&2
      exit 1
    fi
    require_az
    populate_from_project "$RG" "$PROJECT"
    ;;

  create)
    if [[ -z "$RG" || -z "$PROJECT" || -z "$LOCATION" ]]; then
      echo "✗ --create requires <rg>, <project>, and <location>." >&2
      echo "  Usage: ./scripts/setenv.sh --create <rg> <project> <location> [--force]" >&2
      exit 1
    fi
    require_az

    # Create resource group if it doesn't already exist.
    if az group show --name "$RG" >/dev/null 2>&1; then
      echo "ℹ️  Resource group '${RG}' already exists — skipping creation."
    else
      echo "→ Creating resource group '${RG}' in '${LOCATION}'..."
      az group create --name "$RG" --location "$LOCATION" --output none
      echo "✅ Resource group created."
    fi

    # Create the Foundry AI Services resource if it doesn't already exist.
    # Reference: https://learn.microsoft.com/en-us/azure/foundry/how-to/create-projects
    if az cognitiveservices account show --name "$PROJECT" --resource-group "$RG" >/dev/null 2>&1; then
      echo "ℹ️  Foundry project '${PROJECT}' already exists — skipping creation."
    else
      echo "→ Creating Foundry AI Services resource '${PROJECT}'..."
      az cognitiveservices account create \
        --name "$PROJECT" \
        --resource-group "$RG" \
        --kind "AIServices" \
        --sku "S0" \
        --location "$LOCATION" \
        --yes \
        --output none
      echo "✅ Foundry project created."
    fi

    populate_from_project "$RG" "$PROJECT"
    ;;

esac
