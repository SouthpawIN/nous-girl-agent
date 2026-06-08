# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial repo skeleton with vendored Open-LLM-VTuber (vtuber-core/)
- Curated model catalog (models/curated.yaml) with 7 real model entries
- Suggested model candidates (models/suggested.yaml) for promotion
- Nous Girl eikon sprite (pet/sprites/nous-girl/) with 6 state variants
- Nous Girl character config (vtuber-core/characters/nous-girl.yaml)
- Right-click context menu (pet/menus/nous-girl.yaml)
- Three agent prompts: nous-girl-curator, radio-curator, senter-triage
- Wiki handoff library (wiki-handoff/wiki_handoff.py) for pet <-> Hermes
- Radio bridge (plugins/evolution-radio/radio_bridge.py) closing the curation loop
- Vendored evolutionary-radio upstream (plugins/evolution-radio/upstream/)
- Launchers: install.sh, dev.sh, run-pet.sh, run-radio.sh, run-agent.sh
- Tests: tests/test_wiki_handoff.py (unittest, zero deps)
- CI: .github/workflows/ci.yml (lint + test + yaml validation)
- Docs: ARCHITECTURE.md, INSTALL.md, TROUBLESHOOTING.md, EIKON_FORMAT.md, MODEL_FORMAT.md
- AGENTS.md: guidance for future AI agents working in this repo

### Fixed
- 23 broken `file://` cross-references across 7 files in 2 GitHub repos

## [0.1.0] - 2026-06-08

Initial public release. Repo at https://github.com/SouthpawIN/nous-girl-agent.

[Unreleased]: https://github.com/SouthpawIN/nous-girl-agent/compare/main...HEAD
