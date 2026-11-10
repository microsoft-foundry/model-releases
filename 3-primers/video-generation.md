# Video Generation Models

> **Words and pictures in, moving pictures out.** A video generation model turns a
> prompt, and optionally a start image, an end image, or reference clips, into a
> short video clip, often with a matching soundtrack.

```mermaid
flowchart LR
    T[Text prompt] --> S
    I[Start / end image] --> S
    R[Reference images,<br/>video, audio] --> S
    S[Submit job] --> Q[Queue] --> P{Poll status}
    P -- IN_PROGRESS --> P
    P -- COMPLETED --> F[Fetch result] --> V[MP4: video + audio]
```

A video generation model is an image generation model that also has to get
**time** right. Every frame must look good, and the frames must agree with each
other: the same product, the same face, the same light, moving the way real
things move. That is why video costs more, takes longer, and needs a different
kind of prompt than a single image.

<br/>

## When should we reach for video generation?

- **Marketing and social:** product teasers, seasonal variants, and vertical
  clips for every channel from one brief.
- **Product pages:** short loops that show a product in use.
- **Concepts and storyboards:** test a creative idea before booking a shoot.
- **Animating existing assets:** bring a product photo, poster, or illustration
  to life.
- **Localization and variation:** the same scene in other formats, seasons, or
  settings without reshooting.

## When should we *not*?

- **Factual or instructional truth.** A generated how-to clip can show steps that
  are wrong or unsafe. Treat it as illustration and have an expert review it.
- **Real people.** Don't generate the likeness of a real person without consent,
  and check the provider's policies first.
- **Evidence or documentation.** Generated footage must never stand in for a
  record of what happened.
- **Long-form video.** Today's models make clips of seconds, not minutes. Longer
  pieces mean stitching many clips and fixing the joins.
- **Exact text or exact product geometry.** Labels, logos, and small parts can
  drift from frame to frame. Check every clip before it ships.

<br/>

## How does a video request work?

Video takes tens of seconds to minutes to render, so the API is **asynchronous**:

1. **Submit** a job with the prompt and settings. The service returns a `request_id`.
2. **Poll** the status endpoint until it reports `COMPLETED` (or an error).
3. **Fetch** the result. It holds a URL to the MP4, which we download.

Plan for this in code (timeouts, retries, progress) and in the product (a
"we're rendering your video" state, not a spinner on a chat reply).

<br/>

## Key terms

### Text-to-video

*"What do we get from a prompt alone?"*

Text-to-video generates a clip from words only. The model invents everything:
the setting, the product's look, the camera. It's the fastest way to explore an
idea and the least controllable.

### Image-to-video

*"How do we keep our real product in the shot?"*

Image-to-video starts from an image we supply and animates it. The first frame
is (close to) our image, so composition, colors, and the product's look start
where we want them. Most models also accept an optional **end image**.

### First and last frame (keyframes)

*"Can we control where the clip starts and where it ends?"*

First and last frame control pins the opening and closing frames, and the model
invents the motion between them: a packed tent bag at the start, a pitched tent
at the end. Some models also accept a **middle frame** at a set time.

### Reference-to-video

*"How do we put three specific products and one person in the same scene?"*

Reference-to-video takes several reference images (and sometimes video or audio
clips) that the clip should stay faithful to, without fixing any single frame.
The prompt names them by position, for example "the hiker from Image 1 opens the
backpack from Image 2".

### Elements (subject locking)

*"How do we keep the same character across shots?"*

An element is a subject defined once, from a front view plus extra angles or a
short video, and reused across shots. Some models also bind a **voice** to the
element so its dialogue sounds the same every time.

### Multi-shot generation

*"Can one request give us a cut, not just one continuous take?"*

Multi-shot generation produces several connected shots in one clip, keeping the
character, setting, light, and style consistent across the cuts. We either list
the shots (each with its own prompt and length) or let the model decide where to
cut.

### Native audio

*"Do we need a separate sound pass?"*

Native audio means the model generates the soundtrack together with the picture:
ambience, effects, music, and sometimes lip-synced dialogue. It's usually on by
default. Turn it off when the clip will get its own soundtrack. Some models can
also **pin** a soundtrack we supply.

### Duration, resolution, frame rate, aspect ratio

*"What shape of clip can we ask for?"*

These four settings define the clip, and they limit each other:

- **Duration:** seconds of output. Models offer fixed steps or a range, sometimes
  `auto`. The delivered clip can run slightly longer than requested.
- **Resolution:** from 480p drafts to 1080p and, on some models, 4K. Some models
  produce 1080p by **upscaling** a lower native resolution.
- **Frame rate (fps):** 24 looks cinematic, 50 looks smooth for fast motion. Higher
  rates often cap the maximum duration.
- **Aspect ratio:** 16:9 for web, 9:16 for phones, 1:1 for feeds, 21:9 for banners.

### Temporal consistency

*"Why does the logo melt halfway through?"*

Temporal consistency is how well things stay the same over time: shapes, text,
faces, and colors. It's the main quality difference between video models, and
the first thing to check in any clip.

### Camera motion

*"Can we direct the camera?"*

Camera motion describes how the virtual camera moves. Some models take it as a
setting; all of them respond to it in the prompt. Video models learned from real
footage, so film-crew vocabulary works better than "zoom" or "move closer":

| Term | What the camera does | Use it to |
| --- | --- | --- |
| **Dolly in / out** | Moves physically toward or away from the subject, as if on a cart on rails | Draw attention in, or reveal the setting |
| **Track (truck) left / right** | Moves sideways, alongside the subject | Follow someone walking, show a product line-up |
| **Jib (crane) up / down** | Rises or lowers, often tilting to keep the subject in frame | Open a scene from above, end on a wide view |
| **Orbit** | Circles around the subject | Show a product from every side |
| **Pan / tilt** | Turns left or right / up or down from a fixed spot | Scan a landscape, look up at something tall |
| **Zoom** | Stays put; the lens magnifies | A flatter, more mechanical look than a dolly |
| **Rack focus (focus shift)** | Moves the sharp focus from one object to another | Move attention from foreground to background |
| **Static** | Doesn't move | Let the subject's motion carry the shot |

Shot size says how much of the frame the subject fills: a **wide** (or long)
shot shows the whole scene, a **medium** shot shows the subject and some
surroundings, and a **close-up** fills the frame with one detail.

### Prompt expansion

*"Why doesn't the model do exactly what we wrote?"*

Prompt expansion rewrites a short prompt into a longer, more detailed one before
generation. It helps with terse prompts and hurts with carefully written ones.
When a model returns the expanded prompt, read it: it shows what the model was
really asked to make.

### Seed

*"How do we compare two settings fairly?"*

A seed fixes the random starting point. The same seed, prompt, and settings give a
similar result, so a change in output comes from the setting we changed, not from
luck.

### Guidance (CFG) and negative prompt

*"How strictly does the model follow the prompt?"*

Guidance scale (CFG) sets how closely the model sticks to the prompt: higher is
more literal, lower is more natural. A negative prompt lists what to avoid, such
as "blur, distorted text". Use both sparingly.

<br/>

## How do cost, latency, and quality trade off?

Every setting that adds pixels, frames, or seconds adds cost and render time.

| Setting | Quality | Latency | Cost |
| --- | --- | --- | --- |
| Longer duration | More story per clip; more chances to drift | Up | Up (often billed per second) |
| Higher resolution | Sharper detail and text | Up | Often up |
| Higher frame rate | Smoother fast motion | Up | Often up; may cap duration |
| Native audio on | Saves a sound pass | Slightly up | May be up |
| More references | Better subject fidelity | Up | May be up |
| Prompt expansion | Richer scenes from short prompts | Slightly up | Usually none |
| Fast or Turbo tier | Somewhat lower fidelity | Much lower | Lower |

A pattern that works: **draft cheap, finish expensive.** Explore prompts at
480p or 720p, short durations, on a Fast or Turbo model with a fixed seed. Render
only the winner at full resolution on the Pro or Max model.

Rate limits matter more than for text or images. A low quota tier can allow only
a couple of requests per minute, so batch work needs a queue, not a loop.

<br/>

## How do we prompt a video model?

Write a **shot**, not a sentence. A reliable order:

1. **Subject:** who or what, with the details that must stay fixed.
2. **Action:** one clear action per shot, with a start and an end.
3. **Setting:** place, time of day, weather.
4. **Camera:** shot size, angle, and movement.
5. **Light and style:** golden hour, overcast, claymation, film grain.
6. **Audio:** ambience, effects, dialogue (in quotes), or "no music".

For example:

> *Medium shot of the orange-and-green TrailMaster X4 tent on a granite ledge at
> sunrise. Rain starts; drops bead and run off the rainfly while the tent stays
> taut. Slow dolly in toward the door. Soft golden light, light mist over the lake
> below. Audio: steady rain on fabric, distant birds, no music.*

More tips:

- **Name references by position** ("Image 1", "Video 1") exactly as the API documents.
- **Quote on-screen text** and keep it short: a headline and a price, not a paragraph.
- **One change at a time** with a fixed seed, so we learn what each change does.
- **Describe physics** we care about: fabric moving in wind, steam rising, water beading.
- **Avoid contradictions** between the prompt and the input image, such as a prompt
  for night with a midday start frame.
- **Check the expanded prompt** when the model offers one.

<br/>

## What does one prompt look like on five models?

We sent the same prompt, unchanged, to all five fal video models in the Foundry
playground, each set to about **6 seconds**, text-to-video, with default settings
otherwise:

> *Medium shot of an orange-and-green camping tent on a granite ledge at sunrise.
> Rain starts; drops bead and run off the rainfly while the tent stays taut. Slow
> dolly in toward the door. Soft golden light, light mist over the lake below.
> Audio: steady rain on fabric, distant birds, no music.*

The prompt follows the six-part recipe above. Each phrase tells the model
something specific:

| Phrase | Recipe part | What it asks for |
| --- | --- | --- |
| *Medium shot* | Camera | Frame the tent with some of the ledge around it: not a close-up of the fabric, not a wide landscape |
| *an orange-and-green camping tent* | Subject | The fixed detail we can check in every frame: two specific colors |
| *on a granite ledge at sunrise* | Setting | Place (bare grey rock) and time of day (low, warm light) |
| *Rain starts* | Action | A change *during* the clip: dry at the start, raining by the end |
| *drops bead and run off the rainfly* | Action | Physics: water forms round drops on the waterproof outer layer (the **rainfly**) and slides off instead of soaking in |
| *while the tent stays taut* | Subject | The fabric stays tight and the tent keeps its shape, which shows quality |
| *Slow dolly in toward the door* | Camera | The camera itself moves closer to the tent's entrance, slowly (see [Camera motion](#camera-motion)) |
| *Soft golden light* | Light | Warm, low-contrast sunrise light ("golden hour") |
| *light mist over the lake below* | Setting | Atmosphere, and a lake below the ledge, which also implies height |
| *Audio: steady rain on fabric, distant birds* | Audio | Sounds that match what we see: the rain close, the birds far away |
| *no music* | Audio | A negative instruction. Models often add a soundtrack anyway |

Every row is something we can check in the result. A prompt with checkable
phrases is easier to evaluate, and to fix, than one with vague words like
"beautiful" or "cinematic".

Each row below shows five evenly spaced frames from the clip. Select the file name to
play it, with the sound on.

| Model | Five frames from the clip | What we got |
| --- | --- | --- |
| Kling V3 Pro<br/>[fal-kling-v3-pro.mp4](examples/video-generation/fal-kling-v3-pro.mp4) | ![Five frames from the Kling V3 Pro clip](examples/video-generation/fal-kling-v3-pro-strip.webp) | 1920×1080 · 24 fps · 6.04 s · 21.4 MB |
| LTX 2.5 Pro<br/>[fal-ltx-2.5-pro.mp4](examples/video-generation/fal-ltx-2.5-pro.mp4) | ![Five frames from the LTX 2.5 Pro clip](examples/video-generation/fal-ltx-2.5-pro-strip.webp) | 1280×720 · 25 fps · 6.00 s · 2.6 MB |
| LTX 2.5 Fast<br/>[fal-ltx-2.5-fast.mp4](examples/video-generation/fal-ltx-2.5-fast.mp4) | ![Five frames from the LTX 2.5 Fast clip](examples/video-generation/fal-ltx-2.5-fast-strip.webp) | 1280×720 · 25 fps · 6.00 s · 3.9 MB |
| MiniMax H3 Max<br/>[fal-minimax-h3-max.mp4](examples/video-generation/fal-minimax-h3-max.mp4) | ![Five frames from the MiniMax H3 Max clip](examples/video-generation/fal-minimax-h3-max-strip.webp) | 1344×768 · 24 fps · 6.59 s · 6.3 MB |
| MiniMax H3 Max Turbo<br/>[fal-minimax-h3-max-turbo.mp4](examples/video-generation/fal-minimax-h3-max-turbo.mp4) | ![Five frames from the MiniMax H3 Max Turbo clip](examples/video-generation/fal-minimax-h3-max-turbo-strip.webp) | 1344×768 · 24 fps · 6.59 s · 7.2 MB |

All five clips include audio.

### What stands out

- **Did they follow the brief's colors?** The two LTX clips render an orange tent
  with a green base. Both MiniMax clips render a tan, mustard-colored tent with no
  green. Color is a fixed detail in the prompt, so this is a prompt-adherence miss.
  When a product's color must be exact, start from a product image (image-to-video)
  instead of describing it.
- **Who moved the camera?** We asked for a slow dolly in toward the door. In the
  strips, MiniMax H3 Max pushes in from a side angle until the open door fills the
  frame, and LTX 2.5 Pro creeps closer head-on. LTX 2.5 Fast changes angle between
  frames, and Turbo barely moves. Play each clip to judge the speed and smoothness
  of the move, which a strip can't show.
- **Is the rain there?** A strip can't show falling drops. In the MiniMax clips the
  ledge is wet and reflective and mist rises off the lake, which hints at weather;
  in the LTX clips the ledge looks dry and frosty. Watch for drops *running off*
  the fabric, the hardest physical detail in the prompt.
- **What did "6 seconds" mean?** Kling and both LTX clips delivered 6.0 s. Both
  MiniMax clips delivered 6.59 s, in line with the documented "up to about 0.7 s
  longer". Plan to trim if a slot is exact.
- **Why is Kling's file 8× bigger?** It came back at **1080p**; the others are 720p
  or 768p. Defaults differ by model, so "same prompt, default settings" isn't the
  same output size. Compare quality at matched resolutions before drawing
  conclusions.
- **What did speed cost?** Pair each quality tier with its fast sibling: LTX Pro vs
  Fast, H3 Max vs Turbo. Here the Fast and Turbo clips are larger files, not
  smaller: file size tracks motion and detail, not quality tier. Judge them on the
  checklist below, not on megabytes.

**What to look for** when you play them:

- **Subject:** is the tent orange *and* green, and does it keep its shape while it rains?
- **Action:** does the rain *start* during the clip, and do drops bead and run **off** the fabric?
- **Camera:** is there a slow dolly in toward the door, or a static shot or a different move?
- **Light and setting:** sunrise light, a granite ledge, mist over a lake below.
- **Audio:** rain on fabric and distant birds, and **no music**. Negative instructions
  are the easiest ones for a model to miss.

Every run is different, so treat these as one sample each, not a benchmark. To
compare fairly in code, fix the seed where the model supports it, match the
resolution, and change one setting at a time.

<br/>

## Where does video generation pay off?

| Domain | Typical use |
| --- | --- |
| Retail and e-commerce | Product-page loops, launch teasers, seasonal variants |
| Marketing and advertising | Social cut-downs, A/B creative, localized versions |
| Media and entertainment | Previsualization, storyboards, concept trailers |
| Travel and real estate | Destination and property mood clips |
| Training and education | Illustrative scenes (reviewed by an expert) |
| Internal communications | Event openers, explainer intros |

<br/>

## What sets one video model apart from another?

When we compare models, these differences decide the pick:

- **Input modes:** text, image, first and last frame, middle frame, references.
- **Subject control:** element locking, multi-character scenes, voice binding.
- **Shot control:** single take or multi-shot, and per-shot timing.
- **Audio:** none, generated, or pinned to our own clip; which languages it speaks.
- **Camera control:** prompt only, or a dedicated setting.
- **Output range:** durations, resolutions, frame rates, and aspect ratios.
- **Speed tier:** a quality model and a fast sibling of the same family.
- **Hosting and data:** who runs the model, which deployment types and regions
  are offered, and where the data goes.

The fal video family on Microsoft Foundry (preview) shows how wide the spread is:

| Model | Stands out for | Durations | Resolutions | Deployment |
| --- | --- | --- | --- | --- |
| Kling V3 Pro | Multi-shot storyboards, element locking with voice, cinematic camera moves | 3–15 s | Not specified | US Data Zone |
| LTX 2.5 Pro | Detail in complex scenes, legible text, camera-motion setting | 6–10 s | 720p, 1080p | Global Standard |
| LTX 2.5 Fast | Speed, up to 20 s and 4K | 6–20 s | 720p–2160p | Global Standard |
| MiniMax H3 Max | Reference-to-video (images, video, audio), first, middle, and last frames | 1–15 s | 480P–1080P | Global Standard |
| MiniMax H3 Max Turbo | The H3 Max text and image modes, faster | 1–15 s | 480P–1080P | Global Standard |

fal models are hosted by fal, outside Microsoft. Data leaves Microsoft, and
Microsoft's product terms and data-protection agreements don't apply. Check this
with the customer before any production use.

<br/>

## Try it

- [Kling V3 Pro](../4-models/fal-kling-v3-pro/)
- [LTX 2.5 Pro](../4-models/fal-ltx-2.5-pro/)
- [LTX 2.5 Fast](../4-models/fal-ltx-2.5-fast/)
- [MiniMax H3 Max](../4-models/fal-minimax-h3-max/)
- [MiniMax H3 Max Turbo](../4-models/fal-minimax-h3-max-turbo/)

## Learn more

1. [Fal models on Microsoft Foundry (preview)](https://learn.microsoft.com/azure/foundry/how-to/fal-ai-models/enable-fal-models)
2. [Deployment types in Microsoft Foundry](https://learn.microsoft.com/azure/foundry/foundry-models/concepts/deployment-types)
3. [Risk and safety evaluations](https://learn.microsoft.com/azure/foundry/concepts/safety-evaluations-transparency-note)
