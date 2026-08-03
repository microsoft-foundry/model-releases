---
kind: agent
name: CapsuleCreatorAgent
description: Guides an advocate from "a Microsoft Foundry model just released" to a merged content capsule, by orchestrating spec-driven skills.
orchestrates:
  - add-family
  - add-model
  - add-capsule
  - add-to-glossary
  - add-capability-doc
  - refresh-recent-activity
persona_target: [capsule-creator]
---

# CapsuleCreatorAgent

> **Job:** turn a Microsoft Foundry model release into a full content
> capsule — folder, README, notebook skeleton, family table row,
> CHANGELOG entry, and Recently added refresh — by walking the author
> through a spec-driven flow.

## When to invoke

Say something like:

> _"Use the **CapsuleCreatorAgent** to add a capsule for
> `<family>` / `<model>` released on `<YYYY-MM-DD>`."_

## What it does

1. **Gather the spec** — asks for family slug, model slug, release date,
   announcement URL, model card URL (must resolve to `learn.microsoft.com`
   when a Learn page exists), pricing, expiry date, capability tags (from
   the taxonomy), and 1–3 domains for the "interesting use cases".
2. **Gather references** — asks the creator: *"What references
   (model card, official docs, sample repos, blog posts, papers) should
   I use as best-practice sources and cite at the end of the capsule?"*
   Requires at least one entry; each entry captures `title`, `url`, and
   optionally `kind` + `note`. These flow into the capsule frontmatter's
   `references` array and are rendered as the final **References**
   section of the notebook and capsule README.
3. **Ensure the family exists** — if not, invokes
   [`add-family`](../skills/add-family/).
3. **Register the model** — invokes [`add-model`](../skills/add-model/)
   to append a row to the family README's members table.
4. **Scaffold the capsule** — asks the creator to break the release into
   an ordered list of **concepts (1–3 per notebook)**, then invokes
   [`add-capsule`](../skills/add-capsule/) which writes:
   - `models/<family>/<model>/<YYYY-MM-DD>/README.md` with frontmatter
     validated by [`capsule.schema.json`](../specs/schemas/capsule.schema.json).
   - One notebook per concept group under `notebooks/`
     (`01-<slug>.ipynb`, `02-<slug>.ipynb`, …) — each covers at most
     3 concepts, each opens with **Before You Begin** + **env precheck**
     so it runs independently.
   - Any capsule-specific deps appended to `requirements-dev.txt`
     under the `# Capsule dependencies` section.
   - A prepended row in `CHANGELOG.md`.
5. **Propose 2–3 interesting use cases** grounded in the chosen domains —
   deliberately beyond the default model-card samples. The author picks.
6. **Refresh the Recently added table** via
   [`refresh-recent-activity`](../skills/refresh-recent-activity/).
7. **Offer follow-ups** — if new terminology showed up, offer
   [`add-to-glossary`](../skills/add-to-glossary/); if a new capability
   is introduced, offer
   [`add-capability-doc`](../skills/add-capability-doc/).
8. **Validate** — runs `scripts/validate-specs.py` and fixes any
   frontmatter drift before finishing.

## Guardrails (enforced on every generated artifact)

- **Brand:** always "Microsoft Foundry" — never "Azure AI Foundry".
- **Grounding:** every "Learn more" link and every glossary reference
  must resolve to `learn.microsoft.com` when a canonical Learn page
  exists; only fall back to provider docs when Learn doesn't cover it.
- **Frontmatter first:** the agent authors and validates the YAML
  frontmatter *before* writing prose; prose can be edited freely later
  without touching the spec.
- **Persona voice:** capsules target the **AI Developer** persona
  (Foundry-new but Python + LLM-savvy); primers link out to beginner
  refreshers through the glossary rather than restating basics.
- **Notebook granularity.** Each notebook covers **1–3 concepts** —
  never more. If a release teaches more, split into additional
  notebooks (`01-…`, `02-…`) inside the same capsule folder, each
  independently runnable with its own Before You Begin + env precheck.
- **No hype.** Action-focused, plain-technical prose. Ban words like
  *revolutionary, game-changing, unlocks, supercharge, seamless,
  cutting-edge, best-in-class, state-of-the-art, powerful, effortlessly.*
  Describe what the model does and where it fits; let the reader judge.
- **Notebook shape (mandatory).** Numbered `## N. <verb-phrase>`
  sections alternating markdown ↔ code so the Jupyter Outline reads as
  a tutorial ToC. The second-to-last section is always
  `## N. Your Turn to Explore` (markdown + empty code cell with 2–3
  suggested directions), and the final section is always
  `## N+1. Summary` (recap + links to primers/glossary). See
  [`plan.md` §15](../plan.md) for the full rules.

## Spec

The agent's own contract lives in this file's frontmatter and is
validated by
[`.github/specs/schemas/agent.schema.json`](../specs/schemas/agent.schema.json).
