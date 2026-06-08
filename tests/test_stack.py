"""
test_stack.py — End-to-end smoke test for the Nous Girl agent stack.

This is NOT a unit test. It exercises the whole stack as a system:
  - Catalog loads and validates
  - Plug-in manifest is well-formed
  - Wiki handoff works end-to-end
  - Radio bridge sync works
  - Eikon sprite is in place
  - Character config is in place
  - Conf template is in place
  - All expected directories exist

Run with: python3 -m unittest discover -s tests -v
Or:       python3 tests/test_stack.py
"""
import os
import sys
import shutil
import tempfile
import unittest
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent


class StackSmokeTest(unittest.TestCase):
    """End-to-end smoke test for the full Nous Girl agent stack."""

    # ----- Repo structure -----

    def test_repo_root_has_key_directories(self):
        for d in ["vtuber-core", "agent", "pet", "models", "plugins", "wiki-handoff", "scripts", "tests", "docs"]:
            self.assertTrue((_REPO_ROOT / d).is_dir(), f"missing dir: {d}/")

    def test_ag_is_a_real_file(self):
        """The AGENTS.md is the contract for future agents — make sure it's there."""
        self.assertTrue((_REPO_ROOT / "AGENTS.md").is_file(), "AGENTS.md missing")

    def test_changelog_is_a_real_file(self):
        self.assertTrue((_REPO_ROOT / "CHANGELOG.md").is_file(), "CHANGELOG.md missing")

    def test_ci_workflow_is_a_real_file(self):
        ci = _REPO_ROOT / ".github" / "workflows" / "ci.yml"
        self.assertTrue(ci.is_file(), "CI workflow missing")

    # ----- Model catalog -----

    def test_curated_catalog_loads(self):
        import yaml
        with open(_REPO_ROOT / "models" / "curated.yaml") as f:
            data = yaml.safe_load(f)
        self.assertIn("models", data, "catalog missing 'models' key")
        self.assertGreaterEqual(len(data["models"]), 1, "catalog has no models")
        # Default model should be marked
        defaults = [m for m in data["models"] if m.get("default")]
        self.assertEqual(len(defaults), 1, f"expected exactly 1 default model, got {len(defaults)}")

    def test_curated_catalog_schema_is_valid(self):
        """Every model entry has the required fields with valid values."""
        import yaml
        with open(_REPO_ROOT / "models" / "curated.yaml") as f:
            data = yaml.safe_load(f)
        valid_tiers = {"multimodal-native", "text-with-tts", "api-combo"}
        valid_backends = {"llama.cpp", "ollama", "openai-compat", "nous-portal"}
        for m in data["models"]:
            for field in ("id", "display_name", "tier", "backend", "eikon", "capabilities"):
                self.assertIn(field, m, f"model {m.get('id', '?')} missing {field}")
            self.assertIn(m["tier"], valid_tiers, f"bad tier for {m['id']}: {m['tier']}")
            self.assertIn(m["backend"], valid_backends, f"bad backend for {m['id']}: {m['backend']}")
            self.assertIsInstance(m["capabilities"], list, f"capabilities should be list for {m['id']}")
            # If multimodal-native, voice should be model or edge-tts (not None)
            if m["tier"] == "multimodal-native":
                self.assertIn(m.get("voice", {}).get("source"), ("model", "edge-tts"),
                              f"multimodal-native model {m['id']} should have voice source set")

    def test_auxiliaries_catalog_loads(self):
        """The auxiliaries section, if present, is valid."""
        import yaml
        with open(_REPO_ROOT / "models" / "curated.yaml") as f:
            data = yaml.safe_load(f)
        if "auxiliaries" in data:
            for a in data["auxiliaries"]:
                for field in ("id", "display_name", "role", "purpose"):
                    self.assertIn(field, a, f"auxiliary {a.get('id', '?')} missing {field}")

    def test_suggested_catalog_loads(self):
        """The suggested catalog (candidates) is valid."""
        import yaml
        with open(_REPO_ROOT / "models" / "suggested.yaml") as f:
            data = yaml.safe_load(f)
        self.assertIn("suggestions", data, "suggested.yaml missing 'suggestions' key")

    # ----- Eikon sprite -----

    def test_nous_girl_eikon_base_png_exists(self):
        """The default eikon has a base.png."""
        base = _REPO_ROOT / "pet" / "sprites" / "nous-girl" / "base.png"
        self.assertTrue(base.is_file(), "pet/sprites/nous-girl/base.png missing")
        # Should be a reasonable size (>1KB, <5MB)
        size = base.stat().st_size
        self.assertGreater(size, 1000, f"base.png too small: {size}b (corrupted?)")
        self.assertLess(size, 5_000_000, f"base.png too large: {size}b")

    def test_nous_girl_eikon_manifest_exists(self):
        manifest = _REPO_ROOT / "pet" / "sprites" / "nous-girl" / "manifest.json"
        self.assertTrue(manifest.is_file(), "manifest.json missing")
        import json
        with open(manifest) as f:
            data = json.load(f)
        self.assertIsInstance(data, dict)

    def test_vtuber_core_avatar_exists(self):
        """The avatar that Open-LLM-VTuber serves is in place."""
        avatar = _REPO_ROOT / "vtuber-core" / "avatars" / "nous-girl.png"
        self.assertTrue(avatar.is_file(), "vtuber-core/avatars/nous-girl.png missing")

    # ----- Character config -----

    def test_nous_girl_character_config_exists(self):
        char = _REPO_ROOT / "vtuber-core" / "characters" / "nous-girl.yaml"
        self.assertTrue(char.is_file(), "characters/nous-girl.yaml missing")
        import yaml
        with open(char) as f:
            data = yaml.safe_load(f)
        self.assertIn("character_config", data, "missing character_config key")
        cfg = data["character_config"]
        self.assertEqual(cfg.get("conf_name"), "nous-girl")
        self.assertIn("persona_prompt", cfg)
        self.assertIn("TOWARDS SELF-IMPROVEMENT", cfg["persona_prompt"])

    def test_nous_girl_conf_template_exists(self):
        """The drop-in conf.yaml template with OmniStep + OmniSenter wiring."""
        conf = _REPO_ROOT / "vtuber-core" / "conf.nous-girl.yaml"
        self.assertTrue(conf.is_file(), "conf.nous-girl.yaml missing")
        # Should reference both OmniStep and OmniSenter
        with open(conf) as f:
            content = f.read()
        self.assertIn("OmniStep", content)
        self.assertIn("OmniSenter", content)
        self.assertIn("llama_cpp_omnistep", content)
        self.assertIn("llama_cpp_omnisenter", content)

    def test_pet_menu_exists(self):
        menu = _REPO_ROOT / "pet" / "menus" / "nous-girl.yaml"
        self.assertTrue(menu.is_file(), "pet/menus/nous-girl.yaml missing")
        import yaml
        with open(menu) as f:
            data = yaml.safe_load(f)
        self.assertEqual(data["name"], "nous-girl")
        self.assertIsInstance(data["menus"], list)
        self.assertGreater(len(data["menus"]), 0)

    # ----- Agent profiles -----

    def test_curator_profile_template(self):
        """The Nous Girl curator profile template."""
        prof = _REPO_ROOT / "agent" / "profile-template.yaml"
        self.assertTrue(prof.is_file(), "agent/profile-template.yaml missing")
        import yaml
        with open(prof) as f:
            data = yaml.safe_load(f)
        self.assertEqual(data["name"], "evolutionary-radio")
        # Should have a bounded toolset
        for forbidden in ["terminal", "computer_use", "delegation"]:
            self.assertNotIn(forbidden, data.get("toolsets", []),
                             f"curator profile should not have {forbidden}")

    def test_curator_distribution_yaml(self):
        """The distribution.yaml that makes the curator installable."""
        dist = _REPO_ROOT / "agent" / "distribution.yaml"
        self.assertTrue(dist.is_file(), "agent/distribution.yaml missing")
        import yaml
        with open(dist) as f:
            data = yaml.safe_load(f)
        self.assertEqual(data["name"], "evolutionary-radio")
        self.assertIn("distribution_owned", data)

    def test_senter_profile(self):
        """The Senter triage profile."""
        prof = _REPO_ROOT / "agent" / "senter" / "senter-profile.yaml"
        dist = _REPO_ROOT / "agent" / "senter" / "distribution.yaml"
        self.assertTrue(prof.is_file(), "agent/senter/senter-profile.yaml missing")
        self.assertTrue(dist.is_file(), "agent/senter/distribution.yaml missing")
        import yaml
        with open(prof) as f:
            data = yaml.safe_load(f)
        self.assertEqual(data["name"], "senter")
        with open(dist) as f:
            dist_data = yaml.safe_load(f)
        self.assertEqual(dist_data["name"], "senter")

    def test_curator_prompts_exist(self):
        """The three agent persona prompts."""
        for prompt in ["nous-girl-curator.md", "radio-curator.md", "senter-triage.md"]:
            p = _REPO_ROOT / "agent" / "prompts" / prompt
            self.assertTrue(p.is_file(), f"agent/prompts/{prompt} missing")
            with open(p) as f:
                content = f.read()
            # Each should be substantial (>= 500 chars)
            self.assertGreater(len(content), 500, f"{prompt} is too short")

    # ----- Radio plug-in -----

    def test_radio_plugin_manifest(self):
        sys.path.insert(0, str(_REPO_ROOT / "plugins" / "evolution-radio"))
        from evolution_radio_plugin import manifest, COMMANDS
        m = manifest()
        self.assertEqual(m["name"], "evolution-radio")
        self.assertIn("commands", m)
        self.assertEqual(len(m["commands"]), len(COMMANDS))

    def test_radio_plugin_skill_exists(self):
        skill = _REPO_ROOT / "plugins" / "evolution-radio" / "SKILL.md"
        self.assertTrue(skill.is_file(), "evolution-radio SKILL.md missing")
        with open(skill) as f:
            content = f.read()
        self.assertIn("name: evolution-radio", content)

    def test_radio_upstream_present(self):
        """The vendored radio.py + code/ is in place."""
        radio_py = _REPO_ROOT / "plugins" / "evolution-radio" / "upstream" / "radio.py"
        self.assertTrue(radio_py.is_file(), "upstream/radio.py missing")
        code_dir = _REPO_ROOT / "plugins" / "evolution-radio" / "upstream" / "code"
        self.assertTrue(code_dir.is_dir(), "upstream/code/ missing")
        # Should have the core modules
        for m in ["mpv_player.py", "omni_client.py", "acestep_client.py", "track_queue.py"]:
            self.assertTrue((code_dir / m).is_file(), f"upstream/code/{m} missing")

    def test_radio_bridge_importable(self):
        """The wiki<->radio bridge module imports cleanly."""
        sys.path.insert(0, str(_REPO_ROOT / "plugins" / "evolution-radio"))
        try:
            from radio_bridge import sync_taste_profile, signal_current_track, trigger_evolve
            # Just check the functions exist and are callable
            self.assertTrue(callable(sync_taste_profile))
            self.assertTrue(callable(signal_current_track))
            self.assertTrue(callable(trigger_evolve))
        except ImportError as e:
            self.fail(f"radio_bridge import failed: {e}")

    # ----- Wiki handoff -----

    def test_wiki_handoff_module(self):
        sys.path.insert(0, str(_REPO_ROOT / "wiki-handoff"))
        try:
            from wiki_handoff import (
                notes_dir, escalations_dir, curate_chat, write_escalation,
                update_taste_profile, read_recent_curations, read_pending_escalations,
            )
            self.assertTrue(callable(curate_chat))
            self.assertTrue(callable(write_escalation))
        except ImportError as e:
            self.fail(f"wiki_handoff import failed: {e}")

    def test_wiki_handoff_end_to_end(self):
        """Full cycle: curate → read back → escalate → read pending."""
        import tempfile
        sys.path.insert(0, str(_REPO_ROOT / "wiki-handoff"))
        import wiki_handoff
        # Monkey-patch the notes dir to a temp location
        real_notes = wiki_handoff.DEFAULT_NOTES_DIR
        tmp = Path(tempfile.mkdtemp(prefix="wiki-smoke-"))
        wiki_handoff.DEFAULT_NOTES_DIR = tmp / "pet-curated"
        try:
            from wiki_handoff import curate_chat, write_escalation, read_pending_escalations, read_recent_curations
            # 1. Write a curation
            path = curate_chat({
                "title": "Smoke test",
                "user_interests_surfaced": ["testing"],
            })
            self.assertTrue(path.exists())
            # 2. Write an escalation
            esc = write_escalation("needs_code_execution", "test request")
            self.assertTrue(esc.exists())
            # 3. Read back
            recent = read_recent_curations(limit=5)
            self.assertGreaterEqual(len(recent), 1)
            pending = read_pending_escalations()
            self.assertGreaterEqual(len(pending), 1)
        finally:
            wiki_handoff.DEFAULT_NOTES_DIR = real_notes
            shutil.rmtree(tmp, ignore_errors=True)

    # ----- Launchers -----

    def test_launchers_exist_and_executable(self):
        for s in ["install.sh", "dev.sh", "run-pet.sh", "run-radio.sh", "run-agent.sh"]:
            p = _REPO_ROOT / "scripts" / s
            self.assertTrue(p.is_file(), f"scripts/{s} missing")
            # Should be executable
            self.assertTrue(os.access(p, os.X_OK), f"scripts/{s} not executable")

    # ----- Docs -----

    def test_required_docs_exist(self):
        for doc in ["ARCHITECTURE.md", "INSTALL.md", "AGENTS.md", "CHANGELOG.md", "README.md"]:
            p = _REPO_ROOT / doc
            self.assertTrue(p.is_file(), f"{doc} missing")
            with open(p) as f:
                content = f.read()
            # Substantial docs
            self.assertGreater(len(content), 500, f"{doc} is too short")

    def test_docs_subdirectory(self):
        for doc in ["TROUBLESHOOTING.md", "EIKON_FORMAT.md", "MODEL_FORMAT.md", "AUXILIARY_MODEL.md"]:
            p = _REPO_ROOT / "docs" / doc
            self.assertTrue(p.is_file(), f"docs/{doc} missing")


class StackIntegrationTest(unittest.TestCase):
    """Test that components talk to each other correctly."""

    def test_radio_bridge_syncs_with_wiki_handoff(self):
        """The radio bridge can pull signals from the wiki, and the wiki handoff can be called from the bridge."""
        # Set up temp notes dir
        import tempfile
        sys.path.insert(0, str(_REPO_ROOT / "wiki-handoff"))
        sys.path.insert(0, str(_REPO_ROOT / "plugins" / "evolution-radio"))
        import wiki_handoff
        real_notes = wiki_handoff.DEFAULT_NOTES_DIR
        tmp = Path(tempfile.mkdtemp(prefix="bridge-smoke-"))
        wiki_handoff.DEFAULT_NOTES_DIR = tmp / "pet-curated"
        try:
            # 1. Write a curation that mentions music vibes
            from wiki_handoff import curate_chat
            curate_chat({
                "title": "Music chat",
                "user_interests_surfaced": ["ambient and lo-fi beats for coding"],
            })
            # 2. Run the bridge sync
            from radio_bridge import sync_taste_profile
            signals = sync_taste_profile()
            # The bridge should pick up "ambient" and "lo-fi" from the curation
            self.assertIn("ambient", signals["vibes"])
            self.assertIn("lo-fi", signals["vibes"])
            # 3. Verify the taste profile was updated
            import yaml
            with open(wiki_handoff.DEFAULT_NOTES_DIR / "taste.yaml") as f:
                taste = yaml.safe_load(f)
            self.assertIn("music", taste)
            self.assertIn("ambient", taste["music"]["vibes"])
        finally:
            wiki_handoff.DEFAULT_NOTES_DIR = real_notes
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
