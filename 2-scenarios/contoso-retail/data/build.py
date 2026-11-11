"""Build the contoso-retail dataset from Azure-Samples/contoso-web.

Clones the pinned upstream commit, removes LLM-generation leftovers from the manuals,
converts product images to 800px WebP, writes products.json, and checks that every
manual agrees with products.json on name, price, brand and category.

  python 2-scenarios/contoso-retail/data/build.py                          # clone upstream and rebuild
  python 2-scenarios/contoso-retail/data/build.py --source ../contoso-web  # use an existing checkout
  python 2-scenarios/contoso-retail/data/build.py --check                  # only validate the committed data
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

UPSTREAM = "https://github.com/Azure-Samples/contoso-web.git"
COMMIT = "e13b0d346bdc0f2139552df6b9268cbe71b5b644"
HERE = Path(__file__).resolve().parent
IMAGE_SIZE = 800
IMAGE_QUALITY = 80

# Chat-style preambles the upstream generator left in the manuals, e.g. "Certainly! Here's a sample warranty ..."
LEFTOVER = re.compile(r"^\s*(Certainly!|Sure!|Of course!|Here is a |Here's a )", re.IGNORECASE)


def clone(target: Path) -> None:
    subprocess.run(["git", "clone", "-q", "--filter=blob:none", UPSTREAM, str(target)], check=True)
    subprocess.run(["git", "-C", str(target), "checkout", "-q", COMMIT], check=True)


def clean_manual(text: str) -> tuple[str, int]:
    lines = text.splitlines()
    kept = [line.rstrip() for line in lines if not LEFTOVER.match(line)]
    return "\n".join(kept).strip() + "\n", len(lines) - len(kept)


def build(public: Path) -> None:
    from PIL import Image

    for name in ("manuals", "images", "people"):
        shutil.rmtree(HERE / name, ignore_errors=True)
        (HERE / name).mkdir()

    upstream = json.loads((public / "products.json").read_text(encoding="utf-8"))
    products, removed, image_count = [], 0, 0
    for p in sorted(upstream, key=lambda x: x["id"]):
        slug = p["slug"]
        # products.json is authoritative for the manual path; upstream categories.json points every product at product_info_8.md.
        text, n = clean_manual((public / p["manual"].lstrip("/")).read_text(encoding="utf-8"))
        removed += n
        (HERE / "manuals" / f"{slug}.md").write_text(text, encoding="utf-8")

        images = []
        (HERE / "images" / slug).mkdir()
        for i, rel in enumerate(p["images"], start=1):
            out = f"images/{slug}/{i:02d}.webp"
            with Image.open(public / rel.lstrip("/")) as im:
                im.convert("RGB").resize((IMAGE_SIZE, IMAGE_SIZE), Image.LANCZOS).save(
                    HERE / out, "WEBP", quality=IMAGE_QUALITY, method=6
                )
            images.append(out)
            image_count += 1

        products.append(
            {
                "id": p["id"],
                "slug": slug,
                "name": p["name"],
                "price": p["price"],
                "category": p["category"],
                "brand": p["brand"],
                "description": p["description"].strip(),
                "manual": f"manuals/{slug}.md",
                "images": images,
            }
        )

    with Image.open(public / "people" / "sarahlee.jpg") as im:
        im.convert("RGB").save(HERE / "people" / "sarah-lee.webp", "WEBP", quality=85, method=6)

    (HERE / "products.json").write_text(json.dumps(products, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Built {len(products)} products, {image_count} images, removed {removed} leftover manual lines.")


def check() -> int:
    products = json.loads((HERE / "products.json").read_text(encoding="utf-8"))
    problems = []
    for p in products:
        manual_path = HERE / p["manual"]
        if not manual_path.exists():
            problems.append(f"{p['slug']}: missing {p['manual']}")
            continue
        manual = manual_path.read_text(encoding="utf-8")
        header = manual.splitlines()[1] if len(manual.splitlines()) > 1 else ""
        if not header.startswith(f"{p['name']}, price ${p['price']:g}"):
            problems.append(f"{p['slug']}: manual header {header!r} doesn't match name/price")
        for field in ("brand", "category"):
            match = re.search(rf"^## {field}\s*\n+(.+)$", manual, re.IGNORECASE | re.MULTILINE)
            if not match or match.group(1).strip() != p[field]:
                problems.append(f"{p['slug']}: manual {field} doesn't match {p[field]!r}")
        if LEFTOVER.search(manual) or any(LEFTOVER.match(line) for line in manual.splitlines()):
            problems.append(f"{p['slug']}: manual still has LLM leftovers")
        problems += [f"{p['slug']}: missing {img}" for img in p["images"] if not (HERE / img).exists()]

    for line in problems:
        print(f"FAIL {line}")
    print(f"{'OK' if not problems else 'FAIL'} Checked {len(products)} products: {len(problems)} problem(s).")
    return 1 if problems else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--source", type=Path, help="existing contoso-web checkout at the pinned commit (skips the clone)")
    parser.add_argument("--check", action="store_true", help="only validate the committed data")
    args = parser.parse_args()

    if not args.check:
        with tempfile.TemporaryDirectory() as tmp:
            source = args.source.resolve() if args.source else Path(tmp) / "contoso-web"
            if not args.source:
                clone(source)
            build(source / "public")
    return check()


if __name__ == "__main__":
    sys.exit(main())
