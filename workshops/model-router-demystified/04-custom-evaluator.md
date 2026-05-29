# Lab 4 — Custom Evaluator: Policy-Adherence with Adaptive Eval Rubric

> **Surface:** SDK · **Time:** ~25 min · **Outcome:** A domain-specific evaluator that scores responses against WWI policy using the Adaptive Evals framework

## What you'll do

Build a custom Policy-Adherence evaluator using Foundry's **Adaptive Evals** framework. This evaluator uses an **eval-rubric** — a structured YAML definition with criteria, scoring scales, weights, and adaptive rules that shift emphasis based on question context.

## Why generic quality isn't enough

Lab 3's LLM-as-a-judge scores (Accuracy, Completeness, Clarity, Helpfulness) answer: "Is this a good response?" But they don't answer: **"Does this response correctly apply our company's travel policy?"**

A response can be clear, complete, and helpful — but cite the wrong reimbursement limit or invent an approval rule that doesn't exist. That's a policy failure that generic scoring misses entirely.

**Domain-specific evaluators catch domain-specific failures.** This is especially critical with Model Router, because smaller models might "helpfully" fabricate policy details they were never trained on.

## Key concepts

| Concept | Detail |
|---|---|
| **Eval-rubric** | A YAML file defining criteria, scales, weights, and adaptive rules |
| **Adaptive rules** | Logic that shifts scoring weights based on input context (question category) |
| **Prompt-based evaluator** | An LLM judges each response using your rubric as its scoring instructions |
| **Code-based evaluator** | A Python function applies deterministic checks (complementary to prompt-based) |
| **Criteria** | What to measure: rule accuracy, completeness, boundary precision, hallucination absence |
| **Weighted average** | Final score = sum of (criterion_score × criterion_weight) |

## Step-by-step

### 4.1 — Design the eval-rubric

The rubric is in `code/eval-rubric-policy-adherence.yaml`. Here's what each criterion measures and why:

| Criterion | What it catches | Why it matters for Model Router |
|---|---|---|
| **Rule accuracy** | Did it cite the *correct* rule? | Smaller models might confuse Section 6 (hotels) with Section 7 (flights) |
| **Completeness** | Are all conditions/exceptions mentioned? | Fast models might give a partial answer and skip approval requirements |
| **Boundary precision** | Are dollar amounts and thresholds exact? | "$300" vs "$325" is the difference between "reimbursable" and "needs approval" |
| **Hallucination absence** | Did it invent rules not in the policy? | Smaller models are more likely to confabulate plausible-sounding rules |

### 4.2 — Understand the adaptive rules

The rubric doesn't score every question the same way. Adaptive rules shift weight based on context:

```yaml
adaptive_rules:
  # Budget questions → boundary precision matters most
  - condition: "input.category == 'budget_cap' or input.category == 'reimbursement'"
    adjust_weights:
      boundary_precision: 0.40  # up from 0.25

  # Exception/approval questions → completeness matters most
  - condition: "input.category == 'exception' or input.category == 'approval_chain'"
    adjust_weights:
      completeness: 0.40  # up from 0.25

  # Edge cases → hallucination risk is highest
  - condition: "input.category == 'edge_case'"
    adjust_weights:
      hallucination_absence: 0.40  # up from 0.15
```

**Why this is powerful:** The evaluator automatically becomes stricter where it matters most. A budget question with a wrong dollar amount gets penalized heavily. An edge-case question with fabricated rules gets penalized heavily. No manual adjustment per-run.

### 4.3 — Examine the judge prompt

The prompt-based evaluator sends the full rubric to a judge LLM. See `code/policy_adherence_evaluator.py` for the complete prompt, but the key structure is:

```
You are evaluating an AI travel assistant's response against WWI's official policy.

## Policy Document (ground truth):
{{ground_truth}}

## User Question:
{{query}}

## AI Response to Evaluate:
{{response}}

## Scoring Rubric
[detailed 1-5 scale for each criterion with examples]

Output Format (JSON):
{
  "rule_accuracy": <1-5>,
  "completeness": <1-5>,
  "boundary_precision": <1-5>,
  "hallucination_absence": <1-5>,
  "result": <weighted average>,
  "reason": "<justification>"
}
```

### 4.4 — Prepare the policy evaluation dataset

The dataset needs ground truth — the correct policy answer for each question:

```bash
# The dataset is pre-built at sample-data/policy-eval-dataset.jsonl
# Each row includes:
#   - id, prompt, category (the question)
#   - ground_truth (the correct policy answer, citing specific sections)
#   - relevant_sections (which policy sections apply)

python -c "
import json
with open('sample-data/policy-eval-dataset.jsonl') as f:
    rows = [json.loads(l) for l in f if l.strip()]
print(f'Policy eval dataset: {len(rows)} questions')
print(f'Sample: {rows[0][\"prompt\"][:80]}...')
"
```

### 4.5 — Register the evaluator with Foundry SDK

```python
python code/policy_adherence_evaluator.py --action create
```

This uses the Foundry SDK to:
1. Register the prompt-based evaluator in your project's evaluator catalog
2. Set the scoring method to `ordinal` (1–5 scale)
3. Define the data schema (`query`, `response`, `ground_truth`)

### 4.6 — Run the evaluator against baseline and router responses

```python
python code/policy_adherence_evaluator.py --action evaluate \
    --dataset sample-data/policy-eval-dataset.jsonl \
    --responses-baseline results/baseline-vs-balanced/baseline_responses.jsonl \
    --responses-router results/baseline-vs-balanced/router_responses.jsonl
```

### 4.7 — Analyze policy-adherence results

```python
python code/policy_adherence_evaluator.py --action report
```

**What to look for:**

1. **Overall scores:** Does the router maintain policy accuracy?
2. **Per-criterion breakdown:** Where does the router struggle?
   - If `hallucination_absence` drops → smaller models are inventing rules
   - If `boundary_precision` drops → smaller models are approximating numbers
3. **By question category:** Which categories suffer most from routing to cheaper models?
4. **Adaptive vs. flat scoring:** Compare weighted-average (adaptive) vs. simple average — adaptive scoring may reveal problems that flat scoring hides

### 4.8 — The novel insight: adaptive evaluation as a routing quality signal

Here's something unique to this workshop:

**Adaptive eval + Model Router = automatic quality monitoring per task type.**

Because the adaptive rules shift weight based on question category, and Model Router routes different categories to different models, you get a natural feedback signal:

- If policy-adherence drops for `edge_case` prompts → the router is sending them to models that hallucinate
- If it drops for `budget_cap` prompts → the router is sending them to models that approximate numbers
- The fix: adjust your model subset to exclude models that fail on those criteria

**You don't need to manually test every model on every task type.** The adaptive evaluator + routing distribution together reveal exactly where quality is at risk.

## Checkpoint

- [ ] `eval-rubric-policy-adherence.yaml` reviewed and understood
- [ ] Evaluator registered in Foundry project's evaluator catalog
- [ ] Ran evaluator against both baseline and router responses
- [ ] Per-criterion scores analyzed (rule_accuracy, completeness, boundary_precision, hallucination_absence)
- [ ] Understand how adaptive rules shift scoring emphasis
- [ ] Identified which categories (if any) lose policy-adherence quality with routing

## Troubleshooting

| Issue | Fix |
|---|---|
| Judge returns malformed JSON | Ensure judge model is capable (gpt-5 recommended). Add retry logic. |
| All scores are 5.0 | Ground truth might be too vague. Ensure specific policy citations. |
| Huge variance across runs | Increase judge temperature to 0 for determinism. |

---

**Next:** [Lab 5 — Optimize: routing modes →](./05-optimize-modes.md)
