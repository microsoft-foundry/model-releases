# Training Plan — "Right Model, Right Job"

**End‑to‑End AI Development in Microsoft Foundry**

| Field | Content |
|---|---|
| **Format** | 45‑minute training session · 2 co‑instructors (a developer, **Naomi**, and a technical decision maker, **Yina**) |
| **Audience** | Professionals familiar with AI development (have built or shipped LLM‑backed features) but **new to Microsoft Foundry** |
| **Goal** | Teach how to use Foundry to select, customize, evaluate, and optimize models so that a real workload meets quality, cost, and latency targets |
| **Scenario** | WWI Concierge — a **toy demo** with sample data: one enterprise app concept, seven jobs, one recurring traveler (Carmen in San Diego) |
| **Platform** | Microsoft Foundry (portal + SDK + CLI) |
| **Region** | **East US 2** |
| **Model family** | **Azure Direct** only — Azure OpenAI first‑party deployments (no Models‑as‑a‑Service / partner‑hosted) |
| **Build budget** | **7 days from kickoff to dress rehearsal** — drives the toy‑scale data and deployment choices in §9 |
| **Outcome** | Participants leave with a mental model for per‑task model decisions and a working knowledge of the core Foundry capabilities that support that loop |

---

## Learning objectives

By the end of this session, participants will be able to:

1. **Explain** the difference between a monolithic single‑model AI app and a multi‑model agent‑structured AI app, and articulate when each is appropriate.
2. **Identify** at least four distinct *model types* in the Foundry catalog (frontier reasoning, small language model, multimodal vision, embedding) and a workload task that fits each.
3. **Define** a per‑task quality/cost/latency scorecard for a real application and explain why a single global SLO is usually a trap.
4. **Use** Foundry evaluations — datasets, built‑in evaluators, custom evaluators — to make model choice an empirical decision rather than a guess.
5. **Describe** how synthetic data generation, fine‑tuning, and the prompt optimizer fit into an iterative improvement loop.
6. **Recognize** how continuous evaluation closes the loop between production traffic and your eval suite.

A glossary of every Foundry term used in this session is in §11 — participants can take it home.

---

## The bookends

We open and close the session with two statements. The first is the problem we're here to address; the second is what participants should be able to say honestly by the end.

**Where we start (the problem statement):**
> *"I shipped one big frontier model behind one prompt. It works on the demo. In production it's expensive, slow on the cheap tasks and slow on the hard ones, and when something regresses I have one opaque quality number that tells me nothing about which job is actually broken."*

**Where we end (the takeaway):**
> *"The unit of progress isn't the prompt or the agent — it's the **model decision, made per task, against a per‑task scorecard**. Foundry gives me the loop — catalog, eval, customize, optimize, monitor — fast enough to actually run it. Right model, right job, measured."*

Everything in between is the journey from one to the other, taught step by step.

---

## 1. The core idea

A single frontier model can technically "do everything." That's both its appeal and its trap. As soon as a real workload mixes reasoning, classification, vision, retrieval, and translation, that monolith becomes the worst tradeoff on every axis: too expensive for cheap tasks, too slow for hot paths, and impossible to tune without affecting unrelated capabilities.

Decomposing the app into agents isn't really an architecture story. It's what creates **clean seams where you can pick the right model for each task**, evaluate it against a **task‑specific contract**, and optimize each piece independently. So when we talk about agents in this session, agents are the *vehicle*. The *cargo* is the per‑task model decision.

---

## 2. Foundry, briefly — the concepts before we begin

Because most of you are new to Foundry, here are the building blocks we'll be using. We'll come back to each one as it shows up in the demo.

| Concept | Plain‑language definition |
|---|---|
| **Foundry project** | A workspace that ties your model deployments, datasets, evaluations, agents, and traces together under one resource boundary. Think "the home for one application's AI work." |
| **Model catalog** | A browsable inventory of models you can deploy. Filterable by hosting type (Azure Direct vs. Models‑as‑a‑Service), capability (text, vision, audio, embedding), region, and whether the model supports fine‑tuning. |
| **Azure Direct** | First‑party deployments hosted and billed by Microsoft (Azure OpenAI is the main example). Distinct from Models‑as‑a‑Service, which is partner‑hosted. We're staying inside Azure Direct for this session. |
| **Deployment** | A named instance of a model with capacity allocated to it. Your code calls a deployment by name (e.g., `planner-gpt54`), not the model directly. |
| **Evaluation** | A run of one or more evaluators against a dataset, producing scored rows you can review and compare. |
| **Evaluator** | A function — built‑in or custom — that scores a single row of model output against some criterion (relevance, groundedness, task adherence, or a domain‑specific check you write). |
| **Dataset** | A versioned collection of test cases — inputs and (usually) expected outputs or grading rubrics. |
| **Fine‑tuning job** | A training run that takes a parent model + a training dataset + hyperparameters and produces a new deployable model artifact in the catalog. |
| **Synthetic data generation** | Using a model to expand a small seed dataset into a larger one, grounded in source documents. Used for training and stress testing — never for grading. |
| **Prompt optimizer** | An automated search over prompt variants that scores each candidate against your evaluator suite, surfacing the best performer. |
| **Continuous evaluation** | Ongoing sampling of production traffic, scored against your evaluators, with alerts when scores regress. |
| **Tracing** | Per‑request execution data (inputs, outputs, tool calls, timings) captured in the portal. Traces can be promoted back into eval datasets — production failure becomes tomorrow's test case. |

If you remember nothing else from this slide, remember: **catalog → deploy → evaluate → customize → optimize → monitor → back to evaluate.** That's the loop we'll walk through.

---

## 3. Your two instructors

| Role | Name | What they bring to the room |
|---|---|---|
| Developer | **Naomi** | Demonstrates code, runs evaluations, narrates what's happening in Foundry |
| Technical decision maker | **Yina** | Frames the business side — SLOs, cost, governance — and asks the clarifying questions a manager would ask |

The dynamic is **co‑teachers**, not debate. Yina isn't pushing back to challenge Naomi; she's bringing in the angle a participant's manager would care about, so participants leave with both the technical and the organizational vocabulary.

Neither instructor monologues more than ~60 seconds. We pause for understanding before moving on.

---

## 4. The running example — "WWI Concierge" (toy demo)

We'll teach this whole session using one example application. It's an enterprise travel concierge for WWI employees — *as a toy demo, with sample data we wrote ourselves.* That's deliberate: it keeps the build inside a 7‑day window and keeps the focus on the Foundry capabilities, not on real data wrangling.

**What "toy" means in concrete terms:**

- The "WWI policy" is a **2‑page sample document** we author for the demo (per‑diem caps, fare class rules, advance‑booking rules, blackout dates).
- All tools (flight search, hotel search, booking, expense submission) are **mocked** — canned responses living in the repo. No real APIs.
- Evaluation datasets are small and hand‑curated (20 rows curated, ~200 synthetic). See §9.3.
- We deploy the **minimum viable set** of models on Foundry (5 deployments, not 8). Voice and embedding are *discussed and shown in slides* but not deployed. See §9.2.

The toy scale doesn't weaken the lesson — every Foundry capability in scope is exercised end to end. It just means participants can replicate the build in a few evenings rather than a few weeks.

We have one recurring user, **Carmen**, an engineer in the San Diego office. Carmen needs to be in Berlin on Tuesday morning for an offsite. We come back to Carmen in each iteration to show, concretely, how the app gets faster, cheaper, and more accurate **for her** as we apply each Foundry capability.

The product has seven distinct jobs. Each one motivates a different *model type*.

| # | Task | Model type | Why this type fits |
|---|---|---|---|
| 1 | Voice intake | Speech‑to‑text | Audio in, text out. A frontier text model can't even take audio directly. |
| 2 | Intent routing | Tiny SLM classifier | Sub‑100 ms decisions at fractions of a cent. |
| 3 | Itinerary planning | Frontier reasoning | Complex multi‑step planning with tool calls — the one place a large model earns its keep. |
| 4 | Policy compliance | Fine‑tuned SLM | Bounded domain (your company's policy). Fine‑tuning a smaller model beats a frontier model on cost *and* quality here. |
| 5 | Receipt extraction | Multimodal vision | Vision *is* the job. |
| 6 | Policy retrieval | Embedding model | Retrieval quality is set by the embedding model, not by the generator. |
| 7 | Multilingual confirm | Translation‑capable SLM | Text in, text out, tight latency budget. |

Seven tasks, six distinct model types. That's the spine of the training.

---

## 5. Our model lineup — Azure Direct, East US 2

For this training we constrain ourselves to **Azure Direct** models in **East US 2**. That keeps the story coherent and lets you see exactly which models we picked and why. One model family across the session means no surprises from differing prompt formats or tokenizers.

| # | Task | Model (Azure Direct, East US 2) | Role in the training |
|---|---|---|---|
| 1 | Voice intake | **`gpt-4o-mini-transcribe`** | Discussed and shown in architecture; not benched live |
| 2 | Intent routing | **`gpt-5.4-nano`** | The smaller SLM we'll swap in during iteration 2 |
| 3 | Itinerary planning | **`gpt-5.4`** | Our starting monolith model; remains the planner through iteration 3 |
| 4 | Policy compliance | **`gpt-5.4-mini`** → **fine‑tuned `gpt-5.4-mini`** | Iteration 2 hands policy to the mini; iteration 3 fine‑tunes it |
| 5 | Receipt extraction | **`gpt-5.4-mini`** (vision) | Iteration 2 swap — same mini, now with vision input |
| 6 | Policy retrieval | **`text-embedding-3-large`** | Shown in architecture; embedding evaluation mentioned briefly |
| 7 | Multilingual confirm | **`gpt-5.4-mini`** | Reuses the mini deployment to keep the lineup tight |

**Why this set is useful for teaching:**

- One model family (`gpt-5.4` and its variants) → consistent prompt shape and tokenizer, so the lessons isolate the *choice of size*, not the choice of vendor.
- `gpt-5.4-mini` supports fine‑tuning as an Azure Direct deployment, which enables the policy fine‑tuning portion of the session.
- `gpt-5.4-nano` is a genuinely small, fast, cheap SLM — participants see a real latency and cost win from a real swap.
- `text-embedding-3-large` is the strongest first‑party embedding model — credible for the retrieval row even though we won't benchmark it live.

**The catalog filter we'll show on screen:** *Collection = Azure OpenAI* (or "Sold directly by Azure," depending on portal wording), *Region = East US 2*, *Deployable*. Participants see the filtered list — same view they would use on their own projects.

> **Trainer note:** The exact `gpt-5.4`, `gpt-5.4-mini`, and `gpt-5.4-nano` version strings, regional availability in East US 2, and fine‑tune support **must be re‑verified against the live Foundry catalog on Day 1** — the catalog moves faster than this plan does. Query via the Foundry MCP `models_list` / `model_get` tools (or the portal catalog filtered to *Sold directly by Azure*, *East US 2*, *Deployable*) and record exact version strings into `models.md`. If `gpt-5.4-mini` fine‑tune is not yet GA in East US 2 on the day, deploy the fine‑tuned artifact in a supported region and disclose the cross‑region detail during the session.

---

## 6. The Q/C/L scorecard — quality, cost, latency, per task

One of the most useful habits we'll teach in this session is making **per‑task** targets, not a single global SLO. A single number for "quality" averages over tasks that have very different difficulty profiles, and it lets weak rows hide behind strong ones.

| Task | Quality target | p95 latency | Cost / call |
|---|---:|---:|---:|
| Voice intake | WER ≤ 8% | ≤ 1.2 s | low |
| Intent routing | Macro‑F1 ≥ 0.95 | ≤ 150 ms | ~$0.0001 |
| Planning | Task success ≥ 0.85 | ≤ 6 s | allowed |
| Policy compliance | Accuracy ≥ 0.93 | ≤ 600 ms | low |
| Receipt extraction | Field F1 ≥ 0.92 | ≤ 2.5 s | medium |
| Retrieval | Recall@5 ≥ 0.9 | ≤ 200 ms | very low |
| Multilingual confirm | BLEU ≥ 35 + spot check | ≤ 800 ms | low |
| **End‑to‑end** | Task success ≥ 0.85 | p95 ≤ 9 s | ≤ \$0.04 |

This scorecard stays visible on the side of the screen for the whole session. Each iteration moves specific cells; participants should be able to track which Foundry capability moved which cell.

---

## 7. Session plan — three hands‑on iterations

| Time | Segment | What we teach | Scorecard movement |
|---|---|---|---|
| 0:00–0:04 | **Welcome and framing.** Introduce ourselves, the goals, and the running example. | Why model choice matters per task. | empty |
| 0:04–0:08 | **The seven jobs.** Walk through Carmen's request and decompose it. | Mapping a workload to model types. | rows defined |
| 0:08–0:15 | **Iteration 1 — the baseline.** `gpt-5.4` does all seven jobs. Show a smoke evaluation and the full batch from the night before. | What a monolith hides; why per‑task measurement matters. | quality acceptable but blind; cost and latency mostly red |
| 0:15–0:23 | **Foundry evaluations.** Datasets, built‑in evaluators, one custom evaluator for policy compliance. | How to make quality measurable and trustworthy. | quality cells now grounded in evidence |
| 0:23–0:31 | **Iteration 2 — right‑sizing.** Catalog tour. Swap routing → `gpt-5.4-nano`, receipts → `gpt-5.4-mini` (vision). Re‑run the smoke evaluation. | How to choose a model type per task; what a real swap looks like. | two rows fully green |
| 0:31–0:38 | **Iteration 3 — customization.** Synthetic data + fine‑tuned `gpt-5.4-mini` for policy (precomputed). Prompt optimizer for the planner (precomputed). | When to specialize a small model; how the prompt optimizer fits in. | policy row green; planner quality recovers |
| 0:38–0:42 | **Composition.** Show the full architecture and the honest tradeoffs of multi‑agent systems. | Why parallelism matters; how agent boundaries are also observability boundaries. | end‑to‑end row updated |
| 0:42–0:44 | **Continuous evaluation.** How traces flow back into datasets and become regression tests. | How the loop stays closed in production. | "durability" |
| 0:44–0:45 | **Recap and CTA.** Final scorecard reveal; restate the takeaway. | What participants should remember. | all green |

---

## 8. Instructor transcript

> Stage directions are in *italics*. Timestamps are cumulative. Pauses for participant questions are marked **[CHECK‑IN]**. Treat this as a script floor, not a ceiling — deliver naturally.

### 0:00 — Welcome and framing (Yina)

**Yina:** *(slide: title + the two instructors)* Welcome. We've got 45 minutes, and we're going to use all of them to teach you how to use Microsoft Foundry to build AI applications that actually meet the targets you care about — quality, cost, and latency. I'm Yina; I lead engineering on a platform team. This is Naomi, who builds the things I take credit for.

**Naomi:** *(small smile)* The deal is — Yina frames the business side and Naomi shows the code. We're co‑teaching this one. If something we say doesn't land, raise your hand or ask in chat; we'll pause.

**Yina:** Quick check on the room — most of you have built or shipped a feature backed by a large language model. Some of you have shipped two or three. The pattern we keep seeing — and I'd like to share a real example before we start — is that the first version of an AI feature is almost always one big model behind one prompt. It works on the demo. Then it gets to production, and the bill arrives.

**Yina:** A real number from my own team last quarter — one AI feature, one month, $47,000. And it wasn't because the model was bad. The model was great. It was great at expensive jobs, and it was also being asked to do a lot of cheap jobs that didn't need a great model. We were paying flagship token prices to decide whether a user said "book" or "cancel."

**Naomi:** And the lesson there — which is really the lesson of this whole session — isn't *use a smaller model*. It's **use the right model for each piece of the job**. That's what Foundry is built to help you do, and that's what we're going to walk through together.

**Yina:** A quick word on the format. We'll work through one running example — an enterprise travel concierge. We'll iterate on it three times. After each iteration we look at a scorecard together. **[CHECK‑IN]** Does that structure work for everyone? Any questions before we start?

### 0:04 — The seven jobs (Naomi)

*Slide: WWI Concierge — one product, seven jobs.*

**Naomi:** Let me make the example concrete. **Carmen** works in our San Diego office. She's a senior engineer. On a Friday afternoon she finds out she needs to be in Berlin on Tuesday morning for an offsite. She's walking to her car. She opens our app and says — *(reading from the slide)* — "I need to be in Berlin Tuesday morning for the offsite, flying from San Diego, business class if policy allows, vegetarian meal, and I'll expense the airport parking."

**Naomi:** Take a second and look at that sentence. There are seven distinct things our app has to do.

*Seven items animate in one at a time.*

**Naomi:** Carmen's voice has to become text — that's **voice intake**. Something has to figure out she wants to book a flight, not cancel one — that's **intent routing**. Something has to actually *plan* the itinerary, with multiple legs, against her calendar and our corporate fares — **itinerary planning**. Something has to check the policy — is business class okay for a flight over six hours, what's the per‑diem, who approves — **policy compliance**. When she sends the parking receipt three days later, something has to read the image — **receipt extraction**. To check the policy, something has to find the right clauses to cite — **retrieval**. And the confirmation lands in her preferred language — **multilingual confirmation**.

**Yina:** And in version one of this app — which I personally signed off on, more than once — all seven of those jobs go through the same single frontier model.

**Naomi:** That's our starting point. It works on the happy path. The interesting question is what happens when we measure it.

*Slide: the empty scorecard.*

**Naomi:** Before we measure, we have to define what *good* means. This is the scorecard. Quality target, p95 latency, cost per call — set **per task**, not globally. Receipt extraction is allowed to take up to two and a half seconds. Intent routing is not. A planning step is allowed to spend real money; a confirmation step is not. **[CHECK‑IN]** I'll pause here. The big idea is that the average across tasks hides which task is weak. Does that make sense before we move on?

### 0:08 — Iteration 1: the baseline (Naomi)

*Slide: v1 architecture — one box labeled `gpt-5.4`, seven arrows out.*

**Naomi:** Here's version one in Foundry. One **Foundry project** — remember, that's the workspace that ties everything together. One **deployment** of `gpt-5.4` — Azure OpenAI in East US 2 — which we've named `planner-gpt54`. One prompt template per job. One endpoint our app calls.

**Naomi:** I'm going to run what's called a **smoke evaluation** in a moment. A smoke evaluation is a small set of test cases — ten, in our case — designed to verify the pipeline is alive, not to grade quality. The full grading happens on a slightly larger batch — 30 cases for this toy demo — that we ran ahead of time against the same v1 build. We'll look at that in a minute. *(In a real project this batch would be hundreds to thousands of cases; we keep it small here so you can rebuild the whole demo in a week.)*

*Naomi switches to a terminal and runs the smoke eval. ~45 seconds.*

**Naomi:** *(while it runs)* Quick teaching note — separate "did anything execute" from "is anything good." A smoke eval answers the first question quickly; a batch evaluation answers the second carefully. Don't confuse them.

*Eval lands. Naomi switches to the Foundry portal evaluations view.*

**Naomi:** Now here's the full batch from last night. End‑to‑end task success: **0.87**. That's above our 0.85 bar. So the headline looks good. **[BEAT]** Look at the rest, though. Intent routing — **800 milliseconds** to decide one of twelve intents, costing a third of a cent each. Receipt extraction p95 is **4.8 seconds**, because we're using a text model to reason about an image description we generated separately. End‑to‑end p95 is **12.3 seconds**. End‑to‑end cost: **11 cents per interaction**.

**Yina:** Which puts us 40 percent over the latency target, roughly 3× over the cost target. And the only reason the *quality* cell looks acceptable is that the average is hiding what's underneath. We have no idea, at this point, which sub‑task is actually weak — because we never measured them separately.

**Naomi:** That's the main lesson of iteration one, and it's the lesson I want everyone to leave with even if you forget everything else: **a monolith hides the weak spots**. You can't optimize what you can't see. So our next move isn't to swap a model. It's to **measure properly**, and then decide.

*Slide: scorecard updates — quality mostly green, cost and latency mostly red.*

### 0:15 — Foundry evaluations (Naomi, Yina supports)

**Yina:** Before we change anything in the architecture, we want to make sure the numbers we're looking at are numbers we can trust. The most common pattern we see when teams say "it's better now" is that the eval is three prompts in a notebook on somebody's laptop. We'll show you how Foundry helps you do better than that.

**Naomi:** I'll share a small confession that I think is useful for learning. The first eval I ever wrote — I cheated, accidentally. I picked test cases the model already passed because those were the ones I had labels for. The number went up. I shipped. The numbers were honest in a narrow sense and useless in every other sense. So when we talk about trusting an eval, we mean something very specific.

*Naomi opens the evaluations view in the repo.*

**Naomi:** Two ingredients in **Foundry evaluations**. A **dataset** — that's a versioned collection of test cases with inputs and either expected outputs or grading rubrics. And **evaluators** — these are functions that score one row of model output. Foundry ships built‑in evaluators: groundedness, relevance, fluency, task adherence, tool‑call accuracy. Pick the ones that fit each task.

**Naomi:** For most of our rows, the built‑ins are enough. Policy compliance is *our* domain — even our 2‑page sample policy isn't in any base model's training data, and a real corporate policy never is. So we wrote **one** custom evaluator. It takes the model's recommendation, the cited policy clauses, and a human‑labeled expected outcome — compliant, non‑compliant, or needs‑approval — and it returns a structured score with a justification we can audit later.

*Slide: about 15 lines of Python defining the custom evaluator.*

**Yina:** I'd want to ask, if I were a participant: why only one custom evaluator? I might have expected to see one per task.

**Naomi:** Good question — that's the question to ask. Every LLM‑judged evaluator is itself a model. It has its own noise floor, its own biases. Each custom evaluator is something you have to calibrate against human labels. The practical advice is: start with one, where the domain genuinely needs it. Let the built‑ins carry the rest. Add more only when you have evidence you need more.

**Yina:** And the dataset — where does it come from? Because in my role I'd be worried about optimizing against data we generated ourselves.

**Naomi:** Three sources, in order of trust. **Curated human‑labeled cases** — small, expensive, and the gold standard. We use 20 in this toy demo; a real project might have hundreds or thousands. **Production traces** — Foundry can promote a trace into a dataset row, so real failure modes become test cases. **Synthetic cases** — generated by a model, used for coverage and stress, especially edge cases we haven't seen yet. The scorecard on screen is graded against the curated set only. Synthetic rows never appear in the eval set.

*Naomi opens the per‑task breakdown of last night's batch.*

**Naomi:** Now look at the same batch evaluation, but per task. This is where the monolith story falls apart.

**Naomi:** End‑to‑end **0.87** — fine. Intent routing accuracy **0.94** — **below** our 0.95 bar, by the way, and we didn't know it last night. Policy compliance accuracy **0.81** — well below the 0.93 bar, on the task where the regulator cares. Receipt extraction F1 **0.89**.

**Yina:** This is the moment I want everyone to write down a note on. **You don't have *a* quality number. You have a vector of quality numbers — one per task. The average will lie to you.** What Foundry evaluations give you is the vector, broken down per task, with the evaluator that scored each row visible and inspectable. **[CHECK‑IN]** Any questions about evaluations before we move into the catalog?

### 0:23 — Iteration 2: catalog tour and right‑sizing (Naomi)

*Slide: Foundry model catalog, filtered to Azure Direct, East US 2.*

**Naomi:** Now we get to use the **model catalog**. I've filtered it the way you'll filter it when you're working — *Sold directly by Azure*, region *East US 2*, *deployable*. That's our envelope today. No partner‑hosted models, no Models‑as‑a‑Service. Everything you see here is Azure OpenAI first‑party.

**Naomi:** I want you to notice the diversity *inside* this filter. Frontier reasoning — `gpt-5.4`, `o5-mini` for tasks where the model has to think step by step. Smaller variants of the same family — `gpt-5.4-mini` and `gpt-5.4-nano`. Multimodal capability — the mini takes images. Embeddings — `text-embedding-3-large`. Speech — `gpt-4o-mini-transcribe`. All Azure Direct. All in one region.

*Slide: seven jobs → seven model assignments with the Azure Direct model name in each row.*

**Naomi:** Voice → `gpt-4o-mini-transcribe`. Routing → `gpt-5.4-nano`. Planning → `gpt-5.4`. Policy → `gpt-5.4-mini`, fine‑tuned in the next iteration. Receipts → `gpt-5.4-mini` with vision. Retrieval → `text-embedding-3-large`. Multilingual confirm → `gpt-5.4-mini` again. One model family. Three sizes within it. One embedding model. One transcription model.

**Yina:** And in v1 we were paying `gpt-5.4` prices for all seven of those jobs.

**Naomi:** For this iteration I'll swap **two** tasks live — routing and receipts — where the mismatch is most obvious. We'll handle policy in iteration three with a fine‑tune, which is a different technique and worth its own segment.

*Naomi edits the agent configuration: two lines change.*

**Naomi:** That's the entire change. Two lines in the agent metadata. Each agent declares the model it wants by deployment name. Foundry deploys it; we re‑point the agent.

*Naomi runs the smoke eval.*

**Naomi:** *(while it runs)* What I expect to see — and I'll talk through the reasoning so you can predict similar moves on your own workloads. Routing latency should collapse from 800 ms to under 100 because the nano is genuinely small. Cost should drop by roughly 50× for the same reason. Quality should go **up** — and this is the counterintuitive part — because a small instruction‑tuned model is *better* at structured 12‑way classification than a generative frontier model. Receipts quality should go up because we're using a model that actually sees pixels, not a text model speculating about an image caption. Latency on extraction should come down because the mini is purpose‑built for that scale of task.

*Eval lands.*

**Naomi:** Routing macro‑F1 **0.96**, p95 **94 ms**, cost **~$0.0001 per call**. Receipts field F1 **0.93**, p95 **2.1 seconds**. Both rows fully green. End‑to‑end cost dropped from 11 cents to 6 cents. End‑to‑end p95 from 12.3 down to 9.4 seconds.

**Yina:** Still over the latency target end to end.

**Naomi:** Right. The slack is in planning and policy, and those are different problems. Planning is genuinely hard work that the frontier model is doing for a reason. Policy is the one we're going to *specialize* with a fine‑tune, which is the next iteration.

*Scorecard updates: two rows fully green; one still red on quality.*

### 0:31 — Iteration 3: customization with synthetic data + fine‑tuning + prompt optimizer (Naomi, Yina supports)

**Naomi:** Policy compliance. The frontier model is at **0.81**; we need **0.93**. The instinct is to use a bigger model. That makes latency and cost worse and, on this kind of task, often doesn't even fix quality — the model still doesn't *know* your policy. The right move is to **specialize**.

**Naomi:** Two Foundry capabilities together: **synthetic dataset generation** and **fine‑tuning**.

*Slide: synthetic data flow.*

**Naomi:** For this toy demo we have a 2‑page sample policy and 30 hand‑labeled cases. Thirty examples is nowhere near enough to fine‑tune a model reliably, so we use Foundry to generate synthetic policy Q&A — grounded in our sample policy — with variation across roles, fare classes, edge cases like change fees, conference rates, and blackout periods. About 200 synthetic rows for this demo. In a real project, you'd scale both the seed data and the synthetic set up considerably.

**Yina:** And here's where I'd bring in three governance questions, because they'll come up in any organization you work in. **One:** are we training on data we generated and grading ourselves on that same data? **Two:** where did the synthetic data come from, and could it leak anything private? **Three:** who reviews the synthetic data before it becomes training signal?

**Naomi:** Good — these are the answers worth memorizing. **One:** we grade against the curated human set only. No synthetic row ever appears in the eval set, so generating more synthetic data cannot inflate the score. **Two:** the generator is grounded in the policy document plus a redacted seed of historical cases — names and IDs are stripped before generation, so no PII enters the pipeline. **Three:** every synthetic row gets an automated consistency check, plus a 10% human review sample. Failures go in the bin.

**Yina:** That's the answer I'd want documented for any AI work that touches policy or compliance.

**Naomi:** The fine‑tune itself — I'm not going to run a fine‑tuning job live. A real fine‑tune on `gpt-5.4-mini` takes minutes to a couple of hours depending on data size, and we'd rather use that time teaching. I ran it three days ago, and here's the artifact in the Foundry portal — parent model, dataset version, hyperparameters, training metrics, and the resulting deployable model now in the catalog.

*Naomi shows the fine‑tuned `gpt-5.4-mini` in the catalog.*

**Naomi:** A teaching moment from the actual fine‑tune. The first time we ran this, I thought I'd misread the latency number — **410 milliseconds**, from a model that took 1.8 seconds on the same task before fine‑tuning. I asked someone on my team to double‑check. They double‑checked. So the size of the win you can get from specialization, on a bounded domain task, is genuinely larger than most people expect on their first try. Don't be surprised by it; expect it.

**Naomi:** One more capability to introduce — the **prompt optimizer**. The planning agent prompt was written by me two weeks ago at midnight. The prompt optimizer takes the planner's eval set and explores prompt variants automatically, scoring each candidate against the evaluator suite. It's not magic; it's a guided search over prompts. I ran it overnight.

*Slide: prompt optimizer run history with eval deltas.*

**Naomi:** The best candidate improves planning task success from **0.85 to 0.91**, no model change, no new code. We accepted it. That's a quality gain that costs nothing at inference time.

*Naomi runs the iteration 3 smoke eval.*

**Naomi:** Policy compliance: **0.94 accuracy**. Latency **410 ms**. Cost per call about **$0.0008** — versus four cents on the frontier model. That's a **fifty‑times cost reduction with a quality improvement**. Planning task success **0.91**. End‑to‑end cost **2.8 cents per interaction**. End‑to‑end p95 **7.6 seconds** — under target for the first time.

*Slide: scorecard — all rows green.*

**Yina:** And the line I want you to leave the session with: **we did not give up quality to save money. We gained quality because each model is doing a job that fits its shape.** **[CHECK‑IN]** Any questions about fine‑tuning or the prompt optimizer before we close?

### 0:38 — Composition and the honest tradeoffs (Naomi)

*Slide: final architecture — small router, six specialist agents, each labeled with its specific Azure Direct model.*

**Naomi:** Here's the final architecture. A small router classifies intent. Specialist agents handle planning, policy, vision, retrieval, translation, and speech. Each agent has its own model, its own evaluator suite, its own scorecard row.

**Yina:** And here's an honest tradeoff worth knowing before you go build this on your own work. Going from one model to seven doesn't automatically make the app faster. What it does is make the slow steps **the ones that genuinely need to be slow**, and make the fast steps fast. The end‑to‑end latency wins come from running independent agents — retrieval and policy lookup, for example — in **parallel**. If you serialize everything naively, you can lose latency on a multi‑agent design. That's an engineering decision, and it's now *legible*, because each agent has a budget and a contract.

**Naomi:** The other thing worth saying — the agent boundary is also the **observability** boundary. When something regresses in production, you know which agent, which model, which eval row. You're not staring at a single opaque endpoint trying to guess.

### 0:42 — Continuous evaluation (Yina)

*Slide: continuous evaluation loop.*

**Yina:** Last capability we want you to know about. The wins we just showed you are all from controlled evaluations at one moment in time. The harder problem is *keeping* those wins as the world changes around you.

**Yina:** **Continuous evaluation** in Foundry samples your production traffic, scores those samples against the same evaluators you used in development, and alerts you when scores regress. When a model provider ships a new version of `gpt-5.4-mini`, when your traffic mix shifts because your company opened a London office, when an upstream API changes its response shape — you hear about it from a dashboard, not from a customer.

**Yina:** And the traces it captures don't just sit there. They get **promoted back into your eval dataset** — especially the failure modes. Your eval set strengthens over time. Your fine‑tunes get more current data. The loop closes.

**Naomi:** And because each agent's contract is small and explicit, when a regression happens you can swap a single model — back to a known‑good version, or forward to a newly released one — without touching the rest of the system. The architecture makes model decisions **reversible**, which is one of the most underrated properties of a multi‑model design.

### 0:44 — Recap (both)

*Slide: full scorecard journey, v1 → v2 → v3.*

**Yina:** Same product. Same Carmen. Three iterations.

- **Iteration 1**: one `gpt-5.4` does everything. 11 cents, p95 12 seconds, quality blind.
- **Iteration 2**: two right‑sized swaps from the Azure Direct catalog. Cost cut in half. Two rows fully green.
- **Iteration 3**: fine‑tuned `gpt-5.4-mini` for policy, prompt‑optimized `gpt-5.4` for planning. Every row green. 2.8 cents per interaction. Under target.

**Naomi:** What earned each step: **catalog → evaluate → customize → optimize → continuously evaluate**. Each step had a number attached, and each step had a Foundry capability that made the step practical.

**Yina:** One thing we did *not* do: we didn't click a button labeled "make better" and watch numbers improve. Every gain was a hypothesis we tested against an evaluation. Foundry's contribution is making that loop fast enough that you'll actually run it. It doesn't make the loop optional.

**Yina:** What I hope you take from this session isn't only a smaller token bill. It's the habit of being able to look at your AI feature on a Monday morning and **know** — per task, per model, with numbers you trust — whether it's working. That's what Foundry helped us do for our team. It's what we'd like it to help you do for yours.

**Naomi:** Right model. Right job. Measured. Glossary, the exact model lineup in East US 2, and a starter repo are all on the next slide. Thank you for spending this time with us — we're happy to take questions.

*[applause / Q&A]*

---

## 9. Trainer setup and recording guide

This section is for the instructors and any production team running the session. Treat it as a checklist.

### 9.1 Environments

- **Single Foundry project** `wwi-concierge-demo` in **East US 2**. No backup project — at toy scale the cost of standing up a second region isn't worth it within a 7‑day build. The mitigation for an outage is the recorded fallback videos.
- **Repo** with three branches or tags: `v1-baseline`, `v2-rightsized`, `v3-customized`. The repo contains the 2‑page sample policy, the 20‑row curated eval, the ~200‑row synthetic set, the agent code, and the mock tools.
- **Fallback videos** for every live action, stored on the instructor laptop and on a USB stick at the AV booth.

### 9.2 Pre‑deploy these models — minimum viable set (5 deployments)

All deployments are **Azure OpenAI / Azure Direct in East US 2**. Use **Global Standard** or **Standard** SKUs based on quota; record the SKU in `models.md`.

| # | Deployment name | Base model | Used for | Notes |
|---|---|---|---|---|
| 1 | `planner-gpt54` | `gpt-5.4` | iteration 1 monolith + iteration 3 planner | Verify TPM quota; carries v1 traffic |
| 2 | `router-nano` | `gpt-5.4-nano` | iteration 2 intent routing | Tiny, fast; primary v2 win |
| 3 | `mini-vision` | `gpt-5.4-mini` (vision enabled) | iteration 2 receipts **and** multilingual confirm (reuse one deployment) | Confirm vision capability in deployment |
| 4 | `policy-mini-base` | `gpt-5.4-mini` | iteration 2 policy compliance (pre fine‑tune) | Parent for fine‑tune |
| 5 | `policy-mini-ft` | **fine‑tuned `gpt-5.4-mini`** | iteration 3 policy compliance | **Run fine‑tune job at T‑4 days; deploy by T‑3** |

**Not deployed** (discussed only — slides and architecture diagram):

- `gpt-4o-mini-transcribe` for voice intake.
- `text-embedding-3-large` for retrieval.

These two are part of the teaching story but require no deployment to demo. If you have extra time on day 6, deploy them and add a one‑sentence live mention; otherwise the slides alone carry the lesson.

Record everything in `models.md`: base model version (e.g., `gpt-5.4-2025-XX-XX`), deployment name, region, SKU, capacity (TPM/RPM), owning project, and one‑line purpose.

### 9.3 Datasets and runs to precompute — toy scale

| Artifact | Size | Purpose | When |
|---|---|---|---|
| Sample travel policy | 2 pages, authored by hand | Source for synthetic data and retrieval | Day 1 |
| Curated eval set | **20 rows**, hand‑labeled across the 7 tasks | Grading — the gold standard for this demo | Day 1–2 |
| Synthetic training set | **~200 rows**, ~20 spot‑checked by hand | Fine‑tune input only; never used for grading | Day 4 |
| Smoke eval | 10 rows | Live on screen, ≤ 60 s | Day 3 |
| v1 / v2 / v3 batch runs | **30 rows each** | Precomputed; reveal via portal links in instructor notes | Day 6 |
| Fine‑tune job artifact on `gpt-5.4-mini` | 1 completed job | Deep‑link in instructor notes | Day 4–5 |
| Prompt optimizer run for planner | ~10 candidates | Deep‑link in instructor notes | Day 6 |

The "batch eval" is intentionally tiny (30 rows) for this toy demo. In the transcript, Naomi calls this out so participants don't take 30 as a real production number.

### 9.4 Recording fallback videos

Record during the tech rehearsal on Day 6. The instructor narrates live over a silent video if a live action fails.

- **Tool:** OBS Studio, single Display Capture source, one take per loop.
- **Resolution:** 1920×1080 native; confirm projector aspect with the venue.
- **Frame rate:** 30 fps. **Audio:** muted.
- **Fonts:** terminal ≥ 18 pt, IDE ≥ 16 pt, browser zoom 125–150%.
- **Hide:** notifications, bookmarks, other tenants. Use a fresh browser profile.
- **Length budget:** L1 ≤ 75 s, L2 ≤ 75 s, L3 reveal ≤ 60 s.
- **Pre‑roll:** 2 s static start frame so the instructor can introduce before motion.

**Per loop, capture:**

- **L1:** terminal running smoke eval against `planner-gpt54` → portal v1 batch + per‑task breakdown.
- **L2:** the two config diffs (router → `router-nano`, receipts → `mini-vision`) → smoke run → portal v2 deltas vs v1.
- **L3:** fine‑tune artifact (`policy-mini-ft`) in catalog → prompt optimizer run history → smoke run → v3 deltas.

Save as `demo-L1.mp4`, `demo-L2.mp4`, `demo-L3.mp4` on the instructor laptop and the AV booth USB.

### 9.5 Stage and AV checklist

- Two laptops on stage; primary drives demos, secondary holds deck + fallback videos.
- Wired network if available; personal hotspot as backup; test both during sound check.
- Foundry portal pre‑logged‑in on both laptops, **demo tenant only** — sign out of everything else.
- CLI auth refreshed within 30 minutes of doors.
- Slide notes contain deep links to every portal artifact.
- **Scorecard slide is animated** — each iteration updates the visible state. Don't ask the audience to remember.
- **Confidence monitor** with per‑segment timer. If you're over time at the end of iteration 2, **the prompt‑optimizer subsegment of iteration 3 is the designated cut.**

### 9.6 Seven‑day build calendar

Built backwards from session day (T‑0). One person can build this in 7 days; two people can do it in 4–5 with parallelism.

| Day | Task | Output |
|---|---|---|
| **Day 1 (T‑7)** | Provision Foundry project in East US 2. Verify `gpt-5.4` family availability via Foundry MCP `models_list` or portal. Author the 2‑page sample travel policy. Draft the 20 curated eval rows by hand. | Project, policy doc, eval v0 |
| **Day 2 (T‑6)** | Deploy `planner-gpt54`, `router-nano`, `mini-vision`, `policy-mini-base`. Scaffold the agent code with mock flight/hotel/booking tools. Wire v1 (monolith) end to end. | Working v1 |
| **Day 3 (T‑5)** | Define Foundry evaluations: dataset upload, pick built‑in evaluators per task, author the one custom policy evaluator. Run smoke eval against v1. Run the 30‑row batch against v1. | Eval suite + v1 results |
| **Day 4 (T‑4)** | Generate ~200‑row synthetic policy Q&A set using Foundry synthetic data generation; hand‑spot‑check ~20. Wire iteration‑2 model swaps (`router-nano`, `mini-vision`). Run v2 batch. **Kick off fine‑tune job on `gpt-5.4-mini`.** | v2 results + fine‑tune in flight |
| **Day 5 (T‑3)** | Deploy fine‑tuned model as `policy-mini-ft`. Smoke test it. Run v3 batch. Kick off prompt optimizer for the planner. | v3 results |
| **Day 6 (T‑2)** | Tech rehearsal end to end against the real Foundry project. **Record fallback videos** during this rehearsal. Save portal deep links into slide notes. | Polished demos + fallback videos |
| **Day 7 (T‑1)** | Dress rehearsal with full timing. **Failure drill:** disconnect Wi‑Fi for 30 s during iteration 2 to practice the fallback handoff. Final timing pass; cut content if over. | Stage‑ready |
| **Session day (T‑0), –60 min** | Sound check, projector, mic, hotspot test. Heartbeat call to `policy-mini-ft` to avoid cold start. Final smoke eval run to confirm wiring. | Ready to teach |

**Critical path:** the fine‑tune job (Day 4 → Day 5) is the only step with material lead time you cannot compress. If `gpt-5.4-mini` fine‑tuning is unexpectedly slow, queueing it earlier on Day 4 — first thing in the morning — gives the most slack.

### 9.7 Top risks and mitigations

| Risk | Mitigation |
|---|---|
| Live eval runs over | Smoke is ≤ 10 rows, ≤ 60 s. Cut to precomputed 30‑row batch view if it slips. |
| East US 2 quota / capacity hiccup | **Acknowledged single‑region risk for this toy build.** Mitigation is the recorded fallback videos. If a real outage hits during the session, narrate over video and recover. |
| Catalog UI drift overnight | Screenshots of every catalog view in the deck as fallback. |
| Fine‑tuned deployment cold start | Heartbeat call to `policy-mini-ft` every 60 s during the session. |
| Fine‑tune job fails or returns weak quality | Build buffer: kick off the job on Day 4 morning. If it fails, retry once on Day 5 morning. If still weak by Day 5 afternoon, present the *pre‑fine‑tune* mini result and frame iteration 3 around prompt optimization only — call this out honestly in the transcript ad‑lib. |
| Audience asks about dataset size (30‑row batch) | Honest answer: "This is a toy demo we built in a week to show you the loop. In a real project you'd run hundreds or thousands of cases — the Foundry mechanics are the same." |
| Audience asks "why not o‑series for the planner?" | Honest answer: o‑series is in scope as a future variant; `gpt-5.4` was chosen for tool‑call reliability and lower planning latency in our evaluations. |
| Audience asks "what about partner‑hosted SLMs in the catalog?" | "Out of scope today — we constrained ourselves to Azure Direct in East US 2 for a coherent story. The same pattern applies; the catalog filter just changes." |
| Over‑run | Cut the prompt‑optimizer subsegment first. |
| Over‑run | Cut the prompt‑optimizer subsegment first. |

---

## 10. Slides — minimum viable deck (12 slides)

1. Title + instructors + the problem statement quote.
2. Learning objectives for the session.
3. Foundry concepts primer table (the glossary, compressed onto one slide).
4. The seven jobs of WWI — meet Carmen.
5. Q/C/L scorecard, empty.
6. Iteration 1 architecture (one `gpt-5.4`, seven arrows) + iteration 1 scorecard reveal — the per‑task breakdown is the teaching moment.
7. Foundry evaluations: dataset hierarchy + evaluator anatomy + custom evaluator code.
8. Foundry model catalog filtered to Azure Direct, East US 2 + the seven jobs → specific model mapping.
9. Iteration 2 architecture + iteration 2 scorecard update.
10. Synthetic data flow + fine‑tuned `gpt-5.4-mini` artifact + prompt optimizer run history.
11. Iteration 3 scorecard — all green + final architecture (router + six specialists with model names).
12. Recap + takeaway quote + glossary link + starter repo + Q&A.

---

## 11. Glossary (handout for participants)

| Term | Definition |
|---|---|
| **Foundry project** | A workspace that ties model deployments, datasets, evaluations, agents, and traces together under one resource boundary. |
| **Azure Direct** | First‑party model deployments hosted and billed by Microsoft (Azure OpenAI). Distinct from Models‑as‑a‑Service (partner‑hosted). |
| **Model catalog** | Browsable inventory of models you can deploy. Filter by hosting type, capability, region, and fine‑tunability. |
| **Deployment** | A named instance of a model with capacity. Your code calls deployments, not models directly. |
| **Evaluation** | A run of one or more evaluators against a dataset, producing scored rows. |
| **Evaluator** | A function (built‑in or custom) that scores one row of model output against a criterion. |
| **Built‑in evaluator** | Foundry‑provided evaluator — examples include groundedness, relevance, fluency, task adherence, tool‑call accuracy. |
| **Custom evaluator** | Evaluator you author for a domain‑specific criterion (e.g., policy compliance). |
| **Dataset** | Versioned collection of test cases — inputs with expected outputs or grading rubrics. |
| **Smoke evaluation** | A small, fast eval (≤ 10 rows) used to verify the pipeline is alive. Not for grading. |
| **Batch evaluation** | A larger eval (hundreds to thousands of rows) used to grade quality with confidence. |
| **Fine‑tuning job** | A training run that takes a parent model + dataset + hyperparameters and produces a new deployable model artifact in the catalog. |
| **Synthetic data generation** | Using a model to expand a small seed dataset into a larger one, grounded in source documents. For training and stress only — never for grading. |
| **Prompt optimizer** | An automated search over prompt variants, scoring each candidate against your evaluator suite. |
| **Continuous evaluation** | Ongoing sampling of production traffic, scored against your evaluators, with alerts when scores regress. |
| **Tracing** | Per‑request execution data captured in the portal. Traces can be promoted back into datasets. |
| **Q/C/L scorecard** | Per‑task quality, cost, and latency targets — the contract each model has to beat for its task. |

---

## 12. Decisions to make on Day 1

- **Validate Azure Direct availability in East US 2** for the exact model versions you plan to deploy: `gpt-5.4`, `gpt-5.4-mini` (with vision), `gpt-5.4-nano`. Confirm fine‑tune support for `gpt-5.4-mini` in East US 2. Use the Foundry MCP `models_list` tool (or the portal). If `gpt-5.4-mini` fine‑tuning is unavailable in‑region on the day, deploy the fine‑tuned artifact in a supported region and disclose the cross‑region detail during the session.
- **Voice and embedding** are discussed in slides only; not deployed. (Optional stretch on Day 6 if time permits.)
- **All tools** are mocked — never a real flight, hotel, or booking action.
- **Final CTA**: starter repo URL, docs URL, glossary download, and any follow‑on lab.

---

## 13. Participant outcomes

After this session, a participant should be able, without us, to:

1. Name **three model types** beyond "the big one" and a task each fits — with at least one specific Azure Direct model name they could deploy on Monday.
2. Sketch a **per‑task Q/C/L scorecard** for one of their own applications.
3. Name the **Foundry capability** they would use to (a) trust their quality numbers, (b) recover quality on a smaller model, (c) keep quality wins durable in production.
4. Explain to a teammate **why a single global SLO is usually a trap** for multi‑task AI applications.

If they also leave able to have a productive conversation with their CFO about how their token bill should evolve next quarter — even better.
