# Step 1 — Baseline in the playground

> **Foundry lifecycle:** *prerequisite baseline* — v1 = "one frontier model, one prompt." (Portal, low-code)

## Goal

See one frontier model try to do *everything* Carmen's trip needs. Establish the v1 cost and latency, and feel the pain that motivates the rest of the workshop.

**Surface:** Foundry Portal — Playground.

**Time:** 20 min.

**Scorecard at end of step:**
```
Quality   ░░░░░░░░░░  ?     (we don't even have an eval yet!)
Cost      ██████████  ~11¢
Latency   ██████████  ~12.3s
```

## Prereqs

- Step 0 complete (project + catalog access in Sweden Central).
- A copy of `sample-data/carmen-trace.json` for the on-stage prompt.

## Steps

The numbered subsections below (1.1 – 1.5) are the actions to perform in order.

The bars are red. They *should* be red — that's the point.

---

## 1.1 — Open the portal and verify your deployments

> ⚠️ **Enable New Foundry first:** In [ai.azure.com](https://ai.azure.com), ensure the **"New Foundry"** toggle in the top-right header is switched **on**. Without it you'll land in the legacy Azure AI Studio view and the project won't appear.

1. Go to [https://ai.azure.com](https://ai.azure.com) and select project **`nitya-brk230-demo`**. Keep this **Home** tab open.
2. In a **new tab**, open the **Build** menu in the top nav → select **Models** from the left sidebar → click the **Deployments** tab.
3. Confirm you see all three deployments with status **Succeeded**:

| Name | Model | Version | Status |
|---|---|---|---|
| `planner-gpt41` | gpt-4.1 | 2025-04-14 | Succeeded |
| `router-nano` | gpt-4.1-nano | 2025-04-14 | Succeeded |
| `mini-vision` | gpt-4.1-mini | 2025-04-14 | Succeeded |
| `policy-mini-base` | gpt-4.1-mini | 2025-04-14 | Succeeded |

> **Why job-shaped names matter:** We already have `planner-gpt41`. Naming deployments by *job* (not by model) means swapping the underlying model in Step 7 is a one-line config change — no app code changes needed.

## 1.2 — Open the playground and paste Carmen's request

In the **Deployments** view, click **`planner-gpt41`** → **Open in playground**.

System prompt (paste verbatim):

```
You are WWI, an internal agent that helps employees plan
business travel. You can call tools: search_flights, search_hotels,
check_policy, submit_booking. You must respect company policy and
return a final itinerary as JSON with keys: flight, hotel, policy_notes,
total_estimated_cost_usd, booking_status.
```

User prompt (this is **Carmen's trip** from the demo):

```
Hi, I'm Carmen from the San Diego office. I need to be in Berlin
Tuesday morning for an offsite that runs through Thursday evening.
Please book my flights and a hotel near Alexanderplatz. Keep it
under $2,500. Also — here's a parking receipt photo from three days
ago at SAN, can you expense it? [pretend a photo is attached]
```

Click **Send**.

## 1.3 — Observe what happens

You'll see something like:

- A long, thoughtful, well-written response.
- **~14.2 s** wall-clock (observed run: May 24 2026).
- **1,429 tokens** total (bottom panel).
- The model followed the JSON schema correctly — `booking_status: "pending_confirmation_and_tool_access"`.
- It **read the receipt image** successfully: *"SAN economy parking on 2026-05-21, total $27.25, cardholder C. REYES"* — vision works in the playground when an image is attached.
- It **invented** flight and hotel estimates (`not_booked`) because no tools are wired yet.
- It correctly noted it cannot submit expense reports from a travel-booking agent.

Click **View code** → copy the request JSON. Cost at these token counts and `gpt-4.1` pricing lands around **~$0.11 per turn** (exact figure computed by `s02_scorecard.py` in Step 2).

## 1.4 — Write down v1

Open `code/s02_scorecard.py` (we'll create it in Step 2; for now just jot in a note):

```
v1 (gpt-4.1 only, no tools, no eval) — measured 2026-05-24:
  Quality:  unknown   ← we have no measurement yet
  Tokens:   1,429 total
  Cost:     ~$0.11 / task  (computed in Step 2 by s02_scorecard.py)
  Latency:  14.2 s
```

## 1.5 — The lesson

This is what *most* AI demos look like on day one:

- One big model doing every job.
- No tools — so answers are confident fiction.
- No eval — so "it sounds good" is the only quality signal.
- A cost that's fine for a demo and **terrifying at 10,000 tasks/day**.

> **Yina's line in the deck (Step 8):** *"At $0.11 per task and WWI's 8,000 trips a month, that's ~$10,560/year just on travel planning. And we can't tell our CFO whether the answers are right."*

That's the gap the next seven steps close.

## Verify

- `planner-gpt41` deployed in the project's **Models + endpoints** view.
- v1 numbers recorded: cost ≈ 11¢, latency ≈ 12.3 s (per Carmen-trace run).
- You can articulate, in one sentence, *why* this baseline is the wrong production answer.

## Troubleshoot

| Symptom | Likely cause | Fix |
|---|---|---|
| Playground response is much faster/cheaper than 12 s / 11¢ | Different model or shorter prompt used. | Re-paste the full Carmen prompt; confirm deployment is `planner-gpt41`. |
| Deployment doesn't appear after `Deploy` | Provisioning still in progress, or quota hit. | Refresh **Models + endpoints**; if quota, request capacity in Sweden Central. |
| Numbers vary widely between runs | Single-sample noise. | Run 3 times, take the median; this is a story-grade baseline, not a scientific one. |

## Next

➡️ [Step 2 — Baseline agent in VS Code](./02-baseline-sdk.md)
