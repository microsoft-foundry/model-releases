# BRK230 — "Right Model, Right Job" demo replay

This workshop ships a custom Copilot agent that replays the BRK230 demo
for [foundry-models-e2e](README.md) end-to-end in chat. It's the agent
we use for **rehearsals, recordings, and live breakouts** when we don't
want to wait on a real Azure run during the talk.

The agent definition lives at
[brk230-demo.agent.md](../../.github/agents/brk230-demo.agent.md); all
of the data it reads sits under
[brk230-demo/](../../.github/agents/brk230-demo/).

---

## TL;DR

1. Open Copilot Chat → `@BRK230 Demo Replay`.
2. Type **`run the session demo`** (rehearsals/recording) **or**
   **`run the live demo`** (real numbers from the last workshop run).
3. The agent prints a confirmation line (`Loaded SESSION manifest · …`),
   then waits.
4. Paste any of the 5 BRK230 trigger phrases (in order):
   1. `run the baseline evaluation with my single frontier model`
   2. `help me decompose this into a multi-model architecture`
   3. `help me add a custom evaluator to track policy adherence`
   4. `help me optimize the policy model for improving adherence`
   5. `summarize my journey and give me a playbook for future`

Each demo opens with a `Refer to files:` block (links you open in the left
editor pane), waits for you to say `go`, then mimics the run on the right
and finishes with a boxed scorecard plus a one-line takeaway.

---

## Two modes, identical script

| Mode | Trigger | Data dir | Use it for |
|---|---|---|---|
| **SESSION** | `run the session demo` | [session/](../../.github/agents/brk230-demo/session/) | Rehearsals, recordings, anything where you need the numbers to never drift — frozen record of the original BRK230 session run |
| **LIVE** | `run the live demo` | [generated/](../../.github/agents/brk230-demo/generated/) | Showing the audience real eval JSON from the most recent workshop pass |

The flow, beats, and trigger phrases are **identical** between modes — only
the underlying numbers and the cited JSON path differ. Both modes are
fully offline; nothing calls Azure at demo time.

> **Note on the initial state.** In this first commit, `session/` and
> `generated/` contain the **same** eval JSONs and `narrative.json` —
> both seeded from the inaugural BRK230 workshop run. That's intentional:
>
> - **`session/`** is the **frozen BRK230 reference build** — real eval
>   data from the original BRK230 session run, captured at a fixed point
>   in time. It is never auto-updated, and you should never modify it by
>   hand either. It exists so a rehearsal or recording always has the
>   original numbers to fall back on, no matter what you do elsewhere.
> - **`generated/`** is **yours to overwrite**. Nothing in the workshop
>   automatically copies fresh runs into it — it only changes when *you*
>   manually drop new `eval_results_*.json` files in. After that, the
>   agent's live mode walks through your numbers; until then, both modes
>   tell the same BRK230 story.

---

## How the agent stays on rails

The agent definition (frontmatter + system prompt) is the contract.
Important rules baked in:

- **Mimic, don't execute.** Eval/fine-tune/deploy commands are shown in
  fenced bash blocks with realistic-looking output, not actually run.
- **Numbers come from `narrative.json` only.** If a value isn't in the
  manifest, the agent says so instead of inventing it.
- **Each demo opens with a file list and halts.** You drive the editor
  pane while the agent waits — say `go` to continue.
- **Scorecards are boxed ASCII** with target thresholds from
  `manifest.targets` and ▲/▼ arrows colored by `target_status`.
- **No raw progress logs, no jq dumps > 10 lines, no full JSON paste.**
  Same discipline as the workshop instructor-mode rules.

If the agent ever drifts (invents numbers, skips the `Refer to files:`
block, runs commands for real), the fix is almost always in the
`.agent.md` system prompt — not in the data.

### Which model runs the agent?

The agent's frontmatter pins a **default** model list:

```yaml
model:
  - Claude Sonnet 4.6 (copilot)   # primary
  - Claude Opus 4.7 (copilot)     # backup
```

Those are the models we rehearsed and recorded BRK230 against — they
follow the "mimic, don't execute" rules cleanly and render the boxed
scorecards reliably. **You don't have to use them.** The model picker
in the Copilot Chat input row overrides the agent's default for that
turn, so you can flip to GPT, Gemini, or any other available model and
the same `.agent.md` system prompt + `narrative.json` data will drive
the run. If you see drift (invented numbers, skipped halts, running
commands for real) on a different model, fall back to Sonnet 4.6 — the
prompt is tuned for it.

---

## `narrative.json` — the manifest that drives every demo

`narrative.json` is the **single source of truth** for everything numeric
the agent says. It exists in both `session/` and `generated/` and has
the same shape:

```jsonc
{
  "version": 1,
  "data_dir": "...absolute path...",
  "content_hash": "sha256 over the eval JSONs",   // agent prints first 4 chars
  "targets":     { "quality": 0.92, "cost": 0.030, "latency": 8.0, "policy": 0.80 },
  "price_table": { "planner-gpt41": {"in": 0.005, "out": 0.015}, ... },
  "runs": {
    "v1-curated": { ... },   // DEMO 1, 20-row baseline
    "v1-demo":    { ... },   // DEMO 2, 50-row baseline
    "v2-demo":    { ... },   // DEMO 2/3, multi-model
    "v3-demo":    { ... }    // DEMO 4, after fine-tune
  }
}
```

Each `runs.<label>` entry carries:

| Field | Meaning | Where it shows in the demo |
|---|---|---|
| `source_file` | The `eval_results_*.json` it was computed from | The clickable link printed before each scorecard |
| `n_rows` | Row count in the eval set | Inline mention ("50-row demo set") |
| `judge_score` / `quality` | LLM-judge mean — **headline quality metric** | 🎯 row in the scorecard |
| `schema_score` | Schema-validity mean | Background only; not headlined |
| `latency_s` | Mean per-row latency | ⚡ row |
| `cost_usd` | Mean per-row USD cost (computed from `usage_json` × `price_table`) | 💸 row |
| `policy_score` | Custom policy-adherence evaluator mean (null on v1-curated) | 📜 row, DEMOs 3–5 |
| `policy_applicable_frac` | Fraction of rows the policy rubric scored | "applicable to ~⅓ of rows" callout in DEMO 3 |
| `studio_url` | Foundry portal URL for that run | Optional reference |
| `delta_vs_v1` | `{abs, pct}` per metric vs the **`v1-demo`** 50-row baseline | Δ column with ▲/▼ arrows |
| `target_status` | `green` / `amber` / `red` / `na` per metric | Drives ✅/🚨 emoji and the "lead-in" line of each takeaway |

### Where the scorecard insights come from

Every scorecard the agent renders maps directly back to this manifest:

- **Headline cells** (🎯 quality, 💸 cost, ⚡ latency, 📜 policy) =
  `runs.<label>.{quality, cost_usd, latency_s, policy_score}`.
- **Target bar / threshold line** = `manifest.targets`.
- **Pass / fail glyph** = `runs.<label>.target_status.<metric>`
  (`green` → ✅, `amber` → ⚠️, `red` → 🚨, `na` → blank).
- **Δ column on v2/v3 scorecards** = `runs.<label>.delta_vs_v1.<metric>`,
  with the **arrow direction inverted by metric polarity**:
  - quality / policy: `abs > 0` → ▲ green, `abs < 0` → ▼ red
  - cost / latency:   `abs < 0` → ▼ green, `abs > 0` → ▲ red
- **Takeaway lead-in** ("cheaper + faster, but worse on the dimension WWI
  pays the bill for…") is shaped by which `target_status` flipped between
  runs — not by hand-written prose.

If you want a different threshold or a different bucket, change
`TARGETS` in [analyze_eval_run.py](../../.github/agents/brk230-demo/tools/analyze_eval_run.py)
and re-run the analyzer (see below).

---

## Running a fresh **live** demo (refresh `generated/`)

Nothing automatic touches `.github/agents/brk230-demo/generated/` — you
decide when to refresh it, by manually copying the eval JSONs from a
workshop run you're happy with. Once the new files are in place, the
agent runs the analyzer for you on first load (it notices any
`eval_results_*.json` newer than `narrative.json`). To do it manually:

```bash
# 1. Drop the four refreshed eval JSONs into:
#    .github/agents/brk230-demo/generated/
#      eval_results_v1-curated.json   (DEMO 1, 20 rows)
#      eval_results_v1-demo.json      (DEMO 2, 50 rows baseline)
#      eval_results_v2-demo.json      (DEMO 2/3, multi-model)
#      eval_results_v3-demo.json      (DEMO 4, after FT)

# 2. Re-build the manifest (run from repo root):
python3 .github/agents/brk230-demo/tools/analyze_eval_run.py \
    .github/agents/brk230-demo/generated

# 3. Sanity-check the summary it prints:
#       label         n   quality      cost  latency   policy
#       v1-curated   20    0.590  $0.0105   13.20s     na
#       v1-demo      50    0.644  $0.0104   29.14s    0.362
#       v2-demo      50    ...                              ...
#       v3-demo      50    ...                              ...

# 4. Commit narrative.json + the 4 eval JSONs together so the
#    content_hash and the data they describe never get out of sync.
```

The next time the agent loads, it'll print
`Loaded LIVE manifest · 4 runs · hash <new>` with the fresh numbers, and
every scorecard will reflect them automatically — no agent prompt edits
needed.

> **Sensitive-data check:** the eval JSONs contain `studio_url`s with
> subscription/tenant IDs. Either scrub them before commit or accept
> that they ship with the repo (`.reference-copy/` already shows them).

---

## Editing the **session** narrative

`session/narrative.json` is the **frozen record of the original BRK230
session run** — the agent will *not* re-analyze it, even if you drop new
JSONs alongside. That's deliberate: rehearsals and recordings need
numbers that never drift.

If you ever need to tweak the recorded story (e.g. dial up the v3
policy jump for a re-recording):

1. Edit `session/narrative.json` directly.
2. Keep the shape identical to what the analyzer produces (same keys,
   same `delta_vs_v1`, same `target_status`) — the agent reads them by
   name.
3. If you also want the linked `eval_results_*.json` files in
   `session/` to match (the audience may open them), edit those too.
4. Bump `content_hash` to anything new — it's only used as a cache-buster
   indicator the agent prints; it doesn't have to actually hash.

---

## File map

```
.github/agents/
├── brk230-demo.agent.md                  ← agent definition (system prompt)
└── brk230-demo/
    ├── session/                          ← frozen BRK230 session run (real data, fixed in time)
    │   ├── narrative.json                  manifest (frozen — do not modify)
    │   └── eval_results_v{1-curated,1-demo,2-demo,3-demo}.json
    ├── generated/                        ← real run, auto-analyzed
    │   ├── narrative.json                  manifest (regenerated)
    │   └── eval_results_v{1-curated,1-demo,2-demo,3-demo}.json
    └── tools/
        └── analyze_eval_run.py           ← rebuilds narrative.json from JSONs
```

For the workshop content the demo replays, see
[README.md](README.md) and [PLAYBOOK.md](PLAYBOOK.md).

---

## Appendix — what's in `.github/agents/brk230-demo/`

| File | What it is |
|---|---|
| [brk230-demo.agent.md](../../.github/agents/brk230-demo.agent.md) | The agent definition: frontmatter + system prompt that drives the entire 5-demo replay |
| [analyze_eval_run.py](../../.github/agents/brk230-demo/tools/analyze_eval_run.py) | Reads the four `eval_results_*.json` files in a data dir and (re)builds `narrative.json` with quality / cost / latency / policy + Δ + target flags |
| [session/narrative.json](../../.github/agents/brk230-demo/session/narrative.json) | Frozen manifest used in **SESSION** mode — record of the original BRK230 session run, fixed in time |
| [session/eval_results_v1-curated.json](../../.github/agents/brk230-demo/session/eval_results_v1-curated.json) | 20-row baseline eval result from the BRK230 session (DEMO 1 — single frontier model) |
| [session/eval_results_v1-demo.json](../../.github/agents/brk230-demo/session/eval_results_v1-demo.json) | 50-row v1 baseline eval result from the BRK230 session (DEMO 2 — comparison anchor) |
| [session/eval_results_v2-demo.json](../../.github/agents/brk230-demo/session/eval_results_v2-demo.json) | 50-row v2 multi-model eval result from the BRK230 session (DEMO 2/3) |
| [session/eval_results_v3-demo.json](../../.github/agents/brk230-demo/session/eval_results_v3-demo.json) | 50-row v3 post-fine-tune eval result from the BRK230 session (DEMO 4) |
| [generated/narrative.json](../../.github/agents/brk230-demo/generated/narrative.json) | Auto-generated manifest used in **LIVE** mode — refreshed by `analyze_eval_run.py` whenever the eval JSONs change |
| [generated/eval_results_v1-curated.json](../../.github/agents/brk230-demo/generated/eval_results_v1-curated.json) | Real 20-row baseline eval result from the most recent workshop pass (DEMO 1) |
| [generated/eval_results_v1-demo.json](../../.github/agents/brk230-demo/generated/eval_results_v1-demo.json) | Real 50-row v1 baseline eval result (DEMO 2 anchor) |
| [generated/eval_results_v2-demo.json](../../.github/agents/brk230-demo/generated/eval_results_v2-demo.json) | Real 50-row v2 multi-model eval result (DEMO 2/3) |
| [generated/eval_results_v3-demo.json](../../.github/agents/brk230-demo/generated/eval_results_v3-demo.json) | Real 50-row v3 post-fine-tune eval result (DEMO 4) |
| [.reference-copy/](../../.github/agents/brk230-demo/.reference-copy/) | **Reference-only** snapshot of one full live workshop run (eval JSONs, load-test CSVs, fine-tune logs, sample data, progress notes). Kept solely as a "known-good" archive for the BRK230 session — the agent does **not** read from here. |

> **Why these files live here at all.** Workshop runs write everything
> under [code/generated/](code/) which is **`.gitignore`d** — nothing
> from a real run is committed by default. The `session/`,
> `generated/`, and `.reference-copy/` folders above exist *only*
> because we manually copied a chosen run's artifacts into the agent
> tree so the BRK230 replay has something deterministic to read. If
> you re-run the workshop and want those new numbers in the demo,
> you have to copy the fresh `eval_results_*.json` over `generated/`
> yourself (see *Running a fresh live demo* above) — git won't carry
> them across for you.


