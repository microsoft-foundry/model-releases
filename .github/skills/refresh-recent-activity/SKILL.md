---
name: refresh-recent-activity
description: Update the README "What's new?" table from the top 3 CHANGELOG rows. Use after adding or archiving a capsule.
---

# refresh-recent-activity

Rewrite the table between `<!-- BEGIN:LATEST -->` and `<!-- END:LATEST -->` in `README.md` from the first three rows of `CHANGELOG.md`:

| README column | From CHANGELOG |
|---|---|
| Capsule | Model cell text, linked to the Capsule cell's target: `[Model](4-models/<model>/)` |
| Date | Date cell |
| What it does | What's new cell, release-post link removed |

Keep the header row `| Capsule | Date | What it does |`. Then run `python 1-scripts/check.py` — it fails if the two drift.
