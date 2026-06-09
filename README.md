# Omni VA

**The desktop VA, the local model server, the OmniStep Evolution Radio, the curator agent, the Senter triage profile — all in one stack.**

> TOWARDS SELF-IMPROVEMENT · curated by mu

A standalone, voice-interactive, ever-evolving desktop VA that serves as a **curated local-model server manager**. The VA is the face of the model — voice and music come *from the model itself*, with a graceful fallback to Edge TTS and curated playlists when you swap to a text-only LLM.

The **OmniStep Evolution Radio** lives as a plugin inside the agent. It's a perpetual radio that watches what you engage with, builds playlists reflecting your taste, trains LoRAs on what you like, and feeds the Ohm evolutionary chain for self-improvement. Notes the agent curates are handoff-ready to **Hermes Agent** for execution.

**This is the front door for the personal site:** https://southpawin.github.io/

---

## What's in the box

| Component | What it does | Install |
|---|---|---|
| **VA** (forked from Open-LLM-VTuber) | Live2D desktop companion, voice in/out, chat log persistence | `./scripts/install.sh && ./scripts/run-assistant.sh` |
| **Omni VA curator** | Headless Hermes profile: web, fetch, notes, social. Writes to `~/wiki/pet-curated/`. | `hermes profile install github.com/SouthpawIN/nous-girl-agent/agent --name evolutionary-radio` |
| **Senter triage** | On-demand prioritization tier. Reads wiki, returns ranked list. | `hermes profile install github.com/SouthpawIN/nous-girl-agent/agent/senter --name senter` |
| **OmniStep Evolution Radio** | Perpetual radio plugin. Self-evolving playlists. LoRAs. Ohm chain. | `./scripts/run-radio.sh start` |
| **Model catalog** | Hand-curated YAML of local + API + auxiliary models. | Edit `models/curated.yaml` |
| **Wiki handoff** | Shared library for VA ↔ Hermes main. | `wiki-handoff/wiki_handoff.py` |
| **Eikons** | Live2D sprite library. Omni VA is default. | `assistant/sprites/` |
| **Launchers** | `install.sh`, `dev.sh`, `run-assistant.sh`, `run-radio.sh`, `run-agent.sh` | `scripts/` |

---

## Quick start

```bash
# 1. Clone
git clone https://github.com/SouthpawIN/nous-girl-agent
cd nous-girl-agent

# 2. Install
./scripts/install.sh

# 3. Run everything (VA + radio + agent + bridge, with logs)
./scripts/dev.sh

# Or run individually:
./scripts/run-assistant.sh     # the Live2D VA
./scripts/run-radio.sh start  # the radio plugin
./scripts/run-agent.sh   # the curator agent
```

---

## The two-tier architecture

```
┌─────────────────────────────────────────────────────────────┐
│ Tier 1 — VA (Omni VA)                              │
│  • Always-on, low-stakes, ambient                            │
│  • Tools: web search, web fetch, notes, social media         │
│  • Asks questions, curates, runs the radio                   │
│  • Multimodal by default (OmniStep = text+voice+music)      │
│  • Falls back to Edge TTS/Jenny + playlist for text models   │
└─────────────────────────────────────────────────────────────┘
                              │  wiki handoff
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ Tier 2 — HERMES AGENT (full toolset)                        │
│  • Heavyweight, on-demand                                    │
│  • Reads VA's curated wiki → executes ideas                 │
│  • Code, terminal, delegation, computer use — all enabled    │
└─────────────────────────────────────────────────────────────┘
```

Three tiers, actually: **Omni VA (curation) → Senter (prioritization) → Hermes main (execution)**. Senter sits between curation and execution as an on-demand triage step.

---

## Default model: OmniStep

**OmniStep (Qwen2.5-Omni-3B)** is multimodal native — text + voice + vision in, text + voice out. One model. Falls back to Edge TTS Jenny for voice and the curated playlist for music when you swap in a text-only LLM.

The catalog (`models/curated.yaml`) has 8 entries:

| Tier | Models |
|---|---|
| **multimodal-native** | Qwen2.5-Omni-3B (default), OmniStep (pending flagship) |
| **text-with-tts** | Darwin-28B, APEX-MTP, Qwen3-Coder-30B-A3B, Qwen3.5-27B-Claude, Qwen3.5-27B-Sushi, Qwen3.5-35B-A3B |
| **auxiliary** | OmniSenter (pending Stage 1) |

Each entry pairs a model with an eikon, a voice, and capability flags.

---

## Repo layout

```
nous-girl-agent/
├── README.md                  ← you are here
├── ARCHITECTURE.md            ← deep architecture doc
├── INSTALL.md                 ← install + run
├── CHANGELOG.md               ← version history
├── AGENTS.md                  ← rules for future AI agents
├── .github/workflows/ci.yml   ← CI: lint + tests + yaml validation
├── vtuber-core/               ← vendored Open-LLM-VTuber (VA UI, Live2D, ASR, TTS)
├── agent/                     ← Omni VA curator + Senter triage profiles
│   ├── distribution.yaml      ← installable as 'evolutionary-radio' profile
│   ├── profile-template.yaml
│   ├── prompts/               ← personas
│   ├── senter/                ← Senter profile
│   └── voice/                 ← TTS configs
├── VA/                       ← VA-specific config
│   ├── sprites/omni-va/     ← eikon assets
│   └── menus/omni-va.yaml   ← right-click menu
├── models/                    ← curated model catalog
│   ├── curated.yaml           ← hand-picked entries
│   └── suggested.yaml         ← candidates
├── plugins/
│   └── evolution-radio/       ← the radio plugin (real Hermes plug-in)
│       ├── upstream/          ← vendored radio.py + code/
│       ├── radio_bridge.py    ← wiki <-> radio bridge
│       ├── evolution_radio_plugin.py  ← Hermes plug-in entry
│       └── SKILL.md           ← evolution-radio skill
├── wiki-handoff/
│   ├── wiki_handoff.py        ← shared handoff library
│   └── README.md
├── docs/                      ← TROUBLESHOOTING, EIKON_FORMAT, MODEL_FORMAT
├── scripts/                   ← install.sh, dev.sh, run-*.sh
└── tests/                     ← pytest-style tests
```

---

## License

- `vtuber-core/`: MIT (inherited from Open-LLM-VTuber)
- Live2D assets: see `vtuber-core/LICENSE-Live2D.md`
- Everything else: MIT

---

## See also

- **Personal site:** https://southpawin.github.io/
- **Blog:** https://southpawin.github.io/blog/
- 📚 **Master wiki + blog catalog:** [evolutionary-training/wiki](https://github.com/SouthpawIN/evolutionary-training/blob/master/wiki/README.md) — the consolidated knowledge base for the OmniSenter project, in catalog order.
- **OmniSenter pipeline:** https://github.com/SouthpawIN/evolutionary-training
- **Evolutionary Radio (upstream):** https://github.com/SouthpawIN/evolutionary-radio
- **Hermes Agent:** https://github.com/SouthpawIN/hermes-agent
