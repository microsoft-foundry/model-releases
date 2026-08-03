---
kind: script
script: scripts/setenv.sh
purpose: Bootstrap the repo-root .env from scripts/sample.env and populate Microsoft Foundry connection details via Azure CLI.
prereqs:
  - Azure CLI installed and `az login` completed
  - jq optional (not required)
usage:
  - ./scripts/setenv.sh
  - ./scripts/setenv.sh <resource-group> <project-name>
  - ./scripts/setenv.sh <resource-group> <project-name> --force
learn_ref: https://learn.microsoft.com/en-us/cli/azure/get-started-with-azure-cli
idempotent: true
---

# setenv.sh

Copies [`scripts/sample.env`](./sample.env) to the repo root as `.env`
(if it doesn't already exist), then — when a resource group and project
are provided — uses the [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/)
to populate the Microsoft Foundry connection variables.

Grounded in the
[Foundry "Create a project" docs](https://learn.microsoft.com/en-us/azure/foundry/how-to/create-projects).

See [`scripts/setenv.sh`](./setenv.sh) for the implementation.
