---
kind: skill
name: refresh-recent-activity
description: Regenerate the repo README's Recent activity and Expiring soon sections from capsule folders and family expiry dates.
inputs:
  - name: window_days
    type: string
    description: Days ahead to scan for expiring models. Defaults to 60.
    required: false
produces:
  - README.md
validates_against: []
depends_on: []
---

# refresh-recent-activity

Rewrites two marker-bracketed sections in the repo README:

- `<!-- BEGIN:RECENT-ACTIVITY --> … <!-- END:RECENT-ACTIVITY -->` —
  the 3 most recent capsule folders by `YYYY-MM-DD` folder name.
- `<!-- BEGIN:EXPIRING-SOON --> … <!-- END:EXPIRING-SOON -->` —
  every model whose `expires` date (read from each family README's
  members table, cross-checked against the capsule's frontmatter) falls
  within the next `window_days` (default 60), with a suggested
  successor capsule link when one exists in the same family.

Idempotent — safe to run any time. Called automatically at the end of
[`add-capsule`](../add-capsule/), and recommended on a monthly cadence
via a scheduled GitHub Action.
