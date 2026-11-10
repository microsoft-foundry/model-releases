# Scenarios

*"Where do the sample inputs come from, and can I reuse them?"*

A scenario is a reusable, fictitious business setting — data, agent
instructions, and a benchmark — that release capsules share.
Holding the workload fixed means results stay reproducible, and we can compare
models or [optimization levers](../3-primers/optimization.md#optimization-lever)
on the same inputs.

| Scenario | What it is | Used by |
|---|---|---|
| [contoso-travel](contoso-travel/) | An enterprise travel concierge that books policy-compliant flights, hotels, and cars | [Model Router](../4-models/model-router/) |
| [contoso-retail](contoso-retail/) | Contoso Outdoors, an online camping and hiking retailer with a 20-product catalog, manuals, and photos | [MAI-Image-2.6](../4-models/mai-image-2.6/) · [MAI-Image-2.6-Flash](../4-models/mai-image-2.6-flash/) · [Kling V3 Pro](../4-models/fal-kling-v3-pro/) · [LTX 2.5 Pro](../4-models/fal-ltx-2.5-pro/) · [LTX 2.5 Fast](../4-models/fal-ltx-2.5-fast/) · [MiniMax H3 Max](../4-models/fal-minimax-h3-max/) · [MiniMax H3 Max Turbo](../4-models/fal-minimax-h3-max-turbo/) · [fal video family](../5-multi-model/fal-video-family-walkthrough/) |

To add a scenario, follow the steps in [CONTRIBUTING.md](../CONTRIBUTING.md#add-a-scenario).
