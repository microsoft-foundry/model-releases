#!/usr/bin/env python3
"""
generate-catalog.py — build the machine-readable index of this repo.

Writes two artifacts, both generated from artifact frontmatter so they
can never drift from the content:

1. `catalog.json` — the full structured catalog. One fetch gives an
   agent every capsule, scenario, publisher, and primer with its models,
   capabilities, pricing, and notebook paths. Retrieval systems chunk
   per-file, so this exists to spare an agent from crawling the tree.

2. `llms.txt` — the /llms.txt convention: a short, link-dense markdown
   map of the repo for LLM consumers.
   Grounding: https://llmstxt.org/

Usage:
    python scripts/generate-catalog.py           # write the files
    python scripts/generate-catalog.py --check   # verify they're current

Exit code:
    0 = written (or, with --check, already current)
    1 = with --check, the files are stale — re-run without --check
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.stderr.write("Missing dep. Install with: pip install pyyaml\n")
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parents[1]
REPO_URL = "https://github.com/microsoft-foundry/model-releases"
CATALOG = REPO_ROOT / "catalog.json"
LLMS_TXT = REPO_ROOT / "llms.txt"
CAPSULE_TOC = REPO_ROOT / "CAPSULE-TOC.md"
README = REPO_ROOT / "README.md"
DOCS_README = REPO_ROOT / "docs" / "README.md"

# Marker-bracketed regions this script owns. Prose outside them is
# hand-written and preserved.
TOC_MARKERS = ("<!-- BEGIN:CAPSULE-TABLES -->",
               "<!-- END:CAPSULE-TABLES -->")
README_MARKERS = ("<!-- BEGIN:RECENT-CAPSULES -->",
                  "<!-- END:RECENT-CAPSULES -->")
TAXONOMY_MARKERS = ("<!-- BEGIN:CAPABILITY-TAXONOMY -->",
                    "<!-- END:CAPABILITY-TAXONOMY -->")

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
RESERVED_DIRS = {"quickstart", "multi-model-scenarios"}


def read_frontmatter(path: Path) -> dict:
    m = FRONTMATTER_RE.match(path.read_text(encoding="utf-8"))
    if not m:
        return {}
    try:
        return yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return {}


def display_title(path: Path, fallback: str) -> str:
    """The README H1, minus the ' — Release Capsule' suffix.

    Frontmatter carries the lowercase slug; the H1 carries the branded
    name (MAI-Image-2.5-Pro), which is what belongs in search results.
    """
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return re.sub(r"\s*[—-]\s*(Release Capsule|Scenario)\s*$",
                          "", line[2:]).strip()
    return fallback


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def notebooks_of(fm: dict, folder: Path) -> list[dict]:
    out = []
    for nb in fm.get("notebooks") or []:
        if not isinstance(nb, dict) or not nb.get("path"):
            continue
        out.append({
            "path": rel(folder / str(nb["path"])),
            "title": nb.get("title", ""),
            "concepts": nb.get("concepts") or [],
        })
    return out


def collect() -> dict:
    capsules, scenarios, publishers, primers = [], [], [], []

    for p in sorted(REPO_ROOT.glob("models/*/*/README.md")):
        parts = p.relative_to(REPO_ROOT).parts
        if parts[1] in RESERVED_DIRS or parts[2] in RESERVED_DIRS:
            continue
        fm = read_frontmatter(p)
        if fm.get("kind") != "capsule":
            continue
        pricing = fm.get("pricing") or {}
        capsules.append({
            "model": fm.get("model"),
            "name": display_title(p, str(fm.get("model") or "")),
            "publisher": fm.get("publisher"),
            "summary": fm.get("summary"),
            "release_date": str(fm.get("release_date") or ""),
            "last_updated": str(fm.get("last_updated")
                                or fm.get("release_date") or ""),
            "capabilities": fm.get("capabilities") or [],
            "model_card": fm.get("model_card"),
            "announcement": fm.get("announcement"),
            "pricing": {
                "notes": pricing.get("notes"),
                "source": pricing.get("url"),
            } if pricing else None,
            "domains": fm.get("domains") or [],
            "path": rel(p.parent),
            "url": f"{REPO_URL}/tree/main/{rel(p.parent)}",
            "notebooks": notebooks_of(fm, p.parent),
        })

    scen_globs = ("models/multi-model-scenarios/*/README.md",
                  "models/*/multi-model-scenarios/*/README.md")
    for glob in scen_globs:
        for p in sorted(REPO_ROOT.glob(glob)):
            fm = read_frontmatter(p)
            if fm.get("kind") != "scenario":
                continue
            scenarios.append({
                "slug": fm.get("slug"),
                "title": fm.get("title"),
                "summary": fm.get("summary"),
                "last_updated": str(fm.get("last_updated") or ""),
                "scope": fm.get("scope"),
                "publisher": fm.get("publisher"),
                "models": fm.get("models") or [],
                "capabilities": fm.get("capabilities") or [],
                "path": rel(p.parent),
                "url": f"{REPO_URL}/tree/main/{rel(p.parent)}",
                "notebooks": notebooks_of(fm, p.parent),
            })

    for p in sorted(REPO_ROOT.glob("models/*/README.md")):
        fm = read_frontmatter(p)
        if fm.get("kind") != "publisher":
            continue
        publishers.append({
            "slug": fm.get("slug"),
            "name": fm.get("name"),
            "provider": fm.get("provider"),
            "one_line": fm.get("one_line"),
            "path": rel(p.parent),
        })

    capabilities = []
    for p in sorted(REPO_ROOT.glob("docs/primers/*.md")):
        fm = read_frontmatter(p)
        if fm.get("kind") != "primer":
            continue
        primers.append({
            "capability": fm.get("capability"),
            "label": fm.get("label"),
            "slug": fm.get("slug"),
            "one_line": fm.get("one_line"),
            "path": rel(p),
        })
        # The taxonomy: one entry per usable tag, including aliases.
        capabilities.append({
            "capability": fm.get("capability"),
            "label": fm.get("label"),
            "description": fm.get("one_line"),
            "primer": fm.get("slug"),
            "primer_path": rel(p),
        })
        for alias in fm.get("aliases") or []:
            if isinstance(alias, dict):
                capabilities.append({
                    "capability": alias.get("capability"),
                    "label": alias.get("label"),
                    "description": (alias.get("description")
                                    or fm.get("one_line")),
                    "primer": fm.get("slug"),
                    "primer_path": rel(p),
                })
    capabilities.sort(key=lambda c: c["label"] or "")

    capsules.sort(key=lambda c: (c["release_date"], c["model"] or ""),
                  reverse=True)
    return {
        "name": "Microsoft Foundry Model Releases",
        "description": (
            "Release capsules for Microsoft Foundry model announcements — "
            "each pairs a model release with a runnable notebook."
        ),
        "url": REPO_URL,
        "capabilities": capabilities,
        "counts": {
            "capsules": len(capsules),
            "scenarios": len(scenarios),
            "publishers": len(publishers),
            "primers": len(primers),
        },
        "capsules": capsules,
        "scenarios": scenarios,
        "publishers": publishers,
        "primers": primers,
    }


def _sentence(text: str) -> str:
    """Terminate a summary fragment.

    Summaries are written as phrases so they read cleanly in table
    cells next to the model name; llms.txt runs them together with
    further sentences, so it adds the period back here.
    """
    text = (text or "").strip()
    return text if text.endswith((".", "!", "?")) else text + "."


def render_llms_txt(cat: dict) -> str:
    L: list[str] = [
        "# Microsoft Foundry Model Releases",
        "",
        f"> {cat['description']} A capsule is a folder holding a README "
        "and a Jupyter notebook you can run against your own Foundry "
        "project.",
        "",
        "Announcements are tracked in CHANGELOG.md, newest first, "
        "grouped by month. Capsules are indexed in CAPSULE-TOC.md, "
        "grouped by provider. catalog.json holds this same index in "
        "structured form.",
        "",
        "## Capsules",
        "",
    ]
    for c in cat["capsules"]:
        caps = ", ".join(c["capabilities"])
        L.append(
            f"- [{c['name']}]({c['url']}): {_sentence(c['summary'])} "
            f"Publisher: {c['publisher']}. Capabilities: {caps}. "
            f"Released {c['release_date']}."
        )
    if cat["scenarios"]:
        L += ["", "## Multi-model scenarios", ""]
        for s in cat["scenarios"]:
            models = ", ".join(
                m.get("model", "") for m in s["models"]
                if isinstance(m, dict)
            )
            L.append(
                f"- [{s['title']}]({s['url']}): {_sentence(s['summary'])} "
                f"Compares: {models}."
            )
    L += ["", "## Capability primers", ""]
    for p in cat["primers"]:
        L.append(
            f"- [{p['capability']}]({REPO_URL}/blob/main/{p['path']}): "
            f"{p['one_line']}"
        )
    L += ["", "## Optional", "",
          f"- [CHANGELOG]({REPO_URL}/blob/main/CHANGELOG.md): "
          "every Foundry model release announcement",
          f"- [CAPSULE-TOC]({REPO_URL}/blob/main/CAPSULE-TOC.md): "
          "capsule index grouped by provider",
          f"- [Glossary]({REPO_URL}/blob/main/docs/GLOSSARY.md): "
          "terminology used across capsules",
          f"- [Quickstart]({REPO_URL}/tree/main/models/quickstart): "
          "one-time Foundry project and .env setup",
          ""]
    return "\n".join(L)


def _rows(header: list[str], rows: list[list[str]]) -> str:
    """Render a GitHub markdown table."""
    out = ["| " + " | ".join(header) + " |",
           "| " + " | ".join("---" for _ in header) + " |"]
    out += ["| " + " | ".join(r) + " |" for r in rows]
    return "\n".join(out)


def _recency(item: dict) -> str:
    return item.get("last_updated") or item.get("release_date") or ""


def _by_recency(items: list[dict]) -> list[dict]:
    return sorted(items, key=lambda i: (_recency(i), i.get("name") or
                                        i.get("title") or ""), reverse=True)


def render_capsule_toc(cat: dict) -> str:
    """Provider-grouped capsule tables, plus the scenario table."""
    labels = {c["capability"]: c["label"] for c in cat["capabilities"]}
    pub_names = {f["slug"]: f["name"] for f in cat["publishers"]}
    blocks: list[str] = []

    by_publisher: dict[str, list[dict]] = {}
    for c in cat["capsules"]:
        by_publisher.setdefault(c["publisher"], []).append(c)

    for slug in sorted(by_publisher, key=lambda s: pub_names.get(s, s)):
        rows = [
            [f"[{c['name']}]({c['path']}/)",
             ", ".join(labels.get(t, t) for t in c["capabilities"]),
             _recency(c),
             c["summary"]]
            for c in _by_recency(by_publisher[slug])
        ]
        blocks.append(
            f"## {pub_names.get(slug, slug)}\n\n"
            + _rows(["Capsule", "Capability", "Last updated",
                     "Description"], rows)
        )

    if cat["scenarios"]:
        rows = [
            [f"[{s['title']}]({s['path']}/)",
             pub_names.get(s.get("publisher"), s.get("publisher") or "—"),
             _recency(s),
             s["summary"]]
            for s in _by_recency(cat["scenarios"])
        ]
        blocks.append(
            "## Multi-model scenarios\n\n"
            "A scenario covers more than one release in a single "
            "notebook, so it can't live in any one capsule. It sits in a "
            "`multi-model-scenarios/` folder in one of two places. Under a "
            "publisher (`models/<publisher>/multi-model-scenarios/`) it goes "
            "deeper on models from that publisher - often a technical dive "
            "that uses several together, not necessarily a comparison. At "
            "the top level (`models/multi-model-scenarios/`) it spans "
            "publishers.\n\n"
            + _rows(["Scenario", "Publisher", "Last updated", "Description"],
                    rows)
        )
    return "\n\n<br/>\n\n".join(blocks)


def render_recent_capsules(cat: dict, limit: int = 3) -> str:
    """The README's most-recently-updated capsules block."""
    rows = [
        [f"[{c['name']}]({c['path']}/)", _recency(c), c["summary"]]
        for c in _by_recency(cat["capsules"])[:limit]
    ]
    return _rows(["Capsule", "Last updated", "Description"], rows)


def render_taxonomy(cat: dict) -> str:
    """The capability taxonomy table in docs/README.md."""
    rows = [
        [f"`{c['capability']}`", c["label"], c["description"],
         f"[{c['primer']}](primers/{c['primer']}.md)"]
        for c in cat["capabilities"]
    ]
    return _rows(["Tag", "Capability", "What it means", "Primer"], rows)


def replace_block(path: Path, markers: tuple[str, str], body: str) -> str:
    """Swap the content between markers, preserving surrounding prose."""
    begin, end = markers
    text = path.read_text(encoding="utf-8")
    i, j = text.find(begin), text.find(end)
    if i == -1 or j == -1:
        raise SystemExit(f"[catalog] missing {begin} / {end} in {rel(path)}")
    return text[:i] + begin + "\n" + body + "\n" + text[j:]


def main() -> int:
    check = "--check" in sys.argv
    cat = collect()
    catalog_text = json.dumps(cat, indent=2, ensure_ascii=False) + "\n"
    llms_text = render_llms_txt(cat)
    targets = [
        (CATALOG, catalog_text),
        (LLMS_TXT, llms_text),
        (CAPSULE_TOC,
         replace_block(CAPSULE_TOC, TOC_MARKERS, render_capsule_toc(cat))),
        (README,
         replace_block(README, README_MARKERS, render_recent_capsules(cat))),
        (DOCS_README,
         replace_block(DOCS_README, TAXONOMY_MARKERS, render_taxonomy(cat))),
    ]

    if check:
        stale = []
        for path, want in targets:
            have = path.read_text(encoding="utf-8") if path.exists() else ""
            if have != want:
                stale.append(rel(path))
        if stale:
            print(
                "[catalog] stale generated file(s): "
                + ", ".join(stale)
                + "\n  → run `python scripts/generate-catalog.py`"
            )
            return 1
        print("Catalog OK — all generated files are current.")
        return 0

    for path, want in targets:
        path.write_text(want, encoding="utf-8")
    c = cat["counts"]
    print(
        "Wrote " + ", ".join(rel(p) for p, _ in targets)
        + f" — {c['capsules']} capsule(s), "
        f"{c['scenarios']} scenario(s), {c['publishers']} publisher(s), "
        f"{c['primers']} primer(s)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
