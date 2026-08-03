# Schemas

JSON Schemas that validate the YAML frontmatter of every artifact in
this repo. One schema per `kind:` value.

| `kind` | Schema | Applies to |
|---|---|---|
| `capsule` | [`capsule.schema.json`](./capsule.schema.json) | `models/<family>/<model>/<date>/README.md` |
| `family` | [`family.schema.json`](./family.schema.json) | `models/<family>/README.md` |
| `primer` | [`primer.schema.json`](./primer.schema.json) | `docs/primers/*.md` |
| `quickstart` | [`quickstart.schema.json`](./quickstart.schema.json) | `models/quickstart/README.md` |
| `skill` | [`skill.schema.json`](./skill.schema.json) | `.github/skills/<name>/SKILL.md` |
| `agent` | [`agent.schema.json`](./agent.schema.json) | `.github/agents/<name>.md` |
| `script` | [`script.schema.json`](./script.schema.json) | `scripts/<name>.spec.md` |

Run [`scripts/validate-specs.py`](../../../scripts/validate-specs.py) to
check every artifact against its schema.
