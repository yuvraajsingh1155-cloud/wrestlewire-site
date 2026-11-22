"""Tests for optional Gemini drafts without calling any external AI service."""
import datetime as dt
import os
import pathlib
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
import ai_drafts


class FreeGeminiDraftTests(unittest.TestCase):
    def test_disabled_pipeline_skips_all_api_calls(self):
        with patch.dict(os.environ, {"ENABLE_FREE_AI_DRAFTS": "false", "GEMINI_API_KEY": ""}):
            self.assertFalse(ai_drafts.run())

    def test_enabled_without_key_still_skips(self):
        with patch.dict(os.environ, {"ENABLE_FREE_AI_DRAFTS": "true", "GEMINI_API_KEY": ""}):
            self.assertFalse(ai_drafts.run())

    def test_sensitive_claim_regex(self):
        self.assertIsNotNone(ai_drafts.SENSITIVE.search("He has signed with a company"))
        self.assertIsNotNone(ai_drafts.SENSITIVE.search("a confirmed injury"))
        self.assertIsNone(ai_drafts.SENSITIVE.search("Official publisher uploaded a video with this headline"))

    def test_drafts_not_in_site_pages(self):
        self.assertEqual(ai_drafts.DRAFTS.name, "review_drafts")
        self.assertNotIn("index.html", str(ai_drafts.DRAFTS))
        self.assertEqual(ai_drafts.MAX_DRAFTS_PER_DAY, 1)

    def test_source_prompt_requires_review(self):
        self.assertIn("DO NOT invent", ai_drafts.PROMPT)
        self.assertIn("manually fact-checked", ai_drafts.PROMPT)


if __name__ == "__main__":
    unittest.main()
