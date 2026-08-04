---
kind: script
script: scripts/setenv.sh
purpose: Bootstrap the repo-root .env from scripts/sample.env; optionally create a new Foundry project or populate from an existing one via Azure CLI.
prereqs:
  - Azure CLI installed and `az login` completed for any mode beyond copy-only
usage:
  - "./scripts/setenv.sh                                          # copy template only"
  - "./scripts/setenv.sh --use <rg> <project> [--force]          # populate from existing project"
  - "./scripts/setenv.sh --create <rg> <project> <location> [--force]  # create project + populate"
  - "./scripts/setenv.sh <rg> <project> [--force]                # legacy alias for --use"
learn_ref: https://learn.microsoft.com/en-us/cli/azure/get-started-with-azure-cli
idempotent: true
---

# setenv.sh

Copies [`scripts/sample.env`](./sample.env) to the repo root as `.env`
(if it doesn't already exist), then operates in one of two modes:

| Mode | Command | What it does |
|---|---|---|
| Copy only | `./scripts/setenv.sh` | Copies the template; edit `.env` by hand. |
| Use existing | `./scripts/setenv.sh --use <rg> <project>` | Reads an existing Foundry AI Services resource and populates `.env` via Azure CLI. |
| Create new | `./scripts/setenv.sh --create <rg> <project> <location>` | Creates the resource group (if needed) and a new Foundry AI Services resource, then populates `.env`. |

All modes are idempotent: re-running with the same args will not duplicate
the resource group or project, and will not overwrite `.env` unless `--force`
is appended.

Grounded in the
[Foundry "Create a project" docs](https://learn.microsoft.com/en-us/azure/foundry/how-to/create-projects).

See [`scripts/setenv.sh`](./setenv.sh) for the implementation.
