---
name: run-demo/start
description: Begin a new run of a demo — pick the mode, propose a Copilot session name, render the header card, and initialize `.state.json`.
when_to_use: |
  - First time running a demo (`.state.json` is missing).
  - Speaker says "start", "begin", "let's go".
do_not_use_for: |
  - Resuming a paused session (use `resume`).
  - Revealing the next beat once started (use `next-beat`).
---

# Subskill: `run-demo/start`

Begin a new run of the demo in `demos/<id>/`.

## Playbook

1. **Read `demos/<id>/demo.md`.** Parse the YAML frontmatter and count
   beats in the `## Steps to record` section. Do not paste anything
   from the spec into the chat yet.

2. **Ask the mode**, once, in one line:

   > Mode? `live` (default — lean, on-stage) or `record` (deliberate, with
   > READY gates).

   Persist the answer (default to `live` if the speaker says "go" or
   anything that does not look like `record`).

3. **Propose a session name.**

   > Session name? Proposed: `demo-<id>-<slug-of-title>`. Hit return to
   > accept, or type a different one.

   Slug = lowercase, kebab-case from `title`, max 32 chars.

4. **Ask the surface**, once:

   > Where will you drive this? `chat` (Copilot Chat) or `cli` (Copilot CLI).

5. **Render the header card** (see dispatcher §"Header card") using
   the parsed frontmatter values. Then a single closing line:

   > Ready when you are. Say `next` to reveal Beat 1 — or `pause` to
   > save and exit.

6. **Write `.state.json`:**

   ```json
   {
     "demo_id": "<id>",
     "mode": "<live|record>",
     "started_at": "<ISO timestamp now>",
     "current_beat": 0,
     "completed_beats": [],
     "paused": false,
     "session_name": "<accepted name>"
   }
   ```

7. **Update `demos/SESSIONS.md`.** If the demo already has a row,
   update `Session name`, `Surface`, and `Last used`. Otherwise append
   a new row. Format:

   | Demo | Session name | Surface | Last used |
   |---|---|---|---|
   | `<id>` | `<session_name>` | `chat`/`cli` | `YYYY-MM-DD` |

## Guardrails

- Do not reveal Beat 1 in this subskill. That's `next-beat`'s job.
- Do not dump the full `demo.md` in the chat.
- If `.state.json` already exists with `current_beat > 0`, refuse
  and tell the speaker to use `resume` (or delete `.state.json`
  manually to force a fresh start).
