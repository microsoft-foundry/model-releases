# Scripts

Reusable shell / Python helpers for capsule authors and learners.
Anything that automates setup, provisioning, deployment, `.env`
hygiene, or **spec validation** lives here — one script per file, one
purpose per script.

## Conventions

- **Runnable from repo root**, e.g. `./scripts/foo.sh` or `python scripts/foo.py`.
- **Idempotent** — safe to re-run (check-before-create, `--force` flag
  for destructive ops).
- **Grounded in [Microsoft Learn](https://learn.microsoft.com/) docs**
  and the [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/)
  where possible; link the underlying doc from the script's header.
- **Spec-driven** — every script ships with a sidecar
  `<name>.spec.md` whose YAML frontmatter is validated against
  [`.github/specs/schemas/script.schema.json`](../.github/specs/schemas/script.schema.json).
- **Called out from wherever they're needed** (typically
  [`models/quickstart/`](../models/quickstart/) or a capsule README).

## Available scripts

| Script | Spec | Purpose |
|---|---|---|
| [`setenv.sh`](./setenv.sh) | [`setenv.spec.md`](./setenv.spec.md) | Copy `sample.env` → `.env` and populate Foundry connection via Azure CLI |
| [`validate-specs.py`](./validate-specs.py) | _(self-describing)_ | Validate every artifact's YAML frontmatter against its JSON Schema |
| [`sample.env`](./sample.env) | _(template)_ | Reference env vars for every capsule |

## Validating specs

```bash
pip install pyyaml jsonschema
python scripts/validate-specs.py
```

Prints one line per artifact and exits non-zero if any frontmatter drifts
from its schema.

