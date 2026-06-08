#!/usr/bin/env python3
"""
evolutionary_radio_plugin.py — Hermes plug-in entry point for the OmniStep Evolution Radio.

This is the official Hermes plug-in for the radio daemon. It registers the
radio with the Hermes agent runtime so it can be invoked, queried, and
controlled via the standard plug-in interface.

Plug-in contract (see AGENTS.md for full spec):
  - register(cli) -> adds CLI commands: radio:start, radio:stop, radio:skip, radio:like
  - manifest() -> returns plug-in metadata
  - skill -> provides /evolution-radio skill

The actual radio logic lives in plugins/evolution-radio/upstream/radio.py
(vendored from southpawin/evolutionary-radio). We just expose it.
"""
from __future__ import annotations
import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Any

# Make the upstream radio importable
_HERE = Path(__file__).resolve().parent
_UPSTREAM = _HERE / "upstream"
sys.path.insert(0, str(_UPSTREAM))

# The radio module is invoked as a subprocess, not imported, because it
# has its own long-running event loop. The plug-in here is a thin wrapper.

PLUGIN_NAME = "evolution-radio"
PLUGIN_VERSION = "0.1.0"
RADIO_DAEMON = _UPSTREAM / "radio.py"
STATE_DIR = Path("~/.local/share/evolutionary-radio").expanduser()
PID_FILE = STATE_DIR / "radio.pid"
STATE_FILE = STATE_DIR / "state.json"


def manifest() -> dict[str, Any]:
    """Return plug-in metadata. Standard Hermes plug-in contract."""
    return {
        "name": PLUGIN_NAME,
        "version": PLUGIN_VERSION,
        "description": "Perpetual radio with self-evolving playlists. Curates user taste, trains LoRAs, runs Ohm chain.",
        "author": "SouthpawIN",
        "repo": "https://github.com/SouthpawIN/nous-girl-agent",
        "upstream": "https://github.com/SouthpawIN/evolutionary-radio",
        "commands": [
            {"name": "radio:start", "description": "Start the radio daemon", "args": [{"name": "vibe", "type": "string", "default": "chill lofi beats for coding"}]},
            {"name": "radio:stop", "description": "Stop the radio daemon"},
            {"name": "radio:skip", "description": "Skip the current track"},
            {"name": "radio:like", "description": "Like the current track"},
            {"name": "radio:dislike", "description": "Dislike the current track"},
            {"name": "radio:status", "description": "Get the current radio state"},
            {"name": "radio:queue", "description": "Show the upcoming queue"},
            {"name": "radio:evolve", "description": "Trigger an Ohm evolution step"},
            {"name": "radio:sync", "description": "Sync taste profile from wiki"},
        ],
        "skill": "evolution-radio",
    }


def _run_radio(*args: str) -> subprocess.CompletedProcess:
    """Run a radio.py command. Returns the result."""
    env = os.environ.copy()
    env.setdefault("PYTHONUNBUFFERED", "1")
    return subprocess.run(
        ["python3", str(RADIO_DAEMON), *args],
        capture_output=True, text=True, env=env,
        cwd=str(_UPSTREAM),
    )


def cmd_start(vibe: str = "chill lofi beats for coding") -> dict:
    """Start the radio daemon."""
    if PID_FILE.exists():
        return {"ok": False, "error": "radio already running", "pid_file": str(PID_FILE)}
    # Start as a background subprocess
    env = os.environ.copy()
    env.setdefault("PYTHONUNBUFFERED", "1")
    proc = subprocess.Popen(
        ["python3", str(RADIO_DAEMON), "start", "--vibe", vibe],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        env=env, cwd=str(_UPSTREAM),
        start_new_session=True,
    )
    return {"ok": True, "pid": proc.pid, "vibe": vibe, "log_hint": f"tail -f {_UPSTREAM}/radio_crash.log"}


def cmd_stop() -> dict:
    """Stop the radio daemon."""
    r = _run_radio("stop")
    return {"ok": r.returncode == 0, "output": r.stdout, "stderr": r.stderr}


def cmd_skip() -> dict:
    """Skip the current track."""
    r = _run_radio("skip")
    return {"ok": r.returncode == 0, "output": r.stdout}


def cmd_like() -> dict:
    """Like the current track."""
    r = _run_radio("like")
    return {"ok": r.returncode == 0, "output": r.stdout}


def cmd_dislike() -> dict:
    """Dislike the current track."""
    r = _run_radio("dislike")
    return {"ok": r.returncode == 0, "output": r.stdout}


def cmd_status() -> dict:
    """Get the current radio state."""
    r = _run_radio("status")
    out = {"ok": r.returncode == 0, "stdout": r.stdout}
    # Also read the state file for richer info
    if STATE_FILE.exists():
        try:
            out["state"] = json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return out


def cmd_queue() -> dict:
    """Show the upcoming queue."""
    r = _run_radio("queue")
    return {"ok": r.returncode == 0, "output": r.stdout}


def cmd_evolve() -> dict:
    """Trigger an Ohm evolution step."""
    r = _run_radio("evolve")
    return {"ok": r.returncode == 0, "output": r.stdout}


def cmd_sync() -> dict:
    """Sync taste profile from wiki via the radio bridge."""
    bridge = _HERE / "radio_bridge.py"
    r = subprocess.run(["python3", str(bridge), "sync"], capture_output=True, text=True)
    return {"ok": r.returncode == 0, "output": r.stdout, "stderr": r.stderr}


# Standard Hermes plug-in entry points
COMMANDS = {
    "radio:start": cmd_start,
    "radio:stop": cmd_stop,
    "radio:skip": cmd_skip,
    "radio:like": cmd_like,
    "radio:dislike": cmd_dislike,
    "radio:status": cmd_status,
    "radio:queue": cmd_queue,
    "radio:evolve": cmd_evolve,
    "radio:sync": cmd_sync,
}


def register(cli) -> None:
    """Hermes plug-in entry point: register commands with the CLI."""
    cli.add_command_group(PLUGIN_NAME, "OmniStep Evolution Radio")
    for cmd_name, fn in COMMANDS.items():
        cli.add_command(cmd_name, fn, group=PLUGIN_NAME)
    cli.add_skill("evolution-radio", skill_path=str(_UPSTREAM.parent / "SKILL.md"))


if __name__ == "__main__":
    # Standalone CLI mode for testing
    import argparse
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("manifest")
    sub.add_parser("list")
    p = sub.add_parser("call")
    p.add_argument("command")
    p.add_argument("--vibe", default="chill lofi beats for coding")
    args = parser.parse_args()

    if args.cmd == "manifest":
        print(json.dumps(manifest(), indent=2))
    elif args.cmd == "list":
        for c in COMMANDS:
            print(f"  {c}")
    elif args.cmd == "call":
        if args.command not in COMMANDS:
            print(f"Unknown command: {args.command}")
            sys.exit(1)
        if args.command == "radio:start":
            result = COMMANDS[args.command](vibe=args.vibe)
        else:
            result = COMMANDS[args.command]()
        print(json.dumps(result, indent=2))
