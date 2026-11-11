---
name: add-multi-model-capsule
description: Create a scenario notebook under 5-multi-model/<scenario>/ that compares or combines two or more models. Use when a practical task is best shown with several models side by side or working together.
---

# add-multi-model-capsule

## 1. Frame the scenario

Ask for:

- The practical task, phrased as a developer question ("Which MAI-Image variant fits a resale listing pipeline?")
- The models involved — each should already have a capsule in `4-models/`
- Whether it **compares** models on the same inputs or **combines** them in one workflow
- A scenario from `2-scenarios/` that fits, or the inputs to use

## 2. Scaffold

1. Create `5-multi-model/<scenario>/<scenario>.ipynb` following [check-content](../check-content/SKILL.md). In the header table, replace Model card / Pricing with a **Models** row linking each model's capsule.
2. For comparisons, hold inputs fixed and report the same measures for every model (quality notes, latency, cost).
3. Close the Summary with when to choose each model.

## 3. Record and validate

1. Add a CHANGELOG row: Model cell is the scenario name, What's new starts with "Multi-model:", Capsule links to `5-multi-model/<scenario>/`.
2. Add it to the **Try it** list of matching primers with a "— multi-model" suffix.
3. Run [refresh-recent-activity](../refresh-recent-activity/SKILL.md), then `python 1-scripts/check.py`.
