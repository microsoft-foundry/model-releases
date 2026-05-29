# s06_expand_ft_data.py — expand FT training set via knowledge distillation.
# =============================================================================
# DISTILLATION PIPELINE
#
#   TEACHER  →  gpt-4.1 (planner-gpt41)
#   STUDENT  →  gpt-4.1-mini (policy-mini-ft)
#
# The teacher model reads travel-policy.md and generates grounded Q&A answers
# across 12 policy axes.  Those model-generated answers become the training
# labels for the student fine-tune.  The student learns the *teacher's
# reasoning style* — concise, section-cited, correct on edge cases — at a
# fraction of the inference cost.
#
# This is the standard knowledge distillation pattern:
#   1. Teacher generates high-quality responses on a task.
#   2. Student is fine-tuned on teacher outputs (not just human labels).
#   3. At inference time, only the student runs — frontier cost eliminated.
#
# Hand-authored anchor rows (kept in policy-ft-seeds-{train,val}.jsonl, if
# present) are merged with the ~80 teacher-generated rows so the student sees
# both ground-truth and broad-coverage examples.
#
# IDEMPOTENCY (fixed 2026-05-27)
# Earlier versions used the same path for input and output, causing each run
# to load the previous run's output and APPEND, silently doubling the dataset.
# Now: SEEDS are READ-ONLY inputs at a distinct path; TRAIN_OUT/VAL_OUT are
# always overwritten fresh. Safe to re-run any number of times.
#
# If you want to lock in your current train/val as the canonical seed set
# before this fix takes effect, run once:
#   cp ../sample-data/policy-ft-train.jsonl ../sample-data/policy-ft-seeds-train.jsonl
#   cp ../sample-data/policy-ft-val.jsonl   ../sample-data/policy-ft-seeds-val.jsonl
# Otherwise the script will generate the dataset purely from AXES (no anchors).
# =============================================================================
import json
import os
import random
import re
from pathlib import Path

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from s02_config import PROJECT_ENDPOINT, DEPLOY_PLANNER

POLICY_PATH   = "../sample-data/travel-policy.md"
# READ-ONLY seed inputs (optional). Override via env vars for experiments.
SEED_TRAIN    = os.environ.get("FT_SEED_TRAIN", "../sample-data/policy-ft-seeds-train.jsonl")
SEED_VAL      = os.environ.get("FT_SEED_VAL",   "../sample-data/policy-ft-seeds-val.jsonl")
# Outputs — always overwritten fresh on each run.
TRAIN_OUT     = "../sample-data/policy-ft-train.jsonl"
VAL_OUT       = "../sample-data/policy-ft-val.jsonl"
SYSTEM_PROMPT = "You answer WWI policy questions. Concise."

# Safety guard: refuse to clobber seed files if someone misconfigures paths.
assert os.path.realpath(SEED_TRAIN) != os.path.realpath(TRAIN_OUT), \
    f"SEED_TRAIN ({SEED_TRAIN}) must differ from TRAIN_OUT ({TRAIN_OUT}) — outputs are overwritten each run."
assert os.path.realpath(SEED_VAL)   != os.path.realpath(VAL_OUT), \
    f"SEED_VAL ({SEED_VAL}) must differ from VAL_OUT ({VAL_OUT}) — outputs are overwritten each run."

AXES = [
    ("Section 2 — booking windows",        "domestic vs international advance booking, emergency exceptions"),
    ("Section 3 — budget caps",            "domestic 1-2 night, domestic 3+ night, international 1-3 night, international 4+ night, approval thresholds"),
    ("Section 4.1 — ground transport",     "taxi, rideshare, rental car class, luxury approval"),
    ("Section 4.2 — parking",              "airport parking daily cap, receipt deadline, valet rules"),
    ("Section 4.3 — meals per-diem",       "domestic vs international rates, alcohol rules"),
    ("Section 4.4 — connectivity",         "in-flight Wi-Fi threshold, hotel Wi-Fi rules"),
    ("Section 5 — non-reimbursable",       "minibar, spa, independent travel insurance, pet boarding, childcare, cash upgrades"),
    ("Section 6 — hotels",                 "Tier 1/2/3 nightly caps, approval thresholds, city examples"),
    ("Section 7 — flights",                "economy/premium-economy/business/first class rules, carrier preference, schedule constraints"),
    ("Section 8 — client entertainment",   "per-person cap, alcohol in this context, itemized receipts, attendee list"),
    ("Section 9 — receipts",               "itemization threshold, 30-day vs 60-day submission, mobile photos"),
    ("adversarial / policy traps",         "questions that sound legitimate but are disallowed: first class, spa, cash upgrade, expired receipt, over-budget without approval"),
]

GENERATE_PROMPT = """You are writing fine-tuning data for a travel policy Q&A model.
Policy document:
---
{policy}
---

Existing examples (do NOT duplicate):
{existing}

Generate {n} NEW question-answer pairs covering: {axis_desc}.
Rules:
- Every answer must cite the exact section number (e.g. "Section 4.2").
- Answers should be 1-3 sentences max — concise and direct.
- Include a mix of straightforward and edge-case questions.
- Questions must be phrased as an employee would ask them.
- Do NOT add any question already in the existing list.

Return JSON: {{"pairs": [{{"q": "...", "a": "..."}}]}}"""


def load_jsonl(path: str) -> list[dict]:
    p = Path(path)
    if not p.exists():
        return []   # seeds are optional — empty pool is fine
    return [json.loads(line) for line in p.read_text().splitlines() if line.strip()]


def to_row(q: str, a: str) -> dict:
    return {"messages": [
        {"role": "system",    "content": SYSTEM_PROMPT},
        {"role": "user",      "content": q},
        {"role": "assistant", "content": a},
    ]}


def dedup(rows: list[dict], seen_qs: set) -> list[dict]:
    out = []
    for r in rows:
        q = r["messages"][1]["content"].strip().lower()
        if q not in seen_qs:
            seen_qs.add(q)
            out.append(r)
    return out


def main():
    policy = Path(POLICY_PATH).read_text()
    seed_rows = load_jsonl(SEED_TRAIN) + load_jsonl(SEED_VAL)
    if seed_rows:
        print(f"Loaded {len(seed_rows)} hand-authored seed rows from "
              f"{Path(SEED_TRAIN).name} + {Path(SEED_VAL).name}")
    else:
        print("No seed files found — generating dataset purely from AXES. "
              "(Place anchor rows at policy-ft-seeds-{train,val}.jsonl to include them.)")
    seen_qs = {r["messages"][1]["content"].strip().lower() for r in seed_rows}
    existing_snippet = "\n".join(
        f"Q: {r['messages'][1]['content']}" for r in seed_rows)

    project = AIProjectClient(endpoint=PROJECT_ENDPOINT,
                              credential=DefaultAzureCredential())
    client = project.get_openai_client()

    new_rows: list[dict] = []
    n_per_axis = 7  # 12 axes × 7 = 84 new pairs target

    for axis_name, axis_desc in AXES:
        print(f"  generating: {axis_name} ...", flush=True)
        prompt = GENERATE_PROMPT.format(
            policy=policy,
            existing=existing_snippet,
            n=n_per_axis,
            axis_desc=f"{axis_name}: {axis_desc}",
        )
        try:
            resp = client.responses.create(
                model=DEPLOY_PLANNER,
                temperature=0.7,
                instructions="You are a dataset author. Return only valid JSON.",
                input=prompt + "\nReturn JSON only.",
                text={"format": {"type": "json_object"}},
            )
            data = json.loads(resp.output_text)
            pairs = data.get("pairs", [])
            batch = [to_row(p["q"], p["a"]) for p in pairs
                     if p.get("q") and p.get("a")]
            fresh = dedup(batch, seen_qs)
            new_rows.extend(fresh)
            # keep existing_snippet updated so later axes avoid near-duplicates
            existing_snippet += "\n" + "\n".join(f"Q: {r['messages'][1]['content']}"
                                                  for r in fresh)
            print(f"    +{len(fresh)} rows (total new so far: {len(new_rows)})")
        except Exception as e:
            print(f"    ERROR on {axis_name}: {e}")

    # Merge seeds + freshly-generated, shuffle, 80/20 split.
    # NOTE: TRAIN_OUT/VAL_OUT are OVERWRITTEN (never appended) so the script
    # is safe to re-run any number of times without compounding the dataset.
    all_rows = seed_rows + new_rows
    random.seed(42)
    random.shuffle(all_rows)

    split = int(len(all_rows) * 0.8)
    train, val = all_rows[:split], all_rows[split:]

    Path(TRAIN_OUT).write_text("\n".join(json.dumps(r) for r in train) + "\n")
    Path(VAL_OUT).write_text(  "\n".join(json.dumps(r) for r in val)   + "\n")

    print(f"\nDone. {len(train)} train / {len(val)} val "
          f"({len(all_rows)} total = {len(seed_rows)} seed + {len(new_rows)} generated)")
    print(f"Wrote: {TRAIN_OUT}\n       {VAL_OUT}")


if __name__ == "__main__":
    main()
