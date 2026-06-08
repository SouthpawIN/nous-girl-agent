# Nous Girl Agent & OmniStep Evolution Radio Plugin

> **TOWARDS SELF-IMPROVEMENT** — *curated by mu*

A standalone, voice-interactive, ever-evolving desktop pet that serves as a **curated local-model server manager**. The pet is the face of the model — voice and music come *from the model itself*, with a graceful fallback to Edge TTS and curated playlists when you swap to a text-only LLM.

The **OmniStep Evolution Radio** lives as a plugin inside the agent. It's a perpetual radio that watches what you engage with, builds playlists reflecting your taste, trains LoRAs on what you like, and feeds the **Ohm** evolutionary chain for self-improvement. Notes the agent curates are handoff-ready to **Hermes Agent** for execution.

---

## What's in the box

| Component | What it does |
|---|---|
| **Pet** (forked from Open-LLM-VTuber) | Live2D desktop companion, draggable, always-on-top, click-through mode. Voice in/out, screen vision, chat log persistence. |
| **Nous Girl Agent** | Minimal-toolset Hermes profile: web search, web fetch, file write (notes), social media. Asks questions, takes notes, curates your taste. |
| **OmniStep Evolution Radio** | Perpetual playlist loop. Listens to what you skip/like, generates new music (HeartMuLa / ACE-Step), trains LoRAs, evolves via Ohm. |
| **Model Catalog** | Hand-curated YAML of local models, API combos, and auxiliary combos. Each entry pairs an eikon, a voice, and capability flags. |
| **Wiki Handoff** | The pet writes notes to a structured wiki. Hermes main agent reads them as input for execution. |
| **Eikons** | Live2D sprite library. Nous Girl is default. Swap eikon → swap pet character + voice + personality. |

---

## The two-tier architecture

```
┌─────────────────────────────────────────────────────────────┐
│ Tier 1 — PET (Nous Girl Agent)                              │
│  • Always-on, low-stakes, ambient                            │
│  • Tools: web search, web fetch, notes, social media         │
│  • Asks questions, curates, runs the radio                   │
│  • Multimodal by default (Omni-Step = text+voice+music)      │
│  • Falls back to Edge TTS/Jenny + playlist for text models   │
└─────────────────────────────────────────────────────────────┘
                              │  wiki handoff
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ Tier 2 — HERMES AGENT (full toolset)                        │
│  • Heavyweight, on-demand                                    │
│  • Reads pet's curated wiki → executes ideas                 │
│  • Code, terminal, delegation, computer use — all enabled    │
└─────────────────────────────────────────────────────────────┘
```

The pet is the **taste curator**. Hermes is the **action executor**. The wiki is the **handoff layer**. Music is the visible proof the curation loop is healthy.

---

## Default model: OmniStep

**OmniStep is multimodal native.** Text in, text+voice+music out. One model. The pet doesn't *call* Omni-Step — the pet *is* your way of experiencing Omni-Step's full capability.

**Fallback ladder** (when user picks a different model):
1. **Multimodal native** (OmniStep, OmniSenter) → text + voice + music from model
2. **Text LLM + Edge TTS** (any GGUF / OpenAI-compat) → text + voice (Jenny/JennyNeural) + pre-curated playlist
3. **API combo via Nous Portal** → text from API + voice from Edge TTS + playlist

The model catalog flags which tier each model falls into.

---

## Repo layout

```
nous-girl-agent/
├── README.md                  ← you are here
├── ARCHITECTURE.md            ← deep architecture doc
├── INSTALL.md                 ← install + run
├── vtuber-core/               ← forked Open-LLM-VTuber (pet UI, Live2D, ASR, TTS)
├── agent/                     ← Nous Girl agent (Hermes profile, prompts, voice)
├── pet/                       ← pet-specific config (sprites, menus, launcher)
├── models/                    ← curated model catalog (YAML)
│   ├── local/                 ← hand-picked local GGUF models
│   ├── api/                   ← API combos via Nous Portal
│   └── auxiliary/             ← auxiliary combos (e.g. pet = local, escalation = API)
├── plugins/
│   └── evolution-radio/       ← the radio plugin (perpetual loop, LoRAs, Ohm)
├── wiki-handoff/              ← pet → Hermes main wiki handoff layer
├── docs/                      ← additional documentation
└── scripts/                   ← install, run, dev scripts
```

---

## Quick start (placeholder — full INSTALL.md coming)

```bash
# 1. Clone
git clone https://github.com/SouthpawIN/nous-girl-agent
cd nous-girl-agent

# 2. Install vtuber-core
cd vtuber-core && uv sync && cd ..

# 3. Pick a model from models/curated.yaml
# 4. Run
cd vtuber-core && uv run run_server.py
```

---

## Model catalog philosophy

The catalog is **hand-curated, not auto-scraped**. Each entry is a deliberate choice — a model you trust, paired with an eikon you vibe with, with a voice that fits. Add entries to `models/curated.yaml`. Suggestions live in `models/suggested.yaml` for you to pick from.

```yaml
- id: omni-step
  display_name: OmniStep
  tier: multimodal-native           # multimodal-native | text-with-tts | api-combo
  backend: llama.cpp                 # llama.cpp | ollama | openai-compat | nous-portal
  model_path: ~/models/omni-step.gguf
  default: true
  eikon: nous-girl
  voice:
    source: model                    # model | edge-tts | melotts | cosyvoice
    edge_voice: en-US-JennyNeural    # fallback
  music:
    source: model                    # model | heartmula | playlist | none
    playlist: plugins/evolution-radio/playlists/default.json
  capabilities: [text, voice, music]
```

---

## License

- `vtuber-core/`: MIT (inherited from Open-LLM-VTuber)
- Live2D assets: see `vtuber-core/LICENSE-Live2D.md`
- Everything else in this repo: MIT

---

## Status

- ✅ Broken `file://` links across 9 repos — fixed
- ✅ Repo skeleton created
- ✅ Open-LLM-VTuber vendored into `vtuber-core/`
- 🔄 Curated model catalog — scaffolding only, awaiting your entries
- 🔄 Evolutionary-radio plugin — architecture documented, implementation pending
- 🔄 Nous Girl eikon — sprite swap pending

The full Stage 1 SFT training is running uninterrupted on GPU 0+1.
