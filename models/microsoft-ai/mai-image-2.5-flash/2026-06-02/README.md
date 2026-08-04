---
kind: capsule
family: microsoft-ai
model: mai-image-2.5-flash
release_date: "2026-06-02"
capabilities: [image-generation]
model_card: https://ai.azure.com/catalog/models/MAI-Image-2.5-Flash
announcement: https://microsoft.ai/news/microsoft-build-2026-mai-keynote-transcript/
pricing:
  url: https://microsoft.ai/models/mai-image-2-5/
  notes: "lower than MAI-Image-2.5 base — see model page for current rate"
dependencies: [requests]
domains: [e-commerce, product-photography, high-volume-content]
notebooks:
  - path: mai-image-2.5-flash.ipynb
    title: "Production-scale image generation with MAI-Image-2.5-Flash"
    concepts:
      - batch image generation
      - throughput measurement and cost estimation
      - concurrent requests for high-volume workflows
references:
  - title: "Deploy and use MAI image models in Microsoft Foundry"
    url: "https://learn.microsoft.com/en-us/azure/foundry/foundry-models/how-to/use-foundry-models-mai-image?tabs=python"
    kind: docs
    note: "Official how-to covering the generations and edits APIs, authentication, and rate limits."
  - title: "Build 2026 MAI keynote transcript"
    url: "https://microsoft.ai/news/microsoft-build-2026-mai-keynote-transcript/"
    kind: blog
    note: "Keynote introducing the full MAI model family including Flash."
  - title: "MAI-Image-2.5 model page"
    url: "https://microsoft.ai/models/mai-image-2-5/"
    kind: blog
    note: "Model overview, capability comparison, and arena benchmarks."
---

# MAI-Image-2.5-Flash — Release Capsule

**Released:** 2026-06-02 · **Family:** [Microsoft AI](../../README.md) · **Capability:** Image Generation

## Before You Begin

| Detail | Value |
|---|---|
| Model card | [MAI-Image-2.5-Flash — Foundry catalog](https://ai.azure.com/catalog/models/MAI-Image-2.5-Flash) |
| Announcement | [Build 2026 MAI keynote](https://microsoft.ai/news/microsoft-build-2026-mai-keynote-transcript/) |
| Pricing | Lower than base MAI-Image-2.5 — see [model page](https://microsoft.ai/models/mai-image-2-5/) |
| Release date | 2026-06-02 |
| Deployment regions | West Central US · East US · West US · West Europe · Sweden Central · South India · UAE North |

See [models/quickstart/](../../../quickstart/README.md) for first-time Foundry project setup.

**Required env variables:**

```
MICROSOFT_FOUNDRY_ENDPOINT            # e.g. https://<resource>.services.ai.azure.com/api/projects/<project>
MICROSOFT_FOUNDRY_API_KEY             # AIServices API key
AZURE_MAI_IMAGE_25_FLASH_DEPLOYMENT   # your MAI-Image-2.5-Flash deployment name
```

## Notebook

| Notebook | Concepts |
|---|---|
| [mai-image-2.5-flash.ipynb](mai-image-2.5-flash.ipynb) | Batch generation · Throughput measurement · Concurrent requests |

**MAI-Image-2.5-Flash** is the production-efficiency variant of the MAI-Image-2.5 family. It delivers the
same text-to-image generation and image-to-image editing capabilities as the base model, optimised for
lower latency and cost per image at scale. Choose Flash when throughput and cost efficiency matter more
than maximum fidelity.

- [MAI-Image-2.5 capsule](../../mai-image-2.5/2026-06-02/) — base model; start here if new to the family
- [MAI-Image-2.5-Pro capsule](../../mai-image-2.5-pro/2026-07-23/) — Pro variant with portrait quality and text rendering

## API endpoints

| API | URL pattern | Body |
|---|---|---|
| Image generations | `https://<resource>.services.ai.azure.com/mai/v1/images/generations` | JSON |
| Image edits | `https://<resource>.services.ai.azure.com/mai/v1/images/edits` | multipart/form-data |

Constraints: `width` and `height` both ≥ 768; `width × height` ≤ 1,048,576. Output is always PNG.

## References

- [Deploy and use MAI image models in Microsoft Foundry](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/how-to/use-foundry-models-mai-image?tabs=python) — official how-to covering the generations and edits APIs, authentication, and rate limits.
- [Build 2026 MAI keynote transcript](https://microsoft.ai/news/microsoft-build-2026-mai-keynote-transcript/) — keynote introducing the full MAI model family including Flash.
- [MAI-Image-2.5 model page](https://microsoft.ai/models/mai-image-2-5/) — model overview, capability comparison, and arena benchmarks.
