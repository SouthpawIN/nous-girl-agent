# Architecture

## The big idea

A **curated multimodal desktop pet** is the entry point to a two-tier agent system. The pet is intentionally limited — it's a *taste curator*, not a code executor. Notes the pet curates become the input corpus for Hermes main agent to act on.

The pet runs a local model server (llama.cpp / ollama / any OpenAI-compatible backend) and *is* the way you experience that model. With OmniStep as default, the model is multimodal native — text, voice, and music all come from the same forward pass. With a text-only model, the pet falls back to Edge TTS for voice and a curated playlist for music. The fallback is invisible to the user — the pet still *feels* alive.

## Component diagram

```
┌──────────────────────────────────────────────────────────────────┐
│ USER DESKTOP                                                      │
│                                                                   │
│  ┌────────────────┐         ┌──────────────────────┐             │
│  │  Live2D Pet    │◄────────┤  Open-LLM-VTuber     │             │
│  │  (transparent, │  WS     │  Server (FastAPI)    │             │
│  │   draggable)   │         │  - ASR (Whisper)     │             │
│  └────────────────┘         │  - TTS (Edge/Model)  │             │
│                             │  - LLM client        │             │
│                             │  - Live2D renderer   │             │
│                             └──────────┬───────────┘             │
│                                        │                         │
│                            OpenAI-compat API                     │
│                                        │                         │
│  ┌─────────────────────────────────────▼─────────────────────┐   │
│  │  LOCAL MODEL SERVER (llama.cpp / ollama / etc.)            │   │
│  │  Default: OmniStep (text + voice + music outputs)          │   │
│  │  Fallback: any text LLM (TTS via Edge, music via playlist)│   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  EVOLUTIONARY-RADIO PLUGIN (sibling process)               │   │
│  │  - Monitors chat history + audio engagement               │   │
│  │  - Builds playlists reflecting taste                       │   │
│  │  - HeartMuLa / ACE-Step for live generation                │   │
│  │  - LoRA self-training on liked tracks                      │   │
│  │  - Ohm chain for weight evolution                          │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  NOUS GIRL AGENT (Hermes profile, headless)                │   │
│  │  - Toolset: web search, web fetch, file write, social      │   │
│  │  - Continuous Q&A about user interests                     │   │
│  │  - Writes notes to ~/wiki/pet-curated/                     │   │
│  └─────────────────────┬──────────────────────────────────────┘   │
└────────────────────────┼──────────────────────────────────────┘
                         │  one-way wiki handoff
                         ▼
         ┌───────────────────────────────────────┐
         │  ~/wiki/pet-curated/                  │
         │  - structured YAML/notes              │
         │  - taste profile, project ideas       │
         └───────────────────┬───────────────────┘
                             │
                             ▼  Hermes main reads on demand
         ┌───────────────────────────────────────┐
         │  HERMES AGENT (full toolset)          │
         │  - terminal, code, delegation, etc.   │
         │  - reads pet-curated wiki             │
         │  - executes on the ideas              │
         └───────────────────────────────────────┘
```

## Why this shape

- **Pet is constrained on purpose.** A small toolset means it can't accidentally do something dangerous or expensive. It can *think* and *note*, but not *act*. This is also why the wiki handoff is one-way — the pet doesn't trigger Hermes. The user does.
- **Multimodal-native default.** OmniStep being text+voice+music in one model means the pet's "personality" is actually the model's behavior, not a stitched-together illusion. When you swap models, the pet's whole vibe changes — voice, music taste, conversational style. Eikon is the visual layer, model is the behavioral layer.
- **Evolutionary-radio as plugin, not feature.** It's a sibling process the pet orchestrates. Decoupled from chat model. The radio can run ambient (pre-gen playlist) when GPU is busy (e.g. training) or live-generative when idle.
- **Curated catalog.** This isn't a "model browser." The catalog is a small, deliberate set of models you've hand-picked. Each entry is a recommendation, not an option. The user picks from your curation, not from "every model on HF."

## The two-tier contract

The pet writes to `~/wiki/pet-curated/` (or any path you configure). The structure is simple:

```yaml
# ~/wiki/pet-curated/2026-06-08-evening.md
---
curated_at: 2026-06-08T18:30:00
trigger: chat
vibe: curious-exploratory
---
## User interests surfaced
- Wants to merge 8B models into 24A8B or 32A8B via sparse upcycling
- Likes evolutionary-training as a theme
- Currently training Stage 1 SFT on Qwen3-8B base

## Project ideas proposed
- 32A8B MoE: 5-6 experts per layer, 8B active, top-1 routing
- Synthesia layer for cross-modal memory
- Ohm chain for self-evolving weights

## Open questions
- When to switch from text-LLM OmniStep to multimodal-native?

## Taste signal
- Music: ambient, generative, low-tempo
- Visual: monochrome, retro manga, cosmic
```

Hermes main agent reads these on user request and converts them into concrete plans/code/PRs. The pet *never* writes back. Hermes *can* (in theory) write back, but that's not in scope for v1.

## Eikon as identity

Each model in the catalog has an `eikon` field. The eikon is a Live2D sprite + a persona prompt + a voice. When you swap models, the pet's whole identity swaps. This is the "vibe conductor" pattern from the existing Nous Girl agent work — the model is the brain, the eikon is the face, together they are the pet.

Default eikon: Nous Girl (already exists in the eikon work).
Other eikons: can be added to `pet/sprites/` and registered in the catalog.

## Evolutionary-radio coupling

The radio listens to:
- Which model the user is chatting with (for vibe matching)
- What the user types (NLP extract mood/genre)
- Which tracks the user skips vs. plays through
- Time of day, day of week

The radio generates:
- LoRA candidates (one per vibe cluster)
- Hourly playlist updates
- Weekly Ohm evolution runs

GPU policy:
- **Training active (e.g. Stage 1 SFT):** radio runs in ambient mode (pre-gen, no live generation)
- **Training idle:** radio can run live generative mode
- **Override:** user can force live-gen even during training (config flag)

## Status

- Architecture documented ✅
- Repo skeleton ✅
- vtuber-core vendored ✅
- Model catalog schema documented (in README) ✅
- Curated model entries: empty (awaiting mu)
- Plugin implementation: pending
- Wiki handoff: scaffolded
