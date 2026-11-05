---
name: add-capsule
description: Create a capsule for a new model release — notebook(s) under capsules/<model>/, a CHANGELOG row, and the README What's new table. Use when a model is released on Microsoft Foundry and we want a hands-on notebook for it.
---

# add-capsule

## 1. Gather the release facts

Ask for anything missing — don't invent URLs or prices:

- Model name, publisher, release date
- Model card URL (`https://ai.azure.com/catalog/models/<slug>`)
- Release post URL, pricing and its source
- Capabilities (match a primer in `primers/`)
- 1–3 key features to teach per notebook, and references (Microsoft Learn first)
- Deployments and environment variables the notebook needs

If the release is in `.github/planning.md`, start from that row.

## 2. Scaffold the capsule

1. Create `capsules/<model>/<model>.ipynb` (or `<model>-01-<topic>.ipynb`, `<model>-02-<topic>.ipynb` for several notebooks) following the notebook structure in [check-content](../check-content/SKILL.md).
2. Focus on what is **new or different** in this release — the features that would make us pick it.
3. Put input files in `capsules/<model>/images/` or `data/`; write generated files to `output/`.
4. Add new variables to `scripts/sample.env` with a comment naming the capsule, and new packages to `requirements-dev.txt` under **Capsule dependencies**.

## 3. Record it

1. Add a row to the top of `CHANGELOG.md` (format in check-content).
2. Add the capsule to the **Try it** list of each matching primer.
3. Run [refresh-recent-activity](../refresh-recent-activity/SKILL.md).
4. Remove the release from `.github/planning.md` if it was there.

## 4. Validate

Run [check-content](../check-content/SKILL.md) — `python scripts/check.py` must print `OK`.
