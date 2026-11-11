#!/usr/bin/env python3
"""Turn a MAI image capsule's output/ into small, committable replay pictures in examples/.

Each PNG becomes a WebP (longest side 1024 px by default) and its run-log entry is copied to examples/run_log.json.
Entries that point at a shared scenario image (a "file" key) are left alone unless --replace-shared is set,
so the Contoso Outdoors images the fal capsules animate stay the single source.

Usage:
  python 1-scripts/mai_examples.py                     # every 4-models/mai-image-2.6*/ and 5-multi-model/mai-image-*/
  python 1-scripts/mai_examples.py 4-models/mai-image-2.6 --dry-run
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent


def export(capsule: Path, side: int, quality: int, replace_shared: bool, dry_run: bool) -> tuple[float, float]:
    out, ex = capsule / "output", capsule / "examples"
    mine = json.loads((out / "run_log.json").read_text()) if (out / "run_log.json").exists() else {}
    ours = json.loads((ex / "run_log.json").read_text()) if (ex / "run_log.json").exists() else {}
    pictures = [p for p in sorted(out.glob("*.png")) if p.stem in mine]
    print(f"{capsule.name}: {len(pictures)} pictures in output/")
    before = after = 0.0
    for src in pictures:
        if "file" in ours.get(src.stem, {}) and not replace_shared:
            print(f"   {src.stem:44} kept: points at {ours[src.stem]['file'].split('/')[-1]}")
            continue
        size_in = src.stat().st_size / 1e6
        before += size_in
        if dry_run:
            print(f"   {src.stem:44} {size_in:5.1f} MB -> would convert")
            continue
        ex.mkdir(exist_ok=True)
        dst = ex / f"{src.stem}.webp"
        with Image.open(src) as picture:
            picture = picture.convert("RGB")
            picture.thumbnail((side, side))
            picture.save(dst, "WEBP", quality=quality)
        ours[src.stem] = mine[src.stem]
        after += dst.stat().st_size / 1e6
        print(f"   {src.stem:44} {size_in:5.1f} MB -> {dst.stat().st_size / 1e6:4.2f} MB")
    if not dry_run and pictures:
        (ex / "run_log.json").write_text(json.dumps(ours, indent=2, ensure_ascii=False) + "\n")
    return before, after


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("capsules", nargs="*", type=Path, help="capsule folders (default: all MAI image capsules)")
    parser.add_argument("--side", type=int, default=1024, help="longest side in pixels (default 1024)")
    parser.add_argument("--quality", type=int, default=80, help="WebP quality (default 80)")
    parser.add_argument("--replace-shared", action="store_true", help="also replace entries that point at scenario images")
    parser.add_argument("--dry-run", action="store_true", help="list what would change, write nothing")
    args = parser.parse_args()

    capsules = [c.resolve() for c in args.capsules] or sorted(
        [*(ROOT / "4-models").glob("mai-image-2.6*"), *(ROOT / "5-multi-model").glob("mai-image-*")])
    total_in = total_out = 0.0
    for capsule in capsules:
        size_in, size_out = export(capsule, args.side, args.quality, args.replace_shared, args.dry_run)
        total_in, total_out = total_in + size_in, total_out + size_out
    if not args.dry_run:
        print(f"\nTotal: {total_in:.1f} MB in output/ -> {total_out:.1f} MB in examples/")


if __name__ == "__main__":
    main()
