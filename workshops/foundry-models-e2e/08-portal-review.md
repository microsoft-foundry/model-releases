# Step 8 — Back to the portal: evals, red team, versions

> **Foundry lifecycle:** **04 · Operate** + **05 · Improve** — close the loop with monitoring, red team, versioned agents, and safe model adoption.

## Goal

Close the loop. Show that everything you did from code is also *visible, governable, and comparable* from the Foundry Portal — which is what your security, compliance, and decision-maker stakeholders care about.

**Surface:** Foundry Portal.

**Time:** 30 min to set up, plus the on-stage walkthrough.

**Final scorecard:**
```
Quality   █████████░  0.94  ✅
Cost      ██░░░░░░░░  2.8¢  ✅
Latency   ███░░░░░░░  7.6s  ✅
```

We're not changing numbers in this step. We're proving the work.

## Prereqs

- Step 7 complete: v3 numbers met all three targets.
- All eval runs (v1/v2/v3), red-team reports, and agent versions written into the same Foundry project.

## Pre-flight — populate the dashboards with realistic traffic

> **Run this 60+ minutes before you demo Step 8.** The portal monitoring panels are *boring* with no traffic. The loadtester drives a hosted Foundry **Prompt Agent** (`concierge-loadtest`) with a continuous mix of normal / edge-case / adversarial prompts so the dashboards have something to investigate — content-filter blocks, latency outliers, and policy-question failures that motivate the closing narrative (§8.6).

**One-time setup — create the Prompt Agent in the project:**

```bash
cd code
../.venv/bin/python s08_agent_setup.py \
  --name concierge-loadtest --model planner-gpt41 --temperature 0.2
```

This calls `client.agents.create_version(...)` with a `PromptAgentDefinition` whose instructions embed the WWI travel policy (truncated to 12 000 chars). The agent name is written to `generated/agent_concierge_loadtest.name` for the loadtester to pick up. Re-running just creates a new version against the same agent name (idempotent for the demo).

> **Also attach Application Insights to the project** (Portal → Foundry project → Tracing → *Attach Application Insights*). The loadtester auto-discovers the connection via `project.telemetry.get_application_insights_connection_string()` — without it, spans only stay in-process and the **Tracing** tab + Logs queries below will be empty.

**Launch the 2 h loadtester:**

```bash
nohup ../.venv/bin/python -u s08_loadtest_agent.py \
  --duration 2h --base-rpm 5 --spikes 4 --lulls 2 --workers 4 \
  --label monitor-demo \
  > generated/loadtest_agent_monitor-demo.out 2>&1 &
```

What it does:
- Loads [`sample-data/loadtest-prompts.jsonl`](./sample-data/loadtest-prompts.jsonl) (61 prompts tagged `class`: normal · edge · adversarial · `kind`: policy_question / plan_trip / receipt_expense / prompt_injection / jailbreak / pii_fishing / off_topic / non_english / multi_intent / typos / …).
- Drives traffic over 2 hours with a sinusoidal envelope (0.25× .. 1.5× base), 4 random **spike** windows (5× rate, 2–4 min — adversarial weight rises during spikes), and 2 random **lull** windows (silent for 3–8 min).
- Invokes the hosted agent through the Responses API (`agent_reference`), so every call shows up under **Agents → concierge-loadtest → Threads / Tracing** in the portal.
- Wires `AIProjectInstrumentor` + Azure Monitor exporter and stamps each span with WWI custom attributes (`wwi.prompt.class`, `wwi.prompt.kind`, `wwi.expected.is_policy`, `wwi.expected.is_adversarial`, `wwi.workload`, `wwi.agent.name`, `wwi.run.status`, `wwi.run.latency_s`, `wwi.run.answer_chars`, `wwi.run.ok`, `wwi.run.content_filtered`) so you can pivot the App Insights Logs by prompt class/kind.
- Mirrors each call into `generated/loadtest_agent_monitor-demo.csv` (ts, class, kind, run_status, latency, ok, ans_chars, err) as a local fallback.
- Bounded concurrency (default 4 workers), respects TPM caps, Ctrl-C clean shutdown.

While you talk through §8.1–§8.4 the loadtester keeps feeding the dashboards. By the time you reach §8.5 / §8.6, the **Agents → concierge-loadtest → Tracing** view (and App Insights `traces | where customDimensions.["wwi.prompt.class"] != ""` query) has thousands of real spans to filter on — including the content-filter blocks on adversarial prompts that anchor the closing narrative.

## Steps

The numbered subsections below (8.1 – 8.6) are the actions to perform in order.

---

## 8.1 — The Evaluation tab

Portal → **Evaluation**.

You should see (at minimum) three runs you created from `s05_run_eval.py`:

- `v1-batch`   (0.61)
- `v2-batch`   (0.78)
- `v3-final`   (0.94)

Click **Compare** → select v1 vs v3. The portal lays out side-by-side: quality scores, latency, cost, and per-row diffs.

**What to point at on stage:**
- Row-level diffs on the *policy* rows: v1 invents an answer, v3 cites Section 4.2 verbatim.
- The aggregate quality trend chart.
- The dataset version pinned at the top — *"these numbers are only meaningful because the dataset is fixed."*

## 8.2 — Red teaming (built-in)

Portal → **Evaluation** → **+ New run** → **Red team**.

Pick your deployment (`planner-gpt41` for the planner role) and select attack categories:
- Jailbreak
- Prompt injection
- Sensitive content
- Direct violence / self-harm / hate (toggle as appropriate)

Run it. The portal will run a panel of synthetic adversarial prompts and report attack success rate per category.

**What to point at on stage:**
- Categories where v3 is **stronger** than v1 (usually prompt injection — the router shape limits attack surface; the policy model has no tools).
- Any *new* failures introduced by giving the planner more autonomy.

> **Yina's line:** *"This is the difference between 'we tested it on Carmen's trip' and 'we tested it against an adversary'. Both matter. Foundry gives you the second one out of the box."*

## 8.3 — Agent versions, side-by-side

Portal → **Agents** → your agent → **Versions**.

If you registered each milestone as an agent version (recommended: do this after Steps 2, 5, 6 — the Foundry Skill's deploy sub-skill will do it automatically), you'll see v1.0, v2.0, v3.0 with:

- The deployment(s) bound to each version
- The eval run pinned to each version
- A "Compare" button

This is where you screenshot the **architecture diff**: v1 = 1 model, v3 = 4 deployments (counting the fine-tune).

## 8.4 — Tracing & datasets

Two more tabs worth pointing at briefly:

- **Tracing** — open the v3 run, drill into Carmen's trace. The portal shows the router → vision → policy(ft) → planner chain with per-call latency. This is the visual proof that the architecture is real.
- **Datasets** — your `eval-v1` should be listed with lineage back to the seed file and the synthetic generation run. *"This is what 'reproducible eval' actually means."*

## 8.5 — Online evaluation (production monitoring)

Portal → **Agents → `concierge-loadtest` → Tracing** (the Pre-flight loadtester has been feeding this agent for the last hour; you should have hundreds of threads with full span trees).

For deeper slicing, also open **Application Insights → Logs** on the attached resource and use the WWI custom dimensions the loadtester stamped on every span:

```kusto
traces
| where timestamp > ago(1h)
| where customDimensions["wwi.workload"] == "monitor-demo"
| summarize p50=percentile(toreal(customDimensions["wwi.run.latency_s"]), 50),
            p95=percentile(toreal(customDimensions["wwi.run.latency_s"]), 95),
            count() by tostring(customDimensions["wwi.prompt.kind"])
| order by p95 desc
```

**Three things to point at — every one of them seeds an optimization decision:**

1. **Latency by `wwi.prompt.kind`.** Group the query above (or the Tracing tab's grouping picker) by kind. You'll see:
   - `plan_trip` clustered around 6–12 s (planner-heavy, tool-loop dominated).
   - `policy_question` is bimodal — some sub-3 s, some > 20 s — and the slow ones correlate with longer prompts. *"That's a routing decision waiting to happen — cache short policy answers, only invoke the planner for ambiguous ones."*
   - Sharp vertical bands during the loadtester's spike windows. *"This is what your monitoring looks like the morning after a launch goes viral. Without it you wouldn't even know the spike happened."*

2. **Adversarial blocks by `wwi.run.content_filtered`.** Filter on `customDimensions["wwi.expected.is_adversarial"] == "True"` and group by `wwi.run.content_filtered`. You'll see clean clusters of content-filter blocks on `prompt_injection` and `jailbreak` prompts — exactly the adversarial traffic the loadtester injected. *"This is Foundry's built-in safety doing its job. The first thing to set up in any production deployment is a dashboard you can trust to surface this."*

3. **Coverage of intents by `wwi.prompt.class`.** During lull windows the class distribution thins out; during spikes the adversarial slice fattens. *"In production this is how you notice your traffic mix has shifted — a new customer segment, a marketing campaign, an attack."*

Now bind a **Continuous Evaluation** rule (Portal → **Evaluation** → **Continuous monitoring**) to the `concierge-loadtest` agent with a 5–10% sample rate. *"That's where your custom evaluators run on a slice of live traffic — every hour, forever. The hand-rolled evaluator from §5.7 graduates into a managed Eval Rubric here — §8.6 closes that loop."*

## 8.6 — From a hand-rolled prompt to a managed Eval Rubric

> **The thread that runs through the workshop:** every step that moved a needle started with adding a new way to measure. v1 didn't fail because the model was weak — it failed because we couldn't *see* policy hallucinations until we wrote [`s05_policy_adherence_evaluator.py`](./code/s05_policy_adherence_evaluator.py). Then v2 stopped looking like a regression. Then fine-tuning had a number to climb.

**This is exactly the move §8.5 just teed up.** Look back at the Monitoring → Traces view. The signal that motivates the *next* custom evaluator is right there in the loadtester's adversarial slice:
- A cluster of `pii_fishing` prompts that returned answers instead of refusals — a generic safety evaluator won't catch that, but a custom *"WWI PII Disclosure"* evaluator would.
- A cluster of `policy_violation_request` prompts where the model *complied* — a custom *"WWI Approval Authority"* evaluator would catch it.
- The `multi_intent` failures where the agent answered one question and dropped the others — a custom *"Multi-intent Coverage"* evaluator.

That observation-to-evaluator loop is the production version of the planning beat from Step 2: **every gap you can name in the dashboard becomes a measurable target.** The hand-rolled evaluator in §5.7 was the proof-of-concept. The portal flow below is how you industrialize it.

Pull up the custom evaluator we wrote in Step 5 — `code/s05_policy_adherence_evaluator.py` — and the rubric it implements in [`sample-data/README.md`](./sample-data/README.md#evaluating-policy-adherence). That's a **prompt-based custom evaluator**: hand-authored, version-controlled with the code, runs in our harness, surfaces a slice metric the headline Quality score can't see.

It worked for the workshop. **It does not scale to production.** Three reasons:

1. **The rubric is frozen at authoring time.** When the policy document changes (new section 11 on contractor travel, new $40 per-diem cap), the evaluator silently keeps scoring against the old four corners.
2. **There is no feedback loop from real traffic.** The failure modes we trained the evaluator to catch are the ones *we imagined*. Production will invent new ones — and you'll only see them when a customer reports it.
3. **Every team writes their own copy.** The travel team's "Policy Adherence" and the legal team's "Contract Compliance" share 80% of the structure and 0% of the implementation. Drift is the default.

**Portal → Evaluation → + New evaluator → Eval Rubric.** This is the managed equivalent.

What an Eval Rubric gives you that the prompt file doesn't:

| Capability | Hand-rolled prompt (`s05_…`) | Managed Eval Rubric |
|---|---|---|
| **Authoring** | You write JSON-ish instructions and hope the judge follows them. | Foundry **auto-generates the rubric** from a few labeled examples + the source policy doc. |
| **Versioning** | Lives in git; updating means a code review. | First-class versions in the portal; pin any agent run to a specific rubric version. |
| **Updates from traces** | Manual. You inspect failures, edit the prompt, hope you didn't regress. | **Adaptive.** Point it at the `Tracing` tab data, mark a sample of rows as pass/fail, the rubric proposes new sub-axes and tightens thresholds. |
| **Cross-team reuse** | Copy-paste between repos. | Published in the **Evaluator catalog**; other Foundry projects subscribe. |
| **Continuous evaluation** | Re-run by CI. | Wired into §8.5's continuous monitoring with no extra code. |

**What to do on stage:** open the Eval Rubric authoring flow, paste a handful of policy_question rows from our `eval-policy-only.jsonl`, hit *Generate rubric*, and show that Foundry produces something structurally similar to what we hand-wrote — but versioned, attached to the project, and ready to grow as our trace data grows.

> **Yina's line:** *"The hand-rolled evaluator was right for v1 of this workshop. The managed Eval Rubric is right for v1 of production. The first one teaches you what to measure. The second one teaches itself what to measure next."*

**This is the adaptive evaluator story** — the one that turns the v1→v3 hill climb into something an organization can keep doing forever, against models we haven't released yet, against policy versions that don't exist yet.

## 8.7 — The closing slide

```
The unit of progress is the model decision —
made per task, against a per-task scorecard.

What you saw:
  v1 → v3:  1 model → 4 deployments
  Quality:  0.61 → 0.94    (+54%)
  Cost:     $0.108 → $0.028  (–74%)
  Latency:  12.3s → 7.6s    (–38%)

Nothing here required heroics.
It required naming the jobs, measuring them,
and picking the right tool for each one.

Microsoft Foundry — Portal, SDK, Skills — gave us the surface.
The decisions were ours.
```

QR code → your repo. Drop the mic.

---

## You're done

If you've followed Steps 0–8 you have:

- A working multi-model agent on Foundry Sweden Central.
- A reproducible eval pipeline with versioned datasets.
- A fine-tuned `gpt-4.1` deployment for policy.
- Portal artifacts (eval runs, red-team report, agent versions) ready for screenshots.
- Three progress bars that go from red to green over 45 minutes of stage time.

Now go rehearse. See `.plans/foundry-models-e2e-plan.md` §9.4 for the OBS recording recipe and §9.6 for the Day 1–Day 7 build calendar.

## Verify

- Portal **Evaluation** tab shows v1/v2/v3 runs side-by-side.
- Portal **Red team** report attached to v3 with no critical findings.
- Agent versions tagged in the portal match your local git tags.

## Troubleshoot

| Symptom | Likely cause | Fix |
|---|---|---|
| Portal eval comparison panel is empty | Runs went to different projects or different datasets. | Re-run with consistent project endpoint and dataset version. |
| Red-team button missing | Capability not yet enabled in tenant. | Request enablement or skip and disclose on stage. |
| Agent versions lack lineage | Versions tagged outside the portal. | Re-tag via the portal's **Agents** view so lineage is captured. |

## Next

➡️ [99 — Recap](./99-recap.md)
