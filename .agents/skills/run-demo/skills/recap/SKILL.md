---
name: run-demo/recap
description: End the demo on the held end frame, render the one-line takeaway, and reset `.state.json` for the next run.
when_to_use: |
  - All beats are complete and the speaker is ready to wrap.
  - Speaker says "recap", "wrap", "end on the frame".
  - `next-beat` was called past the last beat — auto-dispatch here.
do_not_use_for: |
  - Mid-demo scorecards (use `show-scorecard`).
  - Pausing for later (use `pause`).
---

# Subskill: `run-demo/recap`

Close the demo cleanly so the cut back to the speaker is on a held
frame, not on Copilot.

## Playbook

1. **Read `demos/<id>/demo.md`.** Pull `held_end_frame` and the
   `## Takeaway` section.

2. **Render the held end frame card:**

   ```
   ╭─ Held end frame ────────────────────────────────────────╮
   │ 🪧 <held_end_frame value>                                │
   ╰──────────────────────────────────────────────────────────╯

   🎯 <one-line takeaway from ## Takeaway>
   ```

   Keep the card to two lines plus the takeaway. No scorecard, no
   beat card, no follow-up prompts. The audience should be looking at
   the screen, not at Copilot Chat.

3. **Update `.state.json`:**
   - Set `current_beat` to the total beat count.
   - Append the final beat to `completed_beats` if not already there.
   - Set `paused: false`.
   - Add `ended_at` with the current ISO timestamp.

4. **Update `demos/SESSIONS.md`** — set `Last used` for this demo to
   today's date.

5. **Print one final operator-only line** (after the held frame card,
   visually separated by a blank line):

   ```
   ✅ Demo <id> complete. Re-run anytime — `.state.json` will reset on next `start`.
   ```

## Guardrails

- Do not re-emit the scorecard here unless the held end frame itself
  *is* the scorecard (e.g. `held_end_frame: "updated scorecard"`). In
  that case, render the scorecard as the held frame.
- Do not list "what we covered" in prose. The recap is one frame plus
  one sentence by design.
