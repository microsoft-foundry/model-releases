---
name: run-demo
description: Drive a demo in `demos/<id>/` beat-by-beat, in `live` or `record` mode, with reveal-only-the-current-beat discipline. Pairs with `add-demo`.
when_to_use: |
  - "Run demo D3 for me"
  - "Walk me through demos/<id> so I can record it"
  - "I'm going live in 5 minutes — start the BRK230 router demo"
  - "Resume the demo I paused"
  - "Show me the scorecard for demo D5"
do_not_use_for: |
  - Authoring or refreshing a demo spec (use `add-demo`).
  - Running a workshop end-to-end (use `run-workshop`).
  - Building slides (use `create-slides`).
---

# Skill: `run-demo` (dispatcher)

Drive a demo in `demos/<id>/` **one beat at a time**. The speaker
should only ever see the current beat plus the header card — never the
full `demo.md` dumped at once.

Companion design doc: [`.plans/demo-skills-plan.md`](../../../.plans/demo-skills-plan.md).

## Modes

| Mode | Pace | Output style | Use case |
|---|---|---|---|
| **`live`** *(default)* | Lean. One beat at a time, ≤ 5 lines per beat. | Tabular scorecards, emoji status only (▶ ✅ ⏸ 🎯). No "READY?" prompts. | On-stage. |
| **`record`** | Deliberate. Adds "READY?" pause prompts, mouse-park hints, held-frame timers. | Same visuals plus shot framing notes. | Solo recording. |

Mode is asked once at `start` and persisted in `.state.json`.

## Subskills

| Subskill | Use when |
|---|---|
| [`start`](./skills/start/SKILL.md) | New session; pick demo, confirm mode, show header card. |
| [`next-beat`](./skills/next-beat/SKILL.md) | Reveal the next beat and update `.state.json`. |
| [`prev-beat`](./skills/prev-beat/SKILL.md) | Step back one beat (useful in record retakes). |
| [`show-scorecard`](./skills/show-scorecard/SKILL.md) | Re-print the demo's scorecard at any time. |
| [`pause`](./skills/pause/SKILL.md) | Save state and exit cleanly. |
| [`resume`](./skills/resume/SKILL.md) | Resume from saved beat. |
| [`recap`](./skills/recap/SKILL.md) | Show the held end frame + one-line takeaway. |
| [`troubleshoot`](./skills/troubleshoot/SKILL.md) | A live command failed; fall back to a recorded clip. |

---

## Playbook

1. **Pick the demo.** If the speaker did not name one, list
   `demos/*/` (folders only, excluding hidden and `SESSIONS.md`) and
   ask which one.

2. **Load `.state.json`** at `demos/<id>/.state.json`.
   - If missing or `paused: false` and `current_beat == 0` → dispatch
     to `start`.
   - If `paused: true` → dispatch to `resume`.
   - Otherwise the session is mid-flight; continue.

3. **Choose a subskill** based on the speaker's prompt:

   | Speaker said... | Dispatch to |
   |---|---|
   | "start", "begin", or nothing recognizable yet | `start` |
   | "next", "go", "continue", "✅" | `next-beat` |
   | "back", "prev", "redo this beat" | `prev-beat` |
   | "scorecard", "show the numbers" | `show-scorecard` |
   | "pause", "stop", "save and exit" | `pause` |
   | "resume", "pick up where I left off" | `resume` |
   | "recap", "wrap", "end on the frame" | `recap` |
   | reports a command error / "this failed" | `troubleshoot` |

4. **Reveal-only-the-current-beat rule.** Never paste the full
   `demo.md` into the chat. After every subskill, summarize the next
   recognized control in one line (e.g. *"next · prev · scorecard ·
   pause"*) and wait.

---

## Runtime state

`demos/<id>/.state.json` (gitignored):

```json
{
  "demo_id": "D3",
  "mode": "live",
  "started_at": "2026-05-29T09:00:00Z",
  "current_beat": 2,
  "completed_beats": [1],
  "paused": false,
  "session_name": "demo-D3-multi-model-decomp"
}
```

If the file is missing, treat the demo as not yet started and dispatch
to `start`.

---

## Header card (rendered at `start` and `recap`)

```
╭─ Demo D3 · Multi-model decomposition ─────────────────╮
│ ⏱  target 2:30        🎯 theme: right model per job   │
│ 📺 mode: live          📂 workshop: foundry-models-e2e│
│ 🧭 beats: 4            🪧 ends on: updated scorecard  │
╰───────────────────────────────────────────────────────╯
```

Width is fixed at ~57 chars so it renders cleanly in standard-width
Copilot Chat panes. Substitute real values from `demo.md` frontmatter.

## Beat card (rendered at every `next-beat`)

```
▶ Beat 2 of 4 · 00:45 cumulative · ~0:40 budget
─────────────────────────────────────────────────────────
Run the same Carmen prompt; show the trace fan-out.

  $ python workshops/foundry-models-e2e/code/s05_multi_model_agent.py

🎯 Audience should see: router → policy + planner spans.
🪧 End on: trace timeline view.

✅ Mark done?  ⏭ next  ⏸ pause  ↩ prev
```

Cumulative time = sum of budgets of completed beats. Budget for the
current beat is parsed from the `mm:ss – mm:ss` prefix of the beat in
`## Steps to record`.

In **`record` mode**, append a "READY?" gate:

```
🎬 READY? — start screen capture, then say "go" to reveal the beat.
```

## Scorecard rendering rules

- Always a markdown table.
- Emoji used **only** as status indicators: ✅ improvement, ⚠ regression,
  ➖ neutral.
- Bold the **delta** column.
- Limit to ≤ 4 rows so it fits a single Copilot Chat viewport.

Example:

| Metric | v1 baseline | v3 optimized | **Δ** | |
|---|---|---|---|---|
| Quality | 0.41 | 0.46 | **+12 %** | ✅ |
| Cost / req | $0.023 | $0.006 | **−74 %** | ✅ |
| p50 latency | 12.5 s | 6.5 s | **−48 %** | ✅ |

---

## Visual / tone rules (apply to every message this skill emits)

1. **One beat at a time.** Never dump the full spec.
2. **Tabular over prose** for scorecards, comparisons, and headers.
3. **Subtle status emoji only** — ✅ ⚠ ➖ ▶ ⏸ 🎯 🪧 ⏱ 📺 📂 🧭 🎬 ⏭ ↩.
   No decorative emoji.
4. **Concise takeaways** — one sentence, present tense, audience-facing.
5. **Inclusive language** — "key points" / "sentences", not "bullets".
6. **No competitor cloud names.** Foundry / Azure-direct only.
7. **Held end frame is sacred.** `recap` must end on it so the cut
   back to the speaker is clean.

---

## Command execution rules

The speaker drives their own VS Code, browser, and terminal. This skill
**must not** run terminal commands on the speaker's behalf during a
live or recorded demo — those are part of the on-camera performance.
The only exception is reading files in the demo folder to render the
next beat.
