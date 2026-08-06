---
kind: capsule
family: microsoft-ai
model: mai-transcribe-1.5
release_date: "2026-06-02"
capabilities: [audio-speech]
model_card: https://ai.azure.com/catalog/models/MAI-Transcribe-1.5
announcement: https://microsoft.ai/news/mai-transcribe-1-5more-accurate-context-aware-and-built-for-production/
pricing:
  url: https://microsoft.ai/models/mai-transcribe-1-5/
  notes: "$0.36 per hour of audio"
dependencies: [azure-ai-transcription, azure-identity, soundfile, jiwer, matplotlib, pandas, numpy]
domains: [contact-center, healthcare, media-captioning, meetings]
notebooks:
  - path: mai-transcribe-1.5.ipynb
    title: "Multilingual transcription, transcribe styles, and keyword biasing with MAI-Transcribe-1.5"
    concepts:
      - multilingual transcription with automatic language detection
      - readability vs. verbatim transcribe styles
      - keyword biasing for domain-specific vocabulary
  - path: mai-transcribe-1.5-noise-benchmark.ipynb
    title: "Benchmarking MAI-Transcribe-1.5 accuracy against background noise"
    concepts:
      - mixing speech with noise at controlled SNR levels
      - scoring transcripts with word and character error rate
      - plotting accuracy degradation against signal-to-noise ratio
references:
  - title: "MAI-Transcribe in Azure Speech (preview)"
    url: "https://learn.microsoft.com/en-us/azure/ai-services/speech-service/mai-transcribe?context=%2Fazure%2Ffoundry%2Fcontext%2Fcontext&pivots=ai-foundry"
    kind: docs
    note: "Official how-to covering enhancedMode, transcribeStyle, phraseList, language support, and limitations."
  - title: "LLM Speech for speech transcription and translation"
    url: "https://learn.microsoft.com/en-us/azure/ai-services/speech-service/llm-speech?tabs=new-foundry%2Cwindows&pivots=programming-language-python"
    kind: docs
    note: "Quickstart for the LLM Speech API that MAI-Transcribe runs on — auth, the azure-ai-transcription SDK, and the response shape."
  - title: "Introducing MAI-Transcribe-1.5"
    url: "https://microsoft.ai/news/mai-transcribe-1-5more-accurate-context-aware-and-built-for-production/"
    kind: blog
    note: "Release announcement — 43-language coverage, throughput, and keyword-biasing results."
  - title: "MAI-Transcribe-1.5 model page"
    url: "https://microsoft.ai/models/mai-transcribe-1-5/"
    kind: blog
    note: "Benchmark comparison against MAI-Transcribe-1 and pricing per audio hour."
  - title: "MAI-Transcribe-1.5 model card (PDF)"
    url: "https://microsoft.ai/pdf/MAI-Transcribe-1.5-Model-Card.PDF"
    kind: model-card
    note: "Intended uses, evaluation methodology, and responsible-AI considerations."
---

# MAI-Transcribe-1.5 — Release Capsule

**Released:** 2026-06-02 · **Family:** [Microsoft AI](../../README.md) · **Capability:** Audio / Speech

> **Public preview.** MAI-Transcribe runs on the LLM Speech API, which is in public preview — no SLA, not recommended for production workloads.

## Before You Begin

| Detail | Value |
|---|---|
| Model card | [MAI-Transcribe-1.5 — Foundry catalog](https://ai.azure.com/catalog/models/MAI-Transcribe-1.5) |
| Announcement | [Introducing MAI-Transcribe-1.5](https://microsoft.ai/news/mai-transcribe-1-5more-accurate-context-aware-and-built-for-production/) |
| Pricing | $0.36 per hour of audio — [source](https://microsoft.ai/models/mai-transcribe-1-5/) |
| Release date | 2026-06-02 |
| Deployment regions | See [Speech service regions](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/regions?tabs=llmspeech) — LLM Speech is available in a subset of Speech regions |

See [models/quickstart/](../../../quickstart/README.md) for first-time Foundry project setup.

**Required env variables:**

```
MICROSOFT_FOUNDRY_ENDPOINT   # e.g. https://<resource>.services.ai.azure.com/api/projects/<project>
MICROSOFT_FOUNDRY_API_KEY    # AIServices (Speech) resource key
```

Optional overrides:

```
AZURE_SPEECH_ENDPOINT        # use when your Speech resource differs from the Foundry project resource
MAI_TRANSCRIBE_MODEL         # defaults to mai-transcribe-1.5
```

> Unlike the MAI image models, MAI-Transcribe needs **no deployment name**. You select the model by
> passing `mai-transcribe-1.5` in the request's `enhancedMode` block.

## Notebooks

| Notebook | Concepts |
|---|---|
| [mai-transcribe-1.5.ipynb](mai-transcribe-1.5.ipynb) | Multilingual transcription with auto language detection · Readability vs. verbatim transcribe styles · Keyword biasing with phrase lists |
| [mai-transcribe-1.5-noise-benchmark.ipynb](mai-transcribe-1.5-noise-benchmark.ipynb) | Mixing speech with noise at controlled SNR · Word and character error rate scoring · Plotting accuracy against signal-to-noise ratio |

The benchmark notebook scores against `data/reference/transcripts.json`, which ships **empty** —
fill in a hand-verified transcript before trusting any WER number.

**MAI-Transcribe-1.5** is a speech recognition model from the Microsoft AI Superintelligence team,
served through the LLM Speech API rather than a per-model deployment endpoint. Compared with
MAI-Transcribe-1 (deprecated 2026-08-20), it adds:

- **43 languages** in multi-lingual mode with automatic language detection
- **`transcribeStyle`** — a readability-optimised transcript by default, or `verbatim` to keep filler
  words and disfluencies
- **`phraseList`** — entity biasing toward domain vocabulary (product names, agent names, acronyms)

The notebooks run against the noisy contact-centre clips in [data/](data/), which is where these
knobs earn their keep.

**Limitations** ([source](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/mai-transcribe?context=%2Fazure%2Ffoundry%2Fcontext%2Fcontext&pivots=ai-foundry)):
diarization and prompt-tuning aren't supported; `transcribeStyle` and `phraseList` are
`mai-transcribe-1.5` only. Audio files must be under 300 MB (WAV, MP3, or FLAC).

## API surface

| Piece | Value |
|---|---|
| Endpoint | `https://<resource>.cognitiveservices.azure.com/speechtotext/transcriptions:transcribe?api-version=2025-10-15` |
| Body | `multipart/form-data` — `audio` file + `definition` JSON |
| Auth header | `Ocp-Apim-Subscription-Key`, or Entra ID via `DefaultAzureCredential` |
| Python SDK | [`azure-ai-transcription`](https://pypi.org/project/azure-ai-transcription/) — `TranscriptionClient.transcribe()` |

Model selection and options live in the `definition` payload:

```json
{
  "locales": ["en-US"],
  "phraseList": { "phrases": ["Microsoft Foundry", "AI", "DevOps"] },
  "enhancedMode": {
    "model": "mai-transcribe-1.5",
  }
}
```

Two gotchas the docs don't call out: `locales` needs full BCP-47 tags (`en-US`,
not `en`), and sending `"enabled": true` alongside `model` fails with
`(InvalidRequest) Enhanced mode with model is currently not supported yet` —
naming the model is enough to turn enhanced mode on.

## References

- [MAI-Transcribe in Azure Speech (preview)](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/mai-transcribe?context=%2Fazure%2Ffoundry%2Fcontext%2Fcontext&pivots=ai-foundry) — official how-to covering `enhancedMode`, `transcribeStyle`, `phraseList`, language support, and limitations.
- [LLM Speech for speech transcription and translation](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/llm-speech?tabs=new-foundry%2Cwindows&pivots=programming-language-python) — quickstart for the LLM Speech API that MAI-Transcribe runs on: auth, the `azure-ai-transcription` SDK, and the response shape.
- [Introducing MAI-Transcribe-1.5](https://microsoft.ai/news/mai-transcribe-1-5more-accurate-context-aware-and-built-for-production/) — release announcement: 43-language coverage, throughput, and keyword-biasing results.
- [MAI-Transcribe-1.5 model page](https://microsoft.ai/models/mai-transcribe-1-5/) — benchmark comparison against MAI-Transcribe-1 and pricing per audio hour.
- [MAI-Transcribe-1.5 model card (PDF)](https://microsoft.ai/pdf/MAI-Transcribe-1.5-Model-Card.PDF) — intended uses, evaluation methodology, and responsible-AI considerations.
- [Audio / Speech primer](../../../../docs/primers/audio-speech.md) — background on transcription and speech capabilities on Foundry.
