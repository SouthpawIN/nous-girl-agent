"""
Evolutionary Radio Daemon
=========================

Perpetual playlist loop. Listens to user engagement, builds playlists
reflecting taste, generates new music (HeartMuLa / ACE-Step / model-native),
trains LoRAs on what the user likes, feeds the Ohm chain for self-evolution.

Modes:
  - ambient:   plays pre-generated playlist, no live gen (GPU-safe during training)
  - live-gen:  generates new tracks on the fly (requires idle GPU)

Coupling to model:
  - Reads the active model from the catalog to pick music source
  - multimodal-native → model-native music output
  - text-with-tts / api-combo → playlist (curated or heartmula-generated)

This is a SKELETON. The full implementation lives in the
evolutionary-radio repo. We just orchestrate from here.
"""
from __future__ import annotations
import os
import sys
import json
import time
import signal
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import Literal

import yaml

LOG = logging.getLogger("evolution-radio")
PLUGIN_DIR = Path(__file__).parent.parent  # plugins/evolution-radio/
PLAYLISTS_DIR = PLUGIN_DIR / "playlists"


@dataclass
class RadioConfig:
    """Config derived from the active model + user prefs."""
    music_source: Literal["model", "heartmula", "ace-step", "playlist", "none"]
    playlist_path: Path | None
    default_playlist: Path = PLAYLISTS_DIR / "default.json"
    mode: Literal["ambient", "live-gen"] = "ambient"
    lora_dir: Path = PLUGIN_DIR / "lora"
    ohm_dir: Path = PLUGIN_DIR / "ohm"
    taste_profile: Path = Path("~/wiki/pet-curated/taste.yaml").expanduser()
    poll_interval: int = 60
    evolve_interval_hours: int = 24 * 7  # weekly Ohm run


@dataclass
class RadioState:
    """Runtime state for the daemon."""
    running: bool = False
    last_poll: float = 0.0
    last_evolve: float = 0.0
    current_track: str | None = None
    likes: int = 0
    skips: int = 0
    generation_count: int = 0


def load_active_model(catalog_path: Path = Path("models/curated.yaml")) -> dict:
    """Load the active model entry from the catalog. Returns the entry marked default: true."""
    with open(catalog_path) as f:
        catalog = yaml.safe_load(f)
    models = catalog.get("models", [])
    for m in models:
        if m.get("default"):
            return m
    if models:
        return models[0]
    raise RuntimeError(f"No models in {catalog_path}")


def build_config(model_entry: dict) -> RadioConfig:
    """Translate a model catalog entry into a RadioConfig."""
    music_cfg = model_entry.get("music", {})
    source = music_cfg.get("source", "playlist")
    playlist = None
    if "playlist" in music_cfg:
        playlist = Path(music_cfg["playlist"]).expanduser()
    if not playlist or not playlist.exists():
        playlist = PLAYLISTS_DIR / "default.json"

    return RadioConfig(
        music_source=source,
        playlist_path=playlist,
    )


def poll_taste_profile(state: RadioState, cfg: RadioConfig) -> None:
    """Read ~/wiki/pet-curated/taste.yaml and update internal state."""
    if not cfg.taste_profile.exists():
        return
    try:
        with open(cfg.taste_profile) as f:
            taste = yaml.safe_load(f) or {}
        # Crude: count like/skip markers in recent notes
        likes = taste.get("likes", 0)
        skips = taste.get("skips", 0)
        state.likes = likes
        state.skips = skips
    except Exception as e:
        LOG.warning("Failed to read taste profile: %s", e)


def run_loop(cfg: RadioConfig, state: RadioState) -> None:
    """Main daemon loop. Skeleton — full logic in evolutionary-radio repo."""
    LOG.info("Evolutionary radio daemon started")
    LOG.info("  music source: %s", cfg.music_source)
    LOG.info("  playlist: %s", cfg.playlist_path)
    LOG.info("  mode: %s", cfg.mode)

    state.running = True
    while state.running:
        state.last_poll = time.time()
        poll_taste_profile(state, cfg)
        # TODO: actual playlist progression, generation, lora training, ohm evolution
        # This skeleton just prints status. The real implementation lives in
        # the evolutionary-radio repo (southpawin/evolutionary-radio).
        time.sleep(cfg.poll_interval)


def handle_signal(signum, frame):
    """Graceful shutdown."""
    print("Shutting down evolution-radio daemon...")
    sys.exit(0)


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    # Find the catalog
    cwd = Path.cwd()
    catalog = None
    for candidate in [cwd / "models/curated.yaml", cwd.parent / "models/curated.yaml", cwd.parent.parent / "models/curated.yaml"]:
        if candidate.exists():
            catalog = candidate
            break
    if not catalog:
        LOG.error("Could not find models/curated.yaml")
        sys.exit(1)

    model = load_active_model(catalog)
    cfg = build_config(model)
    state = RadioState()
    run_loop(cfg, state)


if __name__ == "__main__":
    main()
