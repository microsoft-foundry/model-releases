# RERUN.md — Demo replay guide for an already-provisioned workshop

> Use this when you've **already run the workshop once** (resources provisioned,
> fine-tune job done, deployments live, datasets generated) and want to
> **regenerate clean scorecards for a recorded demo** without redoing setup.

## Recent toolchain fixes (2026-05-27)

- **Venv guard in `s02_config.py`** — every script that imports config now
  fails fast with a friendly message if the workshop venv isn't active.
  Detects both `source activate` (sets `$VIRTUAL_ENV`) and direct interpreter
  invocation (`sys.prefix != sys.base_prefix`).
- **Generated artifacts now land in `code/generated/`** (gitignored). Per-run
  files are timestamped. `rm -rf code/generated` is the full reset.
- **`s06_expand_ft_data.py` is idempotent.** Old version read+wrote the same
  paths and silently doubled the dataset each run. New version reads optional
  seeds from `policy-ft-seeds-{train,val}.jsonl` and always overwrites outputs.
- **`s06_policy_only_eval.py` added** — direct base-vs-FT comparison on 35
  policy rows with deterministic constraint checking. The clean FT-lift slide.
- **`s99_replay_demo.sh` added** — interactive 6-stage demo replay driver.

> **Is existing data valid?** Yes. The system Python in this devcontainer has
> **no** Azure SDKs installed, so any past run without venv would have hard-failed
> with `ModuleNotFoundError` before producing output. Result files only exist
> if the venv was active. Going forward, the guard makes this impossible to
> get wrong.

---

## TL;DR

```bash
cd workshops/foundry-models-e2e/code
source ../.venv/bin/activate
./s99_replay_demo.sh           # interactive: ENTER to run each stage, s=skip, q=quit
```

That's it. The script flips `USE_FT_POLICY` for you, names result files with a
session timestamp so prior runs aren't clobbered, and resets the boolean back
to `False` at the end for a clean git state.

---

## 1 · Pre-flight checklist

Before re-running, confirm the environment is healthy. **If any of these fail,
fix them before recording.**

| Check | Command | Expected |
|---|---|---|
| Deployments live | `az cognitiveservices account deployment list -g $AZURE_RESOURCE_GROUP -n $FOUNDRY_ACCOUNT_NAME -o table` | 7 rows: `planner-gpt41`, `router-nano`, `mini-vision`, `policy-mini-base`, `policy-mini-ft`, `auto-router`, `text-embedding-3-large` |
| TPM headroom | Portal → Foundry account → Quotas | `planner-gpt41` ≥ **100K TPM** (default 10K throttles batch eval) |
| Auth | `az account show --query name -o tsv` | Your target subscription |
| .env present | `cat code/.env` | `FOUNDRY_PROJECT_ENDPOINT=…` set |
| Venv works | `python -c "import azure.ai.projects, azure.ai.evaluation, openai"` | No errors |
| FT model accessible | `python -c "from s05_multi_model_agent import _ft_client; print(_ft_client.base_url)"` | AOAI endpoint URL |

---

## 2 · Generated files — what's where, why, when to regenerate

### 2.1 — Data files (`sample-data/`)

| File | Created by | Why | Used by | Regenerate when… |
|---|---|---|---|---|
| `travel-policy.md` | hand-authored | Source of truth for policy QA + distillation grounding | s06_expand_ft_data, eval evaluators, FT teacher prompt | **Never** — committed canonical doc. Edit only to add policy sections. |
| `eval-seed.jsonl` (20 rows) | hand-authored | Curated ground-truth across 3 intents (plan_trip / receipt_expense / policy_question). Baseline for synthetic expansion. | s04_generate_synthetic (as seed pool), eval-v1 curated runs | **Never** — committed. Adding rows = manual edit + bump version. |
| `eval-full.jsonl` (173 rows) | `s04_generate_synthetic.py` | 20 seed + 153 LLM-generated rows. The batch eval set used by every `s05_run_eval.py` run. | s05_run_eval.py (all v1/v2/v3 batches) | **Only if** corrupted/missing. See §3 for validity audit — current file is GOOD. |
| `eval-policy-only.jsonl` (35 rows) | manual extract (grep `policy_question` from eval-full + 1 extra) | Isolated policy slice with deterministic `expected_constraints` (must_cite_section, must_mention, must_say). | s06_policy_only_eval.py, full-agent policy-base/policy-ft runs | **Never** unless `eval-full.jsonl` is regenerated AND policy_question count changes. |
| `synthetic-prompts.jsonl` | hand-authored | **Axis definitions** for the synthetic generator (NOT the generated output — that's `eval-full.jsonl`). 2 lines, mostly a comment header. | s04_generate_synthetic.py | **Never** unless adding new diversity axes. |
| `policy-ft-train.jsonl` (91 rows) | `s06_expand_ft_data.py` (distillation) | gpt-4.1 teacher → mini student Q&A pairs grounded in travel-policy.md. 80 % split. | s06_finetune_policy.py upload | **Only** if FT job needs to be repeated AND you want more/different coverage. ⚠️ See §4 — script appends to itself. |
| `policy-ft-val.jsonl` (23 rows) | `s06_expand_ft_data.py` | 20 % validation split. Used by FT service to track loss. | s06_finetune_policy.py upload | Same as train file. |
| `carmen-parking-receipt.html` | hand-authored | HTML invoice used to host the receipt PNG referenced by Carmen trace | Carmen trace `image_url` (Step 1 portal demo) | **Never** |
| `carmen-trace.json` | hand-authored | Single illustrative request showing all 4 intents + vision in one turn | `python s05_multi_model_agent.py` (live demo) | **Never** |

### 2.2 — Result files (`code/generated/`)

> All produced by `s05_run_eval.py` or `s06_policy_only_eval.py` and written
> under `code/generated/` (gitignored). Each contains per-row outputs +
> aggregated quality/cost/latency. **Safe to delete — `rm -rf code/generated`**
> is the full reset; replay regenerates everything.

| File | Stage | Label arg | Notes |
|---|---|---|---|
| `eval_results_v1-curated.json` | Step 5.3 | `v1-curated` | Single-model agent on the 20 seed rows. Fastest sanity check. |
| `eval_results_v1-batch.json` | Step 5.3 | `v1-batch` | Single-model agent on full 173. Frontier baseline. |
| `eval_results_v2-curated.json` | Step 5.4 | `v2-curated` | Multi-model on 20 seed. |
| `eval_results_v2-batch.json` | Step 5.4 | `v2-batch` | Multi-model on 173, no FT. ⚠️ Re-run if TPM was bumped after this. |
| `eval_results_policy-base.json` | Step 6.3 | `policy-base` | Full agent on 35 policy rows, `USE_FT_POLICY=False`. BEFORE number for §6 narrative. |
| `eval_results_policy-ft.json` | Step 6.7 | `policy-ft` | Full agent on 35 policy rows, `USE_FT_POLICY=True`. AFTER number. Diluted lift (~+18 %) because measured end-to-end. |
| `eval_results_v3-final.json` | Step 7 | `v3-final` | Multi-model + FT on full 173. Final architecture scorecard. |
| `eval_results_policy-isolated.json` | Step 6 (added) | n/a (fixed name) | **THE FT slide.** Side-by-side `policy-mini-base` vs `policy-mini-ft` direct on 35 rows. Deterministic check, no LLM judge. |
| `eval_results_model-router.json` | Step 8 (optional) | `model-router` | `auto-router` deployment comparison. |
| `eval_results_policy-ft-v2/v3.json` | older runs | various | Stale artifacts from prior sessions — safe to delete. |

### 2.3 — Side-effects on disk

| Artifact | Source | Cleanup |
|---|---|---|
| `.foundry/datasets/eval-v1.jsonl` | Step 4.5 (manual `cp`) | Keep — it's the versioned dataset reference. |
| `code/generated/eval_results_*.json` | every eval run | `rm -rf code/generated` for a full reset; gitignored. |
| `code/generated/carmen-trace-out.*.json` | replay Stage 1 | Saved by replay; gitignored. |
| `__pycache__/` | Python | Safe to delete. |

---

## 3 · Audit — is `eval-full.jsonl` valid for reuse?

**Verdict: YES, valid as-is. Do NOT regenerate.**

| Check | Result |
|---|---|
| Total rows | 173 ✓ (20 seed + 153 synthetic) |
| Unique inputs | 173 / 173 — no duplicates ✓ |
| Has `expected_keys` | 173 / 173 ✓ |
| Intent distribution | plan_trip 94, receipt_expense 45, policy_question 34 — healthy mix ✓ |
| `image_url` present | **0 / 45 receipt rows** — see ⚠️ below |

### ⚠️ Known scaffolding gap (don't let it surprise you on stage)

- **No receipt row has an `image_url` field.** The 45 `receipt_expense` rows
  are text-only ("I have a $42 dinner receipt from Tokyo…"), so the
  `mini-vision` deployment is never invoked during batch evals.
- Compounding this: `s05_run_eval.py:target()` calls `mod.run(row["input"])`
  and **drops** any `image_url` even if it were present.
- **Implication:** v2/v3 batch quality numbers reflect a 3-model pipeline
  (router + policy + planner), not a 4-model one.
- **Workaround for demo:** Stage 1 of `s99_replay_demo.sh` runs the Carmen
  single trace which DOES carry an image URL — that's where you show vision
  firing live. Call it out explicitly: *"batch evals measure the text path;
  vision is demoed via the Carmen trace."*

### When you WOULD regenerate `eval-full.jsonl`

1. You've materially edited `travel-policy.md` (policy_question rows become stale).
2. You want a larger/smaller eval set.
3. You want to add image-bearing receipt rows (manual edit, not generator).
4. The file is missing/corrupt.

To regenerate:
```bash
python s04_generate_synthetic.py
# overwrites sample-data/eval-full.jsonl — review before recording
```

---

## 4 · Audit — FT dataset & distillation framing

**Verdict: This IS textbook knowledge distillation. Data is valid. Do NOT
re-run `s06_expand_ft_data.py` without resetting first (see ⚠️).**

### 4.1 What's actually happening

`s06_expand_ft_data.py` documents the pipeline explicitly:

```
TEACHER  →  gpt-4.1   (planner-gpt41)
STUDENT  →  gpt-4.1-mini  (→ policy-mini-ft)
```

The teacher reads `travel-policy.md` and generates Q&A pairs across **12
policy axes** (booking windows, budget caps, ground transport, parking,
per-diem, connectivity, non-reimbursables, hotels, flights, entertainment,
receipts, adversarial traps). Each generated answer cites the relevant
section. The student is fine-tuned to imitate the teacher's section-citing,
concise style.

This is **standard knowledge distillation** — the student learns the
teacher's reasoning at a fraction of inference cost.

### 4.2 Current dataset

| File | Rows | Composition |
|---|---|---|
| `policy-ft-train.jsonl` | 91 | mix of hand-authored seeds + teacher-generated pairs |
| `policy-ft-val.jsonl` | 23 | 20 % validation split (shuffled) |
| **Total** | **114** | sufficient for 3-epoch supervised FT on gpt-4.1-mini |

The 23 508 trained-tokens count from your FT job is consistent with
114 chat-format rows × 3 epochs at this row length.

### 4.3 ⚠️ Bug to be aware of: the expansion script is non-idempotent

`s06_expand_ft_data.py` has identical input and output paths:

```python
TRAIN_IN  = "../sample-data/policy-ft-train.jsonl"
TRAIN_OUT = "../sample-data/policy-ft-train.jsonl"   # same file
```

**Each run loads existing rows + appends ~84 new ones + overwrites.**
Running twice ⇒ ~200 rows. Running thrice ⇒ ~290. Token count and training
time grow each run. Workshop authors should fix this; for demo purposes:

- **Do NOT re-run `s06_expand_ft_data.py` casually.** Current 91/23 split
  is already the result of (at least one) prior expansion.
- If you must regenerate, first restore seeds from git:
  ```bash
  git checkout sample-data/policy-ft-train.jsonl sample-data/policy-ft-val.jsonl
  python s06_expand_ft_data.py
  ```

### 4.4 When you WOULD re-run the FT job

You almost certainly don't need to. The `policy-mini-ft` deployment is
already serving the trained model. Re-run only if:

1. You've materially changed `travel-policy.md` (training data is stale).
2. You want to demo the **FT submission flow live** (job takes 30 min – 2 h —
   not realistic during a recorded demo).
3. You deleted the deployment.

If you do re-run: `python s06_finetune_policy.py`. Then portal → Fine-tuning
→ Deploy as `policy-mini-ft` (DeveloperTier). See workshop Step 6 for the
full click-path.

---

## 5 · Stage-by-stage runtime budget

| Stage | Script | What runs | Expected wall-clock | Cost |
|---|---|---|---|---|
| 1 | `s05_multi_model_agent.py` | 1 Carmen trace, all 4 models | ~15 s | < $0.01 |
| 2 | `s05_run_eval.py v1-batch` | 173 × planner-gpt41 + judge | ~5 min @ 100K TPM | ~$1 |
| 3 | `s05_run_eval.py v2-batch` (FT=False) | 173 × (router + policy-base + planner) + judge | ~5 min | ~$0.40 |
| 4 | `s05_run_eval.py v3-final` (FT=True) | 173 × (router + policy-FT + planner) + judge | ~5 min | ~$0.40 |
| 5 | `s06_policy_only_eval.py` | 35 × policy-base + 35 × policy-FT (no judge) | ~3 min | < $0.10 |
| **Total** | | | **~20 min** | **~$2** |

---

## 6 · Running stages in parallel terminals

If you want to crunch the numbers faster (e.g. while iterating on slides),
each stage in `s99_replay_demo.sh` is **independent**, with one ordering
constraint: **Stage 3 needs `USE_FT_POLICY=False`, Stage 4 needs `True`**.

### Parallelization-safe pattern

```bash
# Terminal A (long): kick off v1 batch — single model, doesn't touch FT
python s05_run_eval.py --agent s02_baseline_agent \
                       --eval ../sample-data/eval-full.jsonl --label v1-A

# Terminal B (long): isolated FT comparison — uses both policy models directly,
# does NOT read USE_FT_POLICY. Safe to run anytime.
python s06_policy_only_eval.py

# Terminal C (sequential): the boolean-flip pair must be serialized
sed -i 's/^USE_FT_POLICY = .*/USE_FT_POLICY = False/' s05_multi_model_agent.py
python s05_run_eval.py --agent s05_multi_model_agent \
                       --eval ../sample-data/eval-full.jsonl --label v2-A
sed -i 's/^USE_FT_POLICY = .*/USE_FT_POLICY = True/' s05_multi_model_agent.py
python s05_run_eval.py --agent s05_multi_model_agent \
                       --eval ../sample-data/eval-full.jsonl --label v3-A
sed -i 's/^USE_FT_POLICY = .*/USE_FT_POLICY = False/' s05_multi_model_agent.py
```

Terminals A and B can run alongside C. **Do NOT run two `s05_run_eval.py`
multi-model invocations in parallel** — they'd race on the boolean.

### TPM caveat

All four model deployments share the regional quota. Running 3 batch evals
in parallel can push planner-gpt41 past 100K TPM and trigger throttling
(visible as `429`s in eval output, latency spikes, possibly evaluator
failures). Safer to stagger: start A, wait 1 min, start B and C.

---

## 7 · What to record for the demo

For a polished recording, capture these on screen in this order:

1. **Carmen trace** (Stage 1) — single request, all 4 models in one frame.
2. **v1 batch scorecard** (Stage 2) — frontier baseline, "expensive + slow".
3. **`git diff s05_multi_model_agent.py`** before Stage 4 — show the
   one-line `USE_FT_POLICY` flip is the *only* code difference between v2
   and v3. This is the workshop's punch line.
4. **v3 batch scorecard** (Stage 4) — cost down ~10×, latency down.
5. **`eval_results_policy-isolated.json`** scorecards (Stage 5) — the clean
   FT lift slide (base vs ft on identical 35 rows, deterministic checker).
6. **Portal screenshot** — Foundry portal → Fine-tuning tab → your job →
   training loss curve. The slide's emotional close.

---

## 8 · "Something broke during my last run" — common rescues

| Symptom | Diagnosis | Fix |
|---|---|---|
| `429 Too Many Requests` | TPM throttling | Portal → Quotas → bump `planner-gpt41` to ≥ 100K TPM. Wait 2 min for propagation. Re-run failed stage only. |
| `DeploymentNotFound: policy-mini-ft` | FT deployment got deleted | Portal → Fine-tuning → your job → Deploy as `policy-mini-ft` (DeveloperTier). 1-2 min. |
| `InvalidApiVersionParameter` on `az cognitiveservices …` | CLI too new for ARM | Use portal for deployment ops, or `az extension update --name cognitiveservices`. |
| All judge scores look like 0.6 | `JudgeEvaluator` exception fallback fired | Check planner-gpt41 quota/health. The eval continues but quality is meaningless. |
| Suspiciously low v2 quality | TPM throttling during run | Re-run v2 only with `--label v2-rerun-${TS}`. |
| FT scorecard shows 0.39 not 0.94 | End-to-end dilution (known) | Use `s06_policy_only_eval.py` instead — that's the isolated lift. |
| Vision branch never fires in batch | Known scaffolding gap (eval driver drops `image_url`) | Acknowledge in narration; show vision via Stage 1 Carmen trace. |

---

## 9 · Reset to "fresh-from-git" state

Use this if a demo went off-rails and you want a clean re-record:

```bash
cd workshops/foundry-models-e2e

# 1. Restore source code (resets USE_FT_POLICY=False if you edited it)
git checkout code/s05_multi_model_agent.py

# 2. Wipe all generated artifacts (gitignored; deployments + datasets remain intact)
rm -rf code/generated

# 3. Re-run replay
cd code && source ../.venv/bin/activate
./s99_replay_demo.sh
```

**You do NOT need to:**
- Re-provision infra (`s00_setup.sh`).
- Re-generate the synthetic eval set (`s04_generate_synthetic.py`).
- Re-expand FT data (`s06_expand_ft_data.py`).
- Re-train the FT model (`s06_finetune_policy.py`).
- Re-deploy `policy-mini-ft`.

All of those produce assets that survive a re-record cleanly.
