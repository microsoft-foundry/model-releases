---
name: check-content
description: The content rules for this repo — layout, notebook structure, voice, brand, CHANGELOG and README formats. Use when writing or reviewing any capsule, multi-model notebook, primer, or scenario, and before every commit.
---

# check-content

The single source of truth for how content in this repo looks. Other skills
follow these rules; reviewers check against them.

## How to run it

1. Run `python 1-scripts/check.py`. It enforces the mechanical rules marked
   **(auto)** below and must print `OK`.
2. Read each changed file against the rules not marked **(auto)** and fix
   what doesn't match. Report anything you couldn't fix.

## Layout

A **release capsule** is the hands-on content we create for a release. The folder it lives in says its scope.

| Path | Holds |
|---|---|
| `0-archive/<model>/` | A release capsule whose model is retired. |
| `1-scripts/` | Setup (`setenv.sh`, `sample.env`), `make_banner.py`, and `check.py`. |
| `2-scenarios/<name>/` | A shared, fictitious business scenario (data, instructions, benchmark). |
| `3-primers/<slug>.md` | A beginner explainer for one model category or capability. |
| `4-models/<model>/` | A single-model release capsule: notebook(s) plus any input assets (`images/`, `data/`) and optional replay clips (`examples/`). |
| `5-multi-model/<scenario>/` | A multi-model release capsule that compares or combines two or more models. |
| `setup.ipynb` | One-time Foundry project and `.env` setup. |

- **(auto)** Folders under `0-archive/`, `4-models/`, and `5-multi-model/` are notebook-only — no `README.md`.
- **(auto)** Every notebook name starts with its folder name: `mai-voice-2/mai-voice-2-01-<topic>.ipynb`.
- Folder names are the model's lowercase catalog name (`mai-image-2.5-pro`). A model updated by date (like model router) keeps one folder and adds dated notebooks: `model-router-<mmm-yyyy>-NN-<topic>.ipynb`.
- Generated files go in a git-ignored `output/` folder inside the capsule.
- Slow or costly capsules may commit a few small sample results to `examples/` and offer a **replay mode**: a `DEMO_MODE` setting (`replay` or `live`, read from `.env`, overridable in the notebook) that shows `output/` first, then `examples/`, and never calls the model in replay.

## Notebook structure

[setup.ipynb](../../../setup.ipynb) is the reference. Every notebook — setup, single-model, and multi-model — follows this order:

1. **Opening cell (markdown).** Banner image (made with `1-scripts/make_banner.py`), `# <Title>`, the guiding question as a `>` quote, one or two plain sentences on what we'll do, then **`## What We Will Do`** (2–4 bullets), then the tip: *Run each cell with Shift + Enter; guess first.*
2. **At a glance (capsules only).** Released, Publisher, Capability (linked to the primer), Model card, Announcement, Pricing (with source), the deployments and env vars needed, and a link to `setup.ipynb` for first-timers.
3. **(auto)** **Env check (code), within the first few cells.** Calls `load_dotenv()`, checks every variable the notebook needs, and names the missing ones.
4. **Numbered question sections.** Each starts with the divider image, then `## N. <Question>?`, 1–2 sentences, an optional `> 🔮 **Guess first:**` prompt, then code. Keep prose short — get to the code.
5. **One `### 🔧 Break it on purpose`** cell somewhere it teaches how to read a failure.
6. **Your Turn to Explore (capsules).** 2–3 concrete directions plus an empty code cell.
7. **Closing cell — `## What We Did`.** ✅ bullets that mirror What We Will Do, then ➡️ **Next**, a "Stuck?" link, and up to 3 references.

Also:

- Prefer short sentences and bullets over tables; put troubleshooting hints in the error messages themselves.
- 1–3 concepts per notebook. More concepts → more notebooks with a shared prefix.
- Each notebook runs on its own; don't depend on another notebook's kernel state.
- Clear large outputs before committing; keep one representative result per section so the notebook renders quickly on GitHub.

### Optional sections

Use these when a capsule doubles as a field enablement guide:

- **What to look for:** a bold line after an output with 2–4 concrete checks (what should be true, what usually goes wrong).
- **`### Scoreboard`:** a table of what we measured across the notebook's calls (latency, output size, requested vs delivered). Never estimate cost from unpublished prices; link the pricing source instead.
- **`## Teach it to a customer`:** before Your Turn to Explore. What it does and why it matters, a prompt recipe, honest answers to common questions (preview status, data handling, limits), and a symptom → cause → fix list.
- **Primer pointer:** when a capability has its own vocabulary, the opening cell tells readers to read the primer first.

## Multi-model notebooks

Same structure, but frame the header around a **practical scenario** (a business task) and list the models compared, each linked to its capsule. Use a scenario from `2-scenarios/` when one fits.

## Primers

`# <Category>`, a one-line quote, a mermaid diagram, then sections covering **when to reach for it**, **when *not* to**, **Key terms** (optional, `### Term` with a developer question in italics), **Try it** (links to capsules — omit when none exist), and **Learn more** (up to 3 links, Microsoft Learn first). Question-style headers ("How does a decision API work?") are preferred for new primers.

## CHANGELOG

One table, newest first. One row per capsule (and per multi-model notebook):

```
| YYYY-MM-DD | [Model](model-card-url) | Publisher | One-line what's new — [release post](url) | [Open](4-models/<model>/) |
```

- **(auto)** The README **What's new** table equals the top 3 CHANGELOG rows (capsule name, link, and date). Use `refresh-recent-activity` to update it.
- Archived capsules keep their row; append ` _(archived)_` to the Model cell and point the link at `0-archive/<model>/`.
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
