# Changelog

Every new model release available on Microsoft Foundry gets one row
below. Newest first.

**Rows may be added before a capsule exists** — the announcement +
model card + pricing links are enough. A later [`add-capsule`](.github/skills/add-capsule/)
run updates the same row in place with the capsule link and any missing
fields, so this table is the single source of truth for what's landed.
The Model cell links directly to the model card when known (no separate
Model card column).

| Date | Family | Model | Capabilities | Pricing | Capsule |
|---|---|---|---|---|---|
| [2026-07-29](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/introducing-gpt-transcribe-and-gpt-live-transcribe-in-microsoft-foundry/4541740) | Azure OpenAI | GPT-transcribe | Audio / Speech | [$0.27 / audio hour _(Global Standard)_](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/introducing-gpt-transcribe-and-gpt-live-transcribe-in-microsoft-foundry/4541740) | _—_ |
| [2026-07-29](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/introducing-gpt-transcribe-and-gpt-live-transcribe-in-microsoft-foundry/4541740) | Azure OpenAI | GPT-live-transcribe | Audio / Speech | [$1.02 / audio hour _(Global Standard)_](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/introducing-gpt-transcribe-and-gpt-live-transcribe-in-microsoft-foundry/4541740) | _—_ |
| [2026-07-28](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/introducing-kimi-k3-through-fireworks-ai-on-microsoft-foundry/4540187) | Fireworks | Kimi K3 | Chat Completion · Long Context | [$3.30 / 1M in · $16.50 / 1M out · $0.33 / 1M cached _(Data Zone)_](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/introducing-kimi-k3-through-fireworks-ai-on-microsoft-foundry/4540187) | _—_ |
| [2026-07-24](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/claude-opus-5-is-available-today-in-microsoft-foundry/4535068) | Anthropic | Claude Opus 5 | Chat Completion · Reasoning · Multimodal · Function Calling | _—_ | _—_ |
| [2026-07-23](https://microsoft.ai/news/introducing-mai-image-2-5-pro-and-mai-voice-2-flash/) | Microsoft AI | [MAI-Image-2.5-Pro](https://ai.azure.com/catalog/models/MAI-Image-2.5-Pro) | Image Generation | [$5 / 1M text-in · $106 / 1M image-out](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/introducing-mai-image-2-5-pro-and-mai-voice-2-flash-in-microsoft-foundry/4539446) | [capsule](models/microsoft-ai/mai-image-2.5-pro/2026-07-23/) |
| [2026-07-23](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/introducing-mai-image-2-5-pro-and-mai-voice-2-flash-in-microsoft-foundry/4539446) | Microsoft AI | MAI-Voice-2 Flash | Audio / Speech | [$15 / 1M characters](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/introducing-mai-image-2-5-pro-and-mai-voice-2-flash-in-microsoft-foundry/4539446) | _—_ |
| [2026-06-02](https://microsoft.ai/news/microsoft-build-2026-mai-keynote-transcript/) | Microsoft AI | [MAI-Image-2.5-Flash](https://ai.azure.com/catalog/models/MAI-Image-2.5-Flash) | Image Generation | _—_ | [capsule](models/microsoft-ai/mai-image-2.5-flash/2026-06-02/) |
| [2026-06-02](https://microsoft.ai/news/microsoft-build-2026-mai-keynote-transcript/) | Microsoft AI | [MAI-Image-2.5](https://ai.azure.com/catalog/models/MAI-Image-2.5) | Image Generation | [$0.05 / image](https://microsoft.ai/models/mai-image-2-5/) | [capsule](models/microsoft-ai/mai-image-2.5/2026-06-02/) |

<!-- Row template (prepended by add-capsule, or added manually for
announcement-only entries). The Model cell links to the model card
when known (plain text otherwise). Both Date and Pricing cells link
to the source of that fact — an official pricing page when one
exists, otherwise the blog post the price was extracted from — so
every pricing figure is verifiable:
| [YYYY-MM-DD](announcement-URL) | <Family> | [<Model>](model-card-URL) | Tag · Tag | [<pricing summary>](pricing-source-URL) | [capsule](models/<family>/<model>/<YYYY-MM-DD>/) |
-->
