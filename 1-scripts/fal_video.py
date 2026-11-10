"""Shared helpers for the fal video capsules in 4-models/fal-*/.

Submit a job, poll until it finishes, download the MP4, and keep a JSON record next to it.
In replay mode, nothing is sent: clips come from the capsule's output/ (yours) or examples/ (ours).

    from fal_video import FalVideo, as_url, scoreboard
    fal = FalVideo(endpoint, deployment, family="minimax/h3-max", here=HERE, mode="live")
    clip = fal.run("01-first-clip", "text-to-video", prompt="...", duration=5)
    fal.show(clip)
"""

from __future__ import annotations

import base64
import io
import json
import mimetypes
import re
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse

import requests

# The Learn page lists routes without /v1, but its working samples use it. Change here if that's fixed.
API_PREFIX = "/providers/falai/v1"
SCOPE = "https://cognitiveservices.azure.com/.default"

HINTS = {
    400: "The service rejected a setting. The message below names it; compare it with the model's limits in the At a glance table.",
    401: "Sign-in failed. Run `az login` in a terminal, then run the cell again.",
    403: "Signed in, but not allowed. Check that Fal.EnableDeploy is registered on the subscription and that you have a Foundry role on the resource.",
    404: "No such deployment or route. Compare the deployment variable in .env with your project's Deployments page.",
    422: "A setting is out of range or the wrong type. The message below says which one.",
}


@dataclass
class Clip:
    name: str
    path: Path
    record: dict = field(default_factory=dict)
    source: str = "live"

    @property
    def info(self) -> dict:
        return self.record.get("probe", {})


def _ffmpeg() -> str:
    import imageio_ffmpeg

    return imageio_ffmpeg.get_ffmpeg_exe()


def probe(path: Path) -> dict:
    """Duration, size, fps, and audio presence, read from the file itself."""
    err = subprocess.run([_ffmpeg(), "-hide_banner", "-i", str(path)], capture_output=True, text=True).stderr
    info: dict = {"has_audio": " Audio: " in err, "size_mb": round(path.stat().st_size / 1e6, 2)}
    if m := re.search(r"Duration: (\d+):(\d+):([\d.]+)", err):
        h, mnt, s = m.groups()
        info["seconds"] = round(int(h) * 3600 + int(mnt) * 60 + float(s), 2)
    if m := re.search(r"Video: .*?, (\d{2,5})x(\d{2,5})", err):
        info["width"], info["height"] = int(m.group(1)), int(m.group(2))
    if m := re.search(r"([\d.]+) fps", err):
        info["fps"] = float(m.group(1))
    return info


def frame_strip(path: Path, frames: int = 5, height: int = 160) -> Path:
    """Save evenly spaced frames side by side as a small WebP, so GitHub can show the clip."""
    from PIL import Image

    out = path.with_name(f"{path.stem}-strip.webp")
    if out.exists() and out.stat().st_mtime >= path.stat().st_mtime:
        return out
    seconds = probe(path).get("seconds") or 5
    vf = f"fps={frames}/{seconds},scale=-2:{height},tile={frames}x1"
    png = subprocess.run(
        [_ffmpeg(), "-hide_banner", "-loglevel", "error", "-i", str(path), "-vf", vf, "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"],
        capture_output=True,
        check=True,
    ).stdout
    Image.open(io.BytesIO(png)).save(out, "WEBP", quality=70)
    return out


def as_url(path: Path, max_side: int | None = 1536) -> str:
    """Turn a local image or audio file into a data URI the API can read. Images are sent as JPEG."""
    path = Path(path)
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    if mime.startswith("image/"):
        from PIL import Image

        with Image.open(path) as im:
            im = im.convert("RGB")
            if max_side and max(im.size) > max_side:
                im.thumbnail((max_side, max_side))
            buf = io.BytesIO()
            im.save(buf, "JPEG", quality=90)
        return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


def _redact(params: dict) -> dict:
    """Keep the request readable in the saved record: data URIs become a short note."""

    def short(v):
        if isinstance(v, str) and v.startswith("data:"):
            return f"<{v[5:v.find(';')]} data, {len(v) // 1024} KB>"
        if isinstance(v, list):
            return [short(x) for x in v]
        if isinstance(v, dict):
            return {k: short(x) for k, x in v.items()}
        return v

    return {k: short(v) for k, v in params.items()}


class FalVideo:
    """One fal model family on one Foundry deployment."""

    def __init__(self, endpoint: str | None, deployment: str, family: str, here: Path, mode: str = "replay",
                 requests_per_minute: int = 2, play_inline: bool = True, credential=None):
        self.deployment, self.family, self.mode, self.play_inline = deployment, family, mode, play_inline
        self.output, self.examples = Path(here) / "output", Path(here) / "examples"
        self.output.mkdir(parents=True, exist_ok=True)
        self.gap = 60 / max(requests_per_minute, 1)
        self._next = 0.0
        self.host = urlparse(endpoint).hostname if endpoint else None
        self.base = f"https://{self.host}{API_PREFIX}/{family}" if self.host else None
        self.credential = credential

    # -- replay ---------------------------------------------------------------------------
    def saved(self, name: str) -> Clip | None:
        """Your clip from output/ first, then ours from examples/."""
        for folder, source in ((self.output, "yours"), (self.examples, "example")):
            mp4 = folder / f"{name}.mp4"
            if mp4.exists():
                rec = folder / f"{name}.json"
                record = json.loads(rec.read_text()) if rec.exists() else {}
                record.setdefault("probe", probe(mp4))
                return Clip(name, mp4, record, source)
        return None

    # -- live -----------------------------------------------------------------------------
    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self.credential.get_token(SCOPE).token}"}

    def _check(self, reply: requests.Response, what: str) -> dict:
        if reply.ok:
            return reply.json()
        try:
            detail = json.dumps(reply.json())[:600]
        except ValueError:
            detail = reply.text[:600]
        hint = HINTS.get(reply.status_code, "The message below usually says what to change.")
        raise RuntimeError(f"{reply.status_code} while {what} on {self.deployment}. {hint}\n{detail}")

    def _wait_turn(self) -> None:
        wait = self._next - time.monotonic()
        if wait > 0:
            print(f"   Waiting {wait:.0f} s for the rate limit ({60 / self.gap:.0f} requests a minute)...")
            time.sleep(wait)
        self._next = time.monotonic() + self.gap

    def run(self, name: str, route: str, poll_every: float = 5, timeout: float = 900, **params) -> Clip:
        """Generate one clip (live) or load the saved one (replay)."""
        if self.mode == "replay":
            clip = self.saved(name)
            if clip is None:
                raise RuntimeError(f"Replay has no saved clip named '{name}'. Set DEMO_MODE to live to make it.")
            return clip
        if not self.base:
            raise RuntimeError("MICROSOFT_FOUNDRY_ENDPOINT isn't set. Fill in .env (see setup.ipynb), then rerun the env check.")

        body = {"model": self.deployment, **params}
        for attempt in range(4):
            self._wait_turn()
            started = time.perf_counter()
            reply = requests.post(f"{self.base}/{route}", json=body, headers=self._headers(), timeout=120)
            if reply.status_code != 429:
                break
            pause = float(reply.headers.get("Retry-After", 30))
            print(f"   Busy (429). Trying again in {pause:.0f} s...")
            time.sleep(pause)
        request_id = self._check(reply, "submitting")["request_id"]
        print(f"   Submitted {name} ({request_id[:8]}...)", end="", flush=True)

        status, queued_for = "", None
        while status != "COMPLETED":
            if time.perf_counter() - started > timeout:
                raise RuntimeError(f"No result after {timeout:.0f} s. The job may still finish; request id {request_id}.")
            time.sleep(poll_every)
            status = self._check(requests.get(f"{self.base}/requests/{request_id}/status", headers=self._headers(), timeout=60), "polling")["status"]
            if status == "IN_PROGRESS" and queued_for is None:
                queued_for = time.perf_counter() - started
            if status in ("FAILED", "ERROR", "CANCELLED"):
                raise RuntimeError(f"The job ended with status {status}. Request id {request_id}.")
            print(".", end="", flush=True)
        result = self._check(requests.get(f"{self.base}/requests/{request_id}", headers=self._headers(), timeout=60), "fetching the result")
        seconds = time.perf_counter() - started

        video = result.get("video") or {}
        if not video.get("url"):
            raise RuntimeError(f"The job finished without a video. Response: {json.dumps(result)[:600]}")
        # Only send our Entra token to the Foundry host, never to a third-party CDN.
        headers = self._headers() if urlparse(video["url"]).hostname == self.host else {}
        download = requests.get(video["url"], headers=headers, timeout=300)
        download.raise_for_status()

        path = self.output / f"{name}.mp4"
        path.write_bytes(download.content)
        response = {k: v for k, v in result.items() if k != "video"} | {"video": {k: v for k, v in video.items() if k != "url"}}
        record = {
            "deployment": self.deployment,
            "route": f"{self.family}/{route}",
            "params": _redact(params),
            "seconds": round(seconds, 1),
            "queued_seconds": round(queued_for, 1) if queued_for is not None else None,
            "request_id": request_id,
            "response": response,
            "probe": probe(path),
        }
        (self.output / f"{name}.json").write_text(json.dumps(record, indent=2, ensure_ascii=False))
        print(f" done in {seconds:.0f} s")
        return Clip(name, path, record, "yours")

    # -- look -----------------------------------------------------------------------------
    def show(self, *clips: Clip, frames: int = 5) -> None:
        """Frame strip for each clip (renders on GitHub), plus a player when play_inline is on."""
        from IPython.display import Image, Video, display

        for clip in clips:
            info, rec = clip.info, clip.record
            facts = [f"{info.get('width')}x{info.get('height')}" if info.get("width") else None,
                     f"{info['seconds']:.1f} s" if "seconds" in info else None,
                     f"{info['fps']:g} fps" if "fps" in info else None,
                     "audio" if info.get("has_audio") else "no audio",
                     f"made in {rec['seconds']:.0f} s" if "seconds" in rec else None,
                     f"({clip.source})"]
            print(f"{clip.name}: " + " | ".join(f for f in facts if f))
            display(Image(filename=str(frame_strip(clip.path, frames))))
            if self.play_inline:
                display(Video(str(clip.path), embed=True, width=480))


def scoreboard(clips: list[Clip]) -> None:
    """One row per clip: time to make it, requested vs delivered length, shape, size."""
    print(f"{'clip':34} {'made in':>8} {'asked':>6} {'got':>6} {'size':>10} {'fps':>5} {'MB':>6} audio")
    for c in clips:
        i, r = c.info, c.record
        asked = r.get("params", {}).get("duration")
        print(f"{c.name:34} {str(r.get('seconds', '-')) + ' s':>8} {str(asked or '-'):>6} {i.get('seconds', '-'):>6} "
              f"{str(i.get('width', '-')) + 'x' + str(i.get('height', '-')):>10} {i.get('fps', '-'):>5} {i.get('size_mb', '-'):>6} "
              f"{'yes' if i.get('has_audio') else 'no'}")
