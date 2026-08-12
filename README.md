# Microsoft Foundry Model Releases

The [Microsoft Foundry catalog](https://ai.azure.com/catalog) has thousands of models from Anthropic, Microsoft, OpenAI, xAI, Hugging Face, Meta, Mistral, Cohere, and NVIDIA - and new releases land almost daily. Keeping up is one thing. Knowing what a release actually does _differently_, and whether it's the right pick for your agent, is another.

That's what this repo is for:

1. **Catching up?** The [CHANGELOG](./CHANGELOG.md) has every announcement in one place.
2. **Want to try one?** Browse [models/](./models/) for a release _capsule_ - a runnable notebook that shows you what it does.
3. **Can't find the one you need?** [Open an issue](https://github.com/microsoft-foundry/model-releases/issues/new) and we'll backfill it.


## Changelog: What's New In Foundry Models?

Every new model release announcement gets a row here, with a link back to the original post plus the family, capabilities, and pricing at a glance. The three most recent:

<!-- BEGIN:RECENTLY-ADDED -->
| Release date | Model | Description |
| --- | --- | --- |
| [2026-07-29](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/introducing-gpt-transcribe-and-gpt-live-transcribe-in-microsoft-foundry/4541740) | **GPT-transcribe** | Real-time speech-to-text transcription via Azure OpenAI |
| [2026-07-29](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/introducing-gpt-transcribe-and-gpt-live-transcribe-in-microsoft-foundry/4541740) | **GPT-live-transcribe** | Live streaming speech-to-text transcription via Azure OpenAI |
| [2026-07-28](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/introducing-kimi-k3-through-fireworks-ai-on-microsoft-foundry/4540187) | **Kimi K3** | Chat completion and long-context model from Fireworks |
<!-- END:RECENTLY-ADDED -->

_See the full [CHANGELOG](./CHANGELOG.md) for everything else._


## Capsule: What Can I Do With This Release?

An announcement tells you a model exists. It doesn't tell you what it's like to use. So each capsule pairs the release with a notebook you can run - practical use cases, code-first - to show you:
- What *tasks* the family is good at
- What *new features* this release brings
- What *tradeoffs* it makes on cost, quality, and latency

Start with the [Quickstart](#quickstart-explore-model-releases-hands-on), then pick one:

<!-- BEGIN:RECENT-CAPSULES -->
| Capsule | Last updated | Description |
| --- | --- | --- |
| [MAI-Image-2.5-Pro](models/microsoft-ai/mai-image-2.5-pro/) | 2026-08-04 | Portraits, text rendering, visual reasoning |
| [MAI-Image-2.5](models/microsoft-ai/mai-image-2.5/) | 2026-08-11 | Text-to-image generation and editing |
| [MAI-Transcribe-1.5](models/microsoft-ai/mai-transcribe-1.5/) | 2026-08-07 | Multilingual transcription and keyword biasing |
<!-- END:RECENT-CAPSULES -->

_Browse [models/](./models/) for the rest._


## Quickstart: Explore Model Releases Hands-on

Want to run a capsule notebook? Four steps, and the first two are one-time setup:

1. **Open in GitHub Codespaces** - you get a ready-to-run environment, no local install.
2. **Do the [quickstart](./models/quickstart/)** once, to set up a Foundry project and your `.env`.
3. **Pick a capsule** - `models/` is organized by provider, then release. Ex: `models/microsoft-ai/mai-image-2.5/`.
4. **Open its notebook in VS Code**, select the kernel, and run.

Each notebook is yours to break - change the prompts, swap the inputs, and try it against your own scenario.


## Reference: Where do I learn more?

Want the background - how this repo is organized, what the model families and capability tags mean, or how to contribute a capsule of your own? It's all in the [reference guide](./docs/README.md).

| Topic | What you'll find |
| --- | --- |
| [Repository structure](./docs/README.md#repository-what-resources-can-i-find-here) | How `docs/`, `models/`, and the capsules fit together |
| [Model families](./docs/README.md#learn-about-model-families) | Every provider and family we track, with links |
| [Model capabilities](./docs/README.md#learn-about-model-capabilities) | What each capability tag means, plus a primer for each |
| [Contributing](./docs/README.md#contributing-how-can-i-add-new-content) | Add a capsule, family, capability, or glossary term |

New to the terminology? Start with the [glossary](./docs/GLOSSARY.md).
