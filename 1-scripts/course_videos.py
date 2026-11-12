#!/usr/bin/env python3
"""Generate course intro/outro videos using the existing Foundry LTX Pro deployment.

Usage (from the repo root, with the existing Azure sign-in):
  python 1-scripts/course_videos.py "2026-11-12 180846-mai-image-2_6-flash.png" --dry-run
  python 1-scripts/course_videos.py "2026-11-12 180846-mai-image-2_6-flash.png"

Reads .env without changing it. Live mode makes two billable image-to-video calls
unless identical results are already saved. fal processes the image outside Microsoft.
Saves a widescreen input, MP4s, and request records in
4-models/fal-ltx-2.5-pro/output/. Requires the existing requirements-dev.txt packages.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
from urllib.parse import urlparse

from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
from PIL import Image, ImageOps

from fal_video import SCOPE, FalVideo, as_url, scoreboard

ROOT = Path(__file__).resolve().parent.parent
CAPSULE = ROOT / "4-models" / "fal-ltx-2.5-pro"

STYLE = """Animate the supplied illustrated course banner, not a new scene.
Preserve all original wording exactly: "MAI MODELS \u00b7 MULTIMODAL PRODUCT LAUNCH",
"One tent, one launch", "What can MAI models do for a real product launch?",
and "MICROSOFT AI SAMPLES". Preserve the compass letters N, E, S, W.
Keep the original serif title, italic subtitle, monospace labels, and logos
stationary, crisp, and readable. Do not redraw letters or introduce new text.
Keep the parchment paper texture, cream #FEF9ED, walnut #5D524B, deep teal
#2E4D4D, and apricot #FBD3BE colors. Retain the flat editorial illustration:
mountains, river, trees, compass, tent, and tiny campfire. No photorealism,
neon, new objects, cuts, camera movement, zoom, cropping, or flashing.
Animate only the scenery; the compass, border, and lettering stay fixed."""

INTRO = STYLE + """
Create an inviting 8-second opening for a hands-on AI course.
Seconds 0-2: begin with the complete banner visible; warm apricot morning light
gently brightens the mountain landscape, without changing text contrast.
Seconds 2-5: add subtle river shimmer, a tiny campfire flicker, and a slow drift
of mist between the distant mountain layers. Keep all motion restrained.
Seconds 5-8: gradually settle the scenery and hold the complete banner readable,
ready to cut into the first lesson. Do not fade the title away.
Audio: original upbeat instrumental music at approximately 112 BPM, warm
electric-piano chords, a light plucked acoustic melody, soft rounded bass,
and gentle brushed percussion. Optimistic, curious, outdoorsy, and welcoming.
Begin with a short melodic hook and finish with a clean musical resolution.
No speech, singing, vocal samples, dramatic impacts, or recognizable songs."""

OUTRO = STYLE + """
Create a satisfying 8-second closing for the same hands-on AI course.
Seconds 0-3: show the complete banner with subtle river shimmer and a tiny
campfire flicker; warm apricot evening light settles over the mountains.
Seconds 3-5: gently bring all background motion to rest.
Seconds 5-7: hold the complete banner perfectly still and readable.
Seconds 7-8: fade the whole composition smoothly into parchment cream #FEF9ED,
ending on a clean cream frame, not black.
Audio: original upbeat instrumental closing music at approximately 112 BPM,
warm electric-piano chords, a light plucked acoustic melody, soft rounded bass,
and gentle brushed percussion. Convey accomplishment and encouragement.
Taper the percussion and resolve into a warm final chord whose decay ends
with the visual fade. No speech, singing, vocal samples, or recognizable songs."""


def prepare_banner(source: Path, destination: Path) -> None:
    """Fit the entire banner into 16:9 without cropping or stretching its text."""
    with Image.open(source) as image:
        artwork = ImageOps.contain(
            ImageOps.exif_transpose(image).convert("RGBA"),
            (1920, 1080),
            Image.Resampling.LANCZOS,
        )
        canvas = Image.new("RGB", (1920, 1080), "#FEF9ED")
        offset = ((1920 - artwork.width) // 2, (1080 - artwork.height) // 2)
        canvas.paste(artwork, offset, artwork)
        canvas.save(destination)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("image", type=Path, help="course banner image")
    parser.add_argument("--dry-run", action="store_true", help="prepare the image and print prompts; no API calls")
    args = parser.parse_args()
    if not args.image.is_file():
        parser.error(f"Image not found: {args.image}")

    load_dotenv(ROOT / ".env")
    required = ("MICROSOFT_FOUNDRY_ENDPOINT", "AZURE_FAL_LTX_25_PRO_DEPLOYMENT")
    missing = [key for key in required if not os.getenv(key, "").strip()]
    if missing:
        parser.error(f"Missing settings in .env or environment: {', '.join(missing)}")
    endpoint = os.environ[required[0]].strip()
    deployment = os.environ[required[1]].strip()
    parsed = urlparse(endpoint)
    if parsed.scheme != "https" or not parsed.hostname:
        parser.error("MICROSOFT_FOUNDRY_ENDPOINT must be an HTTPS URL.")
    rpm = int(os.getenv("FAL_REQUESTS_PER_MINUTE", "2"))
    if rpm < 1:
        parser.error("FAL_REQUESTS_PER_MINUTE must be a positive integer.")

    output = CAPSULE / "output"
    output.mkdir(parents=True, exist_ok=True)
    banner = output / "course-banner-16x9.png"
    prepare_banner(args.image, banner)
    print(f"Prepared widescreen banner: {banner}")
    print("Model: Fal-LTX-2.5-Pro | image-to-video | 8 seconds | 1080p | audio on")

    if args.dry_run:
        for name, prompt in (("course-intro", INTRO), ("course-outro", OUTRO)):
            print(f"\n{name}:\n{prompt}")
        print("\nDry run complete. No credentials requested or API calls made.")
        return

    print("Live mode: two billable generations; fal processes the image outside Microsoft.", flush=True)
    image_url = as_url(banner, max_side=None)
    with DefaultAzureCredential() as credential:
        credential.get_token(SCOPE)
        fal = FalVideo(
            endpoint, deployment, family="lightricks/ltx-2.5", here=CAPSULE,
            mode="live", requests_per_minute=rpm, play_inline=False, credential=credential,
        )
        clips = []
        for name, prompt in (("course-intro", INTRO), ("course-outro", OUTRO)):
            clip = fal.run(
                name, "image-to-video/pro", image_url=image_url, prompt=prompt,
                camera_motion="static", duration=8, resolution="1080p",
                aspect_ratio="16:9", fps=25, generate_audio=True,
            )
            print(f"Downloaded: {clip.path}", flush=True)
            if not clip.info.get("has_audio"):
                raise RuntimeError(f"{clip.path.name} has no audio stream despite generate_audio=True.")
            if (clip.info.get("width"), clip.info.get("height")) != (1920, 1080):
                raise RuntimeError(f"{clip.path.name} is not the requested 1920x1080: {clip.info}")
            seconds = clip.info.get("seconds")
            if seconds is None or abs(seconds - 8) > 0.5:
                raise RuntimeError(f"{clip.path.name} is not approximately 8 seconds: {seconds}")
            clips.append(clip)
        scoreboard(clips)
    print("\nBoth videos downloaded. Review lettering and music before publishing.")


if __name__ == "__main__":
    main()
