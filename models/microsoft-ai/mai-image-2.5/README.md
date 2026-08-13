---
kind: capsule
publisher: microsoft-ai
model: mai-image-2.5
summary: "Generate and edit images from text prompts"
release_date: "2026-06-02"
last_updated: "2026-08-11"
capabilities: [image-generation]
model_card: https://ai.azure.com/catalog/models/MAI-Image-2.5
announcement: https://microsoft.ai/news/microsoft-build-2026-mai-keynote-transcript/
pricing:
  url: https://microsoft.ai/models/mai-image-2-5/
  notes: "$0.05 / image"
dependencies: [requests]
domains: [e-commerce, marketing, creative-media]
notebooks:
  - path: mai-image-2.5.ipynb
    title: "Generate and edit images with MAI-Image-2.5"
    concepts:
      - text-to-image generation
      - image dimensions and aspect ratios
      - image-to-image editing
---

# MAI-Image-2.5 — Release Capsule

**Released:** 2026-06-02 · **Publisher:** [Microsoft AI](../README.md) · **Capability:** Image Generation

## Before You Begin

| Detail | Value |
|---|---|
| Model card | [MAI-Image-2.5 — Foundry catalog](https://ai.azure.com/catalog/models/MAI-Image-2.5) |
| Announcement | [Build 2026 MAI keynote](https://microsoft.ai/news/microsoft-build-2026-mai-keynote-transcript/) |
| Pricing | $0.05 / image — [source](https://microsoft.ai/models/mai-image-2-5/) |
| Release date | 2026-06-02 |
| Deployment regions | West Central US · East US · West US · West Europe · Sweden Central · South India · UAE North |

See [models/quickstart/](../../quickstart/README.md) for first-time Foundry project setup.

**Required env variables:**

```
MICROSOFT_FOUNDRY_ENDPOINT      # e.g. https://<resource>.services.ai.azure.com/api/projects/<project>
MICROSOFT_FOUNDRY_API_KEY       # AIServices API key
AZURE_MAI_IMAGE_25_DEPLOYMENT   # your MAI-Image-2.5 deployment name
```

## Notebook

| Notebook | Concepts |
|---|---|
| [mai-image-2.5.ipynb](mai-image-2.5.ipynb) | Text-to-image generation · Image dimensions · Image-to-image editing |

**MAI-Image-2.5** is the baseline member of the MAI-Image-2.5 family. It uses a diffusion-based approach
to produce visually coherent images from text prompts and supports precise, surgical edits to existing
images — changing specific elements while preserving layout and composition. The Flash and Pro variants
build on this foundation; start here if you are new to the family.

- [MAI-Image-2.5-Flash capsule](../mai-image-2.5-flash/) — same release, optimised for production throughput
- [MAI-Image-2.5-Pro capsule](../mai-image-2.5-pro/) — portrait quality, text rendering, visual reasoning (released 2026-07-23)

## API endpoints

| API | URL pattern | Body |
|---|---|---|
| Image generations | `https://<resource>.services.ai.azure.com/mai/v1/images/generations` | JSON |
| Image edits | `https://<resource>.services.ai.azure.com/mai/v1/images/edits` | multipart/form-data |

Constraints: `width` and `height` both ≥ 768; `width × height` ≤ 1,048,576. Output is always PNG.

## References

- [Deploy and use MAI image models in Microsoft Foundry](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/how-to/use-foundry-models-mai-image?tabs=python) — official how-to covering the generations and edits APIs, authentication, and rate limits.
- [MAI-Image-2.5 model page](https://microsoft.ai/models/mai-image-2-5/) — model overview, capability comparison, and arena benchmarks.
- [Build 2026 MAI keynote transcript](https://microsoft.ai/news/microsoft-build-2026-mai-keynote-transcript/) — keynote introducing the full MAI model family.
