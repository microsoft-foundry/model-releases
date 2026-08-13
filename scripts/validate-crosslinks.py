#!/usr/bin/env python3
"""
validate-crosslinks.py — enforce the structural invariants that hold a
manual (non-agent) contribution together.

Schema validity is checked by `validate-specs.py`; this script covers
what a human reviewer would otherwise have to eyeball:

1. Every capsule folder `models/<family>/<model>/` has a matching
   row in `CHANGELOG.md`.
2. Every capsule appears in its family README's members list (loose
   grep — the model slug must be mentioned somewhere in the family
   README).
3. Every capability tag used by a capsule or scenario has a matching
   primer file in `docs/primers/<slug>.md`.
4. Every notebook declared in frontmatter exists on disk, and every
   `.ipynb` under `models/` is claimed by exactly one artifact.
5. Every model a scenario references resolves to a real capsule.
6. `README.md` "Recently added" top 3 rows match the top 3 rows of
   `CHANGELOG.md` by (date, model).
7. No unresolved `_review_` placeholder tokens remain in the repo.

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
CAPSULE_GLOB = "models/*/*/README.md"
SCENARIO_GLOBS = ("models/multi-model-scenarios/*/README.md",
                  "models/*/multi-model-scenarios/*/README.md")
SCENARIO_DIR = "multi-model-scenarios"
RESERVED_DIRS = {"quickstart", SCENARIO_DIR}

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
    """Capsule READMEs at models/<family>/<model>/README.md.

    The release date lives in frontmatter, not the path, so a folder is
    a capsule when it sits one level under a family and is not one of
    the reserved folder names.
    """
    caps: list[Path] = []
    for p in REPO_ROOT.glob(CAPSULE_GLOB):
        parts = p.relative_to(REPO_ROOT).parts
        # Expect ["models", family, model, "README.md"]
        if len(parts) == 4 and parts[2] not in RESERVED_DIRS \
                and parts[1] not in RESERVED_DIRS:
            caps.append(p)
    return caps


def find_scenarios() -> list[Path]:
    """Scenario READMEs — multi-model walkthroughs.

    Family-scoped: models/<family>/multi-model-scenarios/<slug>/README.md
    Cross-family:  models/multi-model-scenarios/<slug>/README.md
    """
    scen: list[Path] = []
    for glob in SCENARIO_GLOBS:
        scen.extend(REPO_ROOT.glob(glob))
    return sorted(set(scen))


def strip_availability(cell: str) -> str:
    """Drop a trailing `_(public preview)_`-style availability note.

    The annotation documents where a release can be used; it is not
    part of the model name, so no row-matching should see it.
    """
    return re.sub(r"\s*_\([^)]*\)_\s*$", "", cell.strip())


def parse_changelog_rows() -> list[dict[str, str]]:
    """Parse CHANGELOG rows, newest first.

    Rows live in one table per `## <Month> <Year>` section, so this
    walks every table in the file rather than stopping at the first
    blank line after the header.
    """
    if not CHANGELOG.exists():
        return []
    text = CHANGELOG.read_text(encoding="utf-8")
    # Drop the trailing HTML-comment template so its placeholder row
    # is never parsed as a real release.
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    rows: list[dict[str, str]] = []
    in_table = False
    for line in text.splitlines():
        if line.startswith("| Date |"):
            in_table = True
            continue
        if not in_table:
            continue
        if re.match(r"^\|\s*---", line):
            continue
        if not line.strip().startswith("|"):
            # End of this month's table; keep looking for the next one.
            in_table = False
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 5:
            continue
        # Date cell may be `[YYYY-MM-DD](url)` or plain.
        m = re.search(r"\d{4}-\d{2}-\d{2}", cells[0])
        date = m.group(0) if m else cells[0]
        # Family cell is plain text, but tolerate a link if one is
        # ever added.
        m = re.match(r"\[([^\]]+)\]", cells[1])
        family = m.group(1) if m else cells[1]
        # Model cell may be `[Model](url)` or plain, and may carry a
        # trailing availability note like `_(public preview)_`.
        model_cell = strip_availability(cells[2])
        m = re.match(r"\[([^\]]+)\]", model_cell)
        model = m.group(1) if m else model_cell
        rows.append({
            "date": date,
            "family": family.strip(),
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
        if line.startswith("| Model"):
            in_body = True
            continue
        if in_body and re.match(r"^\|\s*---", line):
            continue
        if in_body:
            if not line.strip().startswith("|"):
                break
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 3:
                continue
            date_cell = cells[1]
            m2 = re.search(r"\d{4}-\d{2}-\d{2}", date_cell)
            date = m2.group(0) if m2 else date_cell
            model_cell = cells[0]
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
        _, family, model_slug, _ = rel.parts
        fm = read_frontmatter(cap)
        date = str(fm.get("release_date") or "").strip()
        if not date:
            errs.append(
                f"[crosslink] capsule {rel} has no `release_date` in "
                "frontmatter — it is the only source of the release date "
                "now that the folder no longer carries it"
            )
            continue
        if model_slug != str(fm.get("model") or "").strip():
            errs.append(
                f"[crosslink] capsule {rel} — folder name {model_slug!r} "
                f"does not match frontmatter model {fm.get('model')!r}. "
                "When one model has two releases, give the second folder "
                "a clarifying suffix and match `model:` to it."
            )
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
        _, family, model_slug, _ = rel.parts
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
    """Every capability tag must resolve to a primer.

    Resolution is by the primer's `capability` field (plus any
    `aliases`), not by filename: `reasoning` is documented in
    `reasoning-models.md`, and `vision` is covered by
    `multimodal-models.md`.
    """
    errs: list[str] = []
    known: set[str] = set()
    if PRIMERS_DIR.exists():
        for p in PRIMERS_DIR.glob("*.md"):
            fm = read_frontmatter(p)
            if fm.get("capability"):
                known.add(str(fm["capability"]).strip().lower())
            for alias in fm.get("aliases") or []:
                if isinstance(alias, dict) and alias.get("capability"):
                    known.add(str(alias["capability"]).strip().lower())
    for cap in capsules:
        fm = read_frontmatter(cap)
        tags = fm.get("capabilities") or fm.get("tags") or []
        if not isinstance(tags, list):
            continue
        for tag in tags:
            slug = str(tag).strip().lower()
            if not slug:
                continue
            if slug not in known:
                errs.append(
                    f"[crosslink] capsule "
                    f"{cap.relative_to(REPO_ROOT)} uses capability "
                    f"tag {slug!r} but no primer in docs/primers/ "
                    f"declares it (as `capability:` or in `aliases:`)"
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


def check_notebooks_exist(artifacts: list[Path]) -> list[str]:
    """Every notebook declared in frontmatter must exist on disk."""
    errs: list[str] = []
    for art in artifacts:
        fm = read_frontmatter(art)
        for nb in fm.get("notebooks") or []:
            if not isinstance(nb, dict):
                continue
            rel_nb = str(nb.get("path") or "").strip()
            if not rel_nb:
                continue
            if not (art.parent / rel_nb).exists():
                errs.append(
                    f"[crosslink] {art.relative_to(REPO_ROOT)} declares "
                    f"notebook {rel_nb!r} but no such file exists. "
                    "Notebooks live at the artifact folder root."
                )
    return errs


def check_no_orphan_notebooks(artifacts: list[Path]) -> list[str]:
    """No .ipynb under models/ may go unclaimed by an artifact."""
    declared = set()
    for art in artifacts:
        for nb in read_frontmatter(art).get("notebooks") or []:
            if isinstance(nb, dict) and nb.get("path"):
                declared.add((art.parent / str(nb["path"])).resolve())
    errs: list[str] = []
    for nb_path in FAMILY_ROOT.rglob("*.ipynb"):
        if ".ipynb_checkpoints" in nb_path.parts:
            continue
        if nb_path.resolve() not in declared:
            errs.append(
                f"[crosslink] notebook "
                f"{nb_path.relative_to(REPO_ROOT)} is not declared in "
                "any capsule, scenario, or quickstart `notebooks:` "
                "list — every notebook needs an owning artifact"
            )
    return errs


def check_scenario_models_exist(scenarios: list[Path]) -> list[str]:
    """Each model a scenario references must be a real capsule."""
    errs: list[str] = []
    for scen in scenarios:
        rel = scen.relative_to(REPO_ROOT)
        fm = read_frontmatter(scen)
        for entry in fm.get("models") or []:
            if not isinstance(entry, dict):
                continue
            family = str(entry.get("family") or "").strip()
            model = str(entry.get("model") or "").strip()
            target = FAMILY_ROOT / family / model / "README.md"
            if not target.exists():
                errs.append(
                    f"[crosslink] scenario {rel} references "
                    f"{family}/{model} but no capsule exists at "
                    f"models/{family}/{model}/README.md"
                )
    return errs


def main() -> int:
    capsules = find_capsules()
    scenarios = find_scenarios()
    quickstart = [p for p in [FAMILY_ROOT / "quickstart" / "README.md"]
                  if p.exists()]
    changelog = parse_changelog_rows()
    readme_rows = parse_readme_recent()

    all_errs: list[str] = []
    all_errs += check_capsule_in_changelog(capsules, changelog)
    all_errs += check_capsule_in_family_readme(capsules)
    all_errs += check_capabilities_have_primers(capsules)
    all_errs += check_capabilities_have_primers(scenarios)
    all_errs += check_scenario_models_exist(scenarios)
    all_errs += check_notebooks_exist(capsules + scenarios + quickstart)
    all_errs += check_no_orphan_notebooks(
        capsules + scenarios + quickstart
    )
    all_errs += check_readme_matches_changelog(readme_rows, changelog)
    all_errs += check_no_placeholders()

    if all_errs:
        for e in all_errs:
            print(e)
        print(f"\n{len(all_errs)} crosslink failure(s).")
        return 1
    print(
        f"Crosslinks OK — {len(capsules)} capsule(s), "
        f"{len(scenarios)} scenario(s), "
        f"{len(changelog)} CHANGELOG row(s), "
        f"{len(readme_rows)} README row(s)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
