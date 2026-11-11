# Planning

Maintainer backlog. Pick an item, build its capsule with the `add-capsule` skill, then delete the item here.

## Releases without a capsule

| Date | Model | Publisher | Capabilities | Source |
|---|---|---|---|---|
| 2026-08-12 | [MAI-Thinking-1](https://ai.azure.com/catalog/models/MAI-Thinking-1) _(public preview)_ | Microsoft AI | Reasoning · Chat Completion · Function Calling · Long Context | [post](https://microsoft.ai/news/introducing-mai-thinking-1) |
| 2026-08-11 | [MAI-Code-1.1-Flash](https://microsoft.ai/models/mai-code-1-flash/) _(GitHub Copilot and VS Code)_ | Microsoft AI | Chat Completion | [post](https://microsoft.ai/news/mai-code-1-1-flash-br-better-faster-at-a-quarter-of-the-cost) |
| 2026-07-29 | [GPT-transcribe](https://ai.azure.com/catalog/models/gpt-transcribe) | Azure OpenAI | Audio / Speech | [post](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/introducing-gpt-transcribe-and-gpt-live-transcribe-in-microsoft-foundry/4541740) |
| 2026-07-29 | [GPT-live-transcribe](https://ai.azure.com/catalog/models/gpt-live-transcribe) | Azure OpenAI | Audio / Speech | [post](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/introducing-gpt-transcribe-and-gpt-live-transcribe-in-microsoft-foundry/4541740) |
| 2026-07-28 | [Kimi K3](https://ai.azure.com/catalog/models/FW-Kimi-K3) | Fireworks | Chat Completion · Long Context | [post](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/introducing-kimi-k3-through-fireworks-ai-on-microsoft-foundry/4540187) |
| 2026-07-24 | [Claude Opus 5](https://ai.azure.com/catalog/models/claude-opus-5) | Anthropic | Chat Completion · Reasoning · Multimodal · Function Calling | [post](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/claude-opus-5-is-available-today-in-microsoft-foundry/4535068) |
| 2026-07-23 | [MAI-Voice-2-Flash](https://ai.azure.com/catalog/models/MAI-Voice-2-Flash) | Microsoft AI | Audio / Speech | [post](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/introducing-mai-image-2-5-pro-and-mai-voice-2-flash-in-microsoft-foundry/4539446) |

## Capsule follow-ups

- **Model Router** — planned notebooks, each named `model-router-<mmm-yyyy>-NN-<topic>.ipynb`:
  routing modes (Cost vs. Quality), custom model subset, deployment types and Data Zone,
  automatic failover, agentic routing across providers, and per-agent routers with the refreshed model pool.
- **2-scenarios/contoso-outdoors** — a second shared scenario for reproducible samples.
- **Microsoft-Decision-1** — decision model for gates, routing, and scoring; a good fit for the Contoso Travel scenario (route requests, flag policy breaches). See the [announcement](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/introducing-microsoft-decision-1-in-microsoft-foundry-for-decision-and-classific/4562742), [model card](https://ai.azure.com/catalog/models/Microsoft-Decision-1), and [Learn how-to](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/how-to/use-foundry-models-microsoft-decision). Primer: [decision-models](../3-primers/decision-models.md).
- **Rho-alpha (ρα)** — Microsoft Research VLA robotics model; build a capsule once it's available in Microsoft Foundry. See the [announcement](https://www.microsoft.com/en-us/research/story/advancing-ai-for-the-physical-world/). Primer: [robotics](../3-primers/robotics.md).

## Publishers with no capsule yet

| Publisher | Catalog |
|---|---|
| Azure OpenAI | [Browse](https://ai.azure.com/catalog/models?publisher=openai) |
| Anthropic | [Browse](https://ai.azure.com/catalog/models?publisher=anthropic) |
| Meta | [Browse](https://ai.azure.com/catalog/models?publisher=meta) |
| Cohere | [Browse](https://ai.azure.com/catalog/models?publisher=cohere) |
| Mistral | [Browse](https://ai.azure.com/catalog/models?publisher=mistral%20ai) |
| Hugging Face | [Browse](https://ai.azure.com/catalog/models?publisher=hugging%20face) |
| Fireworks | [Browse](https://ai.azure.com/catalog/models?publisher=fireworks) |
| DeepSeek | [Browse](https://ai.azure.com/catalog/models?publisher=deepseek) |
| xAI | [Browse](https://ai.azure.com/catalog/models?publisher=xai) |
| Black Forest Labs | [Browse](https://ai.azure.com/catalog/models?publisher=black%20forest%20labs) |
| NVIDIA | [Browse](https://ai.azure.com/catalog/models?publisher=nvidia) — NIM candidates: Nemotron 3 (Nano, Super, Ultra), Nemotron-Nano-12B-v2-VL, Nemotron-Parse, Nemotron-3-Content-Safety, NV-EmbedQA / RerankQA, Cosmos-Reason1, Trellis, OpenFold, Boltz2, Evo2, Earth-2 FCN3 |

Catalog filter values are the catalog's display names, not our folder names (`microsoft-ai` is `microsoft`, `azure-openai` is `openai`), and an unrecognized value silently returns the unfiltered catalog.
