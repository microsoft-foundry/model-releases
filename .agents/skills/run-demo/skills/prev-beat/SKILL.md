---
name: run-demo/prev-beat
description: Step back one beat — useful for record-mode retakes.
when_to_use: |
  - Speaker says "back", "prev", "redo this beat", "retake".
  - A take was muffed and the speaker wants the same beat card again.
do_not_use_for: |
  - Pausing and exiting (use `pause`).
  - Restarting from beat 1 (delete `.state.json` and run `start`).
---

# Subskill: `run-demo/prev-beat`

Step backwards one beat without altering the demo content.

## Playbook

1. **Load `.state.json`.** If `current_beat <= 1`, tell the speaker
   "Already at the first beat" and stop.

2. **Set `current_beat` to `current_beat - 1`** and remove that beat
   number from `completed_beats` if present.

3. **Re-render the (now) current beat card inline**, using the exact
   same card format as [`next-beat`](../next-beat/SKILL.md) §4. Do
   *not* delegate to `next-beat` — it would advance `current_beat`
   again. The re-render is read-only against state at this point.

4. **Write `.state.json`.**

## Guardrails

- Do not re-emit the `🎬 READY?` gate when stepping back. The speaker
  is already in the middle of capturing.
- Do not erase data from `completed_beats` other than the immediately
  preceding beat.
