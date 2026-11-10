# Contoso Outdoors — a retail scenario

*"What does a real product catalog look like when every model in a release has to work on it?"*

Contoso Outdoors is a made-up online retailer of camping and hiking gear. It has a
small catalog with product pages, photos, and long-form manuals, and it wants to
modernize how it creates and serves that content: product imagery, spoken product
help, support call transcripts, and grounded answers about specs and warranties.

We use it as a shared workload. Every capsule that uses Contoso Outdoors works on
the same 20 products, so results stay comparable across models and releases.

> This is a shared scenario, not a release capsule. Capsules build on it and link
> back here.

<br/>

## Scope

**In scope today**

- A product catalog: 20 products in 7 categories (Tents, Backpacks, Hiking Clothing,
  Hiking Footwear, Camping Tables, Camping Stoves, Sleeping Bags), 11 brands, priced
  $50–$350.
- One Markdown manual per product: features, technical specs, user guide, care,
  warranty, return policy, and customer reviews.
- 5–6 product photos per product (102 in total).
- One customer persona photo (Sarah Lee).
- 12 generated launch images and a short voiceover for the TrailMaster X4 relaunch
  (see [Generated assets](#generated-assets)).

**Not in scope yet**

- Orders, inventory, stores, or customer accounts.
- Support-call audio and video.
- Agent instructions and a benchmark (as in [contoso-travel](../contoso-travel/)).

We add these when a capsule needs them, as new files under `data/`, and record them
in this README. The catalog itself stays fixed so earlier capsules keep working.

<br/>

## How each capability can use it

| Capability | What Contoso Outdoors does with it | Starts from |
|---|---|---|
| Image generation and editing | New lifestyle shots, seasonal banners, consistent product photos | `images/`, `products.json` |
| Vision | Read a product photo and match it to the catalog | `images/`, `products.json` |
| Speech-to-text | Transcribe customer support calls about a product | `manuals/` (for scripts and ground truth) |
| Text-to-speech | Spoken product summaries and how-to guides | `products.json`, `manuals/` |
| Chat and long context | Grounded answers about specs, warranty, and returns | `manuals/` |

<br/>

## What's in here

```text
2-scenarios/contoso-retail/
├── README.md
└── data/
    ├── products.json            # The catalog, one record per product
    ├── manuals/<slug>.md        # Product manual for each product
    ├── images/<slug>/NN.webp    # Product photos, 01.webp first
    ├── people/sarah-lee.webp    # Customer persona photo
    ├── generated/               # Launch assets made by MAI models (see below)
    └── build.py                 # Rebuilds data/ from upstream, then validates it
```

Each record in [products.json](data/products.json) looks like this. Paths are
relative to `data/`:

```json
{
  "id": 1,
  "slug": "trailmaster-x4-tent",
  "name": "TrailMaster X4 Tent",
  "price": 250.0,
  "category": "Tents",
  "brand": "OutdoorLiving",
  "description": "Unveiling the TrailMaster X4 Tent from OutdoorLiving, ...",
  "manual": "manuals/trailmaster-x4-tent.md",
  "images": ["images/trailmaster-x4-tent/01.webp", "..."]
}
```

To load it from a notebook anywhere in the repo:

```python
import json
from pathlib import Path

ROOT = next(p for p in (Path.cwd(), *Path.cwd().parents) if (p / "2-scenarios").is_dir())
DATA = ROOT / "2-scenarios" / "contoso-retail" / "data"

products = json.loads((DATA / "products.json").read_text(encoding="utf-8"))
tent = next(p for p in products if p["slug"] == "trailmaster-x4-tent")
manual = (DATA / tent["manual"]).read_text(encoding="utf-8")
```

<br/>

## Provenance

| | |
| --- | --- |
| **Source** | [Azure-Samples/contoso-web](https://github.com/Azure-Samples/contoso-web) (archived) |
| **Commit** | [`e13b0d3`](https://github.com/Azure-Samples/contoso-web/tree/e13b0d346bdc0f2139552df6b9268cbe71b5b644) (2024-03-12) |
| **License** | MIT, Copyright (c) Microsoft Corporation |
| **Files used** | `public/products.json`, `public/manuals/product_info_{1..20}.md`, `public/images/{1..20}/*.png`, `public/people/sarahlee.jpg` |
| **Not copied** | The Next.js web app, `brands.json`, `categories.json` (navigation data), hero banners, screenshots |

Every change from upstream is made by [build.py](data/build.py):

| Change | Why |
| --- | --- |
| Images resized from 1024 px PNG to 800 px WebP (quality 80): 312 MB to about 10 MB | Keeps the repo light |
| Files renamed by product slug (`product_info_1.md` to `trailmaster-x4-tent.md`; UUID image names to `01.webp`, ...) | Readable, stable paths |
| 7 chat-style lines removed from 6 manuals (for example *"Certainly! Here's a sample warranty information..."*) | Leftovers from the generator that wrote the manuals |
| Trailing whitespace trimmed in manuals | Clean diffs |
| `sarahlee.jpg` converted to `people/sarah-lee.webp` | Same format as the other images |
| `products.json` fields `manual` and `images` rewritten as relative paths | Paths resolve from `data/` |

Names, prices, brands, categories, descriptions, and all other manual text are
unchanged.

<br/>

## Generated assets

These files were not in the upstream catalog. They were generated for a
TrailMaster X4 relaunch by an earlier MAI multimodal workshop, which will be
published at [aka.ms/mai-samples](https://aka.ms/mai-samples). We reuse them as
starting frames, end frames, and references for video generation. They are
synthetic: logos, labels, and on-screen text may not match the catalog exactly.

| File | What it shows | Good for |
| --- | --- | --- |
| `generated/images/campsite-before.webp` | Lakeside campsite at midday with the tent, 1536×1024 | First frame |
| `generated/images/campsite-after.webp` | The same scene after three edits, including a new tent color, 1248×832 | Last frame (pairs with `campsite-before`) |
| `generated/images/prop-tent.webp` | TrailMaster X4 tent on white, 1024×1024 | Reference image |
| `generated/images/prop-backpack.webp` | Adventurer Pro backpack on white, 1024×1024 | Reference image |
| `generated/images/prop-stove.webp` | EcoFire camping stove on white, 1024×1024 | Reference image |
| `generated/images/prop-sleeping-bag.webp` | CozyNights sleeping bag on white, 1024×1024 | Reference image |
| `generated/images/prop-hiker.webp` | A hiker on white, 1024×1024 | Character reference |
| `generated/images/lifestyle-all-products.webp` | One lifestyle photo with all five props, 1024×1024 | First frame |
| `generated/images/setup-guide.webp` | Flat-vector tent setup infographic, 1536×1024 | How-to animation; compare with the manual |
| `generated/images/phone-story.webp` | Tent under the Milky Way, vertical 900×1600 | 9:16 first frame |
| `generated/images/launch-poster.webp` | "HOME, ANYWHERE." poster with a $250 price badge, 1024×1536 | Does on-screen text survive animation? |
| `generated/images/four-seasons.webp` | 2×2 grid of the tent in four seasons, 1536×1536 | Multi-shot storyboard |

All images were made with MAI-Image-2.6 (the five `prop-` images with
MAI-Image-2.6-Flash) and are copied unchanged as WebP.

<br/>

## Known quirks (kept on purpose)

The manuals were machine-generated, so they're imperfect the way real product
documentation often is. We keep these quirks because they make good test cases for
grounding:

| Quirk | Example |
| --- | --- |
| A manual contradicts itself | `trailmaster-x4-tent.md` says *"Water-resistant construction to withstand light rain"* and, a few lines later, *"Waterproof: Yes"* |
| Reviews make stronger claims than the specs | A TrailMaster X4 review says the tent kept them dry in *heavy* rain |
| Contact details look real but aren't | Phone numbers, emails, and websites in the warranty sections are made up |

When sources disagree, the safe answer is the weaker claim.

<br/>

## Rebuild or check it

```bash
python 2-scenarios/contoso-retail/data/build.py --check   # validate the committed data
python 2-scenarios/contoso-retail/data/build.py           # rebuild from the pinned upstream commit (needs Pillow)
```

`--check` confirms that every manual matches `products.json` on name, price, brand,
and category, that no chat-style leftovers remain, and that every image exists.

Contoso Outdoors and its products, people, and reviews are fictitious. Any
resemblance to real companies or products is coincidental.
