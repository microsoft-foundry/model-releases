---
kind: publisher
name: Microsoft AI
slug: microsoft-ai
one_line: MAI model family — image, voice, transcription, reasoning, and coding.
provider: Microsoft
related_primers: [image-generation, audio-speech, reasoning-models, chat-completion]
---

# Microsoft AI Models on Microsoft Foundry

> **MAI models** are Microsoft's first-party model family, announced at Microsoft Build 2026.
> The family spans image generation and editing, speech synthesis, audio transcription,
> reasoning, and code completion — all available on Microsoft Foundry.

## Why it matters

The MAI family covers the full range of common production AI workloads under a single
Foundry provider:

- **Image** — text-to-image generation and precise editing (MAI-Image-2.5, Flash, Pro)
- **Voice** — speech synthesis with fine-grained emotional control across 15 languages (MAI-Voice-2, Flash)
- **Transcription** — high-accuracy transcription in 43 languages (MAI-Transcribe-1.5)
- **Reasoning** — mid-weight 35B MoE with 256K context for complex reasoning and SWE tasks (MAI-Thinking-1)
- **Coding** — 5B-parameter model tuned for VS Code and GitHub Copilot (MAI-Code-1-Flash)

All models are available on Microsoft Foundry and support fine-tuning via
[Microsoft Frontier Tuning](https://microsoft.ai/models/).

## Members

> **Expires** = model deprecation date when known; `—` means no announced retirement date.

| Model | Capabilities | Model card | Released | Expires | Capsule |
|---|---|---|---|---|---|
| MAI-Image-2.5 | Image Generation | [Foundry catalog](https://ai.azure.com/catalog/models/MAI-Image-2.5) | 2026-06-02 | — | [capsule](mai-image-2.5/) |
| MAI-Image-2.5-Flash | Image Generation | [Foundry catalog](https://ai.azure.com/catalog/models/MAI-Image-2.5-Flash) | 2026-06-02 | — | [capsule](mai-image-2.5-flash/) |
| MAI-Image-2.5-Pro | Image Generation | [Foundry catalog](https://ai.azure.com/catalog/models/MAI-Image-2.5-Pro) | 2026-07-23 | — | [capsule](mai-image-2.5-pro/) |
| MAI-Voice-2 | Audio / Speech | [Foundry catalog](https://ai.azure.com/catalog/models/MAI-Voice-2) | 2026-06-02 | — | _—_ |
| MAI-Voice-2-Flash | Audio / Speech | [Foundry catalog](https://ai.azure.com/catalog/models/MAI-Voice-2-Flash) | 2026-07-23 | — | _—_ |
| MAI-Transcribe-1.5 | Audio / Speech | [Foundry catalog](https://ai.azure.com/catalog/models/MAI-Transcribe-1.5) | 2026-06-02 | — | [capsule](mai-transcribe-1.5/) |
| MAI-Transcribe-1 | Audio / Speech | _—_ | _—_ | 2026-08-20 | _—_ |
| MAI-Thinking-1 | Reasoning · Chat Completion | [Foundry catalog](https://ai.azure.com/catalog/models/MAI-Thinking-1) | 2026-06-02 | — | _—_ |
| MAI-Code-1-Flash | Chat Completion | [Foundry catalog](https://ai.azure.com/catalog/models/MAI-Code-1-Flash) | 2026-06-02 | — | _—_ |

## Multi-model scenarios

Walkthroughs that span more than one release in this family, so they can't live in any single capsule.

| Scenario | Models | Description |
|---|---|---|
| [MAI-Image family walkthrough](multi-model-scenarios/mai-image-family-walkthrough/) | MAI-Image-2.5 · Flash · Pro | Compare all three variants on the same prompts |

## Learn more

### Usage guides

- [Use MAI image models in Microsoft Foundry](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/how-to/use-foundry-models-mai-image?tabs=python)
- [MAI voices — MAI-Voice-2 and Flash](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/mai-voices?context=%2Fazure%2Ffoundry%2Fcontext%2Fcontext&tabs=mai-voice-2-flash&pivots=ai-foundry)
- [MAI transcription — MAI-Transcribe-1.5](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/mai-transcribe?context=%2Fazure%2Ffoundry%2Fcontext%2Fcontext&pivots=ai-foundry)
- [Microsoft Foundry Models overview](https://learn.microsoft.com/en-us/azure/foundry/concepts/foundry-models-overview)

### Announcements

- [Build 2026 MAI keynote](https://microsoft.ai/news/microsoft-build-2026-mai-keynote-transcript/) — MAI-Image-2.5, Flash, MAI-Voice-2, MAI-Transcribe-1.5, MAI-Thinking-1, MAI-Code-1-Flash (2026-06-02)
- [Introducing MAI-Image-2.5-Pro and MAI-Voice-2-Flash](https://microsoft.ai/news/introducing-mai-image-2-5-pro-and-mai-voice-2-flash/) (2026-07-23)
- [MAI-Voice-2 release](https://microsoft.ai/news/mai-voice-2/)

### Background

- [Image generation primer](../../docs/primers/image-generation.md)
- [Audio / Speech primer](../../docs/primers/audio-speech.md)
- [Reasoning models primer](../../docs/primers/reasoning-models.md)
- [Chat completion primer](../../docs/primers/chat-completion.md)
- [Glossary](../../docs/GLOSSARY.md)
