#!/usr/bin/env python3
"""Optional free-tier Gemini draft assistant. Drafts NEVER auto-publish.

Requires a privately configured GEMINI_API_KEY for an explicitly unbilled,
free-tier Google AI Studio project. No key is stored in the repository.
The generated text is a pending editorial draft, never a verified news report.
"""
from __future__ import annotations
import datetime as dt
import json
import os
import pathlib
import re
import urllib.error
import urllib.request

from publish_briefs import safe_video

ROOT = pathlib.Path(__file__).resolve().parents[1]
FEED = ROOT / "data" / "source_radar.json"
DRAFTS = ROOT / "review_drafts"
MODEL = "gemini-2.5-flash-lite"
API_ROOT = "https://generativelanguage.googleapis.com/v1beta/models/"
MAX_DRAFTS_PER_DAY = 1
MAX_SOURCE_AGE_DAYS = 2

PROMPT = """You are drafting an editorial brief for an independent wrestling website.
You have ONLY verified official publisher video metadata below, not the actual video content.
Do NOT invent any match outcome, injuries, quotes, bookings, contracts, retirements,
dates, title changes, revenue, salaries, business claims, or video contents.
Do NOT suggest you watched the video. Do NOT infer a winner, result, contract or
upcoming event from a title.
Write a measured English DRAFT of 120-190 words with an informative headline, a
"What's verified" section and a "What remains unverified" section.
Only claim that the official publisher uploaded a video with this exact given title.
Explain why direct-source attribution and further checking matter, without adding
specific unverified facts. End with the given official URL and date.
The draft will be manually fact-checked before any public article is considered.
Return plain Markdown only.

SOURCE:
"""

SENSITIVE = re.compile(
    r"\b(confirmed (?:injury|death|release|contract|retirement|result)|"
    r"has (?:signed|died|retired|been released)|"
    r"salary of|\$\s*\d+|₹\s*\d+)\b",
    re.IGNORECASE,
)


def choose_source(items: list[dict], today: str) -> dict | None:
    viable = [x for x in items if safe_video(x) and x["published"][:10] <= today]
    if not viable:
        return None
    # Skip reused source IDs and only draft the most recent confirmed upload.
    for item in sorted(viable, key=lambda x: x["published"], reverse=True):
        if not (DRAFTS / (today + "-" + item["video_id"] + ".md")).exists():
            return item
    return None


def generate(key: str, source: dict) -> str:
    if not key or len(key) < 16:
        raise ValueError("No privately configured Gemini key")
    payload = {
        "contents": [{"role": "user", "parts": [{"text": PROMPT + json.dumps(source, ensure_ascii=False)}]}],
        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 600},
    }
    req = urllib.request.Request(
        API_ROOT + MODEL + ":generateContent",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "x-goog-api-key": key},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=35) as response:
        if response.status != 200:
            raise ValueError("Gemini returned a non-OK response")
        data = json.loads(response.read(300_000))
    candidates = data.get("candidates") or []
    if not candidates:
        raise ValueError("AI did not return a candidate")
    blocks = candidates[0].get("content", {}).get("parts", [])
    text = "\n".join(p["text"] for p in blocks if isinstance(p.get("text"), str)).strip()
    if not 200 <= len(text) <= 5_000 or SENSITIVE.search(text):
        raise ValueError("Draft failed basic bounds/safety checks")
    return text


def run():
    if os.environ.get("ENABLE_FREE_AI_DRAFTS", "false").lower() != "true":
        print("AI drafting disabled until free-tier credentials and authorization are configured")
        return False
    key = os.environ.get("GEMINI_API_KEY", "")
    if not key:
        print("No GEMINI_API_KEY; skipping with no API use and no cost")
        return False
    if not FEED.exists():
        print("No verified source cache; skipping")
        return False
    today = dt.datetime.now(dt.timezone.utc).date().isoformat()
    today_existing = list(DRAFTS.glob(today + "-*.md")) if DRAFTS.exists() else []
    if len(today_existing) >= MAX_DRAFTS_PER_DAY:
        print("Daily draft cap reached; no API call")
        return False
    data = json.loads(FEED.read_text(encoding="utf-8"))
    source = choose_source(data.get("entries", []), today)
    if source is None:
        print("No fresh verified source for drafting")
        return False
    published_at = dt.datetime.fromisoformat(source["published"].replace("Z", "+00:00"))
    if (dt.datetime.now(dt.timezone.utc) - published_at) > dt.timedelta(days=MAX_SOURCE_AGE_DAYS):
        print("Official upload too old for AI draft; skip")
        return False
    draft = generate(key, source)
    DRAFTS.mkdir(parents=True, exist_ok=True)
    target = DRAFTS / (today + "-" + source["video_id"] + ".md")
    header = f"""---
status: review_required
auto_publish: false
search_indexing: false
source_promotion: {source['promotion']}
source_url: {source['url']}
source_published: {source['published']}
model: {MODEL}
---
# PENDING EDITORIAL DRAFT — DO NOT PUBLISH WITHOUT FACT CHECK

"""
    target.write_text(header + draft + "\n", encoding="utf-8")
    print("Created one review-required artifact draft (no API key printed or site publication)")
    return True


if __name__ == "__main__":
    try:
        run()
    except (ValueError, urllib.error.URLError, TimeoutError, KeyError, json.JSONDecodeError) as exc:
        # Never print a request header/key or the raw exception (may contain a URL).
        print(f"AI draft skipped safely: {type(exc).__name__}")
