---
name: add-primer
description: Write a beginner primer for a model category or capability under 3-primers/<slug>.md. Use when a capsule introduces a capability that has no primer yet, or when a key term needs explaining.
---

# add-primer

1. Ask for the category name, a one-line description, and up to 3 Microsoft Learn links.
2. Create `3-primers/<slug>.md` with the primer structure in [check-content](../check-content/SKILL.md): quote line, mermaid diagram, When to reach for it, When *not* to, Key terms (optional), Try it (only if capsules exist), Learn more.
3. To add a **term** rather than a category, add a `### Term` under **Key terms** in the closest primer. Open with the developer question in italics, then restate the term ("Right-sizing is about …").
4. Add a row to the **Learn the basics** table in `README.md`.
5. Run `python 1-scripts/check.py`.
