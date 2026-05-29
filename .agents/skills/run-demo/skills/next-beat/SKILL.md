---
name: run-demo/next-beat
description: Reveal the next beat from `demo.md`, render the beat card, and update `.state.json`.
when_to_use: |
  - Speaker says "next", "go", "continue", "✅", or any signal to advance.
  - The current beat is marked done and the speaker is ready for the next one.
do_not_use_for: |
  - Going backwards (use `prev-beat`).
  - The very first reveal of the session (use `start` first, then `next-beat`).
  - Showing the scorecard mid-demo (use `show-scorecard`).
---

# Subskill: `run-demo/next-beat`

Reveal one beat at a time from `demos/<id>/demo.md`.

## Playbook

1. **Load `.state.json`.** If `current_beat == 0`, the next beat is
   beat 1. Otherwise it is `current_beat + 1`.

2. **If the next beat number exceeds the total beats**, dispatch to
   [`recap`](../recap/SKILL.md) instead of rendering anything new.

3. **Parse the target beat** from the `## Steps to record` section.
   The expected line shape is:

   ```
   N. **mm:ss – mm:ss** · <action prose> (optional code in next indented block)
   ```

   Extract: beat number, start offset, end offset, action prose, and
   any indented code block immediately below.

4. **Render the beat card** (see dispatcher §"Beat card"):

   ```
   ▶ Beat <N> of <Total> · <cumulative mm:ss> cumulative · ~<budget mm:ss> budget
   ─────────────────────────────────────────────────────────
   <action prose>

     $ <code if present>

   🎯 <one-line audience hint, if Narrator beats has one for this beat>
   🪧 End on: <held end frame for the LAST beat only; otherwise omit>

   ✅ Mark done?  ⏭ next  ⏸ pause  ↩ prev
   ```

   Cumulative time = sum of budgets of beats already in
   `completed_beats`. Budget = (end − start) for this beat.

5. **In `record` mode**, prepend a READY gate before the card:

   ```
   🎬 READY? — start screen capture, then say "go" to reveal Beat <N>.
   ```

   Wait for confirmation, then send the card. In `live` mode skip this.

6. **Update `.state.json`:**
   - Append the previous `current_beat` to `completed_beats` (skip if
     it was 0).
   - Set `current_beat` to the new beat number.

7. **Wait.** Do not preview Beat N+1. The speaker advances explicitly.

## Guardrails

- ≤ 5 lines of prose per beat in `live` mode (the card itself is
  formatting, not prose).
- Never paste content from sibling AUTHOR sections (`## Theme`,
  `## Takeaway`, `## Narrator beats`) verbatim except a single
  audience-hint line on the 🎯 row.
- Never run the demo's terminal commands yourself — they are part of
  the on-camera performance.
