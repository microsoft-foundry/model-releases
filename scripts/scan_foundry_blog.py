#!/usr/bin/env python3
"""
scan_foundry_blog.py — Scan the Microsoft Foundry blog for new model
announcements and stage draft CHANGELOG + README updates.

Behavior:

1. Fetch the Foundry blog index page and follow "next page" links up
   to --max-pages (default 3).
2. Extract candidate posts (URL, title, publish date).
3. Filter to plausible model announcements (title heuristic: mentions
   a model family, "introducing", "available", "now in Foundry", etc).
4. Diff against blog URLs already referenced in CHANGELOG.md.
5. For each new post, prepend a draft row to CHANGELOG.md with the
   Date linking to the blog post. Family / Model / Capabilities /
   Model card / Pricing cells are filled with `_review_` placeholders
   so the maintainer knows what to complete before merging.
6. Regenerate the README `<!-- BEGIN:RECENTLY-ADDED -->` block from
   the top 3 CHANGELOG rows.
7. Print a short summary to stdout so the workflow can surface it in
   the PR body.

The script uses only Python's stdlib. No API keys.

Design notes:

- The blog listing HTML shape may drift; parsing is intentionally
  forgiving. When a field can't be extracted we fall back to
  `_review_` and let the maintainer fix it in the PR.
- The script never edits existing CHANGELOG rows — it only prepends.
  Manual/curated rows added by hand keep their fidelity.
- A row is considered "already present" if its Date-cell markdown link
  points at the same blog URL (path-normalized, ignoring trailing /).
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Iterable

BLOG_INDEX = (
    "https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/"
)

# Post URLs on the community look like
#   https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/<slug>/<numeric-id>
POST_URL_RE = re.compile(
    r"https://techcommunity\.microsoft\.com/blog/azure-ai-foundry-blog/"
    r"([a-z0-9\-]+)/(\d+)",
    re.IGNORECASE,
)

# Heuristics: a "model announcement" post title usually contains at
# least one of these signal phrases.
MODEL_TITLE_SIGNALS = [
    "introducing",
    "available today",
    "available now",
    "now available",
    "now in microsoft foundry",
    "now in foundry",
    "generally available",
    "ga in",
    "launches in",
    "launch in",
    "coming to microsoft foundry",
    "coming to foundry",
    "arrives in microsoft foundry",
    "arrives in foundry",
]

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/126.0.0.0 Safari/537.36"
)

DEFAULT_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "identity",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Upgrade-Insecure-Requests": "1",
}


@dataclass
class BlogPost:
    url: str
    title: str
    published: date | None

    @property
    def normalized_url(self) -> str:
        """URL used for equality checks against CHANGELOG rows."""
        p = urllib.parse.urlsplit(self.url)
        path = p.path.rstrip("/")
        return urllib.parse.urlunsplit((p.scheme, p.netloc, path, "", ""))


def http_get(url: str, timeout: int = 30) -> str:
    req = urllib.request.Request(url, headers=DEFAULT_HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read()
    # Community pages are UTF-8; be forgiving.
    return raw.decode("utf-8", errors="replace")


def extract_post_urls(page_html: str) -> list[str]:
    seen: dict[str, None] = {}
    for m in POST_URL_RE.finditer(page_html):
        url = m.group(0)
        # Strip query/fragment defensively.
        p = urllib.parse.urlsplit(url)
        url = urllib.parse.urlunsplit(
            (p.scheme, p.netloc, p.path, "", "")
        )
        if url not in seen:
            seen[url] = None
    return list(seen)


def extract_title(post_html: str, fallback: str = "") -> str:
    # <meta property="og:title" content="..."> is the most reliable.
    m = re.search(
        r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)["\']',
        post_html,
        re.IGNORECASE,
    )
    if m:
        return html.unescape(m.group(1)).strip()
    m = re.search(
        r"<title[^>]*>(.*?)</title>", post_html, re.IGNORECASE | re.DOTALL
    )
    if m:
        # Strip trailing " - Microsoft Community Hub" etc.
        title = html.unescape(m.group(1)).strip()
        title = re.split(r"\s+[|\-–]\s+", title, maxsplit=1)[0]
        return title.strip()
    return fallback


def extract_published(post_html: str) -> date | None:
    # JSON-LD is the most reliable source.
    for m in re.finditer(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        post_html,
        re.IGNORECASE | re.DOTALL,
    ):
        try:
            data = json.loads(m.group(1))
        except json.JSONDecodeError:
            continue
        items = data if isinstance(data, list) else [data]
        for item in items:
            if not isinstance(item, dict):
                continue
            for key in ("datePublished", "dateCreated", "dateModified"):
                v = item.get(key)
                if isinstance(v, str):
                    try:
                        return datetime.fromisoformat(
                            v.replace("Z", "+00:00")
                        ).date()
                    except ValueError:
                        pass
    # Fallback: <meta property="article:published_time" ...>
    m = re.search(
        r'<meta[^>]+property=["\']article:published_time["\'][^>]+'
        r'content=["\']([^"\']+)["\']',
        post_html,
        re.IGNORECASE,
    )
    if m:
        try:
            return datetime.fromisoformat(
                m.group(1).replace("Z", "+00:00")
            ).date()
        except ValueError:
            pass
    return None


def looks_like_model_post(title: str) -> bool:
    t = title.lower()
    if any(sig in t for sig in MODEL_TITLE_SIGNALS):
        return True
    # Also accept titles that literally start with a model family name
    # we already know about — cheap heuristic to catch retros.
    families = ["gpt-", "claude ", "kimi ", "mai-", "grok ", "llama ",
                "gemini ", "phi-", "mistral", "deepseek"]
    return any(t.startswith(f) for f in families)


def crawl_index(max_pages: int) -> list[BlogPost]:
    urls: list[str] = []
    for page in range(1, max_pages + 1):
        page_url = BLOG_INDEX if page == 1 else f"{BLOG_INDEX}?page={page}"
        try:
            page_html = http_get(page_url)
        except Exception as e:
            print(f"[warn] failed to fetch {page_url}: {e}", file=sys.stderr)
            continue
        for u in extract_post_urls(page_html):
            if u not in urls:
                urls.append(u)

    posts: list[BlogPost] = []
    for url in urls:
        try:
            post_html = http_get(url)
        except Exception as e:
            print(f"[warn] failed to fetch {url}: {e}", file=sys.stderr)
            continue
        title = extract_title(post_html)
        published = extract_published(post_html)
        if not title:
            continue
        posts.append(BlogPost(url=url, title=title, published=published))
    return posts


CHANGELOG_URL_RE = re.compile(
    r"https://techcommunity\.microsoft\.com/blog/azure-ai-foundry-blog/"
    r"[a-z0-9\-]+/\d+",
    re.IGNORECASE,
)


def existing_changelog_urls(changelog_text: str) -> set[str]:
    urls: set[str] = set()
    for m in CHANGELOG_URL_RE.finditer(changelog_text):
        url = m.group(0)
        p = urllib.parse.urlsplit(url)
        urls.add(
            urllib.parse.urlunsplit(
                (p.scheme, p.netloc, p.path.rstrip("/"), "", "")
            )
        )
    return urls


def draft_row(post: BlogPost) -> str:
    dstr = post.published.isoformat() if post.published else "YYYY-MM-DD"
    # Draft row — maintainer completes Family / Model / Capabilities /
    # Model card / Pricing before merging.
    return (
        f"| [{dstr}]({post.url}) | _review_ | _review_ (blog title: "
        f"\"{post.title}\") | _review_ | _—_ | _—_ |"
    )


TABLE_ROW_RE = re.compile(r"^\|.*\|\s*$")


def insert_rows_into_changelog(
    changelog_text: str, new_rows: list[str]
) -> str:
    """Insert new_rows immediately after the header separator row."""
    if not new_rows:
        return changelog_text
    lines = changelog_text.splitlines()
    # Find the header row + separator.
    for i, line in enumerate(lines):
        if line.startswith("| Date |") and i + 1 < len(lines):
            sep = lines[i + 1]
            if re.match(r"^\|\s*---", sep):
                insert_at = i + 2
                new_block = list(new_rows)
                lines[insert_at:insert_at] = new_block
                return "\n".join(lines) + (
                    "\n" if changelog_text.endswith("\n") else ""
                )
    raise RuntimeError("CHANGELOG.md header row not found")


README_MARK_BEGIN = "<!-- BEGIN:RECENTLY-ADDED -->"
README_MARK_END = "<!-- END:RECENTLY-ADDED -->"


def parse_changelog_top(
    changelog_text: str, n: int
) -> list[dict[str, str]]:
    """Extract the first n data rows from the CHANGELOG table."""
    lines = changelog_text.splitlines()
    rows: list[list[str]] = []
    in_table = False
    for line in lines:
        if line.startswith("| Date |"):
            in_table = True
            continue
        if in_table and re.match(r"^\|\s*---", line):
            continue
        if in_table:
            if not line.strip().startswith("|"):
                break
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 6:
                rows.append(cells)
            if len(rows) >= n:
                break
    keys = [
        "date", "family", "model", "capabilities",
        "pricing", "capsule",
    ]
    return [dict(zip(keys, r)) for r in rows]


def render_readme_block(rows: list[dict[str, str]]) -> str:
    header = (
        "| Release date | Model | Description | Expires |\n"
        "|---|---|---|---|"
    )
    body_lines: list[str] = []
    for r in rows:
        model = r.get("model", "_review_")
        # Description falls back to the blog title captured in the
        # draft row's Capabilities cell if the maintainer hasn't
        # written a real description yet.
        description = r.get("capabilities", "").strip() or "_review_"
        body_lines.append(
            f"| {r.get('date', '_review_')} | **{model}** | {description} | — |"
        )
    caption = (
        "\n\n_Top 3 most recent — see [`CHANGELOG.md`](CHANGELOG.md) "
        "for the full history and pricing._"
    )
    return (
        f"{README_MARK_BEGIN}\n"
        f"{header}\n"
        + "\n".join(body_lines)
        + caption
        + f"\n{README_MARK_END}"
    )


def update_readme_recent(readme_text: str, block: str) -> str:
    pattern = re.compile(
        re.escape(README_MARK_BEGIN)
        + r".*?"
        + re.escape(README_MARK_END),
        re.DOTALL,
    )
    if not pattern.search(readme_text):
        raise RuntimeError("README RECENTLY-ADDED markers not found")
    return pattern.sub(block, readme_text)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--max-pages", type=int, default=3)
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned changes without writing files.",
    )
    args = ap.parse_args(argv)

    changelog_path = args.repo_root / "CHANGELOG.md"
    readme_path = args.repo_root / "README.md"
    if not changelog_path.exists():
        print(f"error: {changelog_path} not found", file=sys.stderr)
        return 2
    if not readme_path.exists():
        print(f"error: {readme_path} not found", file=sys.stderr)
        return 2

    changelog_text = changelog_path.read_text(encoding="utf-8")
    readme_text = readme_path.read_text(encoding="utf-8")
    known = existing_changelog_urls(changelog_text)

    print(f"[scan] fetching up to {args.max_pages} index page(s)…")
    posts = crawl_index(args.max_pages)
    print(f"[scan] discovered {len(posts)} post(s) total")

    if not posts:
        print(
            "[scan] no posts discovered — the community platform may be "
            "returning an anti-bot page. This is a soft failure: the "
            "workflow will exit 0 with no changes. If this persists, "
            "upgrade the scanner to use a headless browser (Playwright)."
        )
        return 0

    # Only consider posts that (a) look like model announcements and
    # (b) are not already referenced in CHANGELOG.
    candidates: list[BlogPost] = []
    for p in posts:
        if p.normalized_url in known:
            continue
        if not looks_like_model_post(p.title):
            continue
        candidates.append(p)

    # Sort newest-first by published date; posts with unknown dates go
    # last so a human can triage.
    candidates.sort(
        key=lambda p: (p.published or date.min), reverse=True
    )

    print(f"[scan] {len(candidates)} new model-announcement post(s):")
    for p in candidates:
        d = p.published.isoformat() if p.published else "unknown"
        print(f"  - {d} · {p.title}")
        print(f"    {p.url}")

    if not candidates:
        print("[scan] nothing new to add.")
        return 0

    new_rows = [draft_row(p) for p in candidates]
    updated_changelog = insert_rows_into_changelog(
        changelog_text, new_rows
    )
    top3 = parse_changelog_top(updated_changelog, 3)
    updated_readme = update_readme_recent(
        readme_text, render_readme_block(top3)
    )

    if args.dry_run:
        print("\n[dry-run] would prepend these CHANGELOG rows:")
        for r in new_rows:
            print(f"  {r}")
        print("\n[dry-run] would update README Recently added block.")
        return 0

    changelog_path.write_text(updated_changelog, encoding="utf-8")
    readme_path.write_text(updated_readme, encoding="utf-8")
    print(
        f"[scan] wrote {len(new_rows)} draft row(s) to CHANGELOG.md "
        f"and refreshed README top 3."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
