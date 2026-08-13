---
kind: publisher
name: NVIDIA
slug: nvidia
one_line: NIM microservices for language, vision, biology, and earth science
provider: NVIDIA
related_primers: [chat-completion, reasoning-models, multimodal-models, embeddings]
---

# NVIDIA Models on Microsoft Foundry

> **NVIDIA NIM microservices on Microsoft Foundry.** Optimized inference
> endpoints spanning language, vision-language, document parsing, content
> safety, embeddings, re-ranking, physical AI, 3D generation, computational
> biology, and earth science.

## Why it matters

NVIDIA packages its models as **NIM (NVIDIA Inference Microservices)** —
pre-optimized containers with standardized APIs. On Microsoft Foundry you
deploy them without managing GPU infrastructure. The catalog spans far
beyond general chat: physical AI (Cosmos), earth-science forecasting
(Earth-2), protein structure prediction (OpenFold, Boltz2, ProteinMPNN),
genomics (Evo2), and 3D generation (Trellis) alongside the main Nemotron
language model series.

## Members

### Language — Nemotron

| Model | Capabilities | Model card | Released | Expires | Capsule |
|---|---|---|---|---|---|
| NVIDIA-Nemotron-3-Nano | Chat Completion | [catalog](https://ai.azure.com/catalog/models/NVIDIA-Nemotron-3-Nano-NIM-microservice) | — | — | — |
| NVIDIA-Nemotron-3-Super | Chat Completion, Summarization | [catalog](https://ai.azure.com/catalog/models/NVIDIA-Nemotron-3-Super-NIM-microservice) | — | — | — |
| NVIDIA-Nemotron-3-Ultra | Chat Completion, Summarization | [catalog](https://ai.azure.com/catalog/models/NVIDIA-Nemotron-3-Ultra-NIM-microservice) | — | — | — |
| NVIDIA-Nemotron-Nano-9B-v2 | Chat Completion | [catalog](https://ai.azure.com/catalog/models/NVIDIA-Nemotron-Nano-9b-v2-NIM-microservice) | — | — | — |
| Llama-3.1-Nemotron-Nano-8B-v1 | Chat Completion | [catalog](https://ai.azure.com/catalog/models/Llama-3.1-Nemotron-Nano-8B-v1-NIM-microservice) | — | — | — |
| Llama-3.3-Nemotron-Super-49B-v1 | Chat Completion | [catalog](https://ai.azure.com/catalog/models/Llama-3.3-Nemotron-Super-49B-v1-NIM-microservice) | — | — | — |
| Llama-3.3-Nemotron-Super-49B-v1.5 | Chat Completion, Reasoning | [catalog](https://ai.azure.com/catalog/models/Llama-3.3-Nemotron-Super-49B-v1.5-NIM-microservice) | — | — | — |

### Language — Third-party NIM

| Model | Capabilities | Model card | Released | Expires | Capsule |
|---|---|---|---|---|---|
| Llama-3.1-8B-Instruct | Chat Completion | [catalog](https://ai.azure.com/catalog/models/Llama-3.1-8B-Instruct-NIM-microservice) | — | — | — |
| Llama-3.3-70B-Instruct | Chat Completion | [catalog](https://ai.azure.com/catalog/models/Llama-3.3-70B-Instruct-NIM-microservice) | — | — | — |
| Mixtral-8x7B-Instruct-v0.1 | Chat Completion | [catalog](https://ai.azure.com/catalog/models/Mixtral-8x7B-Instruct-v0.1-NIM-microservice) | — | — | — |
| Mistral-7B-Instruct-v0.3 | Chat Completion | [catalog](https://ai.azure.com/catalog/models/Mistral-7B-Instruct-v0.3-NIM-microservice) | — | — | — |
| DeepSeek-R1-Distill-Llama-8B | Chat Completion, Reasoning | [catalog](https://ai.azure.com/catalog/models/Deepseek-R1-Distill-Llama-8B-NIM-microservice) | — | — | — |
| Nemotron-3-8B-Chat-SFT | Chat Completion | [catalog](https://ai.azure.com/catalog/models/Nemotron-3-8B-Chat-SFT) | — | — | — |
| Nemotron-3-8B-Chat-RLHF | Chat Completion | [catalog](https://ai.azure.com/catalog/models/Nemotron-3-8B-Chat-RLHF) | — | — | — |
| Nemotron-3-8B-Chat-SteerLM | Chat Completion | [catalog](https://ai.azure.com/catalog/models/Nemotron-3-8B-Chat-SteerLM) | — | — | — |
| Nemotron-3-8B-Chat-4k-SteerLM | Chat Completion | [catalog](https://ai.azure.com/catalog/models/Nemotron-3-8B-Chat-4k-SteerLM) | — | — | — |
| Nemotron-3-8B-QA-4k | Chat Completion | [catalog](https://ai.azure.com/catalog/models/Nemotron-3-8B-QA-4k) | — | — | — |
| Nemotron-3-8B-Base-4k | Text Generation | [catalog](https://ai.azure.com/catalog/models/Nemotron-3-8B-Base-4k) | — | — | — |

### Vision-Language

| Model | Capabilities | Model card | Released | Expires | Capsule |
|---|---|---|---|---|---|
| NVIDIA-Nemotron-Nano-12B-v2-VL | Multimodal, Visual Q&A, Document Intelligence | [catalog](https://ai.azure.com/catalog/models/NVIDIA-Nemotron-Nano-12B-v2-VL-NIM-microservice) | — | — | — |
| Llama-3.1-Nemotron-Nano-VL-8B-v1 | Vision, Image-to-Text, Visual Q&A | [catalog](https://ai.azure.com/catalog/models/Llama-3.1-Nemotron-Nano-VL-8B-v1-NIM-microservice) | — | — | — |

### Document & Content Safety

| Model | Capabilities | Model card | Released | Expires | Capsule |
|---|---|---|---|---|---|
| NVIDIA-Nemotron-Parse | Document Analysis | [catalog](https://ai.azure.com/catalog/models/NVIDIA-Nemotron-Parse-NIM-microservice) | — | — | — |
| NVIDIA-Nemotron-3-Content-Safety | Text & Image Classification | [catalog](https://ai.azure.com/catalog/models/NVIDIA-Nemotron-3-Content-Safety-NIM-microservice) | — | — | — |
| NVIDIA-Nemotron-Content-Safety-Reasoning-4B | Text Classification, Reasoning | [catalog](https://ai.azure.com/catalog/models/NVIDIA-Nemotron-Content-Safety-Reasoning-4B-NIM-microservice) | — | — | — |

### Embeddings & Re-ranking

| Model | Capabilities | Model card | Released | Expires | Capsule |
|---|---|---|---|---|---|
| Llama-3.2-NV-EmbedQA-1B-v2 | Embeddings | [catalog](https://ai.azure.com/catalog/models/Llama-3.2-NV-embedqa-1b-v2-NIM-microservice) | — | — | — |
| Llama-3.2-NV-RerankQA-1B-v2 | Re-ranking | [catalog](https://ai.azure.com/catalog/models/Llama-3.2-NV-rerankqa-1b-v2-NIM-microservice) | — | — | — |

### Physical AI & Robotics

| Model | Capabilities | Model card | Released | Expires | Capsule |
|---|---|---|---|---|---|
| Cosmos-Reason1 | Action Affordance, Task Verification, Next-Action Prediction | [catalog](https://ai.azure.com/catalog/models/Cosmos-reason1-NIM-microservice) | — | — | — |

### 3D Generation

| Model | Capabilities | Model card | Released | Expires | Capsule |
|---|---|---|---|---|---|
| Trellis | Image-to-3D, Text-to-3D | [catalog](https://ai.azure.com/catalog/models/Trellis-NIM-microservice) | — | — | — |

### Computational Biology

| Model | Capabilities | Model card | Released | Expires | Capsule |
|---|---|---|---|---|---|
| OpenFold2 | Protein Structure Prediction | [catalog](https://ai.azure.com/catalog/models/Openfold2-NIM-microservice) | — | — | — |
| OpenFold3 | Biomolecular Complex Structure Prediction | [catalog](https://ai.azure.com/catalog/models/Openfold3_1_2_0-NIM-microservice) | — | — | — |
| ProteinMPNN | Protein Design | [catalog](https://ai.azure.com/catalog/models/ProteinMPNN-NIM-microservice) | — | — | — |
| RFDiffusion | Protein Binder Design | [catalog](https://ai.azure.com/catalog/models/Rfdiffusion-NIM-microservice) | — | — | — |
| MSA-Search | Protein Binder | [catalog](https://ai.azure.com/catalog/models/MSA-search-NIM-microservice) | — | — | — |
| Boltz2 | Biomolecular Structure Prediction | [catalog](https://ai.azure.com/catalog/models/Boltz2-NIM-microservice) | — | — | — |
| Evo2-40B | Genomics | [catalog](https://ai.azure.com/catalog/models/Evo2-40b-NIM-microservice) | — | — | — |

### Earth & Climate Science

| Model | Capabilities | Model card | Released | Expires | Capsule |
|---|---|---|---|---|---|
| Earth-2 FCN3 | Weather Forecasting | [catalog](https://ai.azure.com/catalog/models/earth2studio-fcn3) | — | — | — |
| Earth-2 FCN3 Stormscope | Weather Forecasting, Storm Analysis | [catalog](https://ai.azure.com/catalog/models/earth2studio-fcn3-stormscope) | — | — | — |

## Learn more

- [Microsoft Foundry Models overview](https://learn.microsoft.com/en-us/azure/ai-foundry/concepts/foundry-models-overview)
- [NVIDIA NIM on Azure AI catalog](https://ai.azure.com/catalog/publishers/nvidia,nvidia-ai)
- [Chat completion primer](../../docs/primers/chat-completion.md)
- [Reasoning primer](../../docs/primers/reasoning-models.md)
- [Multimodal models primer](../../docs/primers/multimodal-models.md)
- [Embeddings primer](../../docs/primers/embeddings.md)
- [Glossary](../../docs/GLOSSARY.md)
