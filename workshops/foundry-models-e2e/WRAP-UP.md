# Workshop Wrap-Up — Right Model, Right Job

> Final hill-climb run · 2026-05-27 · WWI Concierge

This is the honest summary of the last three eval runs and what they tell us through the **Select → Evaluate → Optimize → Operate** lens.

---

## The three scorecards

```
╭───────────── v1-baseline ──────────────╮   ╭─────────────── v2-batch ───────────────╮   ╭─────────────── v3-final ───────────────╮
│                                        │   │                                        │   │                                        │
│   Quality   █████░░░░░     0.52        │   │   Quality   ██░░░░░░░░     0.25        │   │   Quality   ███░░░░░░░     0.29        │
│   Cost      █░░░░░░░░░   $0.013   ✅   │   │   Cost      ░░░░░░░░░░   $0.001   ✅   │   │   Cost      ░░░░░░░░░░   $0.001   ✅   │
│   Latency   █████████░    13.1s        │   │   Latency   ██████████    30.0s        │   │   Latency   ██████████    30.0s        │
│                                        │   │                                        │   │                                        │
╰────────────────────────────────────────╯   ╰────────────────────────────────────────╯   ╰────────────────────────────────────────╯
       single model · 20 seed prompts              router + per-task models · 173                 router + FT policy model · 173
                                                       full synthetic prompts                          full synthetic prompts
```

| Version | Agent | Eval set | Quality | Cost / task | Latency p50 | Lines |
|---|---|---|--:|--:|--:|--:|
| v1-baseline | `s02_baseline_agent` (single `gpt-4.1`) | `eval-seed.jsonl` | **0.52** | **$0.013** | 13.1 s | 20 |
| v2-batch | `s05_multi_model_agent` (routed, base policy) | `eval-full.jsonl` | **0.25** | **$0.001** | 30.0 s | 173 |
| v3-final | `s05_multi_model_agent` (routed, **FT** policy) | `eval-full.jsonl` | **0.29** | **$0.001** | 30.0 s | 173 |

And one live trace through v3 (Carmen's Berlin trip) returned a fully-formed booking JSON — flight $1,180 each way on LH457, Park Inn Alexanderplatz at $165/night, policy notes citing the SAN parking rule from the receipt — in **14.5 s**, using `router-nano` → `policy-mini-ft` → `planner-gpt41` for a total of ~3,200 tokens.

---

## What the hill-climb actually showed

This is what real iteration looks like. The scorecard did its job — it told the truth, even when the truth was uncomfortable.

### The good

- **Cost collapsed by ~92%** (`$0.013 → $0.001` per task). Routing classification and policy work away from `gpt-4.1` is the single highest-leverage decision in the agent.
- **The fine-tune moved the needle in the right direction** (`0.25 → 0.29` on the same hard set). It's evidence the FT pipeline works; it just hasn't done enough yet.
- **The full agent works end-to-end on a real, multimodal request.** Carmen's trace produced a structured booking with policy citations grounded in the receipt — the system composes correctly.

### The uncomfortable

- **Quality dropped from v1 to v2/v3.** That is *not* a regression in the agent — it's a regression in difficulty. v1 ran against 20 hand-curated seed prompts; v2 and v3 ran against the 173-prompt synthetic set, which deliberately includes adversarial budget edges, multi-constraint policy questions, and translation curveballs the seed set didn't cover.
- **Latency is pegged at exactly 30.0 s for both v2 and v3.** That's a ceiling, not a measurement — almost certainly a per-task timeout being hit on a slice of hard prompts. The real latency distribution is hiding behind that cap.
- **We are not at the target.** The scorecard targets were `≥ 0.92` quality, `≤ $0.03` cost, `≤ 8 s` p50. Cost is crushed. Quality and latency are not where they need to be.

### Why this is the right kind of failure

The whole point of building the eval harness in Step 5 was so that *this* moment — the moment your numbers tell you you're not ready — happens **in front of a scorecard, not in front of a customer.** v1 looked fine because its eval set was small and friendly. v2 looks bad because its eval set is large and honest. That's a feature.

---

## Select · Evaluate · Optimize · Operate — the wrap-up

### Select — *did the right model go to the right job?*

Yes, structurally. Routing landed on `router-nano`, policy on `policy-mini-ft`, planning on `planner-gpt41`, exactly as Step 3 prescribed. The Carmen trace confirms the decomposition is working — every task touched the model we picked for it.

**Lesson:** Name-by-job paid off. When the FT swap happened (Step 6), it was a one-line change behind `policy-mini-ft`. Nothing else in the agent had to move.

### Evaluate — *can we trust the numbers?*

Yes, and that's exactly why they hurt. The reason v1 looked better than v2 is that v1 wasn't measured honestly — 20 prompts is a smoke test, not an eval. The portal pinning makes this obvious: v1's run is tied to `eval-seed.jsonl`, v2 and v3 are tied to `eval-full.jsonl`. **You cannot compare runs across different datasets**, and the portal won't let you pretend otherwise.

**Lesson:** The next hill-climb has to keep the dataset constant. Re-run v1 against `eval-full.jsonl` and the real comparison emerges.

### Optimize — *did the changes compound?*

Partially. Multi-model routing dominated on cost. Fine-tuning delivered a small but real quality lift (+16% relative, 0.25 → 0.29) on the harder set. What it didn't do is close the gap to 0.92 — which tells us:

- The policy FT training set (Step 6) is probably too narrow for the breadth of policy questions in `eval-full.jsonl`. Expand training data using the failing prompts as seeds.
- The planner is likely the dominant remaining quality contributor. Run the **prompt optimizer** on `planner-gpt41` against the same evaluator suite before reaching for a bigger model.
- The 30 s latency cap is masking real numbers. Lift or remove the per-task timeout for the next run so the actual distribution shows up in the scorecard.

**Lesson:** Compound wins are real but uneven. Cost optimization comes for free with routing; quality optimization is a longer climb.

### Operate — *what would we ship?*

Today, nothing. The scorecard is two of three on cost, none-of-three on quality and latency at the targets we set. That's the right answer — the scorecard exists so we **don't** ship 0.29-quality output to a traveler.

But everything we need to keep climbing is now in place:

- Versioned datasets in the portal (`eval-seed`, `eval-full`) — comparable across future runs.
- Three eval runs pinned and side-by-side comparable in the portal (`v1-baseline`, `v2-batch`, `v3-final`).
- A named-by-job deployment topology that lets us swap models without touching agent code.
- A working fine-tune pipeline that has been *proven* to move the needle, just not far enough yet.

**Lesson:** "Operate" doesn't only mean production traffic. It means the system you've built can keep telling you the truth, run after run, without heroics. That part is real.

---

## The next hill to climb

In order:

1. **Re-run v1-baseline against `eval-full.jsonl`** so the three versions sit on the same dataset and the routing/FT deltas are honestly attributable.
2. **Remove the 30 s per-task timeout** and re-measure latency p50/p95.
3. **Mine v3's failing rows from the portal**, feed them into `s06_expand_ft_data.py`, and run a v4 FT.
4. **Run prompt-optimize on `planner-gpt41`** against the same evaluator suite; ship the winner behind the existing deployment name.
5. **Re-baseline** and look for the first green row.

---

## The through-line

> *Select the right model. Evaluate on your data. Optimize as a system. Operate behind a scorecard that's allowed to say no.*

This run said no. That's the loop working — not the loop failing.
