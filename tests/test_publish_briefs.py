"""Zero-network tests for the free official-video brief publisher."""
import datetime as dt
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import publish_briefs as briefs


class OfficialBriefSafetyTests(unittest.TestCase):
    def entry(self, **kwargs):
        stamp = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        v = {
            "promotion": "WWE", "title": "An official WWE announcement video highlight",
            "video_id": "abcDEF12345",
            "url": "https://www.youtube.com/watch?v=abcDEF12345",
            "published": stamp,
        }
        v.update(kwargs)
        return v

    def test_accept_canonical_youtube_source(self):
        self.assertTrue(briefs.safe_video(self.entry()))

    def test_reject_fake_youtube_domain(self):
        self.assertFalse(briefs.safe_video(self.entry(url="https://phishing.test/abcDEF12345")))

    def test_reject_invented_promotion(self):
        self.assertFalse(briefs.safe_video(self.entry(promotion="FictionalBrand")))

    def test_reject_bad_video_id(self):
        self.assertFalse(briefs.safe_video(self.entry(video_id="../../danger")))

    def test_reject_future_dated_video(self):
        future = (dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
        self.assertFalse(briefs.safe_video(self.entry(published=future)))

    def test_reject_old_video(self):
        old = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=10)).strftime("%Y-%m-%dT%H:%M:%SZ")
        self.assertFalse(briefs.safe_video(self.entry(published=old)))

    def test_html_escapes_official_title(self):
        webpage = briefs.page(self.entry(title='Official <script>alert("x")</script> video'))
        self.assertNotIn("<script>alert", webpage)
        self.assertIn("&lt;script&gt;", webpage)

    def test_page_is_not_search_indexed(self):
        webpage = briefs.page(self.entry())
        self.assertIn('name="robots" content="noindex,follow"', webpage)
        self.assertIn("not an AI-written investigative report", webpage)

    def test_home_cards_only_link_inside_own_site(self):
        output = briefs.content_cards([self.entry()])
        self.assertIn("/news/abcDEF12345/", output)
        self.assertNotIn('href="https://', output)


if __name__ == "__main__":
    unittest.main()
