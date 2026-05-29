---
name: run-demo/troubleshoot
description: A live command failed on-stage — fall back to the recorded clip listed in `recordings/` and continue the demo.
when_to_use: |
  - The current beat's command errored, timed out, or produced wrong output.
  - Speaker says "this failed", "fall back", "use the recording".
do_not_use_for: |
  - Pre-demo authoring problems (fix `demo.md` directly).
  - Generic VS Code / Foundry troubleshooting (use the workshop's own steps).
---

# Subskill: `run-demo/troubleshoot`

Recover gracefully when a live command fails during a demo.

## Playbook

1. **Acknowledge in one line:**

   > ⚠ Beat <N> failed live. Switching to the recorded fallback so the
   > demo keeps moving.

2. **Locate the fallback clip.** Look in `demos/<id>/recordings/`
   for files matching `beat-<N>*.{mp4,mov}` (newest first). If
   nothing matches, look for `fallback*.{mp4,mov}`.

3. **Tell the speaker exactly what to do**, in one block:

   ```
   📺 Play: demos/<id>/recordings/<filename>
   🎯 Audience should still land on: <beat's 🎯 line>
   🪧 End on: <beat's 🪧 line, if set; otherwise the held end frame>

   Say `next` when the clip ends and you are back in control.
   ```

4. **Do not change `current_beat`.** The beat is being covered by the
   clip; once the speaker says `next`, dispatch to
   [`next-beat`](../next-beat/SKILL.md) as usual.

5. **If there is no fallback clip available**, switch to a degraded
   path: render a still describing the missing artifact in plain
   prose, then suggest the speaker bridge verbally and call `next`.

   ```
   ⚠ No fallback clip found in demos/<id>/recordings/.
   Bridge verbally: "What you would see here is <action prose>. The
   net effect is <takeaway>." Then say `next`.
   ```

## Guardrails

- Never tell the speaker to debug the failure live. The demo is the
  product; debugging is post-show.
- Never advance `current_beat` from this subskill.
- Note the failure in `.state.json` by appending `{ "beat": N, "fell_back_to": "<file or 'verbal'>" }` to an optional `incidents` array. This is useful for post-show retrospectives. Create the array if it does not exist.
