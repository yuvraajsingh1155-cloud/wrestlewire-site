"""Offline, zero-cost tests for safe global article and wrestler migration."""
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
import upgrade_reader as app


class ReaderMigrationSafetyTests(unittest.TestCase):
    def test_feature_illustration_becomes_original_nameplate(self):
        doc = ('<html><head></head><body><h1>How Wrestling Works</h1>'
               '<figure class="hero" id="photo"><img src="/assets/features/feature-099-match-star-ratings.svg"></figure>'
               '<div class="credit" id="credit">Old editorial artwork</div></body></html>')
        result = app.upgrade_article(doc, "feature-099-match-star-ratings", {})
        self.assertIn('ww-branded-cover', result)
        self.assertNotIn('src="/assets/features/feature-099', result)
        self.assertIn("not a photograph", result.lower())

    def test_known_matching_photo_has_author_credit(self):
        item = {"verified": True, "commercial_reuse": True, "modification_permitted": True,
                "url": "https://commons.wikimedia.org/example.jpg", "credit": "Author, CC BY",
                "file_page": "https://commons.wikimedia.org/wiki/File:Example.jpg",
                "license_url": "https://creativecommons.org/licenses/by/4.0/", "event": "2011 event"}
        doc = ('<html><body><h1>Rey Mysterio</h1><figure class="hero" id="photo">'
               '<img src="/assets/features/feature-073-rey-mysterio.svg"></figure></body></html>')
        result = app.upgrade_article(doc, "feature-073-rey-mysterio", {"rey-punk-2011": item})
        self.assertIn("Author, CC BY", result)
        self.assertIn("license", result.lower())
        self.assertNotIn("<figure class=\"hero\" id=\"photo\"><figure", result)

    def test_unlicensed_photo_is_never_published(self):
        bad = {"verified": False, "commercial_reuse": True, "modification_permitted": True,
               "url": "https://example.com/unauthorized", "credit": "none", "file_page": "https://example.com",
               "license_url": "https://example.com", "event": "no"}
        with self.assertRaises(ValueError):
            app.license_photo(bad, title="Unknown")

    def test_wrestler_initials_replaced_not_fake_portrait(self):
        html = ('<html><body><h1>AJ Styles</h1><div class="portrait"><svg>'
                '<circle r="3"/></svg></div></body></html>')
        result = app.upgrade_wrestler(html, "aj-styles", {})
        self.assertIn('ww-branded-portrait', result)
        self.assertIn("AJ Styles", result)
        self.assertNotIn("<svg>", result)

    def test_unreviewed_wikipedia_thumbnail_removed(self):
        sample = ('<body><h1>Someone</h1><script>(async()=>{try{const u="https://en.wikipedia.org/w/api.php?action=query"'
                  ';fetch(u)}catch(e){}})();</script><p>Preserve profile text</p></body>')
        self.assertNotIn("w/api.php", app.upgrade_wrestler(sample, "someone", {}))
        self.assertIn("Preserve profile text", app.upgrade_wrestler(sample, "someone", {}))

    def test_reader_controls_and_scripts_added_once(self):
        doc = "<html><head></head><body><main>Article body</main></body></html>"
        first = app.add_shell(doc, "article", "test-article")
        second = app.add_shell(first, "article", "test-article")
        self.assertEqual(first, second)
        self.assertEqual(first.count("ww-reading-progress"), 1)
        self.assertIn('data-ww-reader-share', first)
        self.assertIn('src="/assets/ww-reader.js"', first)

    def test_existing_content_and_sources_remain(self):
        doc = ('<html><head><link rel="canonical" href="https://example.com/x/"></head><body>'
               '<h1>Historic wrestler</h1><p>The source stays unchanged.</p>'
               '<a href="https://www.wwe.com/">Official source</a></body></html>')
        updated = app.add_shell(app.upgrade_article(doc, "other", {}), "article", "other")
        self.assertIn("The source stays unchanged.", updated)
        self.assertIn('href="https://www.wwe.com/"', updated)
        self.assertIn('rel="canonical"', updated)


if __name__ == "__main__":
    unittest.main()
