"""
wiki_handoff.py — Pet → Hermes main handoff module
====================================================

The Nous Girl agent (pet's curator) writes to ~/wiki/pet-curated/.
This module is the shared contract: both sides use these helpers
to read/write structured notes that the other side can consume.

API:
  - curate_chat(notes: dict) -> Path
  - write_escalation(reason: str, request: str) -> Path
  - update_taste_profile(updates: dict) -> None
  - read_recent_curations(limit: int = 10) -> list[dict]
  - read_pending_escalations() -> list[Path]

Files written here go in: ~/wiki/pet-curated/
Files in: ~/wiki/pet-curated/escalations/
The taste profile lives at: ~/wiki/pet-curated/taste.yaml

This is a LIBRARY, not an agent. Import from both sides of the handoff.
"""
from __future__ import annotations
import os
import json
import yaml
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_NOTES_DIR = Path("~/wiki/pet-curated").expanduser()
ESCALATIONS_DIRNAME = "escalations"
TASTE_FILENAME = "taste.yaml"


def notes_dir() -> Path:
    """The pet-curated notes directory. Created on first call."""
    DEFAULT_NOTES_DIR.mkdir(parents=True, exist_ok=True)
    return DEFAULT_NOTES_DIR


def escalations_dir() -> Path:
    """Subdirectory for escalation requests. Created on first call."""
    p = notes_dir() / ESCALATIONS_DIRNAME
    p.mkdir(parents=True, exist_ok=True)
    return p


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _frontmatter(d: dict) -> str:
    """Render a dict as YAML frontmatter delimited by ---."""
    return "---\n" + yaml.safe_dump(d, sort_keys=False, allow_unicode=True) + "---\n"


def _slugify(s: str, max_len: int = 60) -> str:
    """Make a string filesystem-safe."""
    import re
    s = re.sub(r"[^a-zA-Z0-9_-]+", "-", s.strip().lower())
    s = re.sub(r"-+", "-", s).strip("-")
    return (s or "note")[:max_len]


def curate_chat(notes: dict, trigger: str = "chat", vibe: str = "neutral") -> Path:
    """
    Write a curation note. The dict can have any structure, but recommended:
      {
        "user_interests_surfaced": [...],
        "project_ideas_proposed": [...],
        "open_questions": [...],
        "taste_signal": {...},
      }
    Returns the path of the file written.
    """
    fm = {
        "curated_at": _now_iso(),
        "trigger": trigger,
        "vibe": vibe,
        "schema_version": 1,
    }
    slug = _slugify(notes.get("title", "") or notes.get("topic", "") or trigger)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    out = notes_dir() / f"{ts}-{slug}.md"

    body = _frontmatter(fm) + "\n"
    if "title" in notes or "topic" in notes:
        body += f"# {notes.get('title') or notes.get('topic')}\n\n"
    for k, v in notes.items():
        if k in ("title", "topic"):
            continue
        body += f"## {k.replace('_', ' ').title()}\n"
        if isinstance(v, list):
            for item in v:
                body += f"- {item}\n"
        elif isinstance(v, dict):
            for kk, vv in v.items():
                body += f"- **{kk}**: {vv}\n"
        else:
            body += f"{v}\n"
        body += "\n"

    out.write_text(body, encoding="utf-8")
    return out


def write_escalation(reason: str, request: str, context: dict | None = None) -> Path:
    """
    Write an escalation request for Hermes main to handle.
    Reasons: needs_code_execution, needs_terminal, needs_delegation, needs_file_modification
    """
    fm = {
        "curated_at": _now_iso(),
        "reason": reason,
        "status": "pending",
    }
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    slug = _slugify(reason)
    out = escalations_dir() / f"{ts}-{slug}.md"

    body = _frontmatter(fm) + "\n## User request\n\n" + request.strip() + "\n"
    if context:
        body += "\n## Context\n\n```yaml\n" + yaml.safe_dump(context, sort_keys=False, allow_unicode=True) + "```\n"
    body += "\n## Why escalated\n\nOut of scope for the curator profile.\n"

    out.write_text(body, encoding="utf-8")
    return out


def update_taste_profile(updates: dict) -> None:
    """
    Merge updates into ~/wiki/pet-curated/taste.yaml.
    Updates are merged shallow (top-level keys replaced, not deep-merged).
    """
    path = notes_dir() / TASTE_FILENAME
    if path.exists():
        with open(path) as f:
            current = yaml.safe_load(f) or {}
    else:
        current = {
            "created_at": _now_iso(),
            "last_updated": _now_iso(),
            "music": {"likes": [], "skips": [], "vibes": []},
            "visuals": {"aesthetics": [], "color_palettes": []},
            "topics": {"active": [], "recurring": []},
            "projects": {"active": [], "completed": []},
        }

    current["last_updated"] = _now_iso()
    for k, v in updates.items():
        if isinstance(v, dict) and isinstance(current.get(k), dict):
            current[k].update(v)
        else:
            current[k] = v

    with open(path, "w") as f:
        yaml.safe_dump(current, f, sort_keys=False, allow_unicode=True)


def _parse_note(path: Path) -> dict | None:
    """Parse a markdown file with YAML frontmatter into a dict."""
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return None
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end < 0:
        return None
    try:
        fm = yaml.safe_load(text[4:end])
    except Exception:
        return None
    if not isinstance(fm, dict):
        return None
    fm["_path"] = str(path)
    return fm


def read_recent_curations(limit: int = 10) -> list[dict]:
    """Read the most recent curation notes, newest first."""
    files = sorted(notes_dir().glob("*.md"), reverse=True)
    out = []
    for f in files[:limit]:
        note = _parse_note(f)
        if note:
            out.append(note)
    return out


def read_pending_escalations() -> list[Path]:
    """List escalation files that haven't been acted on yet."""
    out = []
    for f in sorted(escalations_dir().glob("*.md"), reverse=True):
        note = _parse_note(f)
        if note and note.get("status") == "pending":
            out.append(f)
    return out


if __name__ == "__main__":
    # CLI mode for quick testing
    import sys
    if len(sys.argv) < 2:
        print("Usage: wiki_handoff.py [curate|escalate|taste|recent|pending] [args...]")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "curate":
        # Read notes JSON from stdin
        notes = json.loads(sys.stdin.read())
        path = curate_chat(notes)
        print(f"Wrote {path}")
    elif cmd == "escalate":
        reason = sys.argv[2]
        request = sys.stdin.read() if not sys.stdin.isatty() else "(no request)"
        path = write_escalation(reason, request)
        print(f"Wrote {path}")
    elif cmd == "taste":
        updates = json.loads(sys.stdin.read())
        update_taste_profile(updates)
        print(f"Updated {notes_dir() / TASTE_FILENAME}")
    elif cmd == "recent":
        for n in read_recent_curations():
            print(f"  {n.get('curated_at', '?')} [{n.get('trigger', '?')}] {n.get('_path', '?')}")
    elif cmd == "pending":
        for p in read_pending_escalations():
            print(f"  {p}")
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
