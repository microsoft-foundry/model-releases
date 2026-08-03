#!/usr/bin/env python3
"""validate-specs.py — walk the repo and check every artifact's YAML frontmatter
against its JSON Schema in .github/specs/schemas/.

Usage:
    python scripts/validate-specs.py            # validate everything
    python scripts/validate-specs.py <path>...  # validate specific files

Exit code:
    0 = all valid
    1 = one or more failures (details printed)

Grounding: JSON Schema draft 2020-12 (https://json-schema.org/).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

try:
    import yaml
    from jsonschema import Draft202012Validator
except ImportError:
    sys.stderr.write(
        "Missing deps. Install with: pip install pyyaml jsonschema\n"
    )
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = REPO_ROOT / ".github" / "specs" / "schemas"

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)

# Glob → kind mapping. First-match wins.
KIND_GLOBS = [
    ("models/*/*/*/README.md", "capsule"),
    ("models/quickstart/README.md", "quickstart"),
    ("models/*/README.md", "family"),
    ("docs/primers/*.md", "primer"),
    (".github/skills/*/SKILL.md", "skill"),
    (".github/agents/*.md", "agent"),
    ("scripts/*.spec.md", "script"),
]


def load_schema(kind: str) -> dict:
    schema_path = SCHEMA_DIR / f"{kind}.schema.json"
    if not schema_path.exists():
        raise FileNotFoundError(f"No schema for kind={kind}: {schema_path}")
    return json.loads(schema_path.read_text())


def read_frontmatter(path: Path) -> dict | None:
    text = path.read_text()
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None
    return yaml.safe_load(m.group(1)) or {}


def kind_for(path: Path) -> str | None:
    rel = path.relative_to(REPO_ROOT).as_posix()
    for glob, kind in KIND_GLOBS:
        # crude glob → regex
        pat = re.escape(glob).replace(r"\*", "[^/]*")
        if re.fullmatch(pat, rel):
            return kind
    return None


def collect_targets(explicit: list[str]) -> list[Path]:
    if explicit:
        return [Path(p).resolve() for p in explicit]
    files: list[Path] = []
    for glob, _ in KIND_GLOBS:
        files.extend(REPO_ROOT.glob(glob))
    return sorted(set(files))


def main() -> int:
    targets = collect_targets(sys.argv[1:])
    if not targets:
        print("No spec-bearing files found.")
        return 0

    schemas: dict[str, Draft202012Validator] = {}
    failures = 0
    checked = 0

    for path in targets:
        kind = kind_for(path)
        if not kind:
            continue
        checked += 1
        fm = read_frontmatter(path)
        if fm is None:
            print(f"✗ {path.relative_to(REPO_ROOT)} — missing YAML frontmatter")
            failures += 1
            continue
        if fm.get("kind") != kind:
            print(
                f"✗ {path.relative_to(REPO_ROOT)} — kind mismatch: "
                f"expected {kind}, got {fm.get('kind')!r}"
            )
            failures += 1
            continue
        if kind not in schemas:
            schemas[kind] = Draft202012Validator(load_schema(kind))
        errors = sorted(schemas[kind].iter_errors(fm), key=lambda e: e.path)
        if errors:
            failures += 1
            print(f"✗ {path.relative_to(REPO_ROOT)}")
            for err in errors:
                loc = ".".join(str(p) for p in err.path) or "<root>"
                print(f"    {loc}: {err.message}")
        else:
            print(f"✓ {path.relative_to(REPO_ROOT)} [{kind}]")

    print(f"\n{checked - failures}/{checked} artifacts valid.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
