# Microsoft Foundry Model Release Changelog

Every new model release on Microsoft Foundry, newest first, grouped by month.

Each row links out to what you need: the date to the announcement, the model to its card, the price to the page it came from. Capability tags like Chat Completion or Image Generation each have a [primer](docs/README.md#learn-about-model-capabilities) if the term is new to you. A row here is an announcement, not a tutorial - when we've built a runnable notebook for a release, it's listed in the [CAPSULE-TOC](CAPSULE-TOC.md).

> [!IMPORTANT]
> **Pricing here is a point-in-time snapshot.** Every figure was read from the linked blog post on the day the release was scanned, and is never updated afterward - it records what was announced, not what you'll be charged. Rates change, and a single row can't capture regional, tier, or deployment-type differences. **Always check the model card for current pricing before you budget against it.**

## August 2026

| Date | Publisher | Model | Capabilities | Pricing |
|---|---|---|---|---|
| [2026-08-12](https://microsoft.ai/news/introducing-mai-thinking-1) | [Microsoft AI](https://ai.azure.com/catalog/models?publisher=microsoft) | [MAI-Thinking-1](https://ai.azure.com/catalog/models/MAI-Thinking-1) _(public preview)_ | Reasoning · Chat Completion · Function Calling · Long Context | _—_ |
| [2026-08-11](https://microsoft.ai/news/mai-code-1-1-flash-br-better-faster-at-a-quarter-of-the-cost) | [Microsoft AI](https://ai.azure.com/catalog/models?publisher=microsoft) | [MAI-Code-1.1-Flash](https://microsoft.ai/models/mai-code-1-flash/) _(GitHub Copilot and VS Code)_ | Chat Completion | _—_ |
| [2026-08-10](https://microsoft.ai/news/mai-image-2-6-launches-at-no-2-on-arena-ahead-of-google-meta-and-xai) | [Microsoft AI](https://ai.azure.com/catalog/models?publisher=microsoft) | MAI-Image-2.6 _(not yet in Foundry)_ | Image Generation | _—_ |

## July 2026

| Date | Publisher | Model | Capabilities | Pricing |
|---|---|---|---|---|
| [2026-07-29](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/introducing-gpt-transcribe-and-gpt-live-transcribe-in-microsoft-foundry/4541740) | [Azure OpenAI](https://ai.azure.com/catalog/models?publisher=openai) | GPT-transcribe | Audio / Speech | [$0.27 / audio hour _(Global Standard)_](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/introducing-gpt-transcribe-and-gpt-live-transcribe-in-microsoft-foundry/4541740) |
| [2026-07-29](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/introducing-gpt-transcribe-and-gpt-live-transcribe-in-microsoft-foundry/4541740) | [Azure OpenAI](https://ai.azure.com/catalog/models?publisher=openai) | GPT-live-transcribe | Audio / Speech | [$1.02 / audio hour _(Global Standard)_](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/introducing-gpt-transcribe-and-gpt-live-transcribe-in-microsoft-foundry/4541740) |
| [2026-07-28](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/introducing-kimi-k3-through-fireworks-ai-on-microsoft-foundry/4540187) | [Fireworks](https://ai.azure.com/catalog/models?publisher=fireworks) | [Kimi K3](https://ai.azure.com/catalog/models/FW-Kimi-K3) | Chat Completion · Long Context | [$3.30 / 1M in · $16.50 / 1M out · $0.33 / 1M cached _(Data Zone)_](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/introducing-kimi-k3-through-fireworks-ai-on-microsoft-foundry/4540187) |
| [2026-07-24](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/claude-opus-5-is-available-today-in-microsoft-foundry/4535068) | [Anthropic](https://ai.azure.com/catalog/models?publisher=anthropic) | [Claude Opus 5](https://ai.azure.com/catalog/models/claude-opus-5) | Chat Completion · Reasoning · Multimodal · Function Calling | _—_ |
| [2026-07-23](https://microsoft.ai/news/introducing-mai-image-2-5-pro-and-mai-voice-2-flash/) | [Microsoft AI](https://ai.azure.com/catalog/models?publisher=microsoft) | [MAI-Image-2.5-Pro](https://ai.azure.com/catalog/models/MAI-Image-2.5-Pro) | Image Generation | [$5 / 1M text-in · $106 / 1M image-out](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/introducing-mai-image-2-5-pro-and-mai-voice-2-flash-in-microsoft-foundry/4539446) |
| [2026-07-23](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/introducing-mai-image-2-5-pro-and-mai-voice-2-flash-in-microsoft-foundry/4539446) | [Microsoft AI](https://ai.azure.com/catalog/models?publisher=microsoft) | MAI-Voice-2 Flash | Audio / Speech | [$15 / 1M characters](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/introducing-mai-image-2-5-pro-and-mai-voice-2-flash-in-microsoft-foundry/4539446) |

## June 2026

| Date | Publisher | Model | Capabilities | Pricing |
|---|---|---|---|---|
| [2026-06-02](https://microsoft.ai/news/mai-transcribe-1-5more-accurate-context-aware-and-built-for-production/) | [Microsoft AI](https://ai.azure.com/catalog/models?publisher=microsoft) | [MAI-Transcribe-1.5](https://ai.azure.com/catalog/models/MAI-Transcribe-1.5) | Audio / Speech | [$0.36 / audio hour](https://microsoft.ai/models/mai-transcribe-1-5/) |
| [2026-06-02](https://microsoft.ai/news/microsoft-build-2026-mai-keynote-transcript/) | [Microsoft AI](https://ai.azure.com/catalog/models?publisher=microsoft) | [MAI-Image-2.5-Flash](https://ai.azure.com/catalog/models/MAI-Image-2.5-Flash) | Image Generation | _—_ |
| [2026-06-02](https://microsoft.ai/news/microsoft-build-2026-mai-keynote-transcript/) | [Microsoft AI](https://ai.azure.com/catalog/models?publisher=microsoft) | [MAI-Image-2.5](https://ai.azure.com/catalog/models/MAI-Image-2.5) | Image Generation | [$0.05 / image](https://microsoft.ai/models/mai-image-2-5/) |

<!-- Row template (prepended by add-capsule, or added manually for
announcement-only entries). Rows live under a `## <Month> <Year>`
heading, newest month first; add a new heading + table header when the
month changes. The Model cell must link to the model's catalog page at
`https://ai.azure.com/catalog/models/<slug>`, using the exact slug the
catalog uses — it is not always the marketing name (`Claude Opus 5` is
`claude-opus-5`). Leave the cell as plain text only when the model has
no catalog entry yet, which is the case for releases announced before
they reach Foundry. Both Date and Pricing cells link to the source
of that fact — an official pricing page when one exists, otherwise the
blog post the price was extracted from — so every pricing figure is
verifiable. Record the price as stated at scan time and do not revise
it later; the note at the top of this file tells readers to check the
model card for current rates. Use `_—_` for an unknown price.
When the announcement states an availability stage, append it to the
Model cell in italic parentheses — `_(public preview)_`,
`_(not yet in Foundry)_` — and leave it off when the post doesn't say.
Parsers strip that annotation, so it never becomes part of the model
name. The Publisher cell links to that publisher's filtered catalog
view at `https://ai.azure.com/catalog/models?publisher=<slug>`, using
the catalog's publisher slug rather than the repo folder name
(`microsoft-ai` is `microsoft`, `azure-openai` is `openai`). Capsules
are tracked in `CAPSULE-TOC.md`, not linked per row:

## <Month> <Year>

| Date | Publisher | Model | Capabilities | Pricing |
|---|---|---|---|---|
| [YYYY-MM-DD](announcement-URL) | <Publisher> | [<Model>](model-card-URL) | Tag · Tag | [<pricing summary>](pricing-source-URL) |
-->
