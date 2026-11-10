"""Shared helpers for the MAI image capsules in 4-models/mai-image-*/.

Draw (generate) or edit pictures through the MAI image API on Microsoft Foundry, with keyless Entra ID sign-in.
Live mode saves PNGs and a run log to the capsule's output/. Replay mode sends nothing: it shows output/ first,
then examples/, where a run-log entry may point at a shared scenario image instead of keeping a second copy.

    from mai_image import MaiImage
    mai = MaiImage(endpoint, here=HERE, mode="live", credential=DefaultAzureCredential())
    poster = mai.generate("A launch poster ...", "01-poster", model="MAI-Image-2.6", size=(1024, 1536))
    mai.show({"Poster": poster})
"""

from __future__ import annotations

import base64
import io
import json
import os
import threading
import time
from collections import defaultdict
from pathlib import Path
from urllib.parse import quote, urlparse

import requests
from PIL import Image

SCOPE = "https://cognitiveservices.azure.com/.default"
HINTS = {
    400: "The model didn't accept a setting. Check the size (each side 768 or more, 2,359,296 pixels at most), the image type (PNG or JPEG), and the options.",
    401: "Sign-in failed. Run `az login` in a terminal, then run the cell again.",
    403: "Signed in, but not allowed. Ask for a Foundry role (such as Foundry User) on the resource.",
    404: "No deployment with that name. Compare the deployment variables in .env with the project's Deployments page.",
}


class MaiImage:
    """MAI image deployments on one Foundry resource, with replay and a run log."""

    def __init__(self, endpoint: str | None, here: Path, mode: str = "replay", requests_per_minute: int = 6, credential=None):
        self.mode, self.credential = mode, credential
        self.host = urlparse(endpoint).hostname if endpoint else None
        self.output, self.examples = Path(here) / "output", Path(here) / "examples"
        self.output.mkdir(parents=True, exist_ok=True)
        self.gap = 60 / max(requests_per_minute, 1)
        self._next: dict[str, float] = defaultdict(float)
        self._turns: dict[str, threading.Lock] = defaultdict(threading.Lock)
        self._log_lock = threading.Lock()
        self._log_file = self.output / "run_log.json"
        self.mine = json.loads(self._log_file.read_text()) if self._log_file.exists() else {}
        ours = self.examples / "run_log.json"
        self.ours = json.loads(ours.read_text()) if ours.exists() else {}
        self.log: dict[str, dict] = {}

    # -- replay ---------------------------------------------------------------------------
    def saved(self, name: str) -> Path | None:
        """Our own picture from output/ first, then the example (or the scenario image it points to)."""
        if (self.output / f"{name}.png").exists():
            return self.output / f"{name}.png"
        entry = self.ours.get(name, {})
        path = (self.examples / entry["file"]).resolve() if "file" in entry else self.examples / f"{name}.webp"
        return path if path.exists() else None

    def _replayed(self, name: str) -> Path | None:
        if self.mode != "replay":
            return None
        path = self.saved(name)
        entry = self.mine.get(name) if path and path.parent == self.output else self.ours.get(name)
        if not (path and entry):
            raise RuntimeError(f"Replay has no saved picture named '{name}'. Set DEMO_MODE to live to make it.")
        self.log[name] = entry
        where = "yours" if path.parent == self.output else "example"
        print(f"   {name}: {entry['model']} | {entry['seconds']} s | {entry['size']} ({where})")
        return path

    # -- live -----------------------------------------------------------------------------
    def _wait_turn(self, model: str) -> None:
        # Each deployment has its own requests-per-minute limit; spacing requests out beats hitting it.
        with self._turns[model]:
            wait = self._next[model] - time.monotonic()
            if wait > 0:
                time.sleep(wait)
            self._next[model] = time.monotonic() + self.gap

    def _call(self, api: str, model: str, **request) -> tuple[dict, float]:
        if not self.host:
            raise RuntimeError("MICROSOFT_FOUNDRY_ENDPOINT isn't set. Fill in .env (see setup.ipynb), then rerun the env check.")
        for _ in range(4):
            self._wait_turn(model)
            token = self.credential.get_token(SCOPE).token
            started = time.perf_counter()
            reply = requests.post(f"https://{self.host}/mai/v1/images/{api}", headers={"Authorization": f"Bearer {token}"},
                                  timeout=300, **request)
            seconds = time.perf_counter() - started
            if reply.status_code == 429 or reply.status_code >= 500:
                pause = float(reply.headers.get("Retry-After", 20))
                print(f"   {model} is busy ({reply.status_code}). Trying again in {pause:.0f} s...")
                time.sleep(pause)
                continue
            if reply.ok:
                return reply.json(), seconds
            try:
                detail = reply.json().get("error", {}).get("message", "")[:400]
            except ValueError:
                detail = reply.text[:400]
            hint = HINTS.get(reply.status_code, "The message below usually says what to change.")
            raise RuntimeError(f"{reply.status_code} from {model}. {hint}\n{detail}")
        raise RuntimeError(f"{model} was still busy after four tries. Wait a minute, then run the cell again.")

    def _keep(self, name: str, model: str, seconds: float, reply: dict) -> Path:
        path = self.output / f"{name}.png"
        path.write_bytes(base64.b64decode(reply["data"][0]["b64_json"]))
        width, height = Image.open(path).size
        entry = {"model": model, "seconds": round(seconds, 1), "size": f"{width}×{height}"}
        with self._log_lock:
            self.log[name] = self.mine[name] = entry
            self._log_file.write_text(json.dumps(self.mine, indent=2, ensure_ascii=False))
        print(f"   {name}: {model} | {entry['seconds']} s | {entry['size']}")
        return path

    def generate(self, prompt: str, name: str, model: str, size: tuple[int, int] | None = (1024, 1024), **options) -> Path:
        """Draw a new picture from words. size=None with auto_aspect_ratio=True lets the model pick the shape."""
        if path := self._replayed(name):
            return path
        body = {"model": model, "prompt": prompt, **options}
        if size:
            body["width"], body["height"] = size
        reply, seconds = self._call("generations", model, json=body)
        return self._keep(name, model, seconds, reply)

    def edit(self, prompt: str, references: list[Path], name: str, model: str, **options) -> Path:
        """Make a picture from one to five reference pictures plus words."""
        if path := self._replayed(name):
            return path
        files = [("image", _as_upload(ref)) for ref in references]
        # The edits API takes a form, so booleans travel as "true" and "false".
        form = {"model": model, "prompt": prompt, **{k: str(v).lower() if isinstance(v, bool) else str(v) for k, v in options.items()}}
        reply, seconds = self._call("edits", model, data=form, files=files)
        return self._keep(name, model, seconds, reply)

    # -- look -----------------------------------------------------------------------------
    def show(self, pictures: dict[str, Path], height: int = 300) -> None:
        """Small inline thumbnails side by side (keeps the notebook light), plus a link to each full-size file."""
        from IPython.display import HTML, Markdown, display

        cards = "".join(
            f'<figure style="display:inline-block;margin:0 12px 12px 0;vertical-align:top;text-align:center">'
            f'<img src="{_thumbnail(path, height)}" style="height:{height}px;border-radius:6px"/>'
            f'<figcaption style="font-size:13px">{caption}</figcaption></figure>'
            for caption, path in pictures.items()
        )
        display(HTML(f"<div>{cards}</div>"))
        links = [f"[{caption}]({quote(Path(os.path.relpath(path, Path.cwd())).as_posix())})" for caption, path in pictures.items()]
        display(Markdown("Full size: " + " · ".join(links)))


def _thumbnail(path: Path, height: int) -> str:
    picture = Image.open(path).convert("RGB")
    picture.thumbnail((height * 4, height))
    buffer = io.BytesIO()
    picture.save(buffer, "JPEG", quality=85)
    return "data:image/jpeg;base64," + base64.b64encode(buffer.getvalue()).decode()


def _as_upload(ref: Path) -> tuple[str, bytes, str]:
    """The edits API takes PNG or JPEG, so WebP examples are sent as PNG."""
    ref = Path(ref)
    if ref.suffix.lower() in (".png", ".jpg", ".jpeg"):
        return ref.name, ref.read_bytes(), "image/png" if ref.suffix.lower() == ".png" else "image/jpeg"
    buffer = io.BytesIO()
    Image.open(ref).save(buffer, "PNG")
    return ref.with_suffix(".png").name, buffer.getvalue(), "image/png"
