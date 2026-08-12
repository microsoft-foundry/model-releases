---
kind: skill
name: refresh-recent-activity
description: Regenerate the repo README's Recently added table from the top 3 CHANGELOG rows.
inputs: []
produces:
  - README.md
validates_against: []
depends_on: []
---

# refresh-recent-activity

Rewrites the marker-bracketed **Recently added** table in the repo
README:

```
<!-- BEGIN:RECENTLY-ADDED --> … <!-- END:RECENTLY-ADDED -->
```

Columns produced, one row per capsule (most recent first, top 3 by
capsule frontmatter `release_date`):

| Column | Source | Link target |
|---|---|---|
| Release date | Capsule frontmatter `release_date` | Capsule frontmatter `announcement` (blog post) — falls back to `model_card` if `announcement` is empty |
| Model | Capsule frontmatter `model` | Capsule README |
| Description | Capsule frontmatter `summary` (or first sentence of capsule README) | plain text — no link |

Neither pricing nor expiry is shown in the README. Pricing lives in
`CHANGELOG.md` (with a verifiable source link) and expiry lives in the
family README members table, which is the single place a retirement
date is tracked. The caption under the README table points readers to
the CHANGELOG for the full history.

Idempotent — safe to run any time. Called automatically at the end of
[`add-capsule`](../add-capsule/), and recommended on a monthly cadence
via a scheduled GitHub Action.
