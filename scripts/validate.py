#!/usr/bin/env python3
"""Run every repo check from one place.

CI no longer validates on each push, so this is the check authors run
before committing. It wraps the three validators that used to be three
separate CI steps:

    1. validate-specs.py        — frontmatter vs. JSON Schema
    2. validate-crosslinks.py   — CHANGELOG / README / capsule wiring
    3. generate-catalog.py      — generated files are current

Usage:

    python scripts/validate.py            # run once, report, exit non-zero on failure
    python scripts/validate.py --watch    # re-run on every save (Ctrl-C to stop)
    python scripts/validate.py --fix      # regenerate catalog files, then re-check
    python scripts/validate.py --no-color # plain output (used by CI)

`--watch` is the interactive session: leave it running in a second
terminal while you edit, and every save re-runs the full set. It polls
mtimes rather than depending on a file-watcher package, so it works
from a bare checkout with no extra installs.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# (label, argv). Order matters: schema errors make the later checks
# noisy, so they run first and their failure is reported first.
CHECKS: list[tuple[str, list[str]]] = [
    ("Schemas", ["scripts/validate-specs.py"]),
    ("Crosslinks", ["scripts/validate-crosslinks.py"]),
    ("Generated files", ["scripts/generate-catalog.py", "--check"]),
]

# Directories whose contents feed a check. Anything else (notebooks,
# .git, caches) can't change a result, so watching it would only cause
# re-runs that report the same thing.
WATCH_DIRS = ["models", "docs", ".github/specs", "scripts"]
WATCH_FILES = ["CHANGELOG.md", "README.md", "CAPSULE-TOC.md", "catalog.json"]
WATCH_SUFFIXES = {".md", ".py", ".json"}


class Style:
    def __init__(self, enabled: bool) -> None:
        self.enabled = enabled

    def _wrap(self, code: str, text: str) -> str:
        return f"\033[{code}m{text}\033[0m" if self.enabled else text

    def ok(self, t: str) -> str:
        return self._wrap("32", t)

    def bad(self, t: str) -> str:
        return self._wrap("31", t)

    def dim(self, t: str) -> str:
        return self._wrap("2", t)

    def bold(self, t: str) -> str:
        return self._wrap("1", t)


def run_checks(style: Style, quiet_when_green: bool = False) -> int:
    """Run every check. Returns the number that failed."""
    failed: list[str] = []
    for label, argv in CHECKS:
        proc = subprocess.run(
            [sys.executable, *argv],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        out = (proc.stdout + proc.stderr).strip()
        if proc.returncode == 0:
            mark = style.ok("PASS")
            # A green run's detail is noise in watch mode; the summary
            # line from each validator is enough.
            tail = out.splitlines()[-1] if out else ""
            print(f"  {mark}  {style.bold(label)}  {style.dim(tail)}")
        else:
            failed.append(label)
            print(f"  {style.bad('FAIL')}  {style.bold(label)}")
            for line in out.splitlines():
                print(f"        {line}")
    print()
    if failed:
        print(
            style.bad(
                f"{len(failed)} check(s) failed: {', '.join(failed)}"
            )
        )
        if "Generated files" in failed:
            print(
                style.dim(
                    "  Generated files are rebuilt, not edited by hand — "
                    "run `python scripts/validate.py --fix`."
                )
            )
    else:
        print(style.ok("All checks passed."))
    return len(failed)


def snapshot() -> dict[str, float]:
    """Map watched path → mtime, for change detection."""
    state: dict[str, float] = {}
    for rel in WATCH_FILES:
        p = REPO_ROOT / rel
        if p.exists():
            state[str(p)] = p.stat().st_mtime
    for rel in WATCH_DIRS:
        base = REPO_ROOT / rel
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if p.suffix not in WATCH_SUFFIXES or not p.is_file():
                continue
            if "__pycache__" in p.parts:
                continue
            try:
                state[str(p)] = p.stat().st_mtime
            except OSError:
                # File vanished mid-walk (editor swap file); the next
                # poll picks up whatever replaced it.
                continue
    return state


def watch(style: Style) -> int:
    print(
        style.dim(
            "Watching models/, docs/, .github/specs/, scripts/ and the "
            "generated files. Ctrl-C to stop.\n"
        )
    )
    prev = snapshot()
    print(style.bold("Initial run"))
    run_checks(style)
    try:
        while True:
            time.sleep(1.0)
            cur = snapshot()
            if cur == prev:
                continue
            changed = sorted(
                {
                    Path(p).relative_to(REPO_ROOT).as_posix()
                    for p in set(cur) ^ set(prev)
                }
                | {
                    Path(p).relative_to(REPO_ROOT).as_posix()
                    for p in set(cur) & set(prev)
                    if cur[p] != prev[p]
                }
            )
            prev = cur
            print()
            print(style.bold(f"Changed: {', '.join(changed[:5])}"))
            if len(changed) > 5:
                print(style.dim(f"  …and {len(changed) - 5} more"))
            run_checks(style)
    except KeyboardInterrupt:
        print("\nStopped.")
        return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Run every repo check from one place."
    )
    ap.add_argument(
        "--watch",
        action="store_true",
        help="re-run on every save until Ctrl-C",
    )
    ap.add_argument(
        "--fix",
        action="store_true",
        help="regenerate catalog files before checking",
    )
    ap.add_argument(
        "--no-color", action="store_true", help="plain output"
    )
    args = ap.parse_args()

    style = Style(enabled=not args.no_color and sys.stdout.isatty())

    if args.fix:
        print(style.bold("Regenerating catalog files"))
        proc = subprocess.run(
            [sys.executable, "scripts/generate-catalog.py"], cwd=REPO_ROOT
        )
        if proc.returncode != 0:
            return proc.returncode
        print()

    if args.watch:
        return watch(style)

    return 1 if run_checks(style) else 0


if __name__ == "__main__":
    raise SystemExit(main())
