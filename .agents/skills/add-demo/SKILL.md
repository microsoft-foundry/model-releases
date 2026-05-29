---
name: add-demo
description: Scaffold or refresh a demo under `demos/<id>/` from an existing workshop, producing a single-source-of-truth `demo.md` spec that `run-demo` can drive beat-by-beat.
when_to_use: |
  - "Create a demo from the foundry-models-e2e workshop"
  - "Add a new demo for the BRK230 router segment"
  - "Refresh demo D5 against the latest workshop"
  - "Author a demo spec for a recording crew or live presenter"
do_not_use_for: |
  - Running an existing demo interactively (use `run-demo`).
  - Creating a new workshop (use `add-workshop`).
  - Editing one specific beat of an existing demo by hand (open `demos/<id>/demo.md` directly).
  - Building slides only (use `create-slides`).
---

# Skill: `add-demo`

Scaffold or refresh a demo under `demos/<id>/` from a workshop in
`workshops/<slug>/`. The output is a single-source-of-truth `demo.md`
spec that `run-demo` can drive beat-by-beat, plus a small set of
companion files.

Companion design doc: [`.plans/demo-skills-plan.md`](../../../.plans/demo-skills-plan.md).

## What this skill produces

```
demos/<id>/
  demo.md              # THE SPEC — frontmatter + AUTO/AUTHOR sections (see §6 of plan)
  README.md            # short landing page: header card + how to run
  transcript.md        # stubbed transcript, one heading per beat
  recordings/
    .gitkeep           # binaries gitignored
  assets/
    .gitkeep           # screenshots, GIFs, fallback stills
  slides/              # ONLY if speaker opts in (delegates to create-slides)
    index.md
```

`.state.json` is **not** scaffolded by `add-demo`; it is written by
`run-demo` at runtime and is gitignored.

## Modes

| Mode | Trigger | Behavior |
|---|---|---|
| **Create** | `demos/<id>/` does not exist. | Full interview, generate folder. |
| **Refresh** | `demos/<id>/demo.md` already exists. | Re-read it + referenced workshop files, regenerate `<!-- AUTO -->` sections, leave `<!-- AUTHOR -->` sections untouched, end with a delta summary. |

The two are mutually exclusive — picking the right one is the very
first thing the skill does.

---

## Playbook — Create mode

1. **Confirm there is a workshop to demo.** List `workshops/*/`
   (directories only). If none exist, refuse and tell the speaker to
   run `add-workshop` first.

2. **Collect inputs** using `ask_user`, one question at a time, in this
   order. Validate each before asking the next.

   | # | Variable | Type / validation | Notes |
   |---|---|---|---|
   | 1 | `workshop_slug` | Pick from `workshops/*/` | Required. |
   | 2 | `id` | `^[a-z0-9][a-z0-9-]*$`, ≤ 32 chars | Kebab-case. If `demos/<id>/` exists, suggest `<id>-v2` and re-prompt. |
   | 3 | `title` | ≤ 80 chars | Short human title. |
   | 4 | `session_context` | Free text, optional | e.g. `BRK230 · Stanza 2 — SELECT`. Stored verbatim. |
   | 5 | `target_duration` | `^\d{1,2}:[0-5]\d$` | `m:ss` (e.g. `2:30`). |
   | 6 | `theme` | One sentence | The idea the demo lands. |
   | 7 | `takeaway` | One sentence | What the audience should remember. |
   | 8 | `source_steps` | Multi-select from numbered step files in the workshop | Default: offer all `[0-9][0-9]-*.md` + code files referenced in those steps. |
   | 9 | `mode_hint` | `portal \| code \| mixed` | Used by `run-demo` to pick presentation style. |
   | 10 | `held_end_frame` | Short sentence | The final on-screen artifact the demo ends on. |

3. **Auto-draft "Steps to record".** Read each file in `source_steps`
   and propose a numbered shot list with `mm:ss – mm:ss` budgets that
   sum to `target_duration`. Show the draft and ask the speaker to
   accept, edit inline, or re-prompt. Aim for 3–6 beats — fewer than
   that is too coarse, more than that is too dense for a short demo.

4. **Auto-draft the scorecard.** If any file in `source_steps` is a
   Python or JSON file with `eval_results_` in its path, parse it and
   pre-populate the `## Scorecard` table with up to 4 rows. Otherwise
   leave the table with `…` placeholders for the speaker to fill in.

5. **Offer a MARP cut-in deck.** Ask "Include a MARP cut-in deck?
   (yes/no)". If yes, **invoke the `create-slides` skill** with the
   demo folder as the target — do not duplicate its logic here. If no,
   skip the `slides/` folder entirely.

6. **Render templates** from `./templates/`. Substitute placeholders:

   - `{{id}}`, `{{title}}`, `{{workshop_slug}}`, `{{session_context}}`,
     `{{target_duration}}`, `{{theme}}`, `{{takeaway}}`,
     `{{mode_hint}}`, `{{held_end_frame}}`, `{{today}}` (ISO date).
   - `{{source_steps_yaml}}` — YAML list rendered from the chosen paths.
   - `{{source_steps_links}}` — markdown bullets with relative links.
   - `{{steps_to_record}}` — the accepted shot list.
   - `{{scorecard_table}}` — the auto-drafted scorecard markdown.

   Files written:
   - `demos/<id>/demo.md` from `templates/demo.md`.
   - `demos/<id>/README.md` from `templates/README.md`.
   - `demos/<id>/transcript.md` from `templates/transcript.md`.
   - `demos/<id>/recordings/.gitkeep` (empty).
   - `demos/<id>/assets/.gitkeep` (empty).

7. **Wire ignores.** Verify the repo root `.gitignore` contains entries
   for `demos/**/recordings/*.mp4`, `demos/**/recordings/*.mov`, and
   `demos/**/.state.json`. If any are missing, add them under a
   `# demos/` section.

8. **Register the demo.** If `demos/SESSIONS.md` does not exist,
   scaffold it with the header row from §7 of the plan. Append a row
   for the new demo with an empty `Session name` and `Last used` —
   `run-demo/start` fills these in later.

9. **Verify and hand off.** Show the rendered folder tree (one level
   deep), confirm `demo.md` parses, and suggest:

   - "Open `demos/<id>/demo.md` and tighten the Theme / Takeaway."
   - "When ready, run `run-demo` on this folder."

---

## Playbook — Refresh mode

1. **Load** `demos/<id>/demo.md`. Parse YAML frontmatter and section
   markers. If parsing fails, refuse and ask the speaker to fix the
   file by hand.

2. **Re-resolve each path in `source_steps`.**
   - If the path exists → keep.
   - If renamed (best-match by basename in the same workshop) →
     propose the rename, apply on confirmation.
   - If deleted → leave as a `⚠ broken source` row in the delta
     summary; do not silently drop.

3. **Regenerate `<!-- AUTO -->` sections only.** These are the
   sections marked `<!-- AUTO -->` or `<!-- AUTO-DRAFTED on create -->`
   in `templates/demo.md`:
   - `## Header card`
   - `## Source steps`
   - `## Steps to record` (only if the speaker accepted the original
     auto-draft verbatim; if any beat differs from the original draft,
     treat the section as AUTHOR-touched and **leave it alone**, just
     note the divergence in the delta summary)
   - `## Scorecard` (re-parse referenced eval files; preserve any
     manual edits inside cells by leaving the row untouched if the
     auto-drafted value still appears)

4. **Never touch** sections marked `<!-- AUTHOR -->`:
   - `## Theme`
   - `## Takeaway`
   - `## Narrator beats`
   - `## Recording notes`

5. **Update `generated_at`** in frontmatter; leave `generated_by` as
   `add-demo@1`.

6. **End with a delta summary** in this exact shape:

   ```
   refresh summary · demos/<id>/demo.md
     · N file links updated
     · M scorecard numbers updated
     · K broken sources (listed below)
     · 0 author sections touched
   ```

---

## Guardrails

- **Refuse to overwrite `demo.md` outside refresh mode.** If
  `demos/<id>/demo.md` exists and the speaker asked for create,
  surface the conflict and suggest refresh instead.
- **Never write binary files.** `.mp4` / `.mov` belong in
  `demos/<id>/recordings/` which is gitignored.
- **Never name competitor clouds.** Examples stay Foundry / Azure-direct.
- **Use inclusive language** — "key points" / "sentences", not
  "bullets".
- **The held end frame is sacred.** Always populate it; `run-demo`
  depends on it to know when to stop.
- **`id` is the suggested Copilot session name root** (see §7 of plan).
  Do not pick ids that collide with another folder under `demos/`.
