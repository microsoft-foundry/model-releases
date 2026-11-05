# Contoso Travel Concierge — a model optimization scenario

A hands-on lab for optimizing a Microsoft Foundry workload the way the model
optimization playbook prescribes: hold the workload, data, and benchmark constant,
change **one lever** at a time, measure the cost/quality/latency frontier, and keep
the change only when the scorecard improves.

The workload is a **Contoso Travel Concierge** — an enterprise agent that helps
employees book **policy-compliant** flights, hotels, and car rentals. It is rich
enough to exercise grounding, policy reasoning, preferences, safety, and structured
output, which makes it a good surface for hill climbing.

> This is a shared scenario, not a release capsule. The
> [Model Router capsule](../../4-models/model-router/) builds on it.

## What's in here

```
2-scenarios/contoso-travel/
  data/           signature datasets + the deterministic policy
  instructions/   a ladder of agent instructions, one lever per rung
  benchmark/      the query set, a baseline runner, and the rubric evaluator
```

- **[data/](data/)** — `flights.json`, `hotels.json`, `car-rentals.json`,
  `employees.json`, `receipts.json`, and the policy in both
  [machine form](data/travel-policy.json) and [readable form](data/travel-policy.md).
  All dates are future (late 2026–2028). Some options deliberately breach policy so
  the concierge has something to catch.
- **[instructions/](instructions/)** — copy one file into the agent's instructions
  to move up or down the quality ladder (see the hill-climb map below).
- **[benchmark/](benchmark/)** — [queries.json](benchmark/queries.json),
  [run_benchmark.py](benchmark/run_benchmark.py), and the
  [custom rubric evaluator](benchmark/evaluators/policy-rubric.md).

## Set up the Foundry project

1. **Create a project.** In the [Foundry portal](https://ai.azure.com), create (or
   open) a project. Sign in to the CLI so scripts can authenticate:
   ```bash
   az login
   export MICROSOFT_FOUNDRY_ENDPOINT="https://<resource>.services.ai.azure.com/api/projects/<project>"
   ```
2. **Deploy models.** For the hill climb you want:
   - a **`model-router`** deployment (the workload's main endpoint), and
   - optionally two baselines — one inexpensive model and one strong model — to
     anchor the frontier.
   For the optimizer, also deploy an **eval model** (e.g. `gpt-4.1-mini`) and an
   **optimization model** (e.g. a `gpt-5.x`).
3. **Attach the data for grounding.** Add the JSON files in [data/](data/) to the
   agent as knowledge/files in the playground. JSON keeps this a
   point-and-click step — no pipeline required.
4. **Create the prompt agent.** Start from a low rung of the instruction ladder
   (for example [`instructions/01-grounding.md`](instructions/01-grounding.md)) so
   the baseline has visible gaps to climb out of. In code, an agent is created with
   `AIProjectClient` + `PromptAgentDefinition` (see the
   [prompt-agent quickstart](https://learn.microsoft.com/en-us/azure/foundry/agents/quickstarts/prompt-agent?tabs=python)).
5. **Baseline it.** Run [benchmark/](benchmark/) to get a scorecard before you
   change anything.

## The hill-climb map

Each instruction rung adds exactly one lever and fixes one class of failure. Copy
the file into the agent, re-run the benchmark, and watch the matching gate improve.

| Rung | Lever added | Failure it fixes |
|---|---|---|
| [00-base](instructions/00-base.md) | — (baseline) | Establishes the low-water mark |
| [01-grounding](instructions/01-grounding.md) | Grounding | Invented flights/hotels/prices |
| [02-policy-aware](instructions/02-policy-aware.md) | Policy enforcement | Over-cap fares, wrong cabin, non-refundable, unapproved vendor |
| [03-preferences](instructions/03-preferences.md) | Preference adherence | Compliant but not personalized |
| [04-structured-output](instructions/04-structured-output.md) | Output contract | Unparseable, uncited answers |
| [05-safety-exception](instructions/05-safety-exception.md) | Deterministic safety | Auto-booking / approving over-cap travel |
| [10-reference-gold](instructions/10-reference-gold.md) | All levers | The target "good" agent |

Beyond instructions, the same benchmark lets you pull the **Model Router** levers —
routing mode (Cost/Balanced/Quality), model subset, and router-per-agent — and the
**Agent Optimizer** can climb the instruction lever automatically using the
[rubric evaluator](benchmark/evaluators/policy-rubric.md).

## Future capability versions

The scenario is built to be re-skinned for other model capabilities by changing
only the **agent + the "Inputs & modalities" block** in an instruction file. The
data, policy, and downstream logic stay put.

| Capability | Travel feature it unlocks | Turned on by |
|---|---|---|
| Chat / reasoning / **model router** | Text concierge (this version) | Base prompt agent |
| Function calling | Live flight/hotel/car search + booking tools | Tool defs + instructions |
| Vision | Photo receipts, boarding passes, signage | Vision model + "read the image" block |
| Audio / speech | Spoken requests and replies (voice agent) | Transcribe + Voice models + voice block |
| Image generation | Itinerary / briefing cards | Image model + "render a card" block |
| Long context | Whole policy + travel history in one prompt | Long-context model / subset |

`receipts.json` shows the pattern: an `artifact.type` of `text` today becomes
`image` or `audio` tomorrow with no schema change, because every modality resolves
to the same structured record.
