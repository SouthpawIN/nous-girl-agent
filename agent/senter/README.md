# Senter — Triage Orchestrator (Hermes profile)

Senter is the on-demand triage agent. It reads curated notes from
`~/wiki/pet-curated/`, recent escalations, and the user's active
projects, then returns a prioritized "what should I focus on?" list.

## Setup

This profile is a custom Hermes profile. Install:

```bash
# From the nous-girl-agent repo root
hermes profile create senter --template agent/senter-profile.yaml
hermes run --profile senter
```

## Trigger

Say any of:
- "triage my inbox"
- "what should I focus on?"
- "what now?"
- "prioritize my day"
- "queue me up"

Senter responds with a numbered list (1-5 items) of prioritized actions,
each tagged with one of: `[execute]`, `[escalate]`, `[defer]`, `[archive]`.

## Behavior

- **Read-only by default.** Senter decides; it doesn't execute.
- **Suggestions to escalate** come pre-formed for Hermes main.
- **Memory is the wiki.** Senter doesn't keep its own state — it reads
  `~/wiki/pet-curated/recent/` and `~/wiki/pet-curated/escalations/`.

## Output format

```markdown
# Triage — <date>

## Top priority (today)
1. [execute] Build a CLI tool that does X — was escalated 2 hours ago
2. [execute] Review the OmniSenter architecture post before training finishes

## This week
3. [escalate] Decide on sparse upcycling strategy — needs code review
4. [defer] Curate the new eikon for the multimodal variant

## Archive
5. [archive] Stale todo from 3 days ago — no longer relevant
```

## Why this profile

The Nous Girl agent is *curation* — it surfaces ideas. Senter is
*prioritization* — it tells you what to do. Together with Hermes
main (execution), that's the three-tier agent system:

```
Nous Girl agent (curation)  →  Senter (prioritization)  →  Hermes main (execution)
            ↑                                                            ↓
            └────────── writes notes to wiki ──────────────────────────┘
```

## Files

- `senter-profile.yaml` — the Hermes profile definition
- `senter-triage.md` — the persona prompt (also in agent/prompts/)

## See also

- `agent/profile-template.yaml` — the curator profile (Nous Girl agent)
- `wiki-handoff/wiki_handoff.py` — the shared handoff library
- `agent/prompts/nous-girl-curator.md` — the curator persona
