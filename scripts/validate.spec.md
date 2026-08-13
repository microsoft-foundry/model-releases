---
kind: script
script: scripts/validate.py
purpose: Run the schema validator, the crosslink validator, and the generated-file check from one command; --watch re-runs them on every save so an author can validate interactively before committing.
prereqs:
  - "Dev dependencies installed: pip install -r requirements-dev.txt"
usage:
  - "python scripts/validate.py             # run once; exits non-zero if any check fails"
  - "python scripts/validate.py --watch     # interactive: re-run on every save, Ctrl-C to stop"
  - "python scripts/validate.py --fix       # regenerate stale generated files, then re-check"
  - "python scripts/validate.py --no-color  # plain output (used by CI and the pre-commit hook)"
learn_ref: https://learn.microsoft.com/en-us/azure/foundry/
idempotent: true
---

# validate.py

The single entrypoint for checking a contribution. It shells out to
the three checks that used to be three separate CI steps, in the order
that produces the most useful first error:

| # | Check | Script |
|---|---|---|
| 1 | Frontmatter matches the JSON Schema for its `kind` | [`validate-specs.py`](./validate-specs.py) |
| 2 | CHANGELOG ↔ README ↔ capsule ↔ primer wiring | [`validate-crosslinks.py`](./validate-crosslinks.py) |
| 3 | Generated files are current | [`generate-catalog.py --check`](./generate-catalog.py) |

Schemas run first because a frontmatter error makes the later checks
report confusing follow-on failures.

## Why this exists

[`validate.yml`](../.github/workflows/validate.yml) runs on pull
requests and on demand, but deliberately **not** on push. That keeps CI
off every individual commit, which means the feedback you get while
drafting has to come from somewhere else. This script is that
somewhere: the pre-commit hook runs it, the workflow runs it, and you
can run it directly. A green local run and a green CI run therefore
mean the same thing, so the PR gate should never be the first place a
problem shows up.

## Interactive use

```bash
python scripts/validate.py --watch
```

Leave that running in a second terminal while you edit. It polls the
mtimes of `models/`, `docs/`, `.github/specs/`, `scripts/`, and the
generated files once a second, prints which file changed, and re-runs
everything. Polling avoids a dependency on a file-watcher package, so
it works from a bare checkout.

`--fix` regenerates the catalog files before checking, which is the
right response to a stale-generated-file failure — those files are
built from frontmatter and are never edited by hand.

See [`scripts/validate.py`](./validate.py) for the implementation.
