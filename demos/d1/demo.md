---
id: d1
title: D1 — Baseline with one frontier model
workshop: foundry-models-e2e
session_context: "BRK230 · Stanza 2 — SELECT"
target_duration: "1:30"
theme: "One frontier model answering every intent looks reasonable in isolation, but it is the strawman the rest of the talk knocks down."
takeaway: "A single `gpt-4.1` baseline gives us measurable numbers — quality 0.41, p50 12.5 s, $0.023/req — to beat, not a system to ship."
mode_hint: code
held_end_frame: "Scorecard panel showing **quality 0.41 · p50 12.5 s · $0.023/req** for the single-model baseline."
source_steps:
  - workshops/foundry-models-e2e/02-baseline-sdk.md
  - workshops/foundry-models-e2e/code/s02_baseline_agent.py
  - workshops/foundry-models-e2e/code/s02_scorecard.py
generated_at: 2026-05-29
generated_by: add-demo@1
---

# d1 · D1 — Baseline with one frontier model

## Header card
<!-- AUTO — regenerated on refresh. Do not edit by hand. -->

| Field | Value |
|---|---|
| Duration | 1:30 |
| Theme | One frontier model answering every intent looks reasonable in isolation, but it is the strawman the rest of the talk knocks down. |
| Takeaway | A single `gpt-4.1` baseline gives us measurable numbers — quality 0.41, p50 12.5 s, $0.023/req — to beat, not a system to ship. |
| Mode hint | code |
| Held end frame | Scorecard panel showing **quality 0.41 · p50 12.5 s · $0.023/req** for the single-model baseline. |

## Source steps
<!-- AUTO — regenerated on refresh. -->

- [`workshops/foundry-models-e2e/02-baseline-sdk.md`](../../workshops/foundry-models-e2e/02-baseline-sdk.md)
- [`workshops/foundry-models-e2e/code/s02_baseline_agent.py`](../../workshops/foundry-models-e2e/code/s02_baseline_agent.py)
- [`workshops/foundry-models-e2e/code/s02_scorecard.py`](../../workshops/foundry-models-e2e/code/s02_scorecard.py)

## Steps to record
<!-- AUTO-DRAFTED on create. Speaker edits freely. Refresh proposes diffs only. -->

1. **0:00 – 0:20 · Code setup.** Open `s02_baseline_agent.py` in VS Code; highlight the single `gpt-4.1` deployment and one system prompt.
2. **0:20 – 0:45 · Run Carmen.** Run the agent against Carmen's request (plan trip + parking receipt + policy question).
3. **0:45 – 1:10 · Cut to scorecard.** Switch to `s02_scorecard.py` output; call out **quality 0.41 · p50 12.5 s · $0.023/req**.
4. **1:10 – 1:30 · Held end frame.** Hold on the scorecard for the speaker handoff.

## Theme
<!-- AUTHOR — never overwritten by refresh. -->

One frontier model answering every intent looks reasonable in isolation, but it is the strawman the rest of the talk knocks down.

## Takeaway
<!-- AUTHOR — never overwritten by refresh. -->

A single `gpt-4.1` baseline gives us measurable numbers — quality 0.41, p50 12.5 s, $0.023/req — to beat, not a system to ship.

## Narrator beats
<!-- AUTHOR — voiceover lines per beat above. Optional. -->

…

## Scorecard
<!-- AUTO-DRAFTED from referenced eval_results_*.json files. Editable. -->

| Metric | Before | After | Delta |
|---|---|---|---|
| … | … | … | … |
| … | … | … | … |
| … | … | … | … |
| … | … | … | … |


## Recording notes
<!-- AUTHOR — never overwritten. Mic level, OBS scene, fallback clip path. -->

…
