#!/usr/bin/env python3
"""Offline publication integrity checks. No external requests or paid services."""
from pathlib import Path
from urllib.parse import urlparse, unquote
import json, re, sys, xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://wrestlewire-site.yuvraajsingh1155.workers.dev"
errors = []
def fail(msg): errors.append(msg)
def slug(name):
    import unicodedata
    name = unicodedata.normalize("NFKD", name.lower())
    name = "".join(c for c in name if not unicodedata.combining(c))
    return re.sub(r"^-|-$", "", re.sub(r"[^a-z0-9]+", "-", name))
def check_page(rel, kind):
    path = ROOT / rel
    if not path.is_file(): fail(f"Missing {kind}: {rel}"); return
    content = path.read_text(encoding="utf-8")
    if not re.search(r"<title>[^<]+</title>", content, re.I): fail(f"No title: {rel}")
    if not re.search(r'<meta name="description" content="[^"]+', content, re.I): fail(f"No description: {rel}")
    if not re.search(r'<link rel="canonical" href="https?://[^"]+', content, re.I): fail(f"No canonical: {rel}")
    expected = BASE + "/" + str(rel).removesuffix("/index.html").removesuffix("index.html").strip("/") + "/"
    match = re.search(r'<link rel="canonical" href="([^"]+)"', content, re.I)
    if match and match.group(1) != expected: fail(f"Wrong canonical: {rel}: {match.group(1)}")
    for link in re.findall(r'(?:src|href)="/([^"#?]+)', content):
        if link.startswith(("api/", "cdn-cgi/")): continue
        target = ROOT / unquote(link)
        if not target.exists() and not (target / "index.html").exists(): fail(f"Broken local link: {rel} -> /{link}")

original = json.loads((ROOT / "data/wrestler-editorial-profiles.json").read_text(encoding="utf-8"))
expanded = json.loads((ROOT / "data/wrestlers-expanded.json").read_text(encoding="utf-8"))
roster = original + expanded
names = [w["n"].casefold() for w in roster]
if len(names) != len(set(names)): fail("Duplicate wrestler names")
if len(roster) != 349: fail(f"Expected 349 wrestler entries, found {len(roster)}")
for w in roster: check_page(Path("wrestlers") / slug(w["n"]) / "index.html", "wrestler profile")
features = json.loads((ROOT / "data/features-100.json").read_text(encoding="utf-8"))
if len(features) != 100: fail(f"Expected 100 feature records, found {len(features)}")
for f in features:
    key = f["slug"]
    rel = Path("articles") / key / "index.html"
    check_page(rel, "feature article")
    cover = ROOT / "assets/features" / (key + ".svg")
    if not cover.is_file(): fail(f"Missing feature cover: {key}")
    elif ("/assets/features/" + key + ".svg") not in (ROOT / rel).read_text(encoding="utf-8"): fail(f"Cover not referenced in article: {key}")
    if 'const q="' in (ROOT / rel).read_text(encoding="utf-8"): fail(f"Legacy Commons image override remains: {key}")
article_dirs = sorted((ROOT / "articles").glob("*/index.html"))
for p in article_dirs: check_page(p.relative_to(ROOT), "article")
for p in article_dirs:
    key = p.parent.name
    if not (ROOT / "assets/features" / (key + ".svg")).exists(): fail(f"Missing cover for article: {key}")
    elif ("/assets/features/" + key + ".svg") not in p.read_text(encoding="utf-8"): fail(f"Article does not embed cover: {key}")
tree = ET.parse(ROOT / "sitemap.xml")
urls = [x.text for x in tree.findall(".//{*}loc")]
if len(urls) != len(set(urls)): fail("Duplicate sitemap URLs")
for p in article_dirs + list((ROOT / "wrestlers").glob("*/index.html")):
    if p.parent.name == "profile": continue
    link = BASE + "/" + p.relative_to(ROOT).as_posix().removesuffix("index.html")
    if link not in urls: fail(f"Missing sitemap URL: {link}")
for url in urls:
    if not url.startswith(BASE + "/"): fail(f"Unexpected sitemap host: {url}"); continue
    rel = url.removeprefix(BASE + "/").strip("/")
    if not (ROOT / rel / "index.html").exists() and not (ROOT / rel).is_file() and not (rel == "" and (ROOT / "index.html").is_file()): fail(f"Dead sitemap target: {url}")
print(f"Checked {len(roster)} wrestlers, {len(article_dirs)} articles, {len(features)} feature covers, {len(urls)} sitemap URLs")
if errors:
    for err in errors[:100]: print("ERROR:", err)
    print(f"FAIL: {len(errors)} errors")
    sys.exit(1)
print("PASS: publication integrity checks")
