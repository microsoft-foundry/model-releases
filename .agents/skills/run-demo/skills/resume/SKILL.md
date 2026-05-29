---
name: run-demo/resume
description: Resume a paused demo from the saved beat.
when_to_use: |
  - `.state.json` has `paused: true`.
  - Speaker says "resume", "pick up", "continue where I left off".
do_not_use_for: |
  - First-time start (use `start`).
  - Mid-flight advance (use `next-beat`).
---

# Subskill: `run-demo/resume`

Resume from the saved beat.

## Playbook

1. **Load `.state.json`.** Refuse if missing — tell the speaker to
   `start` instead.

2. **Set `paused: false`** and clear `paused_at` (if present). Write
   the file back.

3. **Print a one-line re-entry banner:**

   ```
   ▶ Resumed at Beat <current_beat> of <Total> · mode: <mode>.
   ```

4. **Re-render the current beat card inline**, using the exact same
   card format as [`next-beat`](../next-beat/SKILL.md) §4. Do *not*
   delegate to `next-beat` — it would advance `current_beat`. The beat
   that was current when the speaker paused is still the one they
   need to perform.

   In `record` mode, prepend the `🎬 READY?` gate exactly as `next-beat`
   does.

5. **Update `demos/SESSIONS.md`** — set `Last used` for this demo to
   today's date.

## Guardrails

- Do not re-emit the header card (it would push the active beat off
  the visible viewport on small screens).
- Do not change `mode`. The mode chosen at `start` is sticky for the
  life of the session.
