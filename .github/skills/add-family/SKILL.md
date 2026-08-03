---
kind: skill
name: add-family
description: Register a new model family — creates models/<slug>/ with a spec-driven README stub.
inputs:
  - name: slug
    type: string
    description: Kebab-case folder slug (e.g. anthropic).
    required: true
  - name: name
    type: string
    description: Human-readable family name (e.g. Anthropic).
    required: true
  - name: one_line
    type: string
    description: Short pitch for the repo README family table.
    required: true
  - name: provider
    type: string
    description: Underlying provider or vendor.
    required: false
  - name: related_primers
    type: array
    description: Capability primer slugs most relevant to this family.
    required: false
produces:
  - models/<slug>/README.md
validates_against:
  - .github/specs/schemas/family.schema.json
depends_on: []
---

# add-family

Creates a new family folder with a README whose frontmatter conforms to
[`family.schema.json`](../../specs/schemas/family.schema.json). Also
appends a row to the **Model families** table in the repo README.

Fails (non-destructively) if `models/<slug>/` already exists.
