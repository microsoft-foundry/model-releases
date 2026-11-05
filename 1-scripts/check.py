#!/usr/bin/env python3
"""Check repo layout, links, notebook openings, and README/CHANGELOG sync.

Usage: python 1-scripts/check.py
Rules live in .github/skills/check-content/SKILL.md; this script enforces the mechanical ones.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", ".do-not-commit", "node_modules", ".venv", "venv", "output", ".ipynb_checkpoints"}
CAPSULE_ROOTS = ["4-models", "5-multi-model", "0-archive"]
LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)|<img[^>]+src=\"([^\"]+)\"|<a[^>]+href=\"([^\"]+)\"")
BRAND_RE = re.compile(r"Azure AI Foundry|Azure Foundry")

errors: list[str] = []


def rel(p: Path) -> str:
    return str(p.relative_to(ROOT))


def walk(suffixes: tuple[str, ...]):
    for p in sorted(ROOT.rglob("*")):
        if p.is_file() and p.suffix in suffixes and not SKIP_DIRS.intersection(p.relative_to(ROOT).parts):
            yield p


def slugify(heading: str) -> str:
    heading = re.sub(r"[`*_]|\[([^\]]*)\]\([^)]*\)", r"\1", heading.strip().lower())
    return re.sub(r"\s", "-", re.sub(r"[^\w\s-]", "", heading))


def anchors(md: str) -> set[str]:
    return {slugify(m) for m in re.findall(r"(?m)^#{1,6}\s+(.+?)\s*$", md)}


def markdown_of(path: Path) -> str:
    if path.suffix == ".ipynb":
        cells = json.loads(path.read_text())["cells"]
        return "\n\n".join("".join(c["source"]) for c in cells if c["cell_type"] == "markdown")
    return path.read_text()


def strip_code(md: str) -> str:
    return re.sub(r"```.*?```|`[^`\n]*`", "", md, flags=re.S)


def check_links():
    for path in walk((".md", ".ipynb")):
        md = strip_code(markdown_of(path))
        for groups in LINK_RE.findall(md):
            target = next(g for g in groups if g)
            if re.match(r"^(https?:|mailto:|#$)", target) or "<" in target:
                continue
            file_part, _, anchor = target.partition("#")
            dest = path if not file_part else (path.parent / unquote(file_part)).resolve()
            if not dest.exists():
                errors.append(f"{rel(path)}: broken link -> {target}")
            elif anchor and dest.suffix in (".md", ".ipynb") and anchor not in anchors(markdown_of(dest)):
                errors.append(f"{rel(path)}: missing anchor -> {target}")
        if BRAND_RE.search(re.sub(r"\([^)]*\)", "", md)):
            errors.append(f"{rel(path)}: use 'Microsoft Foundry', not 'Azure AI Foundry'")


def check_layout():
    for root in CAPSULE_ROOTS:
        for folder in sorted((ROOT / root).iterdir()) if (ROOT / root).exists() else []:
            if not folder.is_dir():
                continue
            notebooks = sorted(folder.glob("*.ipynb"))
            if not notebooks:
                errors.append(f"{rel(folder)}: needs at least one notebook")
            if (folder / "README.md").exists():
                errors.append(f"{rel(folder)}: capsules are notebook-only; move README content into the first cell")
            for nb in notebooks:
                if not nb.name.startswith(folder.name):
                    errors.append(f"{rel(nb)}: notebook name must start with '{folder.name}'")
                check_notebook_opening(nb)


def check_notebook_opening(nb: Path):
    cells = json.loads(nb.read_text())["cells"]
    first = "".join(cells[0]["source"]) if cells else ""
    if not (cells and cells[0]["cell_type"] == "markdown" and first.startswith("# ")):
        errors.append(f"{rel(nb)}: first cell must be a markdown title ('# <Model>')")
    if "setup.ipynb" not in first:
        errors.append(f"{rel(nb)}: first cell must link to setup.ipynb")
    if not any(c["cell_type"] == "code" and "load_dotenv" in "".join(c["source"]) for c in cells[:8]):
        errors.append(f"{rel(nb)}: an env-check code cell (load_dotenv) must appear near the top")


def changelog_rows() -> list[list[str]]:
    rows = []
    for line in (ROOT / "CHANGELOG.md").read_text().splitlines():
        if re.match(r"^\| \d{4}-\d{2}-\d{2} \|", line):
            rows.append([c.strip() for c in line.strip("|").split("|")])
    return rows


def plain(cell: str) -> str:
    return re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", cell)


def link_target(cell: str) -> str:
    m = re.search(r"\]\(([^)]*)\)", cell)
    return m.group(1) if m else ""


def check_latest():
    readme = (ROOT / "README.md").read_text()
    block = re.search(r"<!-- BEGIN:LATEST -->(.*?)<!-- END:LATEST -->", readme, re.S)
    if not block:
        errors.append("README.md: missing <!-- BEGIN:LATEST --> / <!-- END:LATEST --> block")
        return
    latest = [
        [c.strip() for c in l.strip("|").split("|")]
        for l in block.group(1).strip().splitlines()[2:]
    ]
    expected = [
        [plain(model), date, link_target(link)]
        for date, model, _pub, _note, link in (r[:5] for r in changelog_rows()[:3])
    ]
    got = [[plain(capsule), date, link_target(capsule)] for capsule, date, _what in (r[:3] for r in latest)]
    if got != expected:
        errors.append("README.md: What's new table must match the top 3 CHANGELOG rows (run refresh-recent-activity)")


def main() -> int:
    check_layout()
    check_links()
    check_latest()
    for e in errors:
        print(f"FAIL {e}")
    print("OK" if not errors else f"{len(errors)} problem(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
