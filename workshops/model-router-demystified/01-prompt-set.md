# Lab 1 — Build the Representative Prompt Set

> **Surface:** SDK · **Time:** ~10 min · **Outcome:** 50+ tagged prompts covering the full complexity spectrum

## What you'll do

Design a diverse prompt dataset that exercises the full range of WWI tasks — from trivial FAQ to complex multi-step reasoning. This dataset is the foundation for every evaluation in the workshop.

## Why this matters

Model Router's value depends on your workload mix. If every prompt is equally complex, routing saves nothing. Real workloads have a **distribution**: many simple queries, some moderate tasks, and a few genuinely hard problems. Your eval dataset must mirror that distribution to produce meaningful cost/quality comparisons.

## Key concepts

| Concept | What to know |
|---|---|
| **Complexity spectrum** | Prompts range from trivial (lookup) to frontier-hard (multi-step reasoning with policy edge cases) |
| **Category tagging** | Each prompt gets a `category` so you can analyze routing decisions per task type |
| **Expected difficulty** | Tag `easy` / `medium` / `hard` — later you'll check if the router agrees with your intuition |
| **JSONL format** | One JSON object per line: `{"id": "...", "prompt": "...", "category": "...", "difficulty": "..."}` |

## Step-by-step

### 1.1 — Understand the WWI task categories

The WWI Concierge handles six types of requests:

| Category | Example | Expected difficulty |
|---|---|---|
| `simple_faq` | "What's the per-diem for domestic travel?" | Easy — lookup from policy |
| `policy_question` | "Can I fly business class on a 7-hour flight?" | Easy/Medium — rule with conditions |
| `trip_planning` | "Plan a 3-day trip to Berlin for a client meeting" | Medium — multi-step coordination |
| `receipt_expense` | "I have a $340/night hotel receipt in NYC — is this reimbursable?" | Medium — rule + threshold check |
| `edge_case` | "My flight was cancelled and I rebooked at 2× the price — who approves?" | Hard — exception + approval chain |
| `multi_step_reasoning` | "Compare options: 2 domestic hops vs. 1 international flight for a NYC→London→Berlin trip" | Hard — cost analysis + multiple rules |

### 1.2 — Start from existing eval seed

Copy the eval seed from the original workshop as a starting point:

```bash
# Reuse the 20 curated rows from foundry-models-e2e
cp ../foundry-models-e2e/sample-data/eval-seed.jsonl ./sample-data/base-seed.jsonl
```

### 1.3 — Extend with router-specific prompts

Create `sample-data/router-eval-prompts.jsonl` with 50+ prompts. The file is provided in this workshop, but here's the design rationale:

**Distribution target:**
- 15 × `simple_faq` (easy) — these should route to cheap/fast models
- 10 × `policy_question` (easy/medium) — mix of simple lookups and conditional rules
- 10 × `trip_planning` (medium) — multi-step but well-scoped
- 5 × `receipt_expense` (medium) — number-heavy, boundary checks
- 5 × `edge_case` (hard) — ambiguous, exception-heavy
- 5 × `multi_step_reasoning` (hard) — require frontier-level reasoning

**Example entries:**

```jsonl
{"id": "faq-001", "prompt": "What is the daily meal per-diem for international travel?", "category": "simple_faq", "difficulty": "easy"}
{"id": "faq-002", "prompt": "Is in-flight Wi-Fi reimbursable?", "category": "simple_faq", "difficulty": "easy"}
{"id": "pol-001", "prompt": "I need to fly business class on an 8-hour flight to Tokyo. What approval do I need?", "category": "policy_question", "difficulty": "medium"}
{"id": "trip-001", "prompt": "Plan a 2-night trip to Seattle for a product review meeting next Tuesday. Include flight, hotel, and ground transport within budget.", "category": "trip_planning", "difficulty": "medium"}
{"id": "rcpt-001", "prompt": "I stayed at a hotel in San Francisco for $350/night. The policy says Tier 1 max is $325. Can I get reimbursed?", "category": "receipt_expense", "difficulty": "medium"}
{"id": "edge-001", "prompt": "My international trip was booked 15 days in advance (policy says 21 days). My manager approved verbally but didn't document it. The trip already happened. Can I still get reimbursed?", "category": "edge_case", "difficulty": "hard"}
{"id": "reason-001", "prompt": "I have back-to-back meetings in Boston (Tier 2) and NYC (Tier 1) over 4 days. What's my total budget cap, and should I book two separate domestic trips or one extended trip? Which saves the company more?", "category": "multi_step_reasoning", "difficulty": "hard"}
```

### 1.4 — Validate the dataset

```bash
python -c "
import json
with open('sample-data/router-eval-prompts.jsonl') as f:
    rows = [json.loads(line) for line in f if line.strip()]
print(f'Total prompts: {len(rows)}')
cats = {}
for r in rows:
    cats[r['category']] = cats.get(r['category'], 0) + 1
for cat, count in sorted(cats.items()):
    print(f'  {cat}: {count}')
print('✅ Dataset valid' if len(rows) >= 50 else '⚠️ Need more prompts')
"
```

## The key insight

> After Lab 3, you'll come back to this dataset and see which prompts the router sent to which models. The router's choices will mirror your difficulty tags — simple_faq → nano/mini, edge_case → frontier/reasoning. **The router empirically validates your workload decomposition.**

## Checkpoint

- [ ] `sample-data/router-eval-prompts.jsonl` exists with 50+ prompts
- [ ] Every prompt has `id`, `prompt`, `category`, and `difficulty`
- [ ] Distribution covers all 6 categories
- [ ] Mix of easy/medium/hard matches the 15/25/10 target ratio

---

**Next:** [Lab 2 — Deploy & configure Model Router →](./02-deploy-router.md)
