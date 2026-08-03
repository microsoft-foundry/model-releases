---
kind: skill
name: add-capsule
description: Scaffold a full release capsule — folder, spec-driven README, notebook skeleton, deps, CHANGELOG row.
inputs:
  - name: family
    type: string
    description: Family slug (kebab-case) matching a folder under models/.
    required: true
  - name: model
    type: string
    description: Model slug (kebab-case).
    required: true
  - name: release_date
    type: date
    description: Public release date (YYYY-MM-DD); also the capsule folder name.
    required: true
  - name: capabilities
    type: array
    description: Capability tags from the taxonomy in the repo README.
    required: true
  - name: model_card
    type: url
    description: Official model card URL — prefer learn.microsoft.com when available.
    required: true
  - name: announcement
    type: url
    description: Official release-announcement URL.
    required: false
  - name: expires
    type: date
    description: Retirement date if known; feeds the Expiring Soon section.
    required: false
  - name: pricing
    type: string
    description: Free-form pricing summary or structured object.
    required: false
  - name: dependencies
    type: array
    description: Extra Python packages appended to requirements-dev.txt (Capsule dependencies section).
    required: false
  - name: domains
    type: array
    description: Domains for the interesting use cases (e.g. travel, healthcare).
    required: false
  - name: references
    type: array
    description: Author-supplied best-practice references (model card, docs, sample repos, blog posts). The agent MUST prompt the creator for these before scaffolding. Rendered at the end of the capsule README and in the notebook's final References section.
    required: true
  - name: concepts
    type: array
    description: Ordered list of teaching concepts for this release. Each concept becomes its own notebook (1–3 concepts per notebook max). Provide {slug, title, concepts_covered[]} so the skill can name and scaffold each notebook file.
    required: true
produces:
  - models/<family>/<model>/<release_date>/README.md
  - models/<family>/<model>/<release_date>/notebooks/01-quickstart.ipynb
  - CHANGELOG.md
  - models/<family>/README.md
  - requirements-dev.txt
validates_against:
  - .github/specs/schemas/capsule.schema.json
depends_on:
  - add-family
  - add-model
  - refresh-recent-activity
---

# add-capsule

Produces a complete release capsule:

1. Creates `models/<family>/<model>/<release_date>/` with a README whose
   frontmatter matches [`capsule.schema.json`](../../specs/schemas/capsule.schema.json)
   — including a **Before You Begin** section with pricing, release /
   expiry dates, model-card link, and a link to
   [`models/quickstart/`](../../../models/quickstart/).
2. Scaffolds one or more notebooks under `notebooks/` following the
   pedagogy rules in [`plan.md` §15](../../plan.md):
   - **Each notebook covers 1–3 concepts.** If the release needs more,
     the skill scaffolds additional notebooks (`01-…`, `02-…`, `03-…`)
     rather than growing a single long notebook. The author declares the
     split up front via the `concepts` prompt.
   - Every notebook is **independently runnable** — it repeats the
     Before You Begin + env-precheck cells at the top.
   - **Numbered, alternating markdown ↔ code** sections so the Outline
     reads like a tutorial table of contents. Section titles are verbs
     (e.g. "Send a chat request", "Attach an image").
   - `## 1. Before You Begin` (markdown) — pricing, dates, model card,
     link to `models/quickstart/`.
   - `## 2. Verify your environment` (code) — env precheck against the
     vars listed in `models/quickstart/README.md` frontmatter
     (`required_env`).
   - Content sections `3..N-2` alternating markdown/code.
   - `## N-1. Your Turn to Explore` (markdown + empty code cell) —
     required. Suggests 2–3 concrete directions without solutions.
   - `## N. Summary` (markdown) — required. What was covered, when to
     reach for this model, links to primers and glossary terms.
   - `## N+1. References` (markdown) — required. Renders every entry
     from the capsule frontmatter's `references` array as a bulleted
     list (title → URL, with kind + note when present). If the author
     supplied no references, the scaffold prints a TODO reminder rather
     than silently omitting the section.
   - **Voice**: action-focused, no hype/marketing language.
3. Appends any capsule-specific `dependencies` under the
   `# Capsule dependencies` section of `requirements-dev.txt`.
4. Prepends (or updates in place) a row in `CHANGELOG.md`. Column
   shape: `Date | Family | Model | Capabilities | Pricing | Capsule`.
   The Date cell is a markdown link to the announcement URL (there is
   no separate Announcement column). The Model cell is a markdown link
   to the model card when known — no separate Model card column
   either. **The Pricing cell is also a markdown link when a price is
   stated** — target it at an official pricing page if one exists,
   otherwise at the blog post the figure was extracted from, so every
   price is verifiable. Use `_—_` (no link) when pricing is unknown.
   If an announcement-only row already exists for the same Date +
   Model, the skill updates it in place — adding the capsule link and
   any newly known fields — instead of duplicating.
5. Adds a members-table row to `models/<family>/README.md`.
6. Invokes [`refresh-recent-activity`](../refresh-recent-activity/) so the
   repo README's **Recently added** table (Model / Release date /
   Expires) stays current.
