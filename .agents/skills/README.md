---
name: skills-index
description: Index and authoring guide for repo-scoped skills under `.agents/skills/`.
---

# Repo Skills (`.agents/skills/`)

This folder holds **repo-scoped skills** that Copilot (and humans) can invoke
to help learners explore the models and workshops in this repository.

Skills are deliberately small, single-purpose, and discoverable. Each skill
lives in its own folder and is described by a `SKILL.md` file with YAML
frontmatter. Subskills (used by dispatcher skills like `run-workshop`) live
under `<skill>/skills/<sub>/SKILL.md` with the same shape.

## Current skills

The skills come in three **author → driver pairs**:

| Pair | Author skill (scaffolds content) | Driver skill (walks / drives content) |
|---|---|---|
| Models | [`add-model`](./add-model/SKILL.md) | [`explore-model`](./explore-model/SKILL.md) |
| Workshops | [`add-workshop`](./add-workshop/SKILL.md) | [`run-workshop`](./run-workshop/SKILL.md) |

The model + workshop driver skills share the same five subskills:
`setup`, `complete-step`, `check-status`, `troubleshoot`, `learn-more`.

| Skill | Purpose | When to invoke |
|---|---|---|
| [`add-model`](./add-model/SKILL.md) | Scaffold a new entry under `models/<slug>/` with README, model card, evaluation, and numbered exploration steps. | "Add a new model", "author skilling content for a model". |
| [`explore-model`](./explore-model/SKILL.md) | Guide a learner through a model entry one step at a time. Dispatches to `setup`, `complete-step`, `check-status`, `troubleshoot`, `learn-more`. | "Explore the X model with me", "help me try the next step". |
| [`add-workshop`](./add-workshop/SKILL.md) | Scaffold a new entry under `workshops/<slug>/` with numbered step files. | "Create a workshop", "start a new tutorial". |
| [`run-workshop`](./run-workshop/SKILL.md) | Guide a learner through a workshop one step at a time. Dispatches to `setup`, `complete-step`, `check-status`, `troubleshoot`, `learn-more`. | "Run the X workshop with me", "help me do the next step". |

## Authoring conventions

1. **One folder per skill.** The folder name is the skill name (kebab-case).
2. **`SKILL.md` is required.** It begins with YAML frontmatter:
   ```yaml
   ---
   name: <skill-name>
   description: <one-sentence description, <= 200 chars>
   when_to_use: |
     Short list of triggers/phrases that should invoke this skill.
   do_not_use_for: |
     Short list of cases that look similar but should not invoke it.
   ---
   ```
   The body of `SKILL.md` is the playbook Copilot follows when the skill is
   invoked: numbered steps, prompts to ask the learner, file operations,
   and verification steps.
3. **Templates live in `<skill>/templates/`.** Use `{{placeholder}}` tokens
   that the skill replaces during scaffolding. Templates should be valid
   Markdown so they can be opened directly if a skill isn't invoked.
4. **Subskills are nested.** A dispatcher skill keeps its subskills under
   `<skill>/skills/<sub>/SKILL.md`. The dispatcher decides which subskill
   to call; subskills can be invoked directly by name as well.
5. **Stateless skills, stateful content.** Skills must not store state in
   their own folder. Per-learner state lives next to the content:
   `models/<slug>/.progress.json` for `explore-model`,
   `workshops/<slug>/.progress.json` for `run-workshop`. Both are
   gitignored.
6. **Foundry / Azure framing.** Examples and prompts stay Microsoft
   Foundry-centric. Do not name competitor clouds in skill content.
7. **Inclusive language.** Use "key points" or "sentences" instead of
   "bullets"/"bullet points" in skill prose.

## Adding a new skill

1. Create `.agents/skills/<your-skill>/SKILL.md` following the frontmatter
   shape above.
2. If the skill scaffolds files, put templates in `<your-skill>/templates/`.
3. Add a row to the **Current skills** table above.
4. If the skill dispatches to subskills, list them in its own `SKILL.md`
   and create each `skills/<sub>/SKILL.md`.

## Invoking a skill

Skills are invoked by name in a Copilot prompt, e.g.:

- "Use the `add-workshop` skill to start a new workshop on evaluators."
- "Use the `add-model` skill to add `gpt-5-mini-azure-direct`."
- "Run the `run-workshop` skill on `workshops/foundry-intro`."
- "Use the `explore-model` skill on `models/gpt-5-mini-azure-direct`."
- "Use `run-workshop/learn-more` to explain continuous evaluation."
- "Use `explore-model/troubleshoot` — my first call returned 401."
