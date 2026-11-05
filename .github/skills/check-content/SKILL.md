---
name: check-content
description: The content rules for this repo — layout, notebook structure, voice, brand, CHANGELOG and README formats. Use when writing or reviewing any capsule, multi-model notebook, primer, or dataset, and before every commit.
---

# check-content

The single source of truth for how content in this repo looks. Other skills
follow these rules; reviewers check against them.

## How to run it

1. Run `python scripts/check.py`. It enforces the mechanical rules marked
   **(auto)** below and must print `OK`.
2. Read each changed file against the rules not marked **(auto)** and fix
   what doesn't match. Report anything you couldn't fix.

## Layout

| Path | Holds |
|---|---|
| `capsules/<model>/` | One model release. Notebook(s) plus any input assets (`images/`, `data/`). |
| `multi-model/<scenario>/` | A scenario that compares or combines two or more models. |
| `archive/<model>/` | A capsule whose model is retired. |
| `primers/<slug>.md` | A beginner explainer for one model category or capability. |
| `datasets/<name>/` | A shared, fictitious business scenario (data, instructions, benchmark). |
| `setup.ipynb` | One-time Foundry project and `.env` setup. |

- **(auto)** Capsule, multi-model, and archive folders are notebook-only — no `README.md`.
- **(auto)** Every notebook name starts with its folder name: `mai-voice-2/mai-voice-2-01-<topic>.ipynb`.
- Folder names are the model's lowercase catalog name (`mai-image-2.5-pro`). A model updated by date (like model router) keeps one folder and adds dated notebooks: `model-router-<mmm-yyyy>-NN-<topic>.ipynb`.
- Generated files go in a git-ignored `output/` folder inside the capsule.

## Notebook structure

1. **(auto)** **Cell 1 — header (markdown).** `# <Model>`, a one-sentence summary, then a table with Released, Publisher, Capability (linked to the primer), Model card, Announcement, and Pricing (with source). Multi-notebook capsules list every notebook. Ends with: *First time here? Run `[setup.ipynb](../../setup.ipynb)` once…*
2. **Cell 2 — About this release (markdown).** What's new, the deployments and environment variables this notebook needs, and known limits.
3. **(auto)** **Env check (code), within the first few cells.** Calls `load_dotenv()`, checks every variable the notebook needs, and raises an error naming the missing variables and pointing to `setup.ipynb`.
4. **Numbered sections** — `## 1. <Verb phrase>`, alternating markdown and code. Section titles are actions ("Send a chat request").
5. **Your Turn to Explore** — markdown with 2–3 concrete directions, plus an empty code cell.
6. **Summary** — what we covered, when to reach for this model, links to primers.
7. **References** — markdown links: model card, Microsoft Learn docs, release post.

Also:

- 1–3 concepts per notebook. More concepts → more notebooks with a shared prefix.
- Each notebook runs on its own; don't depend on another notebook's kernel state.
- Clear large outputs before committing; keep one representative result per section so the notebook renders quickly on GitHub.

## Multi-model notebooks

Same structure, but frame the header around a **practical scenario** (a business task) and list the models compared, each linked to its capsule. Use a dataset from `datasets/` when one fits.

## Primers

`# <Category>`, a one-line quote, a mermaid diagram, then sections covering **when to reach for it**, **when *not* to**, **Key terms** (optional, `### Term` with a developer question in italics), **Try it** (links to capsules — omit when none exist), and **Learn more** (up to 3 links, Microsoft Learn first). Question-style headers ("How does a decision API work?") are preferred for new primers.

## CHANGELOG

One table, newest first. One row per capsule (and per multi-model notebook):

```
| YYYY-MM-DD | [Model](model-card-url) | Publisher | One-line what's new — [release post](url) | [Open](capsules/<model>/) |
```

- **(auto)** The README **What's new** table equals the top 3 CHANGELOG rows (capsule name, link, and date). Use `refresh-recent-activity` to update it.
- Archived capsules keep their row; append ` _(archived)_` to the Model cell and point the link at `archive/<model>/`.
- Releases we haven't built a capsule for go in `.github/planning.md`, not here.

## Voice

- Lead with the developer question the content answers.
- Use **"we"**, not "you".
- Start a definition by restating the term ("A context window is …").
- No hype: never *revolutionary, game-changing, unlocks, supercharge, seamless, cutting-edge, best-in-class, state-of-the-art, powerful, effortlessly*.
- Prefer a worked example or a mermaid diagram over abstract prose.
- No emoji, except an occasional "Success".
- Write "model router" in lowercase in prose.

## Brand and grounding

- **(auto)** Always "Microsoft Foundry" (or "Foundry") — never `Azure AI Foundry`. URLs are exempt.
- Prefer `learn.microsoft.com` links; fall back to publisher pages only when Learn has no page.
- **(auto)** Every relative link resolves.
