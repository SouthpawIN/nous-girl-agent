"""
test_radio_plugin.py — Tests for the Evolution Radio Hermes plug-in.

Run with: python3 -m unittest discover -s tests -v
Or:       python3 tests/test_radio_plugin.py
"""
import os
import sys
import unittest
from pathlib import Path

# Make plug-in importable
_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
sys.path.insert(0, str(_REPO_ROOT / "plugins" / "evolution-radio"))

# Import the plug-in
from evolution_radio_plugin import (
    manifest,
    COMMANDS,
    PLUGIN_NAME,
    PLUGIN_VERSION,
    cmd_status,
    cmd_queue,
    cmd_sync,
    cmd_evolve,
)


class RadioPluginManifestTests(unittest.TestCase):
    """Tests for the plug-in manifest contract."""

    def test_manifest_has_required_fields(self):
        m = manifest()
        for field in ("name", "version", "description", "author", "repo", "commands", "skill"):
            self.assertIn(field, m, f"manifest missing '{field}'")
        self.assertEqual(m["name"], PLUGIN_NAME)
        self.assertEqual(m["version"], PLUGIN_VERSION)
        self.assertIsInstance(m["commands"], list)
        self.assertGreater(len(m["commands"]), 0)

    def test_manifest_commands_have_names_and_descriptions(self):
        m = manifest()
        for cmd in m["commands"]:
            self.assertIn("name", cmd, f"command missing name: {cmd}")
            self.assertIn("description", cmd, f"command missing description: {cmd}")
            self.assertTrue(cmd["name"].startswith("radio:"), f"command name should start with 'radio:': {cmd['name']}")

    def test_manifest_skill_is_evolution_radio(self):
        m = manifest()
        self.assertEqual(m["skill"], "evolution-radio")

    def test_commands_dict_matches_manifest(self):
        # Every command in COMMANDS should be in the manifest
        m = manifest()
        manifest_cmd_names = {c["name"] for c in m["commands"]}
        registry_cmd_names = set(COMMANDS.keys())
        self.assertEqual(manifest_cmd_names, registry_cmd_names,
                         f"Mismatch: manifest={manifest_cmd_names} registry={registry_cmd_names}")


class RadioPluginRuntimeTests(unittest.TestCase):
    """Tests that exercise the runtime commands. The radio daemon is not actually
    running, so these should fail gracefully (return ok=False) without crashing."""

    def test_status_handles_no_radio_running(self):
        # If no radio is running, status should still return a structured response
        result = cmd_status()
        self.assertIn("ok", result)
        # If the radio ISN'T running (most likely), ok=False is fine
        # If it IS running, we just check the response shape
        if result["ok"]:
            self.assertIn("stdout", result)
        else:
            self.assertIn("stdout", result)

    def test_queue_handles_no_radio(self):
        result = cmd_queue()
        self.assertIn("ok", result)
        self.assertIn("output", result)

    def test_sync_runs_without_error(self):
        # Sync should work even with no radio running (it operates on the wiki)
        # It will write to the real taste.yaml — that's OK for an integration test
        result = cmd_sync()
        self.assertIn("ok", result)
        # We don't care if it succeeded, just that it didn't crash

    def test_evolve_runs_without_error(self):
        # Evolve writes a log entry to the wiki
        result = cmd_evolve()
        self.assertIn("ok", result)


class RadioPluginCommandSchemaTests(unittest.TestCase):
    """Tests for the schema of each command's expected args."""

    def test_start_command_accepts_vibe(self):
        m = manifest()
        start_cmd = next((c for c in m["commands"] if c["name"] == "radio:start"), None)
        self.assertIsNotNone(start_cmd, "radio:start not in manifest")
        args = start_cmd.get("args", [])
        vibe_arg = next((a for a in args if a.get("name") == "vibe"), None)
        self.assertIsNotNone(vibe_arg, "radio:start should have a 'vibe' arg")
        self.assertEqual(vibe_arg.get("type"), "string")

    def test_no_command_args_for_simple_commands(self):
        # skip, like, dislike, stop, status, queue, evolve, sync shouldn't take args
        m = manifest()
        no_arg_commands = ["radio:skip", "radio:like", "radio:dislike", "radio:stop",
                           "radio:status", "radio:queue", "radio:evolve", "radio:sync"]
        for cmd_name in no_arg_commands:
            cmd = next((c for c in m["commands"] if c["name"] == cmd_name), None)
            self.assertIsNotNone(cmd, f"{cmd_name} not in manifest")
            self.assertEqual(cmd.get("args", []), [], f"{cmd_name} should not take args")


if __name__ == "__main__":
    unittest.main()
