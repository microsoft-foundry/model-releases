<!-- prettier-ignore -->
<p align="center">
  <img src="./docs/images/logo.png" alt="Model Releases from Microsoft Foundry" width="320" />
</p>

<p align="center">
  <b><i>Find the right model for your next agentic task.</i></b>
</p>

<p align="center">
  <a href="https://ai.azure.com/catalog/models"><img src="https://img.shields.io/badge/Microsoft_Foundry-catalog-00A4EF?style=flat-square" alt="Microsoft Foundry catalog" /></a>
  <a href="https://aka.ms/model-mondays"><img src="https://img.shields.io/badge/Model_Mondays-livestream-F25022?style=flat-square" alt="Model Mondays livestream" /></a>
  <a href="https://aka.ms/model-mastery"><img src="https://img.shields.io/badge/Model_Mastery-workshops-7FBA00?style=flat-square" alt="Model Mastery workshops" /></a>
  <a href="./LICENSE"><img src="https://img.shields.io/badge/License-MIT-FFB900?style=flat-square" alt="License: MIT" /></a>
</p>

<p align="center">
  <a href="#changelog-whats-new-in-foundry-models">Changelog</a> &nbsp;•&nbsp;
  <a href="#capsule-what-can-i-do-with-this-release">Capsules</a> &nbsp;•&nbsp;
  <a href="#quickstart-explore-model-releases-hands-on">Quickstart</a> &nbsp;•&nbsp;
  <a href="#reference-where-do-i-learn-more">Reference</a>
</p>

The [Microsoft Foundry catalog](https://ai.azure.com/catalog) has thousands of models from Anthropic, Microsoft, OpenAI, xAI, Hugging Face, Meta, Mistral, Cohere, and NVIDIA - and new releases land almost daily. Keeping up is one thing. Knowing what a release actually does *differently*, and whether it's the right pick for your agent, is another.

That's what this repo is for:

1. **Catching up?** The [CHANGELOG](./CHANGELOG.md) has every announcement in one place.
2. **Want to try one?** Browse [models/](./models/) for a release *capsule* - a runnable notebook that shows you what it does.
3. **Can't find the one you need?** [Open an issue](https://github.com/microsoft-foundry/model-releases/issues/new) and we'll backfill it.

<br/>

## Changelog: What's New In Foundry Models?

Every new model release announcement gets a row here, with a link back to the original post plus the publisher and capabilities at a glance. The three most recent:

<!-- BEGIN:RECENTLY-ADDED -->
| Model | Release date | Capabilities |
| --- | --- | --- |
| **MAI-Thinking-1** | [2026-08-12](https://microsoft.ai/news/introducing-mai-thinking-1) | Reasoning · Chat Completion · Function Calling · Long Context |
| **MAI-Code-1.1-Flash** | [2026-08-11](https://microsoft.ai/news/mai-code-1-1-flash-br-better-faster-at-a-quarter-of-the-cost) | Chat Completion |
| **MAI-Image-2.6** | [2026-08-10](https://microsoft.ai/news/mai-image-2-6-launches-at-no-2-on-arena-ahead-of-google-meta-and-xai) | Image Generation |
<!-- END:RECENTLY-ADDED -->

*See the full* [*CHANGELOG*](./CHANGELOG.md) *for everything else.*

<br/>

## Capsule: What Can I Do With This Release?

An announcement tells you a model exists. It doesn't tell you what it's like to use. So each capsule pairs the release with a notebook you can run - practical use cases, code-first - to show you:
- What *tasks* the publisher's models are good at
- What *new features* this release brings
- What *tradeoffs* it makes on cost, quality, and latency

Start with the [Quickstart](#quickstart-explore-model-releases-hands-on), then pick one:

<!-- BEGIN:RECENT-CAPSULES -->
| Capsule | Last updated | Description |
| --- | --- | --- |
| [MAI-Image-2.5](models/microsoft-ai/mai-image-2.5/) | 2026-08-11 | Generate and edit images from text prompts |
| [MAI-Transcribe-1.5](models/microsoft-ai/mai-transcribe-1.5/) | 2026-08-07 | Transcribe multilingual audio with keyword biasing |
| [MAI-Image-2.5-Pro](models/microsoft-ai/mai-image-2.5-pro/) | 2026-08-04 | Render portraits, in-image text, and complex scenes |
<!-- END:RECENT-CAPSULES -->

*See the full* [*CAPSULE-TOC*](./CAPSULE-TOC.md) *for everything else.*

<br/>

## Quickstart: Explore Model Releases Hands-on

Want to run a capsule notebook? Four steps, and the first two are one-time setup:

1. **Open in GitHub Codespaces** - you get a ready-to-run environment, no local install.
2. **Do the [quickstart](./models/quickstart/)** once, to set up a Foundry project and your `.env`.
3. **Pick a capsule** - `models/` is organized by provider, then release. Ex: `models/microsoft-ai/mai-image-2.5/`.
4. **Open its notebook in VS Code**, select the kernel, and run.

Each notebook is yours to break - change the prompts, swap the inputs, and try it against your own scenario.

<br/>

## Reference: Where do I learn more?

Want the background - how this repo is organized, what the publishers and capability tags mean, or how to contribute a capsule of your own? It's all in the [reference guide](./docs/README.md).

| Topic | What you'll find |
| --- | --- |
| [Repository structure](./docs/README.md#repository-what-resources-can-i-find-here) | How `docs/`, `models/`, and the capsules fit together |
| [Publishers](./docs/README.md#learn-about-publishers) | Every publisher we track, with links |
| [Model capabilities](./docs/README.md#learn-about-model-capabilities) | What each capability tag means, plus a primer for each |
| [Contributing](./docs/README.md#contributing-how-can-i-add-new-content) | Add a capsule, publisher, capability, or glossary term |
| [Using this repo from an agent](./docs/README.md#using-this-repo-from-an-agent) | `catalog.json` and `llms.txt` — the whole catalog in one fetch |

New to the terminology? Start with the [glossary](./docs/GLOSSARY.md).
