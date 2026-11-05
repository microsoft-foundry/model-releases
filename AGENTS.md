# AGENTS.md

Guidance for AI coding agents working in **model-releases**.

This repo exists so developers can get hands-on with a new Microsoft Foundry model release as fast as possible. It answers three questions: what was released recently ([CHANGELOG.md](CHANGELOG.md)), what makes a model category different ([primers/](primers/)), and how do I try it ([capsules/](capsules/), [multi-model/](multi-model/)).

## Golden rules

- **Follow [check-content](.github/skills/check-content/SKILL.md)** — it holds every content rule.
- **Validate after every change:** `python scripts/check.py` must print `OK`.
- **Use the skills** in [.github/skills/](.github/skills/) for adding capsules, multi-model notebooks, primers, and refreshing the README.
- **`.do-not-commit/` is scratch** — never read it or use it as context.

## Where to look

- How to contribute: [CONTRIBUTING.md](CONTRIBUTING.md)
- Backlog of releases and publishers to cover: [.github/planning.md](.github/planning.md)
