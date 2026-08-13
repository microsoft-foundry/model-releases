# Microsoft Foundry Model Release Changelog

Every new model release on Microsoft Foundry, newest first, grouped by month.

Each row links out to what you need: the date to the announcement, the model to its card, the publisher to its catalog view. Capability tags like Chat Completion or Image Generation each have a [primer](docs/README.md#learn-about-model-capabilities) if the term is new to you. A row here is an announcement, not a tutorial - when we've built a runnable notebook for a release, it's listed in the [CAPSULE-TOC](CAPSULE-TOC.md).

## August 2026

| Date | Publisher | Model | Capabilities |
|---|---|---|---|
| [2026-08-12](https://microsoft.ai/news/introducing-mai-thinking-1) | [Microsoft AI](https://ai.azure.com/catalog/models?publisher=microsoft) | [MAI-Thinking-1](https://ai.azure.com/catalog/models/MAI-Thinking-1)<br>_(public preview)_ | Reasoning · Chat Completion · Function Calling · Long Context |
| [2026-08-11](https://microsoft.ai/news/mai-code-1-1-flash-br-better-faster-at-a-quarter-of-the-cost) | [Microsoft AI](https://ai.azure.com/catalog/models?publisher=microsoft) | [MAI-Code-1.1-Flash](https://microsoft.ai/models/mai-code-1-flash/)<br>_(GitHub Copilot and VS Code)_ | Chat Completion |
| [2026-08-10](https://microsoft.ai/news/mai-image-2-6-launches-at-no-2-on-arena-ahead-of-google-meta-and-xai) | [Microsoft AI](https://ai.azure.com/catalog/models?publisher=microsoft) | MAI-Image-2.6<br>_(not yet in Foundry)_ | Image Generation |

## July 2026

| Date | Publisher | Model | Capabilities |
|---|---|---|---|
| [2026-07-29](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/introducing-gpt-transcribe-and-gpt-live-transcribe-in-microsoft-foundry/4541740) | [Azure OpenAI](https://ai.azure.com/catalog/models?publisher=openai) | [GPT-transcribe](https://ai.azure.com/catalog/models/gpt-transcribe) | Audio / Speech |
| [2026-07-29](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/introducing-gpt-transcribe-and-gpt-live-transcribe-in-microsoft-foundry/4541740) | [Azure OpenAI](https://ai.azure.com/catalog/models?publisher=openai) | [GPT-live-transcribe](https://ai.azure.com/catalog/models/gpt-live-transcribe) | Audio / Speech |
| [2026-07-28](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/introducing-kimi-k3-through-fireworks-ai-on-microsoft-foundry/4540187) | [Fireworks](https://ai.azure.com/catalog/models?publisher=fireworks) | [Kimi K3](https://ai.azure.com/catalog/models/FW-Kimi-K3) | Chat Completion · Long Context |
| [2026-07-24](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/claude-opus-5-is-available-today-in-microsoft-foundry/4535068) | [Anthropic](https://ai.azure.com/catalog/models?publisher=anthropic) | [Claude Opus 5](https://ai.azure.com/catalog/models/claude-opus-5) | Chat Completion · Reasoning · Multimodal · Function Calling |
| [2026-07-23](https://microsoft.ai/news/introducing-mai-image-2-5-pro-and-mai-voice-2-flash/) | [Microsoft AI](https://ai.azure.com/catalog/models?publisher=microsoft) | [MAI-Image-2.5-Pro](https://ai.azure.com/catalog/models/MAI-Image-2.5-Pro) | Image Generation |
| [2026-07-23](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/introducing-mai-image-2-5-pro-and-mai-voice-2-flash-in-microsoft-foundry/4539446) | [Microsoft AI](https://ai.azure.com/catalog/models?publisher=microsoft) | [MAI-Voice-2-Flash](https://ai.azure.com/catalog/models/MAI-Voice-2-Flash) | Audio / Speech |

## June 2026

| Date | Publisher | Model | Capabilities |
|---|---|---|---|
| [2026-06-02](https://microsoft.ai/news/mai-transcribe-1-5more-accurate-context-aware-and-built-for-production/) | [Microsoft AI](https://ai.azure.com/catalog/models?publisher=microsoft) | [MAI-Transcribe-1.5](https://ai.azure.com/catalog/models/MAI-Transcribe-1.5) | Audio / Speech |
| [2026-06-02](https://microsoft.ai/news/microsoft-build-2026-mai-keynote-transcript/) | [Microsoft AI](https://ai.azure.com/catalog/models?publisher=microsoft) | [MAI-Image-2.5-Flash](https://ai.azure.com/catalog/models/MAI-Image-2.5-Flash) | Image Generation |
| [2026-06-02](https://microsoft.ai/news/microsoft-build-2026-mai-keynote-transcript/) | [Microsoft AI](https://ai.azure.com/catalog/models?publisher=microsoft) | [MAI-Image-2.5](https://ai.azure.com/catalog/models/MAI-Image-2.5) | Image Generation |

<!-- Row template (prepended by add-capsule, or added manually for
announcement-only entries). Rows live under a `## <Month> <Year>`
heading, newest month first; add a new heading + table header when the
month changes. The Model cell must link to the model's catalog page at
`https://ai.azure.com/catalog/models/<slug>`, using the exact slug the
catalog uses — it is not always the marketing name (`Claude Opus 5` is
`claude-opus-5`, `Kimi K3` is `FW-Kimi-K3`). The announcement post is
the best source for it: these posts link the model card directly. To
hunt for one, browse `?publisher=<slug>&search=<term>` in a browser —
the catalog's own search — but record the clean
`/catalog/models/<slug>` URL here, never the one carrying the
`?publisher=&search=` parameters you found it with. Note a
publisher-filtered page shows at most 51 models and its search runs in
the browser, so a model missing from a fetched page has not been ruled
out. Leave the cell as plain text only when the model has
no catalog entry yet, which is the case for releases announced before
they reach Foundry. The Date cell links to the announcement it came
from. Pricing is deliberately not tracked here — rates change and vary
by region, tier, and deployment type, so a frozen figure in a
changelog goes stale silently. The model card is the source of truth
for price; capsules link to it.
When the announcement states an availability stage, append it to the
Model cell in italic parentheses after a `<br>`, so it sits on its own
line — `[Model](url)<br>_(public preview)_`,
`Model<br>_(not yet in Foundry)_` — and leave it off when the post
doesn't say. The `<br>` is not decoration: without it the annotation
widens the Model column by its full length, which squeezes Date and
Publisher until they wrap mid-value. Parsers strip the `<br>` and the
annotation together, so neither becomes part of the model
name. The Publisher cell links to that publisher's filtered catalog
view at `https://ai.azure.com/catalog/models?publisher=<slug>`. The
slug is the catalog's display name, not our folder name — it can carry
a space (`mistral ai`, `hugging face`, url-encoded as `%20`) and drops
qualifiers we keep (`microsoft-ai` is `microsoft`, `azure-openai` is
`openai`). An unrecognized value silently returns the unfiltered
catalog rather than erroring, so confirm the filter actually applied.
`docs/README.md` lists the mapping for every publisher we track. Capsules
are tracked in `CAPSULE-TOC.md`, not linked per row:

## <Month> <Year>

| Date | Publisher | Model | Capabilities |
|---|---|---|---|
| [YYYY-MM-DD](announcement-URL) | [<Publisher>](publisher-catalog-URL) | [<Model>](model-card-URL) | Tag · Tag |
-->
