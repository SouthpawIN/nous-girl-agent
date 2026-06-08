"""
test_wiki_handoff.py — Tests for the wiki handoff library.

Run with: python3 -m pytest tests/test_wiki_handoff.py
Or:       python3 tests/test_wiki_handoff.py
"""
import os
import sys
import shutil
import tempfile
import unittest
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Make wiki_handoff importable
_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
sys.path.insert(0, str(_REPO_ROOT / "wiki-handoff"))
from wiki_handoff import (
    notes_dir, escalations_dir, curate_chat, write_escalation,
    update_taste_profile, read_recent_curations, read_pending_escalations,
    TASTE_FILENAME,
)


class WikiHandoffTests(unittest.TestCase):
    """Tests for the wiki handoff library. Uses a temp NOTES_DIR to avoid
    clobbering the user's real ~/wiki/pet-curated/."""

    def setUp(self):
        # Save the real notes dir path and monkey-patch
        import wiki_handoff
        self._real_notes_dir = wiki_handoff.DEFAULT_NOTES_DIR
        self.tmp = tempfile.mkdtemp(prefix="wiki-handoff-test-")
        wiki_handoff.DEFAULT_NOTES_DIR = Path(self.tmp) / "pet-curated"

    def tearDown(self):
        import wiki_handoff
        wiki_handoff.DEFAULT_NOTES_DIR = self._real_notes_dir
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_notes_dir_creates(self):
        d = notes_dir()
        self.assertTrue(d.exists())
        self.assertTrue(d.is_dir())

    def test_curate_chat_writes_file(self):
        path = curate_chat({
            "title": "Test note",
            "user_interests_surfaced": ["A", "B"],
        }, trigger="chat", vibe="curious")
        self.assertTrue(path.exists())
        content = path.read_text()
        self.assertIn("---", content)  # has frontmatter
        self.assertIn("trigger: chat", content)
        self.assertIn("vibe: curious", content)
        self.assertIn("# Test note", content)
        self.assertIn("A", content)
        self.assertIn("B", content)

    def test_curate_chat_handles_lists_dicts(self):
        path = curate_chat({
            "title": "Mixed",
            "list_field": ["x", "y"],
            "dict_field": {"k1": "v1", "k2": "v2"},
            "scalar_field": "hello",
        })
        content = path.read_text()
        self.assertIn("x", content)
        self.assertIn("y", content)
        self.assertIn("k1", content)
        self.assertIn("v1", content)
        self.assertIn("hello", content)

    def test_write_escalation(self):
        path = write_escalation(
            reason="needs_code_execution",
            request="Build a CLI tool that does X",
        )
        self.assertTrue(path.exists())
        content = path.read_text()
        self.assertIn("reason: needs_code_execution", content)
        self.assertIn("status: pending", content)
        self.assertIn("Build a CLI tool", content)
        # Make sure it went into escalations/
        self.assertIn("escalations/", str(path))

    def test_update_taste_profile_creates(self):
        # Make sure it works on a fresh directory
        update_taste_profile({"music": {"vibes": ["chill"]}})
        path = notes_dir() / TASTE_FILENAME
        self.assertTrue(path.exists())
        content = path.read_text()
        self.assertIn("chill", content)

    def test_update_taste_profile_merges(self):
        update_taste_profile({"music": {"vibes": ["chill"]}, "topics": {"active": ["x"]}})
        update_taste_profile({"music": {"vibes": ["ambient"]}, "projects": {"active": ["p1"]}})
        path = notes_dir() / TASTE_FILENAME
        content = path.read_text()
        # vibes should be REPLACED, not appended (shallow merge)
        self.assertIn("ambient", content)
        self.assertNotIn("chill", content)
        # topics should be PRESERVED
        self.assertIn("x", content)
        # projects should be ADDED
        self.assertIn("p1", content)

    def test_read_recent_curations(self):
        curate_chat({"title": "One"})
        curate_chat({"title": "Two"})
        curate_chat({"title": "Three"})
        recent = read_recent_curations(limit=2)
        self.assertEqual(len(recent), 2)
        self.assertIn("trigger", recent[0])

    def test_read_pending_escalations(self):
        write_escalation("needs_terminal", "test")
        write_escalation("needs_file_modification", "test2")
        pending = read_pending_escalations()
        self.assertEqual(len(pending), 2)
        # All should have status: pending
        for p in pending:
            self.assertIn("pending", p.read_text())


class RadioBridgeTests(unittest.TestCase):
    """Tests for the radio bridge (sync only — signal/evolve require runtime)."""

    def setUp(self):
        import wiki_handoff
        self._real_notes_dir = wiki_handoff.DEFAULT_NOTES_DIR
        self.tmp = tempfile.mkdtemp(prefix="radio-bridge-test-")
        wiki_handoff.DEFAULT_NOTES_DIR = Path(self.tmp) / "pet-curated"
        # Insert radio_bridge into path
        sys.path.insert(0, str(_REPO_ROOT / "plugins" / "evolution-radio"))
        import radio_bridge
        self.bridge = radio_bridge

    def tearDown(self):
        import wiki_handoff
        wiki_handoff.DEFAULT_NOTES_DIR = self._real_notes_dir
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_sync_with_no_curations(self):
        signals = self.bridge.sync_taste_profile()
        self.assertEqual(signals, {"vibes": [], "moods": []})

    def test_sync_extracts_vibes(self):
        from wiki_handoff import curate_chat
        curate_chat({
            "title": "Music chat",
            "user_interests_surfaced": ["ambient and lo-fi vibes for coding"],
        })
        signals = self.bridge.sync_taste_profile()
        # Should extract at least "ambient" and "lo-fi"
        self.assertIn("ambient", signals["vibes"])
        self.assertIn("lo-fi", signals["vibes"])

    def test_sync_extracts_moods(self):
        from wiki_handoff import curate_chat
        curate_chat({
            "title": "Feeling",
            "user_interests_surfaced": ["feeling very calm and mellow today"],
        })
        signals = self.bridge.sync_taste_profile()
        self.assertIn("calm", signals["moods"])
        self.assertIn("mellow", signals["moods"])


if __name__ == "__main__":
    unittest.main()
