---
kind: skill
name: refresh-recent-activity
description: Regenerate the repo README's Recently added table from capsule folders and family expiry dates.
inputs:
  - name: window_days
    type: string
    description: Days ahead within which an expiring model gets the ⚠️ marker. Defaults to 60.
    required: false
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
`YYYY-MM-DD` folder name):

| Column | Source | Link target |
|---|---|---|
| Release date | Capsule folder date | Capsule frontmatter `announcement` (blog post) — falls back to `model_card` if `announcement` is empty |
| Model | Capsule frontmatter `model` | Capsule README |
| Description | Capsule frontmatter `summary` (or first sentence of capsule README) | plain text — no link |
| Expires | Capsule frontmatter `expires` (cross-checked against family README member row) | Bolded with ⚠️ when the date is within `window_days` (default 60); em-dash when unknown |

Pricing is intentionally **not** shown in the README — pricing data
lives in `CHANGELOG.md` (with a verifiable source link). The caption
under the README table points readers there for the full history and
pricing.

Idempotent — safe to run any time. Called automatically at the end of
[`add-capsule`](../add-capsule/), and recommended on a monthly cadence
via a scheduled GitHub Action.
