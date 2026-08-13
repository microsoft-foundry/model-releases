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
- **Spec-driven** — a script that authors or learners invoke as part
  of the workflow ships a sidecar `<name>.spec.md`, whose YAML
  frontmatter is validated against
  [`.github/specs/schemas/script.schema.json`](../.github/specs/schemas/script.schema.json).
  The validators and generators are self-describing and don't carry
  one — their contract is the `--help` output and this table.
- **Called out from wherever they're needed** (typically
  [`models/quickstart/`](../models/quickstart/) or a capsule README).

## Available scripts

| Script | Spec | Purpose |
|---|---|---|
| [`validate.py`](./validate.py) | [`validate.spec.md`](./validate.spec.md) | **Start here.** Run every check at once; `--watch` re-runs on each save |
| [`setenv.sh`](./setenv.sh) | [`setenv.spec.md`](./setenv.spec.md) | Copy `sample.env` → `.env` and populate Foundry connection via Azure CLI |
| [`generate-catalog.py`](./generate-catalog.py) | [`generate-catalog.spec.md`](./generate-catalog.spec.md) | Regenerate `catalog.json`, `llms.txt`, `CAPSULE-TOC.md`, and the README blocks |
| [`validate-specs.py`](./validate-specs.py) | _(self-describing)_ | Validate every artifact's YAML frontmatter against its JSON Schema |
| [`validate-crosslinks.py`](./validate-crosslinks.py) | _(self-describing)_ | Check CHANGELOG ↔ README ↔ capsule ↔ primer wiring |
| [`scan_foundry_blog.py`](./scan_foundry_blog.py) | _(self-describing)_ | Diff the Foundry blog against the CHANGELOG and draft rows for new posts |
| [`sample.env`](./sample.env) | _(template)_ | Reference env vars for every capsule |

## Validating your changes

CI validates once per pull request, not on every push, so this is the
check that catches things first — and the pre-commit hook runs it for
you.

```bash
pip install -r requirements-dev.txt
python scripts/validate.py
```

It runs the schema validator, the crosslink validator, and the
generated-file check, and exits non-zero if any of them fails.

While drafting, leave it running in a second terminal so every save
re-checks:

```bash
python scripts/validate.py --watch
```

If the generated files are stale, rebuild them rather than editing by
hand:

```bash
python scripts/validate.py --fix
```

