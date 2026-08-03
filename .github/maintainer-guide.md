# Maintainer guide

Everything you need to keep `model-releases` healthy: how the repo is
wired together, how to add your first artifact end-to-end, and how to
test that changes don't drift from the spec.

Companion documents:

- [`.github/plan.md`](./plan.md) — the living design plan.
- [`.github/specs/schemas/`](./specs/schemas/) — JSON Schemas that every
  artifact's YAML frontmatter is validated against.
- [`.github/agents/CapsuleCreatorAgent.md`](./agents/CapsuleCreatorAgent.md) —
  the Copilot custom agent that drives capsule creation.
- [`.github/skills/`](./skills/) — the six spec-driven skills the agent
  orchestrates.

---

## 1. Quickstart — validate the setup and add your first *something*

Do these five steps once, in order, on any fresh clone.

### 1.1 Open the devcontainer

The `.devcontainer/` config installs Python 3.12, Azure CLI, GitHub CLI,
`azd`, `marp-cli`, `uv`, and everything in `requirements-dev.txt`. Reopen
in container from VS Code, or run the post-create script manually.

### 1.2 Install spec-validation deps

```bash
pip install pyyaml jsonschema
```

(Only needed if you skipped the devcontainer.)

### 1.3 Run the spec validator — expect all green

```bash
python scripts/validate-specs.py
```

You should see one `✓` line per artifact and a final `N/N artifacts
valid.` If anything fails, fix the frontmatter before doing anything
else — schema drift compounds fast.

### 1.4 Bootstrap `.env` from the template

```bash
./scripts/setenv.sh                                # copy sample.env → .env
./scripts/setenv.sh <resource-group> <project>     # + populate via Azure CLI
```

Details in [`scripts/setenv.spec.md`](../scripts/setenv.spec.md).

### 1.5 Add your first artifact

Pick the smallest thing that exercises the flow, then work up:

| Want to add | Use | Produces |
|---|---|---|
| A **glossary term** you noticed missing | [`add-to-glossary`](./skills/add-to-glossary/SKILL.md) | Entry in `docs/GLOSSARY.md` under the right letter section |
| A **new model family** | [`add-family`](./skills/add-family/SKILL.md) | `models/<slug>/README.md` |
| A **model** in an existing family (no capsule yet) | [`add-model`](./skills/add-model/SKILL.md) | Row in `models/<family>/README.md` |
| A **full release capsule** | [`CapsuleCreatorAgent`](./agents/CapsuleCreatorAgent.md) → [`add-capsule`](./skills/add-capsule/SKILL.md) | Capsule folder + 1–N notebooks + CHANGELOG row + Recently added refresh |
| A **new capability** in the taxonomy | [`add-capability-doc`](./skills/add-capability-doc/SKILL.md) | Primer under `docs/primers/` + row in repo README taxonomy |

**Suggested first exercise (5 minutes):** run `add-to-glossary` to add
one term. It touches only `docs/GLOSSARY.md`, has clear success criteria,
and lets you see the "creator asks → skill produces → validator confirms"
loop end-to-end.

Then re-run:

```bash
python scripts/validate-specs.py
```

Still all green? The setup is working.

---

## 2. Mental model

```
                   ┌────────────────────────────────────┐
                   │   CapsuleCreatorAgent (Copilot)    │
                   └──────────────┬─────────────────────┘
                                  │ orchestrates
       ┌──────────┬──────────┬────┴─────┬──────────────┬──────────────────┐
       ▼          ▼          ▼          ▼              ▼                  ▼
  add-family  add-model  add-capsule  add-to-  add-capability-  refresh-recent-
                                      glossary       doc              activity
       │          │          │          │              │                  │
       └──────────┴────┬─────┴──────────┴──────────────┴──────────────────┘
                       │ writes
                       ▼
        Markdown files with YAML frontmatter
                       │
                       │ validated by
                       ▼
        .github/specs/schemas/*.schema.json
                       │
                       │ checked by
                       ▼
              scripts/validate-specs.py
```

Everything the agent produces is a plain Markdown file. The YAML
frontmatter at the top of each file is what makes it "spec-driven": each
file declares its `kind:` and is validated against the matching schema.

See [`plan.md` §14](./plan.md#14-authoring-approach--spec-driven-lightweight)
for why we chose Markdown + YAML over a heavier framework, and the
upgrade path to GitHub Spec Kit later.

---

## 3. Routine maintenance tasks

### 3.1 A new release drops

1. Open a session with the `CapsuleCreatorAgent`.
2. The agent asks for family, model, release date, capability tags,
   pricing, expiry, model card + docs + sample references
   (**required**), 1–3 target domains, and a list of teaching concepts
   (each notebook covers 1–3 concepts).
3. The agent invokes `add-family` / `add-model` / `add-capsule` /
   `refresh-recent-activity` in order.
4. Run `python scripts/validate-specs.py` — must be all green.
5. Skim the generated capsule README + notebooks for the voice/hype
   rules ([`plan.md` §15](./plan.md#15-content-authoring--pedagogy-rules)).
6. PR, review, merge.

### 3.2 A model is retiring

Nothing manual — the `expires` field in the family README's members
table + the capsule frontmatter drives the ⚠️ marker in the
**Recently added** table.
Just make sure `expires:` is populated. Run:

```bash
# Agent invocation or:
# The skill lives at .github/skills/refresh-recent-activity/
```

The section warns when anything expires in the next 60 days.

### 3.3 Monthly refresh

Run `refresh-recent-activity` once a month (or wire it up via a
scheduled GitHub Action) to keep the "Recently added" table current
even if no capsule shipped that month.

### 3.4 A new term shows up

Use `add-to-glossary`. Rules:

- On-demand only — do not pre-populate.
- Alphabetized under the correct letter section.
- **Reference required** — prefer `learn.microsoft.com`.

### 3.5 A new capability shows up

Use `add-capability-doc`. This:

- Adds a primer under `docs/primers/<slug>.md`.
- Adds a row to the repo README **Capability taxonomy** table.
- Extends the `capabilities` enum in
  [`capsule.schema.json`](./specs/schemas/capsule.schema.json) so future
  capsules can tag themselves with it — confirm this schema change in
  review.

### 3.6 Renaming a family or model

Slugs appear in three places: the folder path, `family:`/`model:`
frontmatter fields, and cross-references in the repo README + CHANGELOG.
Do the rename in a single PR, then run the validator and grep for the
old slug:

```bash
grep -RIn "<old-slug>" .
python scripts/validate-specs.py
```

---

## 4. Testing strategy

The whole point of the spec-driven layout is that most "tests" are just
schema conformance. Here's the layered approach.

### Layer 1 — Spec validation (fast, deterministic)

```bash
python scripts/validate-specs.py
```

Walks every `models/**/README.md`, `docs/primers/*.md`,
`.github/skills/*/SKILL.md`, `.github/agents/*.md`, and
`scripts/*.spec.md`, matches it to a `kind:`, and validates against the
JSON Schema.

**Wire it into CI** as the very first check. If schemas drift or someone
edits frontmatter by hand and breaks a shape, this catches it in
seconds.

### Layer 2 — Structural checks (Markdown well-formedness)

Grep-based invariants that keep the repo internally consistent:

- **Marker block present in repo README:**
  ```bash
  grep -q "BEGIN:RECENTLY-ADDED"  README.md
  ```
- **Every capsule README ends with `## References`:**
  ```bash
  for f in models/*/*/*/README.md; do
    grep -q "^## References" "$f" || echo "MISSING References: $f"
  done
  ```
- **Every notebook has a `Your Turn to Explore` cell:**
  ```bash
  for nb in models/*/*/*/notebooks/*.ipynb; do
    grep -q "Your Turn to Explore" "$nb" || echo "MISSING YTTE: $nb"
  done
  ```
- **Notebook granularity** — no notebook lists more than 3 concepts in
  its capsule frontmatter (schema enforces `maxItems: 3` on
  `notebooks[].concepts`, but a grep on generated ToCs is a cheap
  double-check).

Package these as a shell script (`scripts/check-structure.sh`) when
they start to bite; keep them ad-hoc until then.

### Layer 3 — Voice and grounding lint

Cheap ripgrep passes catch drift in the two rules we care about most.

**Banned marketing phrases** (see [`plan.md` §15](./plan.md#15-content-authoring--pedagogy-rules)):

```bash
rg -i --glob '!.github/plan.md' --glob '!.github/agents/*' --glob '!.github/maintainer-guide.md' \
  -e 'revolutionary|game-changing|game changer|unlocks?|supercharge' \
  -e 'seamless|cutting-edge|best-in-class|state-of-the-art' \
  -e 'powerful|effortless(ly)?' \
  README.md CHANGELOG.md docs/ models/
```

Expected: no matches outside the plan/agent/guide files that legitimately
name them.

**Brand rule** — never "Azure AI Foundry" (Learn URLs containing
`foundry` are fine):

```bash
rg -n 'Azure AI Foundry' -- README.md CHANGELOG.md docs/ models/ .github/ scripts/
```

Expected: zero matches.

**Grounding rule** — every "Learn more" section links to
`learn.microsoft.com` (fallbacks OK when noted):

```bash
rg -n '^## Learn more' -A 20 docs/primers/ | rg -v 'learn\.microsoft\.com'
```

Expected: only the section headings and blank lines; every bullet
should carry a Learn URL.

### Layer 4 — Notebook execution smoke test (opt-in per capsule)

Notebook validation is opt-in because capsules require real Foundry
deployments + credentials. The recommended pattern for a capsule
maintainer:

1. Populate `.env` via `scripts/setenv.sh`.
2. From the capsule folder:
   ```bash
   jupyter nbconvert --to notebook --execute --inplace notebooks/*.ipynb
   ```
3. If the env-precheck cell fails, the whole notebook stops — that's
   the whole point of the precheck. Fix `.env` and rerun.

Do **not** run these in CI by default (cost + secrets). Instead:

- Manual pre-merge check for capsule PRs.
- Optional monthly job that executes the top-3 recent-activity
  notebooks against a shared test project, with credentials injected
  from GitHub Actions secrets.

### Layer 5 — CI wiring (recommended)

Minimum viable `.github/workflows/validate.yml`:

```yaml
name: Validate specs
on:
  pull_request:
  push: { branches: [main] }
jobs:
  specs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: pip install pyyaml jsonschema
      - run: python scripts/validate-specs.py
      - name: No banned marketing phrases
        run: |
          ! rg -qi -e 'revolutionary|game-changing|unlocks?|supercharge' \
            -e 'seamless|cutting-edge|best-in-class|state-of-the-art' \
            README.md CHANGELOG.md docs/ models/
      - name: Brand rule
        run: |
          ! rg -q 'Azure AI Foundry' README.md CHANGELOG.md docs/ models/ .github/ scripts/
```

This is the **testing floor**. Add Layer 2/3 checks as their own steps
when the repo grows enough that grep-by-hand stops scaling.

---

## 5. When to change the schemas

The JSON Schemas are the load-bearing contract. Change them when:

- You add a **new capability** (extends `capabilities` enum in
  `capsule.schema.json`) — happens via `add-capability-doc`.
- You add a **new artifact kind** — add
  `<kind>.schema.json`, register it in `scripts/validate-specs.py`
  `KIND_GLOBS`, and document it in `plan.md`.
- You want to **tighten a rule** (e.g. make `announcement` required,
  add `format: uri` somewhere). Run the validator immediately after —
  every existing artifact must pass or you have work to do.

Don't change schemas without also updating the corresponding skill(s)
that produce those artifacts, or the agent will happily produce invalid
frontmatter.

---

## 6. Common pitfalls

- **Editing generated files without touching frontmatter.** Fine for
  prose. If you change structure (add/remove sections the schema cares
  about), also update the frontmatter and re-validate.
- **Forgetting the marker blocks.** `refresh-recent-activity` rewrites
  content *between* `<!-- BEGIN:X --> … <!-- END:X -->`. If those
  markers are missing from the repo README, the skill silently no-ops.
- **`.env` in git.** `*.env` is gitignored. If you see one staged, stop
  and unstage it — the sample template is `scripts/sample.env`.
- **Slugs with underscores or spaces.** Everything is kebab-case. The
  family/model regex in `capsule.schema.json` will reject anything else.
- **Notebook that grew past 3 concepts.** Split it. The schema
  (`notebooks[].concepts` has `maxItems: 3`) will reject it, but it's
  cheaper to split during authoring than after review.

---

## 7. Reference — where things live

| Concern | File(s) |
|---|---|
| Design plan | [`.github/plan.md`](./plan.md) |
| Schemas | [`.github/specs/schemas/*.schema.json`](./specs/schemas/) |
| Agent | [`.github/agents/CapsuleCreatorAgent.md`](./agents/CapsuleCreatorAgent.md) |
| Skills | [`.github/skills/*/SKILL.md`](./skills/) |
| Validator | [`scripts/validate-specs.py`](../scripts/validate-specs.py) |
| Crosslink validator | [`scripts/validate-crosslinks.py`](../scripts/validate-crosslinks.py) |
| Env bootstrap | [`scripts/setenv.sh`](../scripts/setenv.sh), [`scripts/sample.env`](../scripts/sample.env) |
| Repo README | [`README.md`](../README.md) |
| Changelog | [`CHANGELOG.md`](../CHANGELOG.md) |
| Glossary | [`docs/GLOSSARY.md`](../docs/GLOSSARY.md) |
| Primers | [`docs/primers/`](../docs/primers/) |
| Quickstart | [`models/quickstart/README.md`](../models/quickstart/README.md) |

---

## 8. Reviewing a manual (non-agent) contribution

Contributors can hand-author capsules and CHANGELOG entries without
going through the agent. Two safety nets catch most mistakes for you:

- **CI** — the `Validate contribution` workflow runs
  [`validate-specs.py`](../scripts/validate-specs.py) (JSON-Schema
  frontmatter) **and**
  [`validate-crosslinks.py`](../scripts/validate-crosslinks.py) on
  every PR. Between them they enforce:
  - Frontmatter matches the schema for its kind
  - Every capsule has a matching `CHANGELOG.md` row (date + model)
  - Every capsule is listed in its family README
  - Every capability tag has a matching `docs/primers/<slug>.md`
  - `README.md` Recently added top 3 = `CHANGELOG.md` top 3
  - No `_review_` placeholders remain in learner-facing files
- **PR template** — [`.github/pull_request_template.md`](./pull_request_template.md)
  gives contributors a checklist per change type (capsule, family,
  primer, glossary, CHANGELOG-only). Anything unchecked in a section
  the PR touches is a signal for the reviewer.

That leaves you to eyeball the things machines can't check:

- **Pedagogy.** Action-focused voice ("You'll deploy…"), 1–3 concepts
  per notebook, alternating markdown ↔ code, and mandatory `Your Turn
  to Explore` / `Summary` / `References` cells at the end.
- **Tone.** No hype words ("revolutionary", "game-changing"…), no
  marketing adjectives, and always **Microsoft Foundry** (never "Azure
  AI Foundry").
- **Grounding.** Learner-facing links point to `learn.microsoft.com`
  when a canonical Learn page exists; provider docs are a fallback.
- **Pricing verifiability.** The Pricing cell in the CHANGELOG row
  links to an official pricing page when one exists, otherwise to the
  blog post the figure came from.

Contributors can run both validators locally before pushing:

```bash
python scripts/validate-specs.py
python scripts/validate-crosslinks.py
```

or install the pre-commit hooks to have them run on every commit:

```bash
pip install pre-commit && pre-commit install
```
