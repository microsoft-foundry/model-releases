#!/usr/bin/env python3
"""
scan_foundry_blog.py — Scan the Microsoft Foundry blog for new model
announcements and stage draft CHANGELOG + README updates.

Behavior:

1. Fetch the Foundry blog index page and follow "next page" links up
   to --max-pages (default 3, though paging is currently
   client-side so one page is all the site serves).
2. Extract candidate posts (URL, title, publish date).
3. Filter to plausible model announcements (title heuristic: mentions
   a model family, "introducing", "available", "now in Foundry", etc).
4. Diff against blog URLs already referenced in CHANGELOG.md.
5. For each new post, add a draft row to CHANGELOG.md under its
   `## <Month> <Year>` heading (creating the heading and table header
   if the month is new), with the Date linking to the blog post.
   Publisher / Model / Capabilities cells are filled with
   `_review_` / `_—_` placeholders so the maintainer knows what to
   complete before merging.
6. Regenerate the README `<!-- BEGIN:RECENTLY-ADDED -->` block from
   the top 3 CHANGELOG rows.
7. Print a short summary to stdout so the workflow can surface it in
   the PR body.

The script uses only Python's stdlib. No API keys.

Design notes:

- The blog listing HTML shape may drift; parsing is intentionally
  forgiving. When a field can't be extracted we fall back to
  `_review_` and let the maintainer fix it in the PR.
- The script never edits existing CHANGELOG rows — it only adds.
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

SITE_ROOT = "https://techcommunity.microsoft.com"

# Tech Community reorganized blogs under /category/<topic>/blog/<name>.
# The old /blog/azure-ai-foundry-blog/ index now 404s.
BLOG_INDEX = f"{SITE_ROOT}/category/ai/blog/azure-ai-foundry-blog"

# Individual posts keep their canonical /blog/... path:
#   https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/<slug>/<numeric-id>
# The index links to them with *relative* hrefs, so the origin is
# optional here and resolved against SITE_ROOT.
POST_URL_RE = re.compile(
    r"(?:https://techcommunity\.microsoft\.com)?"
    r"/blog/azure-ai-foundry-blog/([a-z0-9\-]+)/(\d+)",
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
        url = urllib.parse.urljoin(SITE_ROOT, m.group(0))
        # Strip query/fragment defensively.
        p = urllib.parse.urlsplit(url)
        url = urllib.parse.urlunsplit(
            (p.scheme, p.netloc, p.path, "", "")
        )
        if url not in seen:
            seen[url] = None
    return list(seen)


def _strip_site_suffix(title: str) -> str:
    """Drop the trailing " | Microsoft Community Hub" site branding.

    og:title carries it, and it would otherwise land in the drafted
    CHANGELOG row.
    """
    return re.sub(
        r"\s*[|\-–]\s*Microsoft Community Hub\s*$", "", title.strip(),
        flags=re.IGNORECASE,
    ).strip()


def _parse_date(value: str) -> date | None:
    """Parse the date formats the community has used.

    JSON-LD here carries a US-locale string ("8/5/2026, 6:00:00 PM"),
    not ISO, so `fromisoformat` alone silently yields no date and the
    drafted row gets a YYYY-MM-DD placeholder.
    """
    value = value.strip()
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    except ValueError:
        pass
    m = re.match(r"(\d{1,2})/(\d{1,2})/(\d{4})", value)
    if m:
        month, day, year = (int(g) for g in m.groups())
        try:
            return date(year, month, day)
        except ValueError:
            return None
    return None


def extract_title(post_html: str, fallback: str = "") -> str:
    # <meta property="og:title" content="..."> is the most reliable.
    m = re.search(
        r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)["\']',
        post_html,
        re.IGNORECASE,
    )
    if m:
        return _strip_site_suffix(html.unescape(m.group(1)))
    m = re.search(
        r"<title[^>]*>(.*?)</title>", post_html, re.IGNORECASE | re.DOTALL
    )
    if m:
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
                    parsed = _parse_date(v)
                    if parsed:
                        return parsed
    # Fallback: <meta property="article:published_time" ...>
    m = re.search(
        r'<meta[^>]+property=["\']article:published_time["\'][^>]+'
        r'content=["\']([^"\']+)["\']',
        post_html,
        re.IGNORECASE,
    )
    if m:
        return _parse_date(m.group(1))
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
        new = [u for u in extract_post_urls(page_html) if u not in urls]
        urls.extend(new)
        # Paging is client-side now: ?page=2 serves the same posts as
        # page 1. Stop as soon as a page adds nothing rather than
        # refetching the first page max_pages times. If server-side
        # paging returns, this loop picks it back up automatically.
        if not new:
            break

    if not urls:
        # Discovery breaking silently is how this script rotted before:
        # the index moved, every fetch 404'd, and a run that found
        # nothing looked exactly like a quiet week. Fail loudly instead.
        raise SystemExit(
            f"[scan] no post links found at {BLOG_INDEX}\n"
            "  The blog index has probably moved or changed markup "
            "again. Check BLOG_INDEX and POST_URL_RE."
        )

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

# Hardcoded rather than strftime("%B") so month headings don't change
# with the runner's locale.
MONTH_NAMES = (
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
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
    # Draft row — maintainer completes Publisher / Model /
    # Capabilities / Model card before merging.
    return (
        f"| [{dstr}]({post.url}) | _review_ | _review_ (blog title: "
        f"\"{post.title}\") | _review_ |"
    )


MONTH_HEADING_RE = re.compile(r"^## \w+ \d{4}\s*$")
TABLE_HEADER = "| Date | Publisher | Model | Capabilities |"
TABLE_SEP = "|---|---|---|---|"


def month_heading(date_str: str) -> str:
    """`2026-07-29` -> `## July 2026`."""
    d = date.fromisoformat(date_str)
    return f"## {MONTH_NAMES[d.month - 1]} {d.year}"


def insert_rows_into_changelog(
    changelog_text: str, new_rows: list[tuple[str, str]]
) -> str:
    """Insert new rows under their month's table, newest first.

    `new_rows` is a list of `(date_str, row_text)`. A month heading
    and table header are created if the month isn't present yet.
    """
    if not new_rows:
        return changelog_text
    trailing_nl = changelog_text.endswith("\n")
    lines = changelog_text.splitlines()

    # Oldest first, so repeated top-insertion leaves the newest row on
    # top.
    for date_str, row in sorted(new_rows, key=lambda e: e[0]):
        heading = month_heading(date_str)
        try:
            at = lines.index(heading)
        except ValueError:
            # New month — goes above the newest existing month heading,
            # or at the end if there are none yet.
            first = next(
                (i for i, ln in enumerate(lines)
                 if MONTH_HEADING_RE.match(ln)),
                len(lines),
            )
            lines[first:first] = [
                heading, "", TABLE_HEADER, TABLE_SEP, row, "",
            ]
            continue
        # Existing month — insert directly under that table's separator.
        for i in range(at, len(lines)):
            if lines[i].startswith("| Date |") and re.match(
                r"^\|\s*---", lines[i + 1] if i + 1 < len(lines) else ""
            ):
                lines[i + 2:i + 2] = [row]
                break
        else:
            raise RuntimeError(
                f"CHANGELOG.md: no table found under '{heading}'"
            )
    return "\n".join(lines) + ("\n" if trailing_nl else "")


README_MARK_BEGIN = "<!-- BEGIN:RECENTLY-ADDED -->"
README_MARK_END = "<!-- END:RECENTLY-ADDED -->"


def parse_changelog_top(
    changelog_text: str, n: int
) -> list[dict[str, str]]:
    """Extract the first n data rows, across all month tables."""
    text = re.sub(r"<!--.*?-->", "", changelog_text, flags=re.DOTALL)
    rows: list[list[str]] = []
    in_table = False
    for line in text.splitlines():
        if line.startswith("| Date |"):
            in_table = True
            continue
        if not in_table:
            continue
        if re.match(r"^\|\s*---", line):
            continue
        if not line.strip().startswith("|"):
            # End of this month's table; the next one may follow.
            in_table = False
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 4:
            rows.append(cells)
        if len(rows) >= n:
            break
    keys = [
        "date", "publisher", "model", "capabilities",
    ]
    return [dict(zip(keys, r)) for r in rows]


def render_readme_block(rows: list[dict[str, str]]) -> str:
    header = (
        "| Model | Release date | Capabilities |\n"
        "| --- | --- | --- |"
    )
    body_lines: list[str] = []
    for r in rows:
        # README shows a plain bold model name; the CHANGELOG cell may
        # carry link markup and an availability note, so strip both
        # rather than nesting a link inside bold.
        model = re.sub(
            r"\s*_\([^)]*\)_\s*$", "", r.get("model", "_review_").strip()
        )
        m = re.match(r"\[([^\]]+)\]", model)
        if m:
            model = m.group(1)
        capabilities = r.get("capabilities", "").strip() or "_review_"
        body_lines.append(
            f"| **{model}** | {r.get('date', '_review_')} "
            f"| {capabilities} |"
        )
    # No caption here — the "See the full CHANGELOG" line lives outside
    # the markers in README.md so regeneration doesn't duplicate it.
    return (
        f"{README_MARK_BEGIN}\n"
        f"{header}\n"
        + "\n".join(body_lines)
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

    new_rows = [
        (
            p.published.isoformat() if p.published
            else date.today().isoformat(),
            draft_row(p),
        )
        for p in candidates
    ]
    updated_changelog = insert_rows_into_changelog(
        changelog_text, new_rows
    )
    top3 = parse_changelog_top(updated_changelog, 3)
    updated_readme = update_readme_recent(
        readme_text, render_readme_block(top3)
    )

    if args.dry_run:
        print("\n[dry-run] would add these CHANGELOG rows:")
        for _, r in new_rows:
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
