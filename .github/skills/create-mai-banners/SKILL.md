---
name: create-mai-banners
description: Write copy-ready image-model prompts for MAI-themed course banners, headers, covers, and thumbnails. Takes a banner shape, pixel resolution, and scene description, then applies a warm Microsoft AI-inspired palette, editorial typography, and restrained illustration style. Use for MAI banner prompts or Microsoft AI-inspired banner art direction; does not generate images or call a model.
---

# create-mai-banners

## 1. Gather the banner brief

Use the details already supplied. Ask only for missing required inputs:

- **Shape:** landscape, portrait, square, or a specific aspect ratio or custom silhouette.
- **Resolution:** width x height in pixels, both positive integers.
- **Description:** the subject, scene, or concept we want shown.

Optional inputs:

- Exact title, subtitle, eyebrow label, and footer wording.
- Intended use, such as a course opening, notebook header, or social thumbnail.
- Text placement, an attached reference image, or a preference for a light or dark background.

Do not invent course names, slogans, labels, logos, or Microsoft endorsement.
When no wording is provided, request an illustration-only banner with no text.
Use only user-provided or permitted reference images; never read `.do-not-commit/`.

Check that the shape and dimensions agree. For example, 1920 x 1080 is 16:9
landscape, 1080 x 1920 is 9:16 portrait, and 1080 x 1080 is square.
If an explicit ratio conflicts with the resolution, ask which to preserve.
For a custom silhouette, specify the canvas dimensions and the silhouette's
safe content area separately. Do not silently crop or stretch the composition.

## 2. Apply the shared art direction

This is a **Microsoft AI-inspired treatment**, not an official brand specification.
The palette and font identification come from a
[third-party analysis of microsoft.ai](https://styles.refero.design/style/46781641-8afd-4b01-9f67-06046b6eda71).
Do not describe them as verified current guidelines for every Microsoft AI page.

### Palette

- **Parchment `#FEF9ED`:** default canvas and light lettering on dark backgrounds.
- **Bone `#F5F0E4`:** secondary surfaces and subtle tonal layering.
- **Walnut `#5D524B`:** primary text and warm outlines.
- **Cedar `#72675B`:** secondary text, with sufficient contrast at the chosen size.
- **Linen `#CEC7BC`:** delicate borders and decorative contour lines, not small text.
- **Deep teal / Library Ink `#2E4D4D`:** illustration anchors or the optional dark canvas.
- **Apricot `#FBD3BE`:** restrained warm illumination or atmospheric wash.
- **Faded rose `#8C5462`:** occasional accent, used sparingly.
- **Slate lilac `#666583`:** optional secondary accent, not required in every banner.

Use parchment, walnut, and teal as the core palette, with one or two quiet
accents. Do not force all nine colors into one image. For a dark treatment,
use deep teal with parchment text; do not retain dark walnut text on teal.
Avoid saturated primary colors, neon, and rainbow gradients.

### Typography

- **Headlines:** Bradford LL-inspired transitional serif, warm proportions,
  regular weight, large editorial scale, and slightly tight tracking.
- **Subtitles:** a compatible italic serif for gentle emphasis.
- **Labels:** Red Hat Mono-inspired monospace, small but readable, with modest
  tracking. Do not change the supplied capitalization or punctuation.
- Use size, spacing, and italic emphasis rather than heavy bold or 3D lettering.
- Font names describe the intended appearance; an image model cannot guarantee
  an exact typeface. For exact typography, generate text-free artwork and
  overlay text using a licensed font. Source Serif 4 or Lora can provide a
  similar serif direction when Bradford LL is unavailable.

### Illustration and layout

- Warm, human-centered editorial illustration; calm, curious, and approachable.
- Flat layered shapes, fine linework, subtle paper grain, and soft tonal depth.
- Spacious composition with a clear focal point and generous negative space.
- Optional thin framing rules and small geometric accents, never visual clutter.
- No heavy drop shadows, glossy plastic, metallic 3D text, or generic sci-fi UI.
- Depict the requested subject. Do not add tents, mountains, compasses, robots,
  or circuitry unless the brief calls for them.

For landscape banners, usually place text in one quiet region and artwork in
the other. For portrait banners, stack the title and scene with breathing room.
For squares, balance one focal illustration with a readable text region.
Keep text and essential subjects at least 8% inside the canvas edges and inside
any custom silhouette. Treat that margin as a layout instruction, not a
guarantee of measured model output.

## 3. Return a ready-to-use prompt

Return these three items, with all placeholders replaced:

1. **Image settings:** requested width, height, shape, and reduced aspect ratio.
   If a target model is named, map these only to verified supported controls.
   Explain unsupported sizes and ask before substituting a different size.
   Otherwise keep the settings model-neutral; do not promise exact dimensions
   merely because they appear in the prompt.
2. **Prompt:** one copy-ready block combining the scene, composition, palette,
   typography if needed, exact supplied wording, texture, and exclusions.
3. **Avoid:** a short negative-prompt block. If the model has no negative-prompt
   field, append these exclusions to the main prompt instead.

Do not call an image model, deploy resources, read credentials, or create image
files unless separately requested. Follow [check-content](../check-content/SKILL.md)
when editing repository content.

### Prompt recipe

```text
Create a [shape] banner for [use], composed for [width] x [height] pixels
([ratio]). Show [specific requested scene and subjects].

Composition: [shape-aware arrangement, focal point, and negative space].
Keep essential subjects and all text inside an 8% safe margin.

Art direction: warm editorial illustration inspired by Microsoft AI's website,
with flat layered shapes, delicate linework, subtle parchment grain, and calm,
human-centered storytelling. Use [selected palette with hex codes and roles].
Add only restrained apricot warmth; maintain clear subject/background contrast.

[If text is supplied: reproduce each exact string and specify its placement.
Use a Bradford LL-inspired regular serif headline, an italic serif subtitle
if supplied, and Red Hat Mono-inspired small labels if supplied.]
[Otherwise: no text, letters, numbers, logos, signatures, or watermarks.]

Avoid [brief-specific exclusions plus the shared exclusions].
```

### Worked example

**Brief:** landscape, 1920 x 1080, a course banner showing a tent beside a river
in the mountains. Title: "One tent, one launch". No other wording.

**Settings:** 1920 x 1080 pixels, landscape, 16:9.

**Prompt:**

```text
Create a landscape course banner composed for 1920 x 1080 pixels, 16:9.
Show a small apricot tent beside a winding river, with layered mountain
silhouettes and a few pine trees. Use flat editorial illustration, fine
linework, subtle paper grain, and gentle tonal depth, not photorealism.

Reserve the left 45% as quiet parchment negative space for the exact title
"One tent, one launch". Place the tent and strongest mountain silhouette
on the right, with the river leading toward them across the lower third.
Keep the title and essential subjects at least 8% inside all edges.

Use parchment #FEF9ED as the canvas, bone #F5F0E4 for distant layers,
deep teal #2E4D4D for foreground mountains and trees, walnut #5D524B
for the title, and apricot #FBD3BE for the tent and soft morning warmth.
Set the title in a large Bradford LL-inspired regular transitional serif
with slightly tight tracking. Add no subtitle, labels, logos, or other text.
The mood is spacious, welcoming, curious, and quietly optimistic.
```

**Avoid:**

```text
Neon colors, rainbow gradients, glossy 3D, heavy shadows, sci-fi interfaces,
clutter, illegible or misspelled text, extra wording, logos, watermarks,
cropped title, and distorted tent geometry.
```
