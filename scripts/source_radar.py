#!/usr/bin/env python3
"""WrestleWire source radar: official WWE + AEW YouTube Atom metadata only.

This fetches official video titles + dates + canonical video links. It never
claims medical, financial or private-contract facts or reproduces video text.
No API keys, paid services or non-standard dependencies required.
"""
from __future__ import annotations

import datetime as dt
import html
import json
import pathlib
import re
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from urllib.parse import urlsplit

ROOT = pathlib.Path(__file__).resolve().parents[1]
SITE = ROOT / "index.html"
CACHE = ROOT / "data" / "source_radar.json"
START = "<!-- WRESTLEWIRE_SOURCE_RADAR_START -->"
END = "<!-- WRESTLEWIRE_SOURCE_RADAR_END -->"
ATOM = "{http://www.w3.org/2005/Atom}"
YT = "{http://www.youtube.com/xml/schemas/2015}"
CHANNELS = {
    "WWE": "UCJ5v_MCY6GNUBTO8-D3XoAg",
    "AEW": "UCFN4JkGP_bVhAdBsoV9xftA",
}
MAX_ENTRIES_PER_PROMOTION = 8
MAX_TOTAL = 14


def extract_feed(xml: bytes, promotion: str, channel_id: str) -> list[dict]:
    if len(xml) > 1_500_000:
        raise ValueError("Feed exceeds size limit")
    root = ET.fromstring(xml)
    if root.tag != ATOM + "feed":
        raise ValueError("Unexpected feed format")
    source_id = root.findtext(YT + "channelId")
    if source_id and source_id not in (channel_id, channel_id.removeprefix("UC")):
        raise ValueError(f"Channel mismatch: requested={channel_id}, returned={source_id}")
    items = []
    for entry in root.findall(ATOM + "entry"):
        item_channel = entry.findtext(YT + "channelId")
        if item_channel and item_channel not in (channel_id, channel_id.removeprefix("UC")):
            continue
        video_id = (entry.findtext(YT + "videoId") or "").strip()
        if not re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
            continue
        title = " ".join((entry.findtext(ATOM + "title") or "").split())
        if not 12 <= len(title) <= 180:
            continue
        published = (entry.findtext(ATOM + "published") or "").strip()
        try:
            stamp = dt.datetime.fromisoformat(published.replace("Z", "+00:00"))
            if stamp.tzinfo is None:
                stamp = stamp.replace(tzinfo=dt.timezone.utc)
            stamp = stamp.astimezone(dt.timezone.utc)
        except ValueError:
            continue
        # Ignore garbage data and future-dated items (allow small clock skew).
        if stamp > dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=2):
            continue
        items.append({
            "promotion": promotion,
            "video_id": video_id,
            "title": title,
            "published": stamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "url": "https://www.youtube.com/watch?v=" + video_id,
        })
    # Publishing order can differ from chronology.
    return sorted(items, key=lambda v: v["published"], reverse=True)[:MAX_ENTRIES_PER_PROMOTION]


def get_feed(promotion: str, channel_id: str) -> list[dict]:
    url = "https://www.youtube.com/feeds/videos.xml?channel_id=" + channel_id
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "WrestleWire-Newsroom/1.0 (+https://github.com/yuvraajsingh1155-cloud/wrestlewire-site)",
            "Accept": "application/atom+xml, application/xml;q=0.9",
        },
    )
    with urllib.request.urlopen(request, timeout=14) as response:
        return extract_feed(response.read(1_500_001), promotion, channel_id)


def valid_cached(v: dict) -> bool:
    return (
        isinstance(v, dict)
        and v.get("promotion") in CHANNELS
        and isinstance(v.get("title"), str)
        and re.fullmatch(r"[A-Za-z0-9_-]{11}", str(v.get("video_id", ""))) is not None
        and v.get("url") == "https://www.youtube.com/watch?v=" + v.get("video_id", "")
        and isinstance(v.get("published"), str)
    )


def existing() -> list[dict]:
    if not CACHE.exists():
        return []
    try:
        data = json.loads(CACHE.read_text(encoding="utf-8"))
        return [x for x in data.get("entries", []) if valid_cached(x)][:MAX_TOTAL]
    except (ValueError, OSError, AttributeError, TypeError):
        return []


def render(entries: list[dict]) -> str:
    if not entries:
        cards = '<p class="radar-empty">Official feeds are being prepared. See the linked official WWE and AEW channels for verified updates.</p>'
    else:
        chunks = []
        for item in entries:
            promotion = html.escape(item["promotion"])
            title = html.escape(item["title"], quote=True)
            href = html.escape(item["url"], quote=True)
            day = html.escape(item["published"][:10])
            chunks.append(
                f'<a class="radar-card" href="{href}" target="_blank" rel="noopener noreferrer nofollow" aria-label="Open official {promotion} source: {title}">'
                f'<div class="radar-meta"><span>{promotion} OFFICIAL VIDEO</span> <time datetime="{day}">{day}</time></div>'
                f'<h3>{title}</h3>'
                '<p>New upload listed by the promotion’s official YouTube channel. '
                'This is a source link, not an independently verified news article.</p>'
                '<span class="radar-open">WATCH OFFICIAL SOURCE ↗</span>'
                '</a>'
            )
        cards = "\n".join(chunks)
    return (
        '<section class="auto-radar" id="official-sources" aria-labelledby="radar-heading">'
        '<div class="eyebrow">✦ DIRECT FROM THE PROMOTIONS</div>'
        '<h2 id="radar-heading">OFFICIAL <span>SOURCE RADAR.</span></h2>'
        '<p class="radar-intro">Automatically updated links from WWE and AEW official video feeds. '
        'Links and video titles are attributed to their publishers; they are not original WrestleWire reporting.</p>'
        '<div class="radar-grid">' + cards + '</div>'
        '<p class="radar-disclaimer">Source Radar refresh is best-effort and depends on official feed availability. '
        'Video uploads and on-screen storylines do not independently confirm rumors, injuries or salary figures.</p>'
        '</section>'
    )


def update():
    past = existing()
    by_promotion: dict[str, list[dict]] = {
        name: [x for x in past if x["promotion"] == name] for name in CHANNELS
    }
    succeeded = 0
    for promotion, channel_id in CHANNELS.items():
        try:
            fresh = get_feed(promotion, channel_id)
            if not fresh:
                print(f"{promotion}: feed returned no valid items, retaining cache")
                continue
            by_promotion[promotion] = fresh
            succeeded += 1
            print(f"{promotion}: received {len(fresh)} verified channel entries")
        except (urllib.error.URLError, TimeoutError, ValueError, ET.ParseError, OSError) as exc:
            print(f"{promotion}: fetch failed ({exc}); retaining previous entries")
    merged = {}
    for items in by_promotion.values():
        for item in items:
            if valid_cached(item):
                merged[item["video_id"]] = item
    entries = sorted(merged.values(), key=lambda v: v["published"], reverse=True)[:MAX_TOTAL]
    # Never erase a working feed on transient network failure.
    if succeeded == 0 and not past:
        print("No verified sources available; leaving site unchanged")
        return False
    if entries != past:
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        CACHE.write_text(json.dumps({"entries": entries}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if not SITE.exists():
        raise FileNotFoundError(SITE)
    page = SITE.read_text(encoding="utf-8")
    if page.count(START) != 1 or page.count(END) != 1:
        raise ValueError("Missing or duplicate protected Source Radar markers in index.html")
    a = page.index(START) + len(START)
    b = page.index(END)
    if a >= b:
        raise ValueError("Source Radar markers out of order")
    generated = "\n" + render(entries) + "\n"
    revised = page[:a] + generated + page[b:]
    if revised != page:
        SITE.write_text(revised, encoding="utf-8")
        print(f"Website refreshed with {len(entries)} official source links")
        return True
    print("No source changes; website unchanged")
    return False


if __name__ == "__main__":
    update()
