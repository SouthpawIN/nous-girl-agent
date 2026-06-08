# AGENTS.md — guidance for AI agents working in this repo

This file tells AI agents (Claude Code, OpenCode, Codex, future-me) how
to behave when working in the Omni VA repo.

## Project overview

A curated local-model desktop VA + the OmniStep Evolution Radio plugin.
Two-tier agent architecture:
- Tier 1: VA (Omni VA curator, headless) — limited toolset, notes/curates
- Tier 2: Hermes main agent — full toolset, executes on the VA's notes

The VA runs a local model from `models/curated.yaml` (hand-curated by mu)
and serves it via the forked Open-LLM-VTuber in `vtuber-core/`. The
evolutionary-radio plugin lives in `plugins/evolution-radio/`.

## Repo map

```
nous-assistant-agent/
├── README.md                # project overview
├── ARCHITECTURE.md          # deep architecture
├── INSTALL.md               # install + run
├── .github/workflows/ci.yml # CI: lint + tests + yaml validation
├── vtuber-core/             # vendored Open-LLM-VTuber (DO NOT MODIFY)
├── agent/                   # Hermes profile templates + agent prompts
│   ├── profile-template.yaml
│   └── prompts/
│       ├── nous-assistant-curator.md  # the curator persona
│       ├── radio-curator.md      # headless ambient curator
│       └── senter-triage.md      # on-demand triage
├── VA/                     # VA-specific config (sprites, menus, launcher)
│   ├── sprites/nous-assistant/   # eikon assets (vendored from herm-tui)
│   └── menus/nous-assistant.yaml # right-click menu definitions
├── models/                  # curated model catalog
│   ├── curated.yaml         # active entries (hand-picked)
│   └── suggested.yaml       # candidates
├── plugins/evolution-radio/ # the radio plugin
│   ├── upstream/            # vendored radio.py + code/ (DO NOT MODIFY)
│   └── radio_bridge.py      # bridge: wiki <-> radio
├── wiki-handoff/
│   ├── wiki_handoff.py      # shared handoff library
│   └── README.md            # schema + usage
├── docs/                    # TROUBLESHOOTING, EIKON_FORMAT, MODEL_FORMAT
├── scripts/                 # install.sh, dev.sh, run-*.sh launchers
└── tests/                   # pytest-style tests for wiki_handoff + radio_bridge
```

## What you should NOT do

1. **Do not modify `vtuber-core/` directly.** It's vendored from
   Open-LLM-VTuber. To upgrade: re-vendor from upstream, don't hand-edit.
2. **Do not modify `plugins/evolution-radio/upstream/` directly.** Same
   reason — vendored from the evolutionary-radio repo. To upgrade: re-vendor.
3. **Do not auto-add models to `curated.yaml`.** The catalog is hand-curated
   by mu. Add candidates to `suggested.yaml` and let mu promote.
4. **Do not touch the user's `~/wiki/pet-curated/`** without explicit
   permission — only write files there via the `wiki_handoff` API.
5. **Do not run the VA or radio daemon during active training.** The
   Stage 1 SFT is currently running on GPU 0+1. The VA + radio consume
   GPU. Always check `nvidia-smi` before starting a server.

## What you SHOULD do

1. **Run tests** before pushing: `python3 -m unittest discover -s tests`
2. **Validate YAML** before pushing: `python3 -c "import yaml; yaml.safe_load(open('models/curated.yaml'))"`
3. **Update both the wiki and the README** when adding new features
4. **Commit often with clear messages** — Chris wants constant GitHub updates
5. **Speak over voice when Chris asks** — the TTS bubble in the chat
   delivers audio; Chris is on a Surface Duo via SSH

## Architectural rules

- **One-way wiki handoff.** VA writes to `~/wiki/pet-curated/`, Hermes
  main reads. VA cannot trigger Hermes. User stays in control.
- **No code execution in the curator profile.** Curator is bounded to
  web + file (notes dir only) + skills. Use escalations for everything else.
- **Multimodal default falls back gracefully.** OmniStep / Qwen-Omni =
  full multimodal. Text-only LLMs fall back to Edge TTS + playlist.
- **Eikon is a visual layer, not a model.** The model is the brain. Swap
  models in the catalog → VA's whole personality swaps.

## Tooling preferences

- `uv` for Python deps (faster than pip)
- `ruff` for Python linting
- `gh` CLI for GitHub operations
- `mpv` for audio playback
- `git` for version control (no SVN, no Mercurian)

## Style

- Match Nous brand for any visual asset (monochrome + cosmic variant)
- "TOWARDS SELF-IMPROVEMENT." tagline for major doc headers
- Use the existing folder structure — don't create new top-level dirs
  without a really good reason

## CI

`.github/workflows/ci.yml` runs on every push to main. It:
- Lints `wiki-handoff/wiki_handoff.py` and `plugins/evolution-radio/radio_bridge.py`
- Runs `tests/test_wiki_handoff.py` (unittest, not pytest, for zero deps)
- Validates `models/curated.yaml`, `models/suggested.yaml`, `agent/profile-template.yaml`

If you break the CI, fix it before merging.
