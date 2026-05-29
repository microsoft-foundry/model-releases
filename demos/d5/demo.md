---
id: d5
title: D5 — Distillation, fine-tune, and after-scorecard
workshop: foundry-models-e2e
session_context: "BRK230 · Stanza 4 — OPTIMIZE"
target_duration: "3:30"
theme: "Once the evaluator points at a specific weak slice, fine-tuning `gpt-4.1-mini` with teacher-expanded data fixes the regression without giving up the cost and latency wins."
takeaway: "A targeted FT (24 → 84 pairs, one-line swap) lifts policy quality 0.47 → 0.68 while holding the v1 → v3 trajectory at **+12% quality · −74% cost · −48% latency**."
mode_hint: mixed
held_end_frame: "Full v1 → v3 scorecard with **quality +12% · cost −74% · latency −48%** for the speaker handoff."
source_steps:
  - workshops/foundry-models-e2e/06-finetune.md
  - workshops/foundry-models-e2e/code/s06_expand_ft_data.py
  - workshops/foundry-models-e2e/code/s06_finetune_policy.py
  - workshops/foundry-models-e2e/sample-data/policy-ft-train.jsonl
generated_at: 2026-05-29
generated_by: add-demo@1
---

# d5 · D5 — Distillation, fine-tune, and after-scorecard

## Header card
<!-- AUTO — regenerated on refresh. Do not edit by hand. -->

| Field | Value |
|---|---|
| Duration | 3:30 |
| Theme | Once the evaluator points at a specific weak slice, fine-tuning `gpt-4.1-mini` with teacher-expanded data fixes the regression without giving up the cost and latency wins. |
| Takeaway | A targeted FT (24 → 84 pairs, one-line swap) lifts policy quality 0.47 → 0.68 while holding the v1 → v3 trajectory at **+12% quality · −74% cost · −48% latency**. |
| Mode hint | mixed |
| Held end frame | Full v1 → v3 scorecard with **quality +12% · cost −74% · latency −48%** for the speaker handoff. |

## Source steps
<!-- AUTO — regenerated on refresh. -->

- [`workshops/foundry-models-e2e/06-finetune.md`](../../workshops/foundry-models-e2e/06-finetune.md)
- [`workshops/foundry-models-e2e/code/s06_expand_ft_data.py`](../../workshops/foundry-models-e2e/code/s06_expand_ft_data.py)
- [`workshops/foundry-models-e2e/code/s06_finetune_policy.py`](../../workshops/foundry-models-e2e/code/s06_finetune_policy.py)
- [`workshops/foundry-models-e2e/sample-data/policy-ft-train.jsonl`](../../workshops/foundry-models-e2e/sample-data/policy-ft-train.jsonl)

## Steps to record
<!-- AUTO-DRAFTED on create. Speaker edits freely. Refresh proposes diffs only. -->

1. **0:00 – 0:35 · Distill.** Show `policy-ft-train.jsonl` (24 seed pairs); run `s06_expand_ft_data.py` to fan out via the teacher (24 → 84 pairs across 12 axes).
2. **0:35 – 1:15 · FT job.** Foundry Portal → Fine-tuning job for `gpt-4.1-mini` (suffix `wwi-policy-v1`); show status = succeeded and the deployed FT model card.
3. **1:15 – 1:45 · One-line swap.** Back in code, flip `USE_FT_POLICY = True` — one-line swap into the multi-model agent.
4. **1:45 – 2:35 · Re-run eval.** Re-run the policy eval; show the new scorecard side-by-side: **policy quality 0.47 → 0.68**, cost held, latency held.
5. **2:35 – 3:30 · v1 → v3 (held).** End on the full v1 → v3 scorecard (**quality +12% · cost −74% · latency −48%**) to hand back to the speaker.

## Theme
<!-- AUTHOR — never overwritten by refresh. -->

Once the evaluator points at a specific weak slice, fine-tuning `gpt-4.1-mini` with teacher-expanded data fixes the regression without giving up the cost and latency wins.

## Takeaway
<!-- AUTHOR — never overwritten by refresh. -->

A targeted FT (24 → 84 pairs, one-line swap) lifts policy quality 0.47 → 0.68 while holding the v1 → v3 trajectory at **+12% quality · −74% cost · −48% latency**.

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
