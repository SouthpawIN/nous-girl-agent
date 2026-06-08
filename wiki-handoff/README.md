# Wiki Handoff

This directory contains the contract between the VA's curator agent
(Omni VA, headless) and Hermes main agent (full toolset).

## Direction

**One-way: VA → Hermes main.**

The VA writes to `~/wiki/pet-curated/` (configured in `agent/profile-template.yaml`).
Hermes main agent reads from there on user request.

## Files

- `wiki_handoff.py` — shared library used by both sides of the handoff
- `README.md` — this file

## Quick start

### From the VA (Omni VA curator agent)

```python
from wiki_handoff import curate_chat, write_escalation, update_taste_profile

# Write a curation note
curate_chat({
    "title": "OmniSenter architecture chat",
    "user_interests_surfaced": [
        "Wants to merge 8B models into 24A8B via sparse upcycling",
        "Likes evolutionary-training theme",
    ],
    "project_ideas_proposed": [
        "32A8B MoE: 5-6 experts/layer, 8B active, top-1 routing",
    ],
    "open_questions": [
        "When to switch from text-LLM OmniStep to multimodal-native?",
    ],
}, trigger="chat", vibe="curious-exploratory")

# Escalate to Hermes main
write_escalation(
    reason="needs_code_execution",
    request="Build a CLI tool that does X",
)

# Update the taste profile
update_taste_profile({
    "music": {"vibes": ["ambient", "generative", "low-tempo"]},
    "topics": {"active": ["omnisenter", "sparse-upcycling"]},
})
```

### From Hermes main

```python
from wiki_handoff import read_recent_curations, read_pending_escalations

# Read recent curations
for note in read_recent_curations(limit=20):
    print(note["curated_at"], note.get("trigger"), note.get("vibe"))

# Check pending escalations
for path in read_pending_escalations():
    print("Escalation pending:", path)
```

Or from the shell:

```bash
# List recent curations
python3 wiki-handoff/wiki_handoff.py recent

# List pending escalations
python3 wiki-handoff/wiki_handoff.py pending

# Curation: pipe a JSON note to stdin
echo '{"title":"foo","user_interests_surfaced":["bar"]}' | \
    python3 wiki-handoff/wiki_handoff.py curate
```

## Schema

Each curation file is markdown with YAML frontmatter:

```yaml
---
curated_at: 2026-06-08T18:30:00+00:00
trigger: chat | web | social | radio
vibe: curious-exploratory | focused-building | restful-ambient
schema_version: 1
---
## User Interests Surfaced
- ...

## Project Ideas Proposed
- ...
```

Plus one persistent file: `taste.yaml` — the accumulated taste profile,
updated on every curation run.

## Why this shape

- **Filesystem = API.** Both agents run locally. Shared filesystem is the
  simplest possible interface. No RPC, no service discovery, no auth.
- **YAML frontmatter is greppable.** Hermes main can quickly filter by
  `trigger`, `vibe`, `projects_touched`, etc. without parsing the body.
- **One-way means no loops.** VA can't trigger Hermes. User stays in control.
- **No new schema = no migration hell.** It's just markdown + YAML.
