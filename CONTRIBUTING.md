# Contributing

This repo helps developers get hands-on with a new Microsoft Foundry model as fast as possible. Every change should make that path shorter or clearer.

All content rules — layout, notebook structure, voice, CHANGELOG format — live in one place: the [check-content skill](.github/skills/check-content/SKILL.md). The fastest way to contribute is to ask GitHub Copilot to use the matching skill below.

## Before you start

```bash
pip install -r requirements-dev.txt
pip install pre-commit && pre-commit install   # runs 1-scripts/check.py on each commit
```

Run [setup.ipynb](setup.ipynb) once so you can run notebooks against your own Foundry project.

## Add a capsule

Use the [add-capsule](.github/skills/add-capsule/SKILL.md) skill:

```text
Use the add-capsule skill to create a capsule for <model>, released <date>. Release post: <url>
```

It creates `4-models/<model>/`, adds the CHANGELOG row, updates matching primers, and refreshes the README. Pick candidates from the backlog in [.github/planning.md](.github/planning.md).

## Add a multi-model capsule

Use the [add-multi-model-capsule](.github/skills/add-multi-model-capsule/SKILL.md) skill when a practical scenario is best shown by comparing or combining models.

## Add a primer or key term

Use the [add-primer](.github/skills/add-primer/SKILL.md) skill.

## Create an MAI-themed banner prompt

Use the [create-mai-banners](.github/skills/create-mai-banners/SKILL.md) skill
to apply the shared warm palette, editorial typography, and illustration style:

```text
Use create-mai-banners: landscape, 1920 x 1080 pixels. Show a tent beside a
mountain river. Title: "One tent, one launch". No other text.
```

The skill returns a copy-ready image prompt and settings, not a generated image.

## Add a scenario

1. Create `2-scenarios/<name>/` with `data/` and a `README.md` describing the fictitious scenario and each file.
2. Keep it modality-neutral where possible so text, image, and audio capsules can share it.
3. Add a row to [2-scenarios/README.md](2-scenarios/README.md).

## Archive a capsule

When a model is retired, or a newer version replaces it (MAI-Image-2.5 → 2.6, MAI-Transcribe-1.5 → 2):

1. `git mv 4-models/<model> 0-archive/<model>`
2. Add a banner under the title of each notebook's first cell, leaving the code as-is:
   - Retired: `> **Retired YYYY-MM-DD.** This model is no longer available. Try [<replacement>](../../4-models/<replacement>/) instead.`
   - Replaced: `> **Archived YYYY-MM-DD: superseded by [<replacement>](../../4-models/<replacement>/).** The notebook still runs while <model> is deployed.`
3. In `CHANGELOG.md`, append ` _(archived)_` to the Model cell and point the Capsule link at `0-archive/<model>/`. Archived capsules stay discoverable from there.
4. In [1-scripts/sample.env](1-scripts/sample.env), move the capsule's variables to the **ARCHIVE** section at the bottom, so current capsules' settings stay at the top.
5. Run [refresh-recent-activity](.github/skills/refresh-recent-activity/SKILL.md) if the row is in the top 3.

Multi-model walkthroughs in `5-multi-model/` work differently: they stay in place and move to the newest models. Copy the old version to `0-archive/<old-name>/` (for example `mai-image-2.5-family-walkthrough`), banner it, and point its CHANGELOG row there.

## Check your work

```bash
python 1-scripts/check.py
```

It must print `OK`. CI runs the same check on every pull request.

For changes to the MAI-Transcribe-2 request configuration, also run the offline
SDK serialization checks (no Azure credentials or service calls):

```bash
python -m unittest discover -s 1-scripts -p test_mai_transcribe.py -v
```
