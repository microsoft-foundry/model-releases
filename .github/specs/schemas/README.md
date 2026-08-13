# Schemas

JSON Schemas that validate the YAML frontmatter of every artifact in
this repo. One schema per `kind:` value.

| `kind` | Schema | Applies to |
|---|---|---|
| `capsule` | [`capsule.schema.json`](./capsule.schema.json) | `models/<publisher>/<release>/README.md` |
| `scenario` | [`scenario.schema.json`](./scenario.schema.json) | `models/<publisher>/multi-model-scenarios/<slug>/README.md`, `models/multi-model-scenarios/<slug>/README.md` |
| `publisher` | [`publisher.schema.json`](./publisher.schema.json) | `models/<publisher>/README.md` |
| `primer` | [`primer.schema.json`](./primer.schema.json) | `docs/primers/*.md` |
| `quickstart` | [`quickstart.schema.json`](./quickstart.schema.json) | `models/quickstart/README.md` |
| `skill` | [`skill.schema.json`](./skill.schema.json) | `.github/skills/<name>/SKILL.md` |
| `agent` | [`agent.schema.json`](./agent.schema.json) | `.github/agents/<name>.md` |
| `script` | [`script.schema.json`](./script.schema.json) | `scripts/<name>.spec.md` |

Run [`scripts/validate-specs.py`](../../../scripts/validate-specs.py) to
check every artifact against its schema.

## What belongs in frontmatter

Schemas live here, centrally. The **data** stays in the artifact it
describes. That split is deliberate, and the rule for deciding where a
field goes is:

> Frontmatter holds facts a machine needs to index the artifact.
> Everything a human reads goes in the body.

Frontmatter is not a second copy of the page. Before adding a field,
check it isn't already stated in prose — a field that exists only to be
rendered back out belongs in the body instead. `references` used to be
frontmatter and was moved to the `## References` section for exactly
this reason: it was restated verbatim, and markdown links are followed
by crawlers and agents while frontmatter URLs are not.

**Why not move all metadata to a central registry?** Because retrieval
systems chunk per file. When an agent fetches a single capsule README,
co-located frontmatter is the only thing telling it the model, the
capability, and the price. Centralizing it would make every page
context-free. Instead,
[`scripts/generate-catalog.py`](../../../scripts/generate-catalog.py)
derives the central index (`catalog.json`, `llms.txt`) *from* these
per-file fields, so you get one-fetch discovery without giving up
self-describing pages. `scripts/validate.py` fails if the generated
files drift.

`summary` is the field to get right: it is the meta description reused
in `catalog.json`, `llms.txt`, `CAPSULE-TOC.md`, and the repo README.
