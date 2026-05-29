---
name: run-demo/show-scorecard
description: Re-print the demo's scorecard table at any time, without advancing beats.
when_to_use: |
  - Speaker says "scorecard", "show the numbers", "remind me of the deltas".
  - During recap or between beats when the speaker wants the chart on screen.
do_not_use_for: |
  - Advancing the demo (use `next-beat`).
  - Editing scorecard values — those live in `demo.md`.
---

# Subskill: `run-demo/show-scorecard`

Re-render the `## Scorecard` table from `demos/<id>/demo.md`.

## Playbook

1. **Read `demos/<id>/demo.md`.** Extract the `## Scorecard` section.

2. **Render it as-is** if it is already a clean markdown table that
   follows the dispatcher's scorecard rules (≤ 4 rows, bold delta
   column, ✅/⚠/➖ status only).

3. **If the table violates the rules** (too many rows, missing delta,
   decorative emoji), render the first 4 rows only and append a single
   line:

   > *(scorecard trimmed to 4 rows for on-stage rendering — full table
   > in `demos/<id>/demo.md`)*

4. **Do not change `.state.json`.** This subskill is read-only.

## Guardrails

- Never invent numbers. If a cell is blank or `…`, render it as `—`.
- Do not paste the rest of `demo.md` — just the scorecard.
