<p align="center">
  <img src="./.github/images/banner.png" alt="Model Releases: Select, Optimize, Scale" width="100%" />
</p>

<p align="center">
  <b><i>Learn what each new model does well — and where it fits in our agent.</i></b>
</p>

<p align="center">
  <a href="https://codespaces.new/microsoft-foundry/model-releases"><img src="https://github.com/codespaces/badge.svg" alt="Open in GitHub Codespaces" /></a>
</p>

<p align="center">
  <a href="https://ai.azure.com/catalog/models"><img src="https://img.shields.io/badge/Microsoft_Foundry-catalog-00A4EF?style=flat-square" alt="Microsoft Foundry catalog" /></a>
  <a href="https://aka.ms/model-mondays"><img src="https://img.shields.io/badge/Model_Mondays-livestream-F25022?style=flat-square" alt="Model Mondays livestream" /></a>
  <a href="https://aka.ms/model-mastery"><img src="https://img.shields.io/badge/Model_Mastery-workshops-7FBA00?style=flat-square" alt="Model Mastery workshops" /></a>
  <a href="./LICENSE"><img src="https://img.shields.io/badge/License-MIT-FFB900?style=flat-square" alt="License: MIT" /></a>
</p>

<br/>

Building our first agent is easy. Keeping it reliable — at the right cost, speed, and quality, as new models keep shipping — is the hard part. That's the climb on our banner: **select** the right model, **optimize** it one measured step at a time, and **scale** what works through automation.

Model Releases is the first step up that hill. Every new release we cover gets a **capsule**: a hands-on notebook that shows what the model does well and how it might improve an agent we already run.

> [!IMPORTANT]
> **Coming from an old link?** We reorganized the repo in November 2026 — see [where things moved](#did-an-old-link-break).

<br/>

## What's new?

<!-- BEGIN:LATEST -->
| Capsule | Date | What it does |
|---|---|---|
| [fal video family](5-multi-model/fal-video-family-walkthrough/) | 2026-11-10 | Multi-model: five fal video models on one launch campaign, each on its specialty, cut into one reel |
| [Fal-Kling-V3-Pro](4-models/fal-kling-v3-pro/) | 2026-11-06 | Cinematic text- and image-to-video with multi-shot storyboards, locked elements, and native audio (preview) |
| [Fal-MiniMax-H3-Max](4-models/fal-minimax-h3-max/) | 2026-11-06 | Reference-to-video with up to 12 images, clips, and audio; first, middle, and last frames (preview) |
<!-- END:LATEST -->

Looking for an older release? Every capsule is in the [CHANGELOG](CHANGELOG.md). Don't see the model we need? [Open an issue](https://github.com/microsoft-foundry/model-releases/issues/new) — requests shape what we build next.

<br/>

## How do I get started?

Three steps, and the first two happen only once:

1. **Open in GitHub Codespaces** with the button above — Python, the Azure CLI, and every package are already installed.
2. **Run [setup.ipynb](setup.ipynb).** It signs us in, connects or creates a Microsoft Foundry project, and writes the `.env` every capsule reads.
3. **Open a capsule and run it top to bottom.** Its first cell lists the models to deploy, and the env check names anything still missing.

<br/>

## How do we learn the most from a capsule?

Every capsule follows the same order — **release at a glance → env check → numbered steps → Your Turn to Explore → summary** — so after one, the rest feel familiar.

Running the cells shows us what the model *can* do. Changing them shows us what it does *for us*. In **Your Turn to Explore**, we swap in our own prompts or data, predict the result, run it, and compare.

When a cell fails, we treat it as a clue:

| What we see | What it usually means | What to try |
|---|---|---|
| The env check lists missing names | A setting isn't in `.env` yet | Re-run [setup.ipynb](setup.ipynb), or add the listed variables |
| `401` / `403` | Wrong key, or our identity lacks access | Check the key in `.env` and our role on the Foundry project |
| `404` model or deployment not found | The deployment name doesn't match the portal | Match it exactly — names are case-sensitive |
| The output surprises us | The model behaves differently on our input | Change one thing, re-run, compare |

Still stuck? [Open an issue](https://github.com/microsoft-foundry/model-releases/issues/new) with the failing cell's output.

<br/>

## New to these models? Which primer should we read first?

Each primer explains one model category in plain language — what it is, when to reach for it, when *not* to — and links to a capsule where we can try it.

| Primer | Read it when we want to… |
|---|---|
| [Chat Completion](3-primers/chat-completion.md) | Understand how instruction-following and dialogue models work |
| [Reasoning](3-primers/reasoning-models.md) | Know when an extended-thinking model is worth the extra cost |
| [Function Calling](3-primers/function-calling.md) | Let a model call our tools and APIs |
| [Multimodal](3-primers/multimodal-models.md) | Send images or audio alongside text |
| [Long Context](3-primers/long-context.md) | Fit whole documents or codebases into one prompt |
| [Embeddings](3-primers/embeddings.md) | Search and compare text by meaning |
| [Image Generation](3-primers/image-generation.md) | Create or edit images from a prompt |
| [Video Generation](3-primers/video-generation.md) | Turn a prompt, image, or references into a short clip with sound |
| [Audio / Speech](3-primers/audio-speech.md) | Transcribe speech or generate a voice |
| [Decision Models](3-primers/decision-models.md) | Classify, route, gate, or score inputs with typed answers instead of prose |
| [Robotics (VLA)](3-primers/robotics.md) | See how vision-language-action models turn instructions into robot motion |
| [Fine-tuning](3-primers/fine-tuning.md) | Customize a model for our domain |
| [Model Router](3-primers/model-router.md) | Let one endpoint pick the right model for each request |
| [Optimization](3-primers/optimization.md) | Lower cost and latency without losing quality |

<br/>

## Which scenarios do the labs share?

Most capsules work on one of two fictitious businesses, so we learn the data once and can compare models on the same inputs:

- **[Contoso Outdoors](2-scenarios/contoso-retail/)** — an online camping and hiking retailer with a product catalog, manuals, and photos. We use it for content and multimodal work: images, video, and speech about real products.
- **[Contoso Travel](2-scenarios/contoso-travel/)** — an enterprise travel concierge with flights, hotels, a travel policy, and a benchmark. We use it to measure and optimize an agent's cost, speed, and quality.

Each scenario's README describes its data and which capsules use it. See [2-scenarios/](2-scenarios/) for the full list.

<br/>

## How do capsules help an agent we already run?

A capsule is one step on the climb. We try a new model against the job our agent already does, and keep it only if the agent gets better:

```mermaid
flowchart LR
    S["Select<br/>a candidate model"] --> M{"Measure on our workload<br/>cost · speed · quality"}
    M -->|better| K["Keep it"]
    M -->|worse| R["Roll back,<br/>learn why"]
    K --> N["Next lever"]
    R --> N
    N --> M
    K -.once it holds.-> A["Scale<br/>automate the loop"]
```

- **Measure on shared data.** [Contoso Travel](2-scenarios/contoso-travel/) gives us a fixed workload and benchmark, so comparisons are fair.
- **See the full loop in action.** The [Model Router capsule](4-models/model-router/) optimizes instructions first, then routes each request to a right-sized model.
- **Learn the vocabulary of the climb** — tokenomics, right-sizing, hill climbing — in the [Optimization primer](3-primers/optimization.md).

<br/>

## What else is in this repo?

Folders are numbered in the order we build on them: tools and data first, then explainers, then release capsules from single models to multi-model scenarios.

| Folder | What we'll find |
|---|---|
| [`0-archive/`](0-archive/) | Release capsules for models that have been retired |
| [`1-scripts/`](1-scripts/) | Setup, banner, and content-check scripts |
| [`2-scenarios/`](2-scenarios/) | Fictitious business scenarios that capsules share, so results are reproducible |
| [`3-primers/`](3-primers/) | Beginner-friendly explainers for each model category |
| [`4-models/`](4-models/) | Release capsules for **one model** — one folder per release |
| [`5-multi-model/`](5-multi-model/) | Release capsules that compare or combine **several models** on a real task |
| [`setup.ipynb`](setup.ipynb) | One-time setup every capsule relies on |

<br/>

## Where can we go next?

- **[Model Mondays](https://aka.ms/model-mondays)** — a weekly livestream on new models in Microsoft Foundry.
- **[Model Mastery](https://aka.ms/model-mastery)** — hands-on workshops that go deeper.
- **Want to add a capsule, primer, or scenario?** [CONTRIBUTING.md](CONTRIBUTING.md) walks through it, and the GitHub Copilot skills in this repo handle most of the scaffolding.

<br/>

## Did an old link break?

We reorganized the repo in November 2026 so capsules are faster to find:

| Old path | New path |
|---|---|
| `models/<publisher>/<model>/` | [`4-models/<model>/`](4-models/) |
| `models/model-router/aug-2026/` | [`4-models/model-router/`](4-models/model-router/) |
| `models/<publisher>/multi-model-scenarios/<name>/` | [`5-multi-model/<name>/`](5-multi-model/) |
| `models/quickstart/` | [`setup.ipynb`](setup.ipynb) |
| `docs/primers/` and `docs/GLOSSARY.md` | [`3-primers/`](3-primers/) |
| `demos/` | [`2-scenarios/`](2-scenarios/) |
| `CAPSULE-TOC.md`, publisher READMEs | [`CHANGELOG.md`](CHANGELOG.md) |
