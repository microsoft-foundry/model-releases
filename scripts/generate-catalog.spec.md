---
kind: script
script: scripts/generate-catalog.py
purpose: Generate catalog.json, llms.txt, and every marker-bracketed index table from artifact frontmatter, so the indexes of the repo can never drift from the content.
prereqs:
  - "pyyaml (`pip install -r requirements-dev.txt`)"
usage:
  - "python scripts/generate-catalog.py           # write all generated files"
  - "python scripts/generate-catalog.py --check   # fail if any is stale"
learn_ref: https://llmstxt.org/
idempotent: true
---

# generate-catalog.py

Builds every index of this repo from one source: artifact frontmatter.
All of these are **generated** — edit the frontmatter, never the output.

| File | Audience | What it holds |
|---|---|---|
| `catalog.json` | Agents, scripts | Every capsule, scenario, publisher, primer, and capability tag with models, capabilities, pricing, and notebook paths |
| `llms.txt` | LLM consumers | A short, link-dense markdown map of the repo, per the [/llms.txt convention](https://llmstxt.org/) |
| `CAPSULE-TOC.md` | Humans | Capsule tables grouped by provider, plus the multi-model scenario table |
| `README.md` | Humans | The three most recently updated capsules |
| `docs/README.md` | Humans | The capability taxonomy table |

The three markdown files are only rewritten **between markers**
(`<!-- BEGIN:CAPSULE-TABLES -->` and friends). Prose outside the
markers is hand-written and preserved, so the generator never
flattens someone's intro paragraph.

## Why these exist

Retrieval systems chunk per file. An agent that fetches one capsule
README gets that capsule's frontmatter and nothing else — it has no way
to know what else the repo covers without crawling the tree. These two
files answer "what is in this repo?" in a single request.

That is also why capsule metadata stays **in** the capsule README
rather than moving to a central registry: co-locating it keeps each
page self-describing when fetched alone, and this script derives the
central index from those same fields.

## Fields it reads

`summary` is the load-bearing one. It is the meta description for a
capsule — used in `catalog.json`, `llms.txt`, the repo README table,
and `CAPSULE-TOC.md`. Write it to stand alone out of context: name the
model, say what you can do with it, and mention Microsoft Foundry.

`last_updated` drives ordering and the **Last updated** column, and
falls back to `release_date` when absent. It lives in frontmatter
rather than being read from git so that a shallow CI checkout produces
byte-identical output.

The display name comes from the README **H1**, not frontmatter, so
search results show `MAI-Image-2.5-Pro` rather than the
`mai-image-2.5-pro` slug.

Capability **labels** come from the `label` field of the matching
primer in `docs/primers/`. A primer may also declare `aliases` so one
primer serves several tags — `multimodal-models.md` covers both
`multimodal` and `vision`. This is the single source of truth for the
taxonomy table, so a tag is usable exactly when a primer declares it.

## Checking for drift

`--check` is one of the three checks in
[`scripts/validate.py`](./validate.py), which runs from the pre-commit
hook and from the
[`validate.yml`](../.github/workflows/validate.yml) workflow. If you
change frontmatter and forget to regenerate, it fails with the list of
stale files; `python scripts/validate.py --fix` regenerates them.
