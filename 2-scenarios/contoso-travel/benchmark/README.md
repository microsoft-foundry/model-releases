# Benchmark & optimization

Two complementary ways to score the Contoso Travel Concierge and drive a hill climb.

## What's here

| File | Purpose |
|---|---|
| [queries.json](queries.json) | Seed benchmark: ~30 cases across the workload classes, each tagged with the `gate` (lever) it exercises and `expected` fields for deterministic grading. Extend toward 100+ for production-like runs. |
| [run_benchmark.py](run_benchmark.py) | Local baseline runner. Records the router's `selected_model`, latency, and tokens per query, applies a deterministic grade, and writes a scorecard. |
| [evaluators/policy-rubric.md](evaluators/policy-rubric.md) | Starting-point rubric to paste into Foundry's **custom rubric evaluator** for the Agent Optimizer. |

## A. Local baseline scorecard

Establish a baseline before you change any lever.

```bash
az login
export MICROSOFT_FOUNDRY_ENDPOINT="https://<resource>.services.ai.azure.com/api/projects/<project>"
export AGENT_NAME="contoso-travel-concierge"      # a deployed prompt agent, OR
# export AZURE_MODEL_ROUTER_DEPLOYMENT="model-router"   # a router deployment

pip install azure-ai-projects>=2.3.0 azure-identity
python run_benchmark.py
```

It prints a scorecard (quality, policy accuracy, p50/p95 latency, token totals,
and the selected-model distribution) and writes `results.json`. Re-run it after
each lever change and compare — that comparison *is* the hill climb.

The deterministic grader is intentionally strict and fails closed, so a weak
instruction set (for example `instructions/00-base.md`) scores low on grounding,
policy, and safety gates. Swapping in a higher rung should lift exactly those gates.

## B. Foundry Agent Optimizer (rubric-driven)

Use the portal optimizer to generate and rank better instructions automatically.

1. Deploy a **prompt agent** using one of the `instructions/` files (start low, e.g. `01-grounding.md`).
2. Export an optimizer dataset from the benchmark:
   ```bash
   python run_benchmark.py --export-jsonl contoso-eval.jsonl
   ```
   The JSONL uses the `query` / `response` / `reference` columns the rubric
   evaluator expects (the wizard does not remap columns).
3. In the Foundry portal open the agent → **Optimize** → **Create optimization run**:
   - **Target**: the agent version, an optimization model (`gpt-5.x`), max candidates, and an eval model (`gpt-4.1-mini`).
   - **Dataset**: upload `contoso-eval.jsonl`.
   - **Criteria**: **Create a custom rubric evaluator** and paste
     [evaluators/policy-rubric.md](evaluators/policy-rubric.md) as the starting point.
   - **Review**: check the estimated cost range, then submit.
4. **Compare** candidate scores to the baseline, then **Promote** the best candidate
   to a new agent version.

Grounding: [Create a prompt agent](https://learn.microsoft.com/en-us/azure/foundry/agents/quickstarts/prompt-agent?tabs=python)
· [Optimize a prompt agent](https://learn.microsoft.com/en-us/azure/foundry/agents/quickstarts/quickstart-optimize-prompt-agent)
· [Agent optimizer overview](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/agent-optimizer-overview)
· [Agent optimizer costs](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/agent-optimizer-costs)

## Reading the numbers

- A composite-score change **< 0.03** is noise; **0.03–0.10** is worth deploying;
  **> 0.10** is significant (per the optimizer docs).
- Optimized instructions are often longer — watch the token trade-off against the
  quality gain, since tokens are what you pay for.
- The optimizer invokes the agent for every dataset row. If you later add real
  booking tools, mock them during optimization to avoid side effects.
