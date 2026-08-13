---
kind: skill
name: refresh-recent-activity
description: Regenerate the repo README's Recently added table (Model / Release date / Capabilities) from the top 3 CHANGELOG rows.
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

Columns produced, one row per CHANGELOG row (the top 3, newest first —
these may include announcements that have no capsule yet):

| Column | Source | Link target |
|---|---|---|
| Model | CHANGELOG Model cell, minus any link markup and availability note | plain bold text — no link |
| Release date | CHANGELOG Date cell | the announcement (carried over from the CHANGELOG cell) |
| Capabilities | CHANGELOG Capabilities cell, verbatim | plain text — no link |

Column order mirrors `CAPSULE-TOC.md`: what it is first, when it
landed second. Every cell is copied from the CHANGELOG row rather than
written by hand, so the table can be regenerated at any time without
losing prose.

Neither pricing nor expiry is shown in the README. Neither is in the
CHANGELOG either — price lives on the model card a capsule links to,
and expiry lives in the publisher README members table, which is the
single place a retirement date is tracked. The caption under the
README table points readers to the CHANGELOG for the full history.

Idempotent — safe to run any time. Called automatically at the end of
[`add-capsule`](../add-capsule/), and recommended on a monthly cadence
via a scheduled GitHub Action.
