---
id: d4
title: D4 — Adaptive evaluation with a rubric (LLM-as-judge)
workshop: foundry-models-e2e
session_context: "BRK230 · Stanza 3 — EVALUATE"
target_duration: "3:00"
theme: "Moving from 'looks right' to a rubric-judged scorecard turns a vague quality plateau into a specific list of failures you can act on."
takeaway: "A schema + rubric evaluator surfaces the failing axes (geography, language, policy_trap) and tells you targeted optimization — not a bigger model — is what's needed."
mode_hint: mixed
held_end_frame: "Takeaway slide reading **0.47 average · regression on edge cases → targeted optimization, not a bigger model.**"
source_steps:
  - workshops/foundry-models-e2e/05-evaluations.md
  - workshops/foundry-models-e2e/code/s05_run_eval.py
  - workshops/foundry-models-e2e/sample-data/eval-policy-only.jsonl
generated_at: 2026-05-29
generated_by: add-demo@1
---

# d4 · D4 — Adaptive evaluation with a rubric (LLM-as-judge)

## Header card
<!-- AUTO — regenerated on refresh. Do not edit by hand. -->

| Field | Value |
|---|---|
| Duration | 3:00 |
| Theme | Moving from 'looks right' to a rubric-judged scorecard turns a vague quality plateau into a specific list of failures you can act on. |
| Takeaway | A schema + rubric evaluator surfaces the failing axes (geography, language, policy_trap) and tells you targeted optimization — not a bigger model — is what's needed. |
| Mode hint | mixed |
| Held end frame | Takeaway slide reading **0.47 average · regression on edge cases → targeted optimization, not a bigger model.** |

## Source steps
<!-- AUTO — regenerated on refresh. -->

- [`workshops/foundry-models-e2e/05-evaluations.md`](../../workshops/foundry-models-e2e/05-evaluations.md)
- [`workshops/foundry-models-e2e/code/s05_run_eval.py`](../../workshops/foundry-models-e2e/code/s05_run_eval.py)
- [`workshops/foundry-models-e2e/sample-data/eval-policy-only.jsonl`](../../workshops/foundry-models-e2e/sample-data/eval-policy-only.jsonl)

## Steps to record
<!-- AUTO-DRAFTED on create. Speaker edits freely. Refresh proposes diffs only. -->

1. **0:00 – 0:25 · Dataset.** Show the eval dataset in VS Code (35 policy rows; intent + expected constraints + `axis_varied`).
2. **0:25 – 1:05 · Run the judges.** Trigger the eval run in Foundry Portal → Evaluations for `policy-mini-base`; let the schema + rubric judges complete.
3. **1:05 – 1:45 · Cluster failures.** Open results; sort by `judge.judge_score`; cluster failures by `axis_varied` (geography, language, policy_trap).
4. **1:45 – 2:25 · One row deep.** Drill into one failing row (e.g. `seed-007` Tokyo per-diem); show the wrong number and the judge's reason.
5. **2:25 – 3:00 · Takeaway (held).** End on the takeaway slide: **0.47 average · regression on edge cases → targeted optimization, not a bigger model.**

## Theme
<!-- AUTHOR — never overwritten by refresh. -->

Moving from 'looks right' to a rubric-judged scorecard turns a vague quality plateau into a specific list of failures you can act on.

## Takeaway
<!-- AUTHOR — never overwritten by refresh. -->

A schema + rubric evaluator surfaces the failing axes (geography, language, policy_trap) and tells you targeted optimization — not a bigger model — is what's needed.

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
