# Datasets

*"Where do the sample inputs come from, and can I reuse them?"*

A dataset is a reusable, fictitious business scenario — data, agent
instructions, and a benchmark — that capsules and multi-model notebooks share.
Holding the workload fixed means results stay reproducible, and we can compare
models or [optimization levers](../primers/optimization.md#optimization-lever)
on the same inputs.

| Dataset | Scenario | Used by |
|---|---|---|
| [contoso-travel](contoso-travel/) | An enterprise travel concierge that books policy-compliant flights, hotels, and cars | [Model Router](../capsules/model-router/) |

To add a dataset, follow the steps in [CONTRIBUTING.md](../CONTRIBUTING.md#add-a-dataset).
