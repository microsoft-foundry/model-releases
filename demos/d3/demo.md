---
id: d3
title: D3 — Multi-model decomposition
workshop: foundry-models-e2e
session_context: "BRK230 · Stanza 2 — SELECT"
target_duration: "2:30"
theme: "Decomposing Carmen's request across four named-by-job deployments shrinks cost and latency immediately — and reveals exactly where quality plateaus."
takeaway: "A nano-router + policy-mini + planner-gpt-4.1 + vision-mini split beats the single-model baseline on cost and latency, and tells you where to invest next — the policy slice at 0.47."
mode_hint: mixed
held_end_frame: "Cliffhanger card reading **'the policy slice is where this stalls'** over the updated scorecard."
source_steps:
  - workshops/foundry-models-e2e/03-model-selection.md
  - workshops/foundry-models-e2e/code/s03_router.py
  - workshops/foundry-models-e2e/code/s05_multi_model_agent.py
generated_at: 2026-05-29
generated_by: add-demo@1
---

# d3 · D3 — Multi-model decomposition

## Header card
<!-- AUTO — regenerated on refresh. Do not edit by hand. -->

| Field | Value |
|---|---|
| Duration | 2:30 |
| Theme | Decomposing Carmen's request across four named-by-job deployments shrinks cost and latency immediately — and reveals exactly where quality plateaus. |
| Takeaway | A nano-router + policy-mini + planner-gpt-4.1 + vision-mini split beats the single-model baseline on cost and latency, and tells you where to invest next — the policy slice at 0.47. |
| Mode hint | mixed |
| Held end frame | Cliffhanger card reading **'the policy slice is where this stalls'** over the updated scorecard. |

## Source steps
<!-- AUTO — regenerated on refresh. -->

- [`workshops/foundry-models-e2e/03-model-selection.md`](../../workshops/foundry-models-e2e/03-model-selection.md)
- [`workshops/foundry-models-e2e/code/s03_router.py`](../../workshops/foundry-models-e2e/code/s03_router.py)
- [`workshops/foundry-models-e2e/code/s05_multi_model_agent.py`](../../workshops/foundry-models-e2e/code/s05_multi_model_agent.py)

## Steps to record
<!-- AUTO-DRAFTED on create. Speaker edits freely. Refresh proposes diffs only. -->

1. **0:00 – 0:30 · Four deployments.** Open `s05_multi_model_agent.py`; highlight the four named-by-job deployments (`router-nano`, `policy-mini-base`, `vision-mini`, `planner-gpt41`).
2. **0:30 – 1:10 · Same prompt, new shape.** Run the same Carmen prompt; show the trace fan-out (router → policy + planner).
3. **1:10 – 1:50 · Updated scorecard.** Cut to the updated scorecard — cost down, latency down, **quality plateau on the policy slice at 0.47**.
4. **1:50 – 2:30 · Cliffhanger (held).** Hold on the "the policy slice is where this stalls" card for the speaker handoff into Stanza 3.

## Theme
<!-- AUTHOR — never overwritten by refresh. -->

Decomposing Carmen's request across four named-by-job deployments shrinks cost and latency immediately — and reveals exactly where quality plateaus.

## Takeaway
<!-- AUTHOR — never overwritten by refresh. -->

A nano-router + policy-mini + planner-gpt-4.1 + vision-mini split beats the single-model baseline on cost and latency, and tells you where to invest next — the policy slice at 0.47.

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
