#!/usr/bin/env bash
# setenv.sh
# Purpose:    Bootstrap the repo-root .env from scripts/sample.env and
#             auto-populate Microsoft Foundry connection details using
#             the Azure CLI when a project is provided.
# Prereqs:    Azure CLI logged in (`az login`) if you want auto-populate.
# Learn ref:  https://learn.microsoft.com/en-us/cli/azure/get-started-with-azure-cli
#             https://learn.microsoft.com/en-us/azure/foundry/how-to/create-projects
# Usage:
#   ./scripts/setenv.sh                         # copy template only, edit by hand
#   ./scripts/setenv.sh <rg> <project>          # copy + populate from Azure CLI
#   ./scripts/setenv.sh <rg> <project> --force  # overwrite existing .env
#
# The .env file is git-ignored. Never commit real keys.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SAMPLE="${REPO_ROOT}/scripts/sample.env"
TARGET="${REPO_ROOT}/.env"

RG="${1:-}"
PROJECT="${2:-}"
FORCE="${3:-}"

if [[ ! -f "$SAMPLE" ]]; then
  echo "✗ scripts/sample.env missing — cannot continue." >&2
  exit 1
fi

# 1. Copy template into place (idempotent unless --force).
if [[ -f "$TARGET" && "$FORCE" != "--force" ]]; then
  echo "ℹ️  .env already exists — leaving it alone."
  echo "   Pass --force as the third arg to overwrite."
else
  cp "$SAMPLE" "$TARGET"
  echo "✅ Copied scripts/sample.env → .env"
fi

# 2. If a resource group + project were provided, use Azure CLI to fill values.
if [[ -z "$RG" || -z "$PROJECT" ]]; then
  echo "ℹ️  No <rg> <project> passed — edit .env by hand or re-run with args."
  echo "   Example: ./scripts/setenv.sh my-rg my-foundry-project"
  exit 0
fi

if ! command -v az >/dev/null 2>&1; then
  echo "✗ Azure CLI not found. Install: https://learn.microsoft.com/en-us/cli/azure/install-azure-cli" >&2
  exit 1
fi

if ! az account show >/dev/null 2>&1; then
  echo "✗ Not logged in. Run: az login" >&2
  exit 1
fi

echo "→ Reading project '${PROJECT}' in resource group '${RG}'..."

SUB_ID="$(az account show --query id -o tsv)"
TENANT_ID="$(az account show --query tenantId -o tsv)"

# Foundry project lookup — adjust the resource type if your project uses a
# different provider surface. Reference:
#   https://learn.microsoft.com/en-us/azure/foundry/how-to/create-projects
ENDPOINT="$(az cognitiveservices account show \
  --name "$PROJECT" --resource-group "$RG" \
  --query "properties.endpoint" -o tsv 2>/dev/null || true)"

API_KEY="$(az cognitiveservices account keys list \
  --name "$PROJECT" --resource-group "$RG" \
  --query "key1" -o tsv 2>/dev/null || true)"

REGION="$(az cognitiveservices account show \
  --name "$PROJECT" --resource-group "$RG" \
  --query "location" -o tsv 2>/dev/null || true)"

# 3. Rewrite matching lines in .env (portable sed for macOS + Linux).
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

update_env "AZURE_SUBSCRIPTION_ID"      "$SUB_ID"
update_env "AZURE_TENANT_ID"            "$TENANT_ID"
update_env "AZURE_RESOURCE_GROUP"       "$RG"
update_env "AZURE_FOUNDRY_PROJECT_NAME" "$PROJECT"
update_env "AZURE_FOUNDRY_ENDPOINT"     "$ENDPOINT"
update_env "AZURE_FOUNDRY_API_KEY"      "$API_KEY"
update_env "AZURE_FOUNDRY_REGION"       "$REGION"

echo "✅ Populated .env from Azure CLI."
echo "→ Next: add deployment names (ROUTER_DEPLOYMENT, CHAT_DEPLOYMENT, …) as your capsule needs them."
