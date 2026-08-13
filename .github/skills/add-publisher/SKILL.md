---
kind: skill
name: add-publisher
description: Register a new model publisher — creates models/<slug>/ with a spec-driven README stub.
inputs:
  - name: slug
    type: string
    description: Kebab-case folder slug (e.g. anthropic).
    required: true
  - name: name
    type: string
    description: Human-readable publisher name (e.g. Anthropic).
    required: true
  - name: one_line
    type: string
    description: Short pitch for the repo README publisher table.
    required: true
  - name: provider
    type: string
    description: Underlying provider or vendor.
    required: false
  - name: related_primers
    type: array
    description: Capability primer slugs most relevant to this publisher.
    required: false
produces:
  - models/<slug>/README.md
validates_against:
  - .github/specs/schemas/publisher.schema.json
depends_on: []
---

# add-publisher

Creates a new publisher folder with a README whose frontmatter conforms to
[`publisher.schema.json`](../../specs/schemas/publisher.schema.json). Also
appends a row to the **Model publishers** table in the repo README.

Fails (non-destructively) if `models/<slug>/` already exists.
