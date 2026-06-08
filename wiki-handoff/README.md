# Wiki Handoff

This directory contains the contract between the pet's curator agent
(Nous Girl agent, headless) and Hermes main agent (full toolset).

## Direction

**One-way: pet → Hermes main.**

The pet writes to `~/wiki/pet-curated/` (configured in `agent/profile-template.yaml`).
Hermes main agent reads from there on user request.

## Schema

Each file in `pet-curated/` is a markdown file with YAML frontmatter:

```yaml
---
curated_at: 2026-06-08T18:30:00
trigger: chat | web | social | radio
vibe: curious-exploratory | focused-building | restful-ambient
projects_touched: [omnisenter, nous-girl-agent]
---
## User interests surfaced
- ...

## Project ideas proposed
- ...

## Open questions
- ...

## Taste signal
- ...
```

Plus one persistent file: `taste.yaml` — the accumulated taste profile,
updated on every curation run.

## Escalation

If the pet's toolset is too limited (user asks for code execution, terminal,
etc.), the pet writes to `~/wiki/pet-curated/escalations/<timestamp>.md`:

```yaml
---
curated_at: 2026-06-08T18:30:00
reason: needs_code_execution
---
## User request
Build a CLI tool that does X

## Why escalated
Out of scope for curator profile (no terminal access).
```

Hermes main agent can list and act on escalations.

## Why this shape

- **Filesystem = API.** Both agents run locally. Shared filesystem is the
  simplest possible interface. No RPC, no service discovery, no auth.
- **YAML frontmatter is greppable.** Hermes main can quickly filter by
  `projects_touched`, `vibe`, etc. without parsing the body.
- **One-way means no loops.** Pet can't trigger Hermes. User stays in control.
