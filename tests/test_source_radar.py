"""Offline safety tests; no network calls, secrets or paid API needed."""
import datetime as dt
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import source_radar as radar


def sample_xml(channel_id, video_id="123456789ab", title="Official recap &amp; latest confirmed announcement"):
    stamp = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
    return f"""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:yt="http://www.youtube.com/xml/schemas/2015">
 <yt:channelId>{channel_id}</yt:channelId>
 <entry>
 <yt:channelId>{channel_id}</yt:channelId>
 <yt:videoId>{video_id}</yt:videoId>
 <title>{title}</title>
 <published>{stamp}</published>
 </entry>
</feed>""".encode("utf-8")


class SourceRadarSafetyTests(unittest.TestCase):
    def test_valid_official_wwe_entry(self):
        feed = radar.extract_feed(sample_xml(radar.CHANNELS["WWE"]), "WWE", radar.CHANNELS["WWE"])
        self.assertEqual(len(feed), 1)
        self.assertEqual(feed[0]["url"], "https://www.youtube.com/watch?v=123456789ab")
        self.assertEqual(feed[0]["title"], "Official recap & latest confirmed announcement")

    def test_valid_official_aew_entry(self):
        feed = radar.extract_feed(sample_xml(radar.CHANNELS["AEW"]), "AEW", radar.CHANNELS["AEW"])
        self.assertEqual(feed[0]["promotion"], "AEW")

    def test_reject_mismatched_channel(self):
        with self.assertRaises(ValueError):
            radar.extract_feed(sample_xml("UC000wrong000"), "WWE", radar.CHANNELS["WWE"])

    def test_reject_invalid_video_id(self):
        entries = radar.extract_feed(sample_xml(radar.CHANNELS["WWE"], video_id="../../bad"), "WWE", radar.CHANNELS["WWE"])
        self.assertEqual(entries, [])

    def test_html_escaping_prevents_injection(self):
        entry = {
            "promotion": "WWE", "video_id": "123456789ab",
            "title": '<img src=x onerror=alert(1)>',
            "published": "2026-11-22T10:00:00Z",
            "url": "https://www.youtube.com/watch?v=123456789ab",
        }
        rendered = radar.render([entry])
        self.assertNotIn('<img src=x', rendered)
        self.assertIn("&lt;img", rendered)

    def test_reject_fake_official_url(self):
        self.assertFalse(radar.valid_cached({
            "promotion": "WWE", "video_id": "123456789ab",
            "title": "Anything", "published": "2026-11-22T10:00:00Z",
            "url": "https://malicious.example/steal",
        }))

    def test_empty_state_is_honest(self):
        page = radar.render([])
        self.assertIn("being prepared", page)
        self.assertNotIn("Breaking:", page)

    def test_feed_size_limit(self):
        with self.assertRaises(ValueError):
            radar.extract_feed(b"x" * 1_500_001, "WWE", radar.CHANNELS["WWE"])

    def test_markers_are_distinct(self):
        self.assertNotEqual(radar.START, radar.END)
        self.assertIn("SOURCE_RADAR", radar.START)


if __name__ == "__main__":
    unittest.main()
