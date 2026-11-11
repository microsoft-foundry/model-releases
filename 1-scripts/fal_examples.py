#!/usr/bin/env python3
"""Turn a fal capsule's output/ into small, committable replay clips in examples/.

Each MP4 is re-encoded to a short side of 480 px (H.264 + AAC, web-ready). The JSON record and
frame strip are copied alongside. The record keeps the original "probe" and gains a "preview" probe.

Usage:
  python 1-scripts/fal_examples.py                          # every 4-models/fal-*/ and 5-multi-model/fal-*/ capsule
  python 1-scripts/fal_examples.py 4-models/fal-kling-v3-pro --dry-run
  python 1-scripts/fal_examples.py --height 360 --crf 30 --force
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "1-scripts"))
from fal_video import _ffmpeg, frame_strip, probe  # noqa: E402


def shrink(src: Path, dst: Path, height: int, crf: int) -> None:
    info = probe(src)
    short = min(info.get("width", height), info.get("height", height))
    side = min(height, short)
    # Scale the short side so portrait, square, and landscape clips all land at the same quality.
    scale = f"scale='if(lt(iw,ih),{side},-2)':'if(lt(iw,ih),-2,{side})'"
    cmd = [_ffmpeg(), "-hide_banner", "-loglevel", "error", "-y", "-i", str(src), "-vf", scale,
           "-c:v", "libx264", "-preset", "slow", "-crf", str(crf), "-pix_fmt", "yuv420p", "-movflags", "+faststart"]
    cmd += ["-c:a", "aac", "-b:a", "96k"] if info.get("has_audio") else ["-an"]
    subprocess.run([*cmd, str(dst)], check=True)


def export(capsule: Path, height: int, crf: int, force: bool, dry_run: bool) -> tuple[float, float]:
    out, ex = capsule / "output", capsule / "examples"
    clips = sorted(out.glob("*.mp4")) if out.is_dir() else []
    if not clips:
        print(f"{capsule.name}: no clips in output/")
        return 0.0, 0.0
    print(f"{capsule.name}:")
    before = after = 0.0
    for src in clips:
        dst = ex / src.name
        size_in = src.stat().st_size / 1e6
        if dst.exists() and dst.stat().st_mtime >= src.stat().st_mtime and not force:
            print(f"   {src.stem:36} up to date ({dst.stat().st_size / 1e6:.1f} MB)")
            before, after = before + size_in, after + dst.stat().st_size / 1e6
            continue
        if dry_run:
            print(f"   {src.stem:36} {size_in:6.1f} MB -> would shrink")
            before += size_in
            continue
        ex.mkdir(exist_ok=True)
        shrink(src, dst, height, crf)
        size_out = dst.stat().st_size / 1e6

        record_src = src.with_suffix(".json")
        record = json.loads(record_src.read_text()) if record_src.exists() else {}
        record.setdefault("probe", probe(src))
        record["preview"] = probe(dst)
        dst.with_suffix(".json").write_text(json.dumps(record, indent=2) + "\n")
        frame_strip(dst)

        print(f"   {src.stem:36} {size_in:6.1f} MB -> {size_out:5.1f} MB")
        before, after = before + size_in, after + size_out
    return before, after


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("capsules", nargs="*", type=Path, help="capsule folders (default: 4-models/fal-* and 5-multi-model/fal-*)")
    parser.add_argument("--height", type=int, default=480, help="short side in pixels (default 480)")
    parser.add_argument("--crf", type=int, default=28, help="H.264 quality, higher is smaller (default 28)")
    parser.add_argument("--force", action="store_true", help="redo clips that are already up to date")
    parser.add_argument("--dry-run", action="store_true", help="list what would change, write nothing")
    args = parser.parse_args()

    capsules = [c.resolve() for c in args.capsules] or sorted([*(ROOT / "4-models").glob("fal-*"), *(ROOT / "5-multi-model").glob("fal-*")])
    total_in = total_out = 0.0
    for capsule in capsules:
        size_in, size_out = export(capsule, args.height, args.crf, args.force, args.dry_run)
        total_in, total_out = total_in + size_in, total_out + size_out
    if not args.dry_run:
        print(f"\nTotal: {total_in:.1f} MB in output/ -> {total_out:.1f} MB in examples/")


if __name__ == "__main__":
    main()
