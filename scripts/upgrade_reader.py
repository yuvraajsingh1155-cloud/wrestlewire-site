#!/usr/bin/env python3
"""Upgrade existing static articles and wrestler pages in place.

Conservative, idempotent migration: retains original URLs, prose, sources and
links; removes unrelated artwork and unsafe unreviewed Wikipedia thumbnail
lookups; adds accessible reading tools and only registered licensed photos.
No AI inference, network calls, secrets, new dependencies or paid services.
"""
from __future__ import annotations

import html
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RIGHTS = ROOT / "data" / "photo-rights.json"
MAX_FILES = 650

RIGHTS_BY_ID = {
    "rey-mysterio": "rey-punk-2011",
    "hangman-adam-page": "aew-page-2019",
    "ricochet": "ricochet-aerial-2014",
    "the-great-khali": "great-khali-2011",
    "sting": "sting-aew-2023",
}

PHOTO_FEATURES = {
    "feature-073-rey-mysterio": "rey-punk-2011",
    "feature-077-hangman-adam-page": "aew-page-2019",
    "feature-078-will-ospreay": None,
    "feature-071-the-great-khali": "great-khali-2011",
    "feature-080-darby-allin": None,
    "great-khali-vs-undertaker-judgment-day-2006": "great-khali-2011",
    "aew-vs-wwe-top-10-shows-attendance-crowd-energy": "aew-all-in-2023",
    "feature-076-jon-moxley": None,
}
# Explicit subject matching only. Do not infer photo identity from resemblance.
PHOTO_FEATURES = {k: v for k, v in PHOTO_FEATURES.items() if v}

BRANDED = "WrestleWire original typography-only graphic, not a photograph or event depiction."

def escape(s: str) -> str:
    return html.escape(s, quote=True)

def human_name(s: str) -> str:
    return s.replace("-", " ").title()

def license_photo(photo: dict, *, title: str, portrait: bool = False) -> str:
    if not photo.get("verified") or not photo.get("commercial_reuse") or not photo.get("modification_permitted"):
        raise ValueError("Unverified or non-reusable image cannot be used")
    photo_url = photo["url"]
    credit = photo["credit"]
    event = photo["event"]
    desc = f"Archival photograph: {event}; {title}"
    inner = (
        f'<img class="ww-licensed-photo" loading="lazy" src="{escape(photo_url)}" alt="{escape(desc)}">'
        f'<figcaption class="ww-license-caption">{escape(credit)}. '
        f'<a href="{escape(photo["file_page"])}" target="_blank" rel="noopener noreferrer">Photo file &amp; credits</a> · '
        f'<a href="{escape(photo["license_url"])}" target="_blank" rel="noopener noreferrer">Reuse license</a>. '
        'Archive photo, not a current match image.</figcaption>'
    )
    return f'<figure class="ww-license-figure">{inner}</figure>'

def branded_cover(title: str, sublabel: str) -> str:
    return (
        '<div class="ww-branded-cover" role="img" aria-label="Original typography nameplate, not a photograph">'
        f'<small>{escape(sublabel)}</small><strong>{escape(title)}</strong></div>'
    )

def reading_toolbar(kind: str, path: str) -> str:
    return (
        '<div id="ww-reading-progress" role="presentation"></div>'
        '<div class="ww-article-tools" role="toolbar" aria-label="Reader actions">'
        '<a href="/">WrestleWire</a>'
        f'<a href="/{"wrestlers" if kind == "wrestler" else "latest"}/">← {"All wrestlers" if kind == "wrestler" else "Articles"}</a>'
        '<span class="ww-separator" aria-hidden="true"></span>'
        '<button type="button" data-ww-reader-save aria-pressed="false">☆ Save</button>'
        '<button type="button" data-ww-reader-share>Share</button>'
        '<button type="button" data-ww-reader-theme>Theme</button>'
        '<a href="/search/">⌕ Search</a>'
        '<a href="/media-credits/">Photo rights</a>'
        '</div>'
    )

def old_photo_script(html_text: str) -> str:
    # Remove only the legacy unsourced, unreviewed thumbnail lookup scripts.
    return re.sub(
        r'<script>\(async\(\)=>\{try\{const u="https://en\.wikipedia\.org/w/api\.php\?action=query[\s\S]*?</script>',
        "",
        html_text,
        flags=re.I,
    )

def replace_figure(old: str, new_inner: str, tag_class: str = "hero", ident: str = "photo") -> str:
    pattern = re.compile(r'<figure\b(?=[^>]*\bclass="' + re.escape(tag_class)
                         + r'")(?=[^>]*\bid="' + re.escape(ident)
                         + r'")[^>]*>[\s\S]*?</figure>', re.I)
    return pattern.sub(lambda _: f'<figure class="{tag_class}" id="{ident}">{new_inner}</figure>', old, count=1)

def upgrade_article(content: str, slug: str, photos: dict[str, dict]) -> str:
    title_match = re.search(r"<h1\b[^>]*>([\s\S]*?)</h1>", content, re.I)
    plain_title = re.sub(r"<[^>]+>", "", title_match.group(1)).strip() if title_match else human_name(slug)
    plain_title = html.unescape(plain_title)[:160]
    picture = photos.get(PHOTO_FEATURES.get(slug, ""))
    media = license_photo(picture, title=plain_title) if picture else branded_cover(plain_title, "Original WrestleWire editorial cover")
    if '<figure class="hero" id="photo">' in content:
        content = replace_figure(content, media)
        if picture:
            credit = "Archival, source-linked photograph · please consult caption and photo rights"
        else:
            credit = BRANDED
        content = re.sub(r'<div class="credit" id="credit">[\s\S]*?</div>',
                         lambda _: '<div class="credit" id="credit">' + credit + '</div>',
                         content, count=1)
    # Replace branded *illustration*, not an already licensed photograph.
    content = re.sub(
        r'<figure class="editorial-art">\s*<img\b[^>]+/assets/features/[^>]+>\s*(?:<figcaption>[\s\S]*?</figcaption>)?\s*</figure>',
        lambda _: '<figure class="editorial-art">' + media + '</figure>',
        content,
        count=1,
    )
    if picture:
        content = re.sub(
            r'<meta\b[^>]*property="og:image"[^>]*>',
            '<meta property="og:image" content="' + escape(picture["url"]) + '">',
            content,
            count=1,
        )
    else:
        # An illustration is original editorial artwork, not an event photo.
        # Avoid social meta suggesting the image is an actual event depiction.
        content = re.sub(r'<meta\b[^>]*property="og:image"[^>]*>', "", content, count=1)
    return content

def upgrade_wrestler(content: str, slug: str, photos: dict[str, dict]) -> str:
    title_match = re.search(r"<h1\b[^>]*>([\s\S]*?)</h1>", content, re.I)
    name = html.unescape(re.sub(r"<[^>]+>", "", title_match.group(1)).strip()) if title_match else human_name(slug)
    registered = photos.get(RIGHTS_BY_ID.get(slug, ""))
    picture = license_photo(registered, title=name, portrait=True) if registered else (
        '<div class="ww-branded-portrait" role="img" aria-label="Branded nameplate, not a wrestler photograph">'
        '<small>WrestleWire / Career Archive</small>'
        f'<strong>{escape(name)}</strong>'
        '<span>Photo not yet license-verified</span>'
        '</div>'
    )
    content = old_photo_script(content)
    # Generic directory portrait is a stylized illustration, not a portrait.
    content = re.sub(
        r'<div class="portrait">\s*<svg\b[\s\S]*?</svg>\s*</div>',
        lambda _: '<div class="portrait">' + picture + '</div>',
        content,
        count=1,
    )
    content = re.sub(
        r'<p class="note">Original illustrated name card — not a real photo or likeness\.</p>',
        lambda _: '<p class="note">License-reviewed archival photograph or original nameplate. '
        'Photographs appear only when the matching wrestler and reuse rights are verified.</p>',
        content,
        count=1,
    )
    # Explicit curated profiles formerly loaded arbitrary Wikipedia pageimages.
    content = re.sub(
        r'<figure\b[^>]*>\s*<img id="wrestler-portrait"[\s\S]*?</figure>',
        lambda _: picture,
        content,
        count=1,
    )
    return content

def add_shell(content: str, kind: str, slug: str) -> str:
    if 'id="ww-reading-progress"' in content:
        return content
    header = (
        '<link rel="stylesheet" href="/assets/ww-reader.css">'
        '<link rel="icon" href="/favicon.svg" type="image/svg+xml">'
        '<link rel="manifest" href="/manifest.webmanifest">'
        '<script>try{const p=localStorage.getItem("ww.theme")||"dark";'
        'document.documentElement.dataset.wwTheme=p==="system"?'
        '(matchMedia("(prefers-color-scheme:light)").matches?"light":"dark"):p}catch{}</script>'
    )
    content = content.replace("</head>", header + "</head>", 1)
    content = re.sub(r"<body\b[^>]*>",lambda match: match.group(0) + reading_toolbar(kind, slug),content,count=1)
    content = content.replace("</body>", '<script defer src="/assets/ww-reader.js"></script></body>', 1)
    return content

def main() -> None:
    data = json.loads(RIGHTS.read_text(encoding="utf-8"))
    photos = {p["id"]: p for p in data["photos"]}
    files = [(p, "article") for p in (ROOT / "articles").glob("*/index.html")]
    files.extend((p, "wrestler") for p in (ROOT / "wrestlers").glob("*/index.html"))
    if len(files) > MAX_FILES:
        raise ValueError(f"Refusing unexpected mass edit: {len(files)} pages")
    counts = {"article": 0, "wrestler": 0, "unchanged": 0}
    for path, kind in sorted(files):
        slug = path.parent.name
        old = path.read_text(encoding="utf-8")
        if kind == "article":
            updated = upgrade_article(old, slug, photos)
        else:
            updated = upgrade_wrestler(old, slug, photos)
        updated = add_shell(updated, kind, slug)
        if updated != old:
            path.write_text(updated, encoding="utf-8")
            counts[kind] += 1
        else:
            counts["unchanged"] += 1
    print(f"WrestleWire reader upgrade: {counts}; all article/profile slugs preserved")

if __name__ == "__main__":
    main()
