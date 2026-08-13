---
kind: capsule
publisher: microsoft-ai
model: mai-image-2.5-pro
summary: "Render portraits, in-image text, and complex scenes"
release_date: "2026-07-23"
last_updated: "2026-08-04"
capabilities: [image-generation]
model_card: https://ai.azure.com/catalog/models/MAI-Image-2.5-Pro
announcement: https://microsoft.ai/news/introducing-mai-image-2-5-pro-and-mai-voice-2-flash/
pricing:
  url: https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/introducing-mai-image-2-5-pro-and-mai-voice-2-flash-in-microsoft-foundry/4539446
  notes: "$5 / 1M text tokens in · $106 / 1M image tokens out"
dependencies: [requests]
domains: [brand-identity, editorial-photography, marketing]
notebooks:
  - path: mai-image-2.5-pro.ipynb
    title: "Portraits, text rendering, and visual reasoning with MAI-Image-2.5-Pro"
    concepts:
      - high-fidelity portrait generation
      - accurate text rendering in images
      - visual reasoning across complex scenes
---

# MAI-Image-2.5-Pro — Release Capsule

**Released:** 2026-07-23 · **Publisher:** [Microsoft AI](../README.md) · **Capability:** Image Generation

## Before You Begin

| Detail | Value |
|---|---|
| Model card | [MAI-Image-2.5-Pro — Foundry catalog](https://ai.azure.com/catalog/models/MAI-Image-2.5-Pro) |
| Announcement | [Introducing MAI-Image-2.5-Pro and MAI-Voice-2-Flash](https://microsoft.ai/news/introducing-mai-image-2-5-pro-and-mai-voice-2-flash/) |
| Pricing | $5 / 1M text tokens in · $106 / 1M image tokens out — [source](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/introducing-mai-image-2-5-pro-and-mai-voice-2-flash-in-microsoft-foundry/4539446) |
| Release date | 2026-07-23 |
| Deployment regions | West Central US · East US · West US · West Europe · Sweden Central · South India · UAE North |

See [models/quickstart/](../../quickstart/README.md) for first-time Foundry project setup.

**Required env variables:**

```
MICROSOFT_FOUNDRY_ENDPOINT          # e.g. https://<resource>.services.ai.azure.com/api/projects/<project>
MICROSOFT_FOUNDRY_API_KEY           # AIServices API key
AZURE_MAI_IMAGE_25_PRO_DEPLOYMENT   # your MAI-Image-2.5-Pro deployment name
```

## Notebook

| Notebook | Concepts |
|---|---|
| [mai-image-2.5-pro.ipynb](mai-image-2.5-pro.ipynb) | High-fidelity portraits · Accurate text rendering · Visual reasoning |

**MAI-Image-2.5-Pro** extends the base MAI-Image-2.5 with stronger capabilities for complex scenes:

- **High-fidelity portraits** — accurate facial structure, natural skin tones, consistent lighting
- **Text rendering** — readable labels, signage, and packaging text within generated images
- **Visual reasoning** — coherent spatial relationships, object consistency, and material accuracy
- **Character consistency** — same person recognisable across poses, angles, and lighting conditions

If you are new to the family, start with [MAI-Image-2.5](../mai-image-2.5/) to understand the baseline generation and editing APIs.

## API endpoints

| API | URL pattern | Body |
|---|---|---|
| Image generations | `https://<resource>.services.ai.azure.com/mai/v1/images/generations` | JSON |
| Image edits | `https://<resource>.services.ai.azure.com/mai/v1/images/edits` | multipart/form-data |

Constraints: `width` and `height` both ≥ 768; `width × height` ≤ 1,048,576. Output is always PNG.

## References

- [Deploy and use MAI image models in Microsoft Foundry](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/how-to/use-foundry-models-mai-image?tabs=python) — official how-to covering the generations and edits APIs, authentication, and rate limits.
- [Introducing MAI-Image-2.5-Pro and MAI-Voice-2-Flash](https://microsoft.ai/news/introducing-mai-image-2-5-pro-and-mai-voice-2-flash/) — release announcement for the Pro variant.
- [MAI-Image-2.5 model page](https://microsoft.ai/models/mai-image-2-5/) — model overview, capability comparison, and arena benchmarks for the full family.
