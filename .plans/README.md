# Plans

This folder holds the **original design docs** for workshops and models —
speaker scripts, trainer guides, scorecards, day-by-day build calendars,
model-card drafts, evaluation notes, and any other "what we set out to
build" material that predates the learner-facing content itself.

Keeping plans next to (but separate from) the published content makes it
easy to **correlate what was planned to what was built** without
cluttering the learner-facing files.

## Convention

- One file per piece of content, named `<slug>-plan.md`.
- The matching content lives at `../workshops/<slug>/` or `../models/<slug>/`.
- This folder sits at the repo root and is hidden (`.plans/`) so it does
  not show up in the default workshop or model listings that the
  `run-workshop` / `explore-model` skills walk.
- The `run-workshop/learn-more` and `explore-model/learn-more` subskills
  may link out to a plan when a learner asks for the deeper "why" behind
  a step.

## Current plans

| Plan | Content |
|---|---|
| [`foundry-models-e2e-plan.md`](./foundry-models-e2e-plan.md) | [`../workshops/foundry-models-e2e/`](../workshops/foundry-models-e2e/) |
| [`model-router-demystified-plan.md`](./model-router-demystified-plan.md) | [`../workshops/model-router-demystified/`](../workshops/model-router-demystified/) |
| [`demo-skills-plan.md`](./demo-skills-plan.md) | `../.agents/skills/add-demo/` + `../.agents/skills/run-demo/` (proposed) |
