---
kind: skill
name: add-to-glossary
description: Insert or update a term in docs/GLOSSARY.md under the correct letter section, with a required grounding reference.
inputs:
  - name: term
    type: string
    description: The term as displayed (e.g. "Mixture of Experts").
    required: true
  - name: definition
    type: string
    description: 2–4 sentence explainer.
    required: true
  - name: reference_url
    type: url
    description: Grounding link — prefer learn.microsoft.com.
    required: true
  - name: reference_title
    type: string
    description: Text shown for the reference link.
    required: true
produces:
  - docs/GLOSSARY.md
validates_against: []
depends_on: []
---

# add-to-glossary

Adds a new entry to [`docs/GLOSSARY.md`](../../../docs/GLOSSARY.md):

- Placed under the correct **A–Z letter section**.
- Level-3 heading (`### Term Name`) with kebab-case anchor.
- 2–4 sentence definition.
- Ends with `**Reference:** [title](url)` — required.

Replaces the section's `_No entries yet._` placeholder if the section
was empty. Refuses to add duplicates.
