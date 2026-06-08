"""
radio_bridge.py — Bridge between the radio daemon and the wiki handoff
============================================================================

The radio daemon (upstream/radio.py) generates tracks, plays them, and
evolves its playlists. This bridge module:

  1. Reads curated notes from ~/wiki/pet-curated/ for taste signals
  2. Updates the taste profile with the current vibe
  3. Optionally writes back "listening context" notes when the user
     explicitly engages with the radio

This module is the loop that closes the curation -> radio -> curation cycle.
It's intended to be run as a periodic background task (cron or asyncio loop),
NOT as a hot path inside the radio itself.

Usage:
  python3 radio_bridge.py sync          # one-shot sync from wiki -> taste.yaml
  python3 radio_bridge.py signal        # push current playing track to wiki
  python3 radio_bridge.py evolve        # trigger an evolutionary step + write note
"""
from __future__ import annotations
import os
import sys
import json
import time
import argparse
from datetime import datetime, timezone
from pathlib import Path

# Make wiki_handoff importable
_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "wiki-handoff"))
from wiki_handoff import (
    notes_dir,
    read_recent_curations,
    update_taste_profile,
    curate_chat,
)

# Path to the radio's state file (written by upstream/radio.py)
RADIO_STATE_DIR = Path("~/.local/share/evolutionary-radio").expanduser()
RADIO_STATE_FILE = RADIO_STATE_DIR / "state.json"
RADIO_PID_FILE = RADIO_STATE_DIR / "radio.pid"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_iso(s: str) -> datetime | None:
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None


def _extract_music_signals(notes: list[dict]) -> dict:
    """
    Extract music-relevant signals from recent curation notes.
    Naive: just looks for explicit 'music' / 'vibe' / 'playlist' mentions.
    """
    vibes: list[str] = []
    moods: list[str] = []
    for n in notes:
        # Look at the raw markdown body for keywords
        path = Path(n.get("_path", ""))
        if not path.exists():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        lower = text.lower()
        for kw in ("ambient", "lo-fi", "lofi", "chill", "dreamy", "synth", "jazz",
                   "classical", "electronic", "house", "techno", "downtempo",
                   "generative", "instrumental", "vocal", "acoustic"):
            if kw in lower:
                vibes.append(kw)
        for kw in ("focused", "tired", "energetic", "calm", "mellow", "intense",
                   "melancholy", "happy", "sad", "reflective", "playful"):
            if kw in lower:
                moods.append(kw)

    # Dedupe, keep order, cap
    seen = set()
    vibes_dedup = []
    for v in vibes:
        if v not in seen:
            vibes_dedup.append(v)
            seen.add(v)
    moods_dedup = []
    for m in moods:
        if m not in seen:
            moods_dedup.append(m)
            seen.add(m)

    return {
        "vibes": vibes_dedup[:10],
        "moods": moods_dedup[:10],
    }


def sync_taste_profile(days: int = 7) -> dict:
    """
    Read recent curations (last N days) and merge extracted music signals
    into the taste profile's music section.

    Returns the updated taste profile dict.
    """
    notes = read_recent_curations(limit=200)
    cutoff = time.time() - days * 86400
    recent = []
    for n in notes:
        ts = n.get("curated_at", "")
        parsed = _parse_iso(ts) if ts else None
        if parsed and parsed.timestamp() < cutoff:
            continue
        recent.append(n)

    signals = _extract_music_signals(recent)
    update_taste_profile({
        "music": {
            "last_synced_at": _now(),
            "signals_source": "wiki-handoff",
            "vibes": signals["vibes"],
            "moods": signals["moods"],
        },
    })
    return signals


def signal_current_track() -> dict | None:
    """
    Read the radio's current state and write a 'listening context' note
    to the wiki. Called when the user engages with the radio.
    """
    if not RADIO_STATE_FILE.exists():
        return None
    try:
        state = json.loads(RADIO_STATE_FILE.read_text())
    except Exception:
        return None

    track = state.get("current_track")
    if not track:
        return None

    path = curate_chat({
        "title": f"Listening: {track.get('title', '?')}",
        "track_info": track,
        "radio_state": {
            "queue_depth": state.get("queue_depth", 0),
            "vibe": state.get("vibe", "?"),
        },
    }, trigger="radio", vibe="listening")

    return {
        "wrote": str(path),
        "track": track.get("title", "?"),
    }


def trigger_evolve() -> Path:
    """
    Write a 'evolutionary step triggered' note. The actual Ohm chain
    runs in the radio upstream; this just records that it was triggered.
    """
    return curate_chat({
        "title": "Evolutionary step triggered",
        "trigger": "manual",
        "evolution": {
            "chain": "ohm",
            "expected_duration_minutes": 30,
        },
    }, trigger="radio", vibe="evolving")


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("sync", help="Pull music signals from wiki into taste profile")
    sub.add_parser("signal", help="Write current radio track to wiki")
    sub.add_parser("evolve", help="Trigger an evolutionary step + log it")
    args = parser.parse_args()

    if args.cmd == "sync":
        sig = sync_taste_profile()
        print(f"Synced. {len(sig['vibes'])} vibes, {len(sig['moods'])} moods.")
    elif args.cmd == "signal":
        result = signal_current_track()
        if result:
            print(f"Wrote: {result['wrote']} (track: {result['track']})")
        else:
            print("No radio state found or no current track.")
    elif args.cmd == "evolve":
        path = trigger_evolve()
        print(f"Logged evolution trigger: {path}")


if __name__ == "__main__":
    main()
