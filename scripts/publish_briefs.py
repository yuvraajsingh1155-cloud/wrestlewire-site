#!/usr/bin/env python3
"""Publish only verifiable source *metadata* as short, attributed briefs.

No AI-generated speculation, no image copying, no paid API or external packages.
Automated posts describe a video upload, NOT the factual claims inside it.
"""
from __future__ import annotations

import datetime as dt
import html
import json
import pathlib
import re
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
FEED = ROOT / "data" / "source_radar.json"
SITE = ROOT / "index.html"
SITEMAP = ROOT / "sitemap.xml"
BASE = "https://wrestlewire-site.yuvraajsingh1155.workers.dev"
START = "<!-- WRESTLEWIRE_AUTO_BRIEFS_START -->"
END = "<!-- WRESTLEWIRE_AUTO_BRIEFS_END -->"
MAX_NEW_PER_RUN = 2
MAX_NEW_PER_DAY = 2
MAX_CARDS = 12
MAX_NEWS_PAGES = 120


def safe_video(item: object) -> bool:
    if not isinstance(item, dict):
        return False
    video_id = item.get("video_id", "")
    url = item.get("url", "")
    title = item.get("title", "")
    pub = item.get("published", "")
    if item.get("promotion") not in {"WWE", "AEW"}:
        return False
    if not isinstance(video_id, str) or re.fullmatch(r"[a-zA-Z0-9_-]{11}", video_id) is None:
        return False
    if url != "https://www.youtube.com/watch?v=" + video_id:
        return False
    if not isinstance(title, str) or not (16 <= len(title) <= 180):
        return False
    if not isinstance(pub, str):
        return False
    try:
        stamp = dt.datetime.fromisoformat(pub.replace("Z", "+00:00"))
        if not stamp.tzinfo:
            return False
        age = dt.datetime.now(dt.timezone.utc) - stamp.astimezone(dt.timezone.utc)
        return dt.timedelta(0) <= age <= dt.timedelta(days=4)
    except ValueError:
        return False


def clean_heading(s: str) -> str:
    return " ".join(s.split())[:150]


def page(item: dict) -> str:
    name, title, url, vid, published = (
        html.escape(item["promotion"]),
        html.escape(clean_heading(item["title"])),
        html.escape(item["url"], quote=True),
        item["video_id"],
        item["published"][:10],
    )
    canonical = f"{BASE}/news/{vid}/"
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,follow">
<title>{title} | {name} Official Source | WrestleWire</title>
<meta name="description" content="Verified {name} official video upload, {published}. Publisher attribution, source link and editorial context.">
<link rel="canonical" href="{canonical}">
<style>*{{box-sizing:border-box}}body{{margin:0;background:#0e0f14;color:#f6f1f2;font:17px/1.8 system-ui,Arial,sans-serif}}
header{{padding:18px;background:#181117;border-bottom:3px solid #ef2841}}header a{{font-size:24px;font-weight:1000;letter-spacing:-.045em;color:#fff;text-decoration:none}}
header span{{color:#ef2841}}main{{max-width:830px;margin:auto;padding:46px 23px 75px}}
.kicker{{color:#ff92a2;font-size:12px;letter-spacing:.12em;font-weight:900;text-transform:uppercase}}
h1{{font:1000 clamp(36px,6vw,62px)/1.06 Impact,"Arial Narrow",Arial,sans-serif;text-transform:uppercase;margin:16px 0 24px}}
p{{color:#ded3d8}}.notice{{padding:17px;background:#24191f;border-left:4px solid #ef2841}}
a{{color:#ff879b}}.button{{display:inline-block;padding:12px 18px;background:#ed2842;color:#fff;text-decoration:none;font-weight:900;margin-top:22px}}
footer{{padding:30px;text-align:center;border-top:1px solid #45323a;color:#bfb2b8;font-size:12px}}</style>
</head><body><header><a href="/">WRESTLE<span>WIRE</span></a></header><main>
<div class="kicker">{name} / VERIFIED PUBLISHER LINK / {published}</div>
<h1>{title}</h1>
<p><strong>{name}'s official YouTube feed published an item titled “{title}” on {published}.</strong> This update identifies a publisher upload and links to the original source, so readers can check the material directly.</p>
<p>WrestleWire has not independently confirmed any results, injuries, contract changes, departures, backstage claims or other events that may be discussed inside this video. The headline is the publisher's title, not independent reporting.</p>
<p class="notice"><strong>Source notice:</strong> This is an automated, factual source brief based on official video metadata. It is not an AI-written investigative report, verified transcript or match-result article.</p>
<p>For a fuller report, we would cross-check the underlying broadcast, published match results and any relevant primary statements before making further claims.</p>
<a class="button" href="{url}" target="_blank" rel="noopener noreferrer nofollow">WATCH ORIGINAL {name} SOURCE ↗</a>
<p><a href="/#official-sources">← Back to the official source radar</a></p>
</main><footer>Independent wrestling coverage. Not affiliated with WWE, AEW or any performer.</footer><script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon='{{"token":"07d17fc48e50449187f9739232103de4"}}'></script></body></html>"""


def content_cards(items: list[dict]) -> str:
    out = []
    for v in items[:MAX_CARDS]:
        n = html.escape(v["promotion"])
        t = html.escape(clean_heading(v["title"]))
        link = f"/news/{v['video_id']}/"
        day = html.escape(v["published"][:10])
        out.append(
            '<a class="auto-brief-card" href="' + link + '" aria-label="Read source brief: ' + t + '">'
            f'<span class="auto-brief-tag">{n} · {day} · OFFICIAL SOURCE</span>'
            f'<strong>{t}</strong>'
            '<span class="auto-brief-open">Read attributed source brief ↗</span>'
            '</a>'
        )
    if not out:
        return '<p class="radar-empty">Verified source briefs will appear after a successful scheduled update.</p>'
    return "\n".join(out)


def all_items() -> list[dict]:
    if not FEED.exists():
        return []
    data = json.loads(FEED.read_text(encoding="utf-8"))
    found = data.get("entries", [])
    return [x for x in found if safe_video(x)]


def current_pages() -> list[pathlib.Path]:
    return sorted((ROOT / "news").glob("*/index.html")) if (ROOT / "news").exists() else []


def refresh() -> int:
    entries = all_items()
    pages = current_pages()
    known = {p.parent.name for p in pages}
    old_ids = set(known)
    today = dt.datetime.now(dt.timezone.utc).date().isoformat()
    published_today = sum(today in p.read_text(encoding="utf-8")[:2000] for p in pages)
    created_this_run = 0
    for item in entries:
        if len(known) >= MAX_NEWS_PAGES:
            break
        if created_this_run >= MAX_NEW_PER_RUN or published_today + created_this_run >= MAX_NEW_PER_DAY:
            break
        if item["video_id"] in known:
            continue
        vid = item["video_id"]
        file = ROOT / "news" / vid / "index.html"
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(page(item), encoding="utf-8")
        known.add(vid)
        created_this_run += 1

    pages = current_pages()
    by_id = {item["video_id"]: item for item in entries}
    # Display only existing verified source pages in most-recent-first order.
    shown = [x for x in entries if (ROOT / "news" / x["video_id"] / "index.html").exists()]
    if SITE.exists():
        original = SITE.read_text(encoding="utf-8")
        if original.count(START) != 1 or original.count(END) != 1:
            raise ValueError("Source brief insertion markers missing or duplicate")
        before, rest = original.split(START, 1)
        _, after = rest.split(END, 1)
        changed = before + START + "\n" + content_cards(shown) + "\n" + END + after
        if changed != original:
            SITE.write_text(changed, encoding="utf-8")

    # Source metadata briefs are deliberately not indexed: substantial verified
    # articles already live in the public sitemap. Prevent scaled-content SEO abuse.
    print(f"Official source briefs: {len(pages)} published; {len(shown)} recent cards")
    return len(pages)


if __name__ == "__main__":
    refresh()
