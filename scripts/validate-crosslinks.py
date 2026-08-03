#!/usr/bin/env python3
"""
validate-crosslinks.py — enforce the structural invariants that hold a
manual (non-agent) contribution together.

Schema validity is checked by `validate-specs.py`; this script covers
what a human reviewer would otherwise have to eyeball:

1. Every capsule folder `models/<family>/<model>/<YYYY-MM-DD>/` has a
   matching row in `CHANGELOG.md`.
2. Every capsule appears in its family README's members list (loose
   grep — the model slug must be mentioned somewhere in the family
   README).
3. Every capability tag used by a capsule has a matching primer file
   in `docs/primers/<slug>.md`.
4. `README.md` "Recently added" top 3 rows match the top 3 rows of
   `CHANGELOG.md` by (date, model).
5. No unresolved `_review_` placeholder tokens remain in the repo.

Exit 0 if all invariants hold, 1 otherwise (per-issue messages
printed).

Usage:
    python scripts/validate-crosslinks.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.stderr.write("Missing dep. Install with: pip install pyyaml\n")
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parents[1]
CHANGELOG = REPO_ROOT / "CHANGELOG.md"
README = REPO_ROOT / "README.md"
FAMILY_ROOT = REPO_ROOT / "models"
PRIMERS_DIR = REPO_ROOT / "docs" / "primers"

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
CAPSULE_GLOB = "models/*/*/*/README.md"
DATE_DIR_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

README_MARK_BEGIN = "<!-- BEGIN:RECENTLY-ADDED -->"
README_MARK_END = "<!-- END:RECENTLY-ADDED -->"


def read_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    try:
        return yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return {}


def find_capsules() -> list[Path]:
    caps: list[Path] = []
    for p in REPO_ROOT.glob(CAPSULE_GLOB):
        # Skip the shared quickstart, which lives at
        # models/quickstart/README.md — depth check handles that.
        rel = p.relative_to(REPO_ROOT)
        parts = rel.parts
        # Expect ["models", family, model, date, "README.md"]
        if len(parts) == 5 and DATE_DIR_RE.match(parts[3]):
            caps.append(p)
    return caps


def parse_changelog_rows() -> list[dict[str, str]]:
    if not CHANGELOG.exists():
        return []
    rows: list[dict[str, str]] = []
    in_table = False
    for line in CHANGELOG.read_text(encoding="utf-8").splitlines():
        if line.startswith("| Date |"):
            in_table = True
            continue
        if in_table and re.match(r"^\|\s*---", line):
            continue
        if in_table:
            if not line.strip().startswith("|"):
                break
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 6:
                continue
            # Date cell may be `[YYYY-MM-DD](url)` or plain.
            date_cell = cells[0]
            m = re.search(r"\d{4}-\d{2}-\d{2}", date_cell)
            date = m.group(0) if m else date_cell
            # Model cell may be `[Model](url)` or plain.
            model_cell = cells[2]
            m = re.match(r"\[([^\]]+)\]", model_cell)
            model = m.group(1) if m else model_cell
            rows.append({
                "date": date,
                "family": cells[1],
                "model": model.strip(),
            })
    return rows


def parse_readme_recent() -> list[dict[str, str]]:
    if not README.exists():
        return []
    text = README.read_text(encoding="utf-8")
    m = re.search(
        re.escape(README_MARK_BEGIN) + r"(.*?)" + re.escape(README_MARK_END),
        text,
        re.DOTALL,
    )
    if not m:
        return []
    rows: list[dict[str, str]] = []
    in_body = False
    for line in m.group(1).splitlines():
        if line.startswith("| Release date"):
            in_body = True
            continue
        if in_body and re.match(r"^\|\s*---", line):
            continue
        if in_body:
            if not line.strip().startswith("|"):
                break
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 4:
                continue
            date_cell = cells[0]
            m2 = re.search(r"\d{4}-\d{2}-\d{2}", date_cell)
            date = m2.group(0) if m2 else date_cell
            model_cell = cells[1]
            m2 = re.match(r"\*\*([^*]+)\*\*", model_cell)
            model = (m2.group(1) if m2 else model_cell).strip()
            rows.append({"date": date, "model": model})
    return rows


def check_capsule_in_changelog(
    capsules: list[Path], changelog: list[dict[str, str]]
) -> list[str]:
    errs: list[str] = []
    idx = {(r["date"], r["model"].lower()) for r in changelog}
    for cap in capsules:
        rel = cap.relative_to(REPO_ROOT)
        _, family, model_slug, date, _ = rel.parts
        fm = read_frontmatter(cap)
        model_name = str(fm.get("model") or model_slug).strip()
        key = (date, model_name.lower())
        # Also accept match on model slug (some manual authors put slug
        # in the Model cell).
        alt = (date, model_slug.lower())
        if key not in idx and alt not in idx:
            errs.append(
                f"[crosslink] capsule {rel} has no matching CHANGELOG "
                f"row (looked for date={date} + model={model_name!r})"
            )
    return errs


def check_capsule_in_family_readme(capsules: list[Path]) -> list[str]:
    errs: list[str] = []
    for cap in capsules:
        rel = cap.relative_to(REPO_ROOT)
        _, family, model_slug, _date, _ = rel.parts
        family_readme = FAMILY_ROOT / family / "README.md"
        if not family_readme.exists():
            errs.append(
                f"[crosslink] capsule {rel} — family README "
                f"{family_readme.relative_to(REPO_ROOT)} does not exist"
            )
            continue
        content = family_readme.read_text(encoding="utf-8").lower()
        if model_slug.lower() not in content:
            errs.append(
                f"[crosslink] family README models/{family}/README.md "
                f"does not mention model slug {model_slug!r} "
                f"(capsule {rel})"
            )
    return errs


def check_capabilities_have_primers(capsules: list[Path]) -> list[str]:
    errs: list[str] = []
    known_primers = {
        p.stem for p in PRIMERS_DIR.glob("*.md")
    } if PRIMERS_DIR.exists() else set()
    for cap in capsules:
        fm = read_frontmatter(cap)
        tags = fm.get("capabilities") or fm.get("tags") or []
        if not isinstance(tags, list):
            continue
        for tag in tags:
            slug = str(tag).strip().lower()
            if not slug:
                continue
            if slug not in known_primers:
                errs.append(
                    f"[crosslink] capsule "
                    f"{cap.relative_to(REPO_ROOT)} uses capability "
                    f"tag {slug!r} but no primer exists at "
                    f"docs/primers/{slug}.md"
                )
    return errs


def check_readme_matches_changelog(
    readme_rows: list[dict[str, str]],
    changelog: list[dict[str, str]],
) -> list[str]:
    errs: list[str] = []
    if not changelog:
        return errs
    if not readme_rows:
        errs.append(
            "[crosslink] README.md is missing the "
            "<!-- BEGIN:RECENTLY-ADDED --> table"
        )
        return errs
    expected = [
        (r["date"], r["model"].lower()) for r in changelog[:3]
    ]
    actual = [
        (r["date"], r["model"].lower()) for r in readme_rows[:3]
    ]
    if expected != actual:
        errs.append(
            "[crosslink] README Recently added top 3 does not match "
            "CHANGELOG top 3:\n"
            f"    README:    {actual}\n"
            f"    CHANGELOG: {expected}\n"
            "  → run `refresh-recent-activity` or update README by hand."
        )
    return errs


PLACEHOLDER_RE = re.compile(r"_review_")


def check_no_placeholders() -> list[str]:
    errs: list[str] = []
    # Files where placeholders are legitimate documentation examples.
    ALLOW = {
        REPO_ROOT / "scripts" / "scan_foundry_blog.py",
        REPO_ROOT / ".github" / "workflows" / "scan-foundry-blog.yml",
        REPO_ROOT / ".github" / "pull_request_template.md",
        REPO_ROOT / ".github" / "maintainer-guide.md",
    }
    scan_globs = ["CHANGELOG.md", "README.md", "docs/**/*.md",
                  "models/**/*.md", ".github/**/*.md"]
    for glob in scan_globs:
        for p in REPO_ROOT.glob(glob):
            if p in ALLOW:
                continue
            try:
                text = p.read_text(encoding="utf-8")
            except Exception:
                continue
            if PLACEHOLDER_RE.search(text):
                errs.append(
                    f"[crosslink] {p.relative_to(REPO_ROOT)} contains "
                    "an unresolved `_review_` placeholder — please "
                    "complete it before merging."
                )
    return errs


def main() -> int:
    capsules = find_capsules()
    changelog = parse_changelog_rows()
    readme_rows = parse_readme_recent()

    all_errs: list[str] = []
    all_errs += check_capsule_in_changelog(capsules, changelog)
    all_errs += check_capsule_in_family_readme(capsules)
    all_errs += check_capabilities_have_primers(capsules)
    all_errs += check_readme_matches_changelog(readme_rows, changelog)
    all_errs += check_no_placeholders()

    if all_errs:
        for e in all_errs:
            print(e)
        print(f"\n{len(all_errs)} crosslink failure(s).")
        return 1
    print(
        f"Crosslinks OK — {len(capsules)} capsule(s), "
        f"{len(changelog)} CHANGELOG row(s), "
        f"{len(readme_rows)} README row(s)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
