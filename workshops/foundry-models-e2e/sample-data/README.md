# Sample Data — WWI Concierge Workshop

This folder is the **canonical dataset** for the `foundry-models-e2e` workshop. Every demo, every scorecard, and every fine-tune job in steps 02 → 08 reads from these files. Treat them as the workshop's source of truth: change a row here and the downstream eval numbers move.

> **World Wide Importers (WWI)** is the fictitious enterprise used throughout the workshop. The application we're building is **WWI Concierge**, an internal AI travel assistant. All content in this folder is synthetic and exists solely to drive the demos.

---

## Why this dataset is shaped the way it is

The whole workshop is built around the claim that **one frontier model behind one prompt is the wrong answer for a real workload**. To prove that empirically we need a dataset that forces the agent to do three very different kinds of work in a single user request:

| Workload intent | What it stresses | Right-sized model class | Where it shows up in this folder |
|---|---|---|---|
| **Multimodal extraction** | OCR + spatial reasoning over a real-world artifact (a parking receipt). Vision capability is required. | A mini multimodal model (e.g. `gpt-4.1-mini` vision) | [`carmen-parking-receipt.html`](carmen-parking-receipt.html), the receipt rows in [`eval-full.jsonl`](eval-full.jsonl) |
| **Lightweight policy Q&A** | Short, factual, citation-heavy answers grounded in a finite policy document. Latency and cost matter; reasoning depth does not. | A nano / mini text model, then a small fine-tune on top | [`travel-policy.md`](travel-policy.md), [`wwi-travel-policy.html`](wwi-travel-policy.html), [`eval-policy-only.jsonl`](eval-policy-only.jsonl), [`policy-ft-train.jsonl`](policy-ft-train.jsonl), [`policy-ft-val.jsonl`](policy-ft-val.jsonl) |
| **Deep planning & constraint solving** | Multi-step trip plans that must satisfy budget caps, hotel tiers, booking-window rules, and class-of-service rules simultaneously. | A frontier reasoning model (e.g. `gpt-4.1`) | The `plan_trip` rows in [`eval-seed.jsonl`](eval-seed.jsonl) and [`eval-full.jsonl`](eval-full.jsonl), Carmen's request in [`carmen-trace.json`](carmen-trace.json) |

This is the *multi-model story* the demo lands. The dataset is intentionally constructed so a single-frontier-model solution wins on quality by a hair but loses badly on cost and latency, while a **router → vision · policy · planner** decomposition wins on all three axes.

---

## File index

| File | Purpose | Read by |
|---|---|---|
| [`travel-policy.md`](travel-policy.md) | The 10-section WWI Travel & Expense policy document. The grounding doc for every policy-Q&A row and the Policy Adherence evaluator below. | Steps 02 (prompt context), 04 (synth generation), 05 (eval grader), 06 (fine-tune system prompt context) |
| [`wwi-travel-policy.html`](wwi-travel-policy.html) | A polished single-page visual of the policy handbook. Render in a browser, then screenshot or export to PNG for slides and demo splash frames. Pairs with `carmen-parking-receipt.html` as the workshop's two hero visuals. | Slides, recordings, social cards |
| [`carmen-parking-receipt.html`](carmen-parking-receipt.html) | A photorealistic SAN airport parking receipt. Render to PNG and feed the image into the vision branch of the multi-model agent. Embeds the $32/day overage that triggers the policy-violation flag. | Step 02 vision tests, Step 07 multi-model agent, recordings |
| [`carmen-trace.json`](carmen-trace.json) | Carmen's seed user message — the canonical opening request used in every recorded demo. Includes a hook for an `image_url` so you can wire in the receipt PNG when ready to demo vision. | All demos (the "cold open"), Step 02 baseline trace |
| [`eval-seed.jsonl`](eval-seed.jsonl) | ~20 hand-authored evaluation rows covering all three intents (`plan_trip`, `policy_question`, `receipt_expense`). The starting point that Step 04's synthetic generator expands. | Step 02 (smoke), Step 04 (seed for synth) |
| [`synthetic-prompts.jsonl`](synthetic-prompts.jsonl) | Axes + starter prompts the Step 04 generator uses to produce ~180 additional rows balanced across intents, complexity, and policy axes. | Step 04 |
| [`eval-full.jsonl`](eval-full.jsonl) | The full 170-row evaluation set: seed rows + synthetic rows, curated. This is what every scorecard in steps 05, 06, 07 is measured against. | Steps 05, 06, 07 |
| [`eval-policy-only.jsonl`](eval-policy-only.jsonl) | The policy-only slice (`intent == "policy_question"`) extracted from `eval-full.jsonl`. Used to evaluate the small/fine-tuned policy model in isolation, and to compute the **Policy Adherence** metric defined below. | Steps 05, 06 (FT evals) |
| [`policy-ft-train.jsonl`](policy-ft-train.jsonl) | Chat-format fine-tuning training set for the policy model. ~50 high-quality Q&A pairs grounded in `travel-policy.md`. System prompt: *"You answer WWI policy questions. Concise."* | Step 06 fine-tune job |
| [`policy-ft-val.jsonl`](policy-ft-val.jsonl) | Validation split for the same fine-tune. Held out from training; used by Foundry's fine-tune job for loss reporting and by Step 06 for the FT-vs-base scorecard. | Step 06 fine-tune job, Step 06 eval |
| [`README.md`](README.md) | This file. | Humans |

---

## Quick conventions

- **Format:** JSONL files are one JSON object per line, UTF-8, no trailing comma, no BOM.
- **Row shape (eval files):** every row has `id`, `intent`, `input`, `expected_keys`, and `expected_constraints`. The constraints object is what graders check against.
- **Row shape (FT files):** OpenAI / Foundry SFT chat format — `{"messages": [{"role": "system", ...}, {"role": "user", ...}, {"role": "assistant", ...}]}`.
- **Image hand-off:** the demos render `carmen-parking-receipt.html` to a PNG (`assets/00-receipt.png`) and pass that path/URL as `image_url` in `carmen-trace.json` when the vision branch is wired up.
- **Don't shrink the policy doc.** It is deliberately small enough to fit in a system prompt but large enough that nano models drop citations. That gap is the whole point of the fine-tune demo in Step 06.

---

## Rendering the visual assets

The two HTML files are designed to be opened in a browser, then captured as PNG for slides and the recorded demo splash frames.

```bash
# from repo root, with a headless Chromium available:
npx --yes playwright install chromium >/dev/null 2>&1 || true

# Receipt — portrait card, ~ 420×620
npx --yes playwright screenshot \
  workshops/foundry-models-e2e/sample-data/carmen-parking-receipt.html \
  workshops/foundry-models-e2e/assets/00-receipt.png \
  --viewport-size=480,720 --full-page

# Policy handbook — letter-ish portrait, ~ 860×1180
npx --yes playwright screenshot \
  workshops/foundry-models-e2e/sample-data/wwi-travel-policy.html \
  workshops/foundry-models-e2e/assets/00-policy.png \
  --viewport-size=860,1180 --full-page
```

(Any headless-Chromium tool works — `playwright`, `puppeteer`, `chromium --headless --screenshot`, even a VS Code "Capture screenshot" of the rendered tab.)

---

## Evaluating policy adherence

Several models in this workshop are asked the same kind of question — *"Can I expense X?" · "What's the cap on Y?" · "What approval do I need for Z?"* — and the only thing that distinguishes a good answer from a confidently-wrong one is whether the answer **stays inside the four corners of [`travel-policy.md`](travel-policy.md)**.

We measure that with a single custom metric called **Policy Adherence**. It is the eval rubric we'll wire into the Foundry custom evaluator in Step 05 and re-use to score the fine-tune in Step 06.

### The rubric — at a glance

Policy Adherence is the weighted sum of five sub-scores, each scored 0 / 1 / 2:

| # | Sub-score | What it asks | Weight |
|---|---|---|---|
| **A** | **Grounding** | Is every factual claim in the answer traceable to a specific section of the policy document? | 0.30 |
| **B** | **Citation correctness** | When a section is cited (`§ 4.2`, `Section 7.1`, etc.), does that section actually contain the claim? | 0.20 |
| **C** | **Value & threshold accuracy** | Are dollar amounts, hour thresholds, day windows, and percentages quoted exactly as written in the policy? | 0.20 |
| **D** | **Approval-path correctness** | If the question turns on who must approve an exception, does the answer name the right role (Manager / VP / CFO / Travel-Ops) and the right trigger? | 0.15 |
| **E** | **Scope discipline** | Does the answer refuse to invent rules the policy does not state, and decline gracefully when out of scope? | 0.15 |

Total Policy Adherence score is `0.30·A + 0.20·B + 0.20·C + 0.15·D + 0.15·E`, normalized to `0.0 – 1.0` (divide by 2). A score of **≥ 0.85** is "production-ready"; **0.70 – 0.84** is "ship with caveats"; **< 0.70** is a regression.

### The evaluator prompt

Paste the prompt below into a Foundry custom evaluator (LLM-as-judge) configured against a strong judge model (e.g. `gpt-4.1`). The placeholders `{{policy_document}}`, `{{user_question}}`, and `{{model_answer}}` are filled in by the evaluator runtime for each row in [`eval-policy-only.jsonl`](eval-policy-only.jsonl).

````text
SYSTEM:
You are a strict, evidence-bound evaluator for the World Wide Importers (WWI)
Travel & Expense Policy assistant. Your job is to score one model answer at a
time against a fixed policy document, on a single metric: POLICY ADHERENCE.

POLICY ADHERENCE is the degree to which the model answer stays inside the four
corners of the policy document — no invented rules, no misquoted thresholds,
no wrong approval paths, no confident hallucinations. It is NOT a measure of
helpfulness, tone, or completeness beyond what the policy itself supports.

You will score five sub-axes from 0 to 2 (integers only), then return a single
JSON object. You MUST cite the section number from the policy document for
every sub-axis where you award 2 points or deduct points. If you cannot cite
the policy, you cannot award full marks.

────────────────────────────────────────────────────────────────────────────
SCORING RUBRIC

A. Grounding (weight 0.30)
   2 = Every factual claim in the answer is directly supported by the policy.
   1 = Most claims supported; at most one minor unsupported claim.
   0 = Two or more unsupported claims, OR a key claim is invented.

B. Citation correctness (weight 0.20)
   2 = All cited sections (e.g. "§ 4.2", "Section 7.1") actually contain the
       cited claim.
   1 = At least one citation is off by one sub-section but in the right area.
   0 = A citation points to a section that does not contain the claim, OR
       the answer makes a claim that obviously needs a citation and gives none.

C. Value & threshold accuracy (weight 0.20)
   2 = Every dollar amount, hour, day, and percentage matches the policy
       exactly (e.g. "$25/day", "≥ 6 hours", "30 days", "≤ 15%").
   1 = Values are directionally right but one is off by a small amount
       (e.g. "about $25" when policy says "$25/day"; "around a month" for "30 days").
   0 = A value is wrong, fabricated, or contradicts the policy.

D. Approval-path correctness (weight 0.15)
   2 = Names the correct approver(s) (Manager / VP / CFO / Travel-Ops) AND
       the correct trigger (e.g. "VP if over by ≤ 15%, CFO if over by > 15%").
   1 = Approver is right but trigger is vague or partial.
   0 = Wrong approver, OR claims no approval needed when policy requires one,
       OR invents an approver role not in the policy.
   N/A = The question does not involve an exception or approval. Score this
         axis as 2 by default and note "n/a" in the rationale.

E. Scope discipline (weight 0.15)
   2 = Answer refuses to invent rules the policy does not state; if the
       question is out of scope (e.g. contractors, personal travel), the
       answer says so and points to the right workflow.
   1 = Answer hedges appropriately but slips in one minor opinion or
       extra-policy guideline.
   0 = Answer fabricates a rule, OR contradicts the policy, OR cites a
       non-existent section.

FINAL = (0.30·A + 0.20·B + 0.20·C + 0.15·D + 0.15·E) / 2
        rounded to two decimal places, in [0.00, 1.00].

VERDICT thresholds (use exactly these labels):
  ≥ 0.85           → "pass"
  0.70 – 0.8499    → "ship-with-caveats"
  < 0.70           → "fail"

────────────────────────────────────────────────────────────────────────────
OUTPUT FORMAT — strict JSON. No prose outside the JSON. No code fences.

{
  "scores": {
    "A_grounding":              { "score": 0 | 1 | 2, "evidence_section": "string or null", "note": "≤ 25 words" },
    "B_citation_correctness":   { "score": 0 | 1 | 2, "evidence_section": "string or null", "note": "≤ 25 words" },
    "C_value_accuracy":         { "score": 0 | 1 | 2, "evidence_section": "string or null", "note": "≤ 25 words" },
    "D_approval_path":          { "score": 0 | 1 | 2 | "n/a", "evidence_section": "string or null", "note": "≤ 25 words" },
    "E_scope_discipline":       { "score": 0 | 1 | 2, "evidence_section": "string or null", "note": "≤ 25 words" }
  },
  "final_score": 0.00,
  "verdict": "pass" | "ship-with-caveats" | "fail",
  "violations": ["short tag per violation, e.g. 'hallucinated_section_4.5', 'wrong_threshold_$25'"],
  "rationale": "≤ 60 words summarizing the decision."
}

If the answer is empty, refuses to answer, or is not in English, return all
sub-scores as 0, final_score 0.00, verdict "fail", and add the violation tag
"non_answer".

────────────────────────────────────────────────────────────────────────────
USER:
POLICY DOCUMENT (authoritative — only this counts as evidence):
---
{{policy_document}}
---

QUESTION ASKED OF THE MODEL:
{{user_question}}

MODEL ANSWER UNDER EVALUATION:
{{model_answer}}

Score now. Return only the JSON object specified above.
````

### Why this rubric, not a free-form judge

A free-form "is the answer good?" judge would mostly reward fluency and politeness — the very things a frontier model wins at by default. That hides the real bug we're hunting: a small or stale model that **sounds confident but cites the wrong section or fabricates a $25/day cap as $50/day**. The five-axis decomposition forces the judge to look for exactly those failures, and the strict JSON output keeps the metric machine-comparable across model versions (base → v1 fine-tune → v2 fine-tune).

### How to use it in this workshop

| Step | Use |
|---|---|
| **05 — Evaluations** | Wire this prompt into a Foundry custom evaluator. Run it against [`eval-policy-only.jsonl`](eval-policy-only.jsonl) for the baseline `gpt-4.1` and `gpt-4.1-mini` models. Record `final_score` per row and the mean as the **Policy Adherence** column on the scorecard. |
| **06 — Fine-tune** | Re-run the same evaluator against the fine-tuned policy model (`wwi-policy-v1`). The delta on Policy Adherence is the headline number for the fine-tune demo (and the row that should move while quality, cost, and latency move only slightly). |
| **07 — Multi-model agent** | The router decides whether a request goes to the policy model at all. Policy Adherence is only computed on rows that the router classified as `policy_question` — failures here are the router's fault as much as the model's. |
| **08 — Portal review** | Show the per-section breakdown (which `evidence_section` values appear most in `violations`) to explain *where* the policy model is weakest, then point to the FT data slice that addresses it. |

> **Tip for demos:** when showing a regression, lead with the `violations` array — `["wrong_threshold_$25", "hallucinated_section_4.5"]` is a far more visceral failure mode on stage than a 0.71 → 0.68 score drop.
