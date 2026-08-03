---
kind: skill
name: add-capability-doc
description: Scaffold a new capability primer under docs/primers/ and add the capability to the repo README taxonomy.
inputs:
  - name: capability
    type: string
    description: Canonical capability name (added to the taxonomy).
    required: true
  - name: slug
    type: string
    description: Kebab-case slug used as the filename and anchor.
    required: true
  - name: one_line
    type: string
    description: Short pitch used in the taxonomy table.
    required: true
  - name: learn_more
    type: array
    description: Up to 3 grounding resources (Learn URLs preferred).
    required: true
produces:
  - docs/primers/<slug>.md
  - README.md
validates_against:
  - .github/specs/schemas/primer.schema.json
depends_on: []
---

# add-capability-doc

Creates a new primer file with frontmatter validated by
[`primer.schema.json`](../../specs/schemas/primer.schema.json), and
appends a row to the **Capability taxonomy** table in the repo README.

Also updates the [`capsule.schema.json`](../../specs/schemas/capsule.schema.json)
`capabilities` enum so future capsules can tag themselves with the new
capability. (Author confirms this schema change explicitly.)
