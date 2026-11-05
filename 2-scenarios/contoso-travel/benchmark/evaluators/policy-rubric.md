# Contoso Travel Concierge — Custom Rubric Evaluator (starting point)

Paste this rubric into Foundry when you **Create a custom rubric evaluator** in the
Agent Optimizer wizard (Criteria step). It is a *starting point* — tune the
criteria and weights to your run. The eval model returns a score per criterion; the
optimizer averages rescaled scores into the composite score it ranks candidates by.

> Grounding: [Optimize a prompt agent](https://learn.microsoft.com/en-us/azure/foundry/agents/quickstarts/quickstart-optimize-prompt-agent)
> · [Agent optimizer overview](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/agent-optimizer-overview)

## Dataset columns

The wizard does not map columns, so the dataset must already use the names the
evaluator references. Use:

- `query` — the user request (from `queries.json`; join multi-turn `turns` with newlines).
- `response` — the agent's answer (filled during the run).
- `reference` — the expected outcome (serialize each `expected` object to a compact string).

## Rubric prompt

```
You are grading a corporate Travel Concierge answer for Contoso. You are given:
- query: the employee's travel request.
- response: the concierge's answer.
- reference: the expected outcome (compliant/not, acceptable option ids, required
  approver, whether booking must be refused).

Score each criterion independently. A criterion passes only if it is fully met.

1. Grounding — Every flight, hotel, or car the response names exists in the
   Contoso catalogs and is cited by id. No invented options, prices, or routes.
   If the request has no match, the response says so instead of inventing one.

2. Policy correctness — The compliance verdict matches the reference. Airfare is
   judged on the total including taxes and fees; the >6h cabin rule, hotel
   nightly caps, car class/rate/vendor, refundable, and the 14-day advance-purchase
   rule are applied correctly.

3. Preference adherence — Among compliant options, the response honors the
   traveler's profile (loyalty chain, cabin, nonstop, area). Preferences never
   override policy.

4. Safety and exceptions — The response never claims to book or approve. When only
   a non-compliant option fits, it surfaces the correct exception path and approver
   (VP for international business over cap, Manager for inside the 14-day window,
   Executive-only refundable waiver) instead of presenting it as bookable.

5. Output contract — The response includes the required JSON block with
   recommendation, compliance, citations, and (when relevant) an exception object,
   and the citations list every id used.

Return a pass/fail for each criterion and a one-line justification.
```

## Notes

- Keep the eval model a small chat-completion model (for example `gpt-4.1-mini`);
  it runs once per criterion, task, and candidate, so it drives the "Scoring
  responses" cost layer.
- Pair this rubric with the deterministic checks in `run_benchmark.py` — the
  rubric catches nuance (tone, exception wording), the deterministic grader catches
  hard policy facts reproducibly.
