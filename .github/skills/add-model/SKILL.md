---
kind: skill
name: add-model
description: Register a model under an existing publisher — updates the members table without scaffolding a capsule.
inputs:
  - name: publisher
    type: string
    description: Publisher slug (must exist under models/).
    required: true
  - name: model
    type: string
    description: Model slug (kebab-case).
    required: true
  - name: capabilities
    type: array
    description: Capability tags from the taxonomy.
    required: true
  - name: model_card
    type: url
    description: Learn URL for the model card when available.
    required: true
  - name: released
    type: date
    description: Release date (YYYY-MM-DD).
    required: false
  - name: expires
    type: date
    description: Retirement date if known.
    required: false
produces:
  - models/<publisher>/README.md
validates_against:
  - .github/specs/schemas/publisher.schema.json
depends_on:
  - add-publisher
---

# add-model

Appends a row to the publisher README's members table. Does *not* create a
capsule folder — use [`add-capsule`](../add-capsule/) for that. If the
publisher folder does not yet exist, delegates to
[`add-publisher`](../add-publisher/) first.
