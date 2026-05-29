---
name: run-demo/pause
description: Save runtime state and exit cleanly so the speaker can return later via `resume`.
when_to_use: |
  - Speaker says "pause", "stop", "save and exit", "I need to step away".
do_not_use_for: |
  - Ending the demo on the held end frame (use `recap`).
  - Restarting from beat 1 (delete `.state.json` and run `start`).
---

# Subskill: `run-demo/pause`

Persist runtime state and exit the session cleanly.

## Playbook

1. **Load `.state.json`.** If missing, tell the speaker "No active
   session to pause" and stop.

2. **Set `paused: true`** and add `paused_at` with the current ISO
   timestamp. Do not modify `current_beat` or `completed_beats`.

3. **Write `.state.json`.**

4. **Print a one-line confirmation:**

   ```
   ⏸ Paused at Beat <N> of <Total>. Resume with: "Use `run-demo` on `demos/<id>`".
   ```

## Guardrails

- Do not show the next beat preview.
- Do not modify `demos/SESSIONS.md` here — pausing is not "last used"
  in the registry sense; `resume` and `recap` update that.
