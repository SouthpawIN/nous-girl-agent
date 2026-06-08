# Architecture

## The big idea

A **curated multimodal desktop assistant** is the entry point to a three-tier agent system. The VA is intentionally limited — it's a *taste curator*, not a code executor. Notes the VA curates become the input corpus for Senter (prioritization), then Hermes main (execution).

The VA runs a local model server (llama.cpp / ollama / any OpenAI-compatible backend) and *is* the way you experience that model. With OmniStep as default, the model is multimodal native — text, voice, and music all come from the same forward pass. With a text-only model, the VA falls back to Edge TTS for voice and a curated playlist for music. The fallback is invisible to the user — the VA still *feels* alive.

## Three-tier agent system

```
┌──────────────────────────────────────────────────────────────────┐
│ Tier 1 — Omni VA (curation)                              │
│  • Always-on, low-stakes, ambient                                │
│  • Tools: web search, fetch, file (notes), social                │
│  • Asks questions, curates, runs the radio                       │
│  • Writes to ~/wiki/pet-curated/                                 │
│  • Cannot execute code (by design)                               │
└──────────────────────────────────────────────────────────────────┘
                              │  one-way wiki handoff
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│ Tier 2 — Senter (prioritization)                                 │
│  • On-demand, trigger: "triage", "what now", etc.                 │
│  • Reads ~/wiki/pet-curated/ + active projects                   │
│  • Returns a numbered list (1-5 items)                           │
│  • Tags each: [execute] [escalate] [defer] [archive]              │
│  • Does NOT execute, only decides                                │
└──────────────────────────────────────────────────────────────────┘
                              │  user says "go" → escalates
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│ Tier 3 — Hermes main agent (execution)                           │
│  • Heavyweight, on-demand                                        │
│  • Full toolset: terminal, code, delegation, browser, etc.       │
│  • Reads ~/wiki/pet-curated/escalations/                        │
│  • Executes the curated ideas                                   │
└──────────────────────────────────────────────────────────────────┘
```

The VA is the *taste curator*. Senter is the *prioritizer*. Hermes is the *executor*. The wiki is the *handoff layer*. Music is the visible proof the curation loop is healthy.

## Component diagram

```
┌──────────────────────────────────────────────────────────────────┐
│ USER DESKTOP                                                     │
│                                                                  │
│  ┌────────────────┐         ┌──────────────────────┐             │
│  │  Live2D VA    │◄────────┤  Open-LLM-VTuber     │             │
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
│  │  Default: OmniStep (Qwen2.5-Omni-3B, multimodal native)   │   │
│  │  Auxiliary: OmniSenter (Qwen3-8B + Stage 1 SFT LoRA)      │   │
│  │  Fallback: text LLM → Edge TTS + playlist                 │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  EVOLUTION-RADIO PLUGIN (sibling process, real plug-in)    │   │
│  │  - Monitors chat history + audio engagement                │   │
│  │  - Builds playlists reflecting taste                       │   │
│  │  - HeartMuLa / ACE-Step / model-native for live gen        │   │
│  │  - LoRA self-training on liked tracks                      │   │
│  │  - Ohm chain for weight evolution                          │   │
│  │  - Reads ~/wiki/pet-curated/ for taste signals             │   │
│  │  - Updates ~/wiki/pet-curated/taste.yaml                   │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  NOUS GIRL CURATOR AGENT (Hermes profile, headless)        │   │
│  │  - Toolset: web, file (notes dir), skills, social          │   │
│  │  - Asks questions, curates, runs the radio                 │   │
│  │  - Writes to ~/wiki/pet-curated/                           │   │
│  └─────────────────────┬──────────────────────────────────────┘   │
└────────────────────────┼────────────────────────────────────────┘
                         │  one-way wiki handoff
                         ▼
         ┌───────────────────────────────────────┐
         │  ~/wiki/pet-curated/                  │
         │  - structured YAML/notes              │
         │  - taste profile, project ideas       │
         │  - escalations/ for Tier 3            │
         │  - triage/ for Tier 2                 │
         └───────────────────┬───────────────────┘
                             │
                             ▼  Hermes main reads on demand
         ┌───────────────────────────────────────┐
         │  HERMES AGENT (full toolset)          │
         │  - terminal, code, delegation, etc.   │
         │  - reads pet-curated wiki + escalations│
         │  - executes on the ideas              │
         └───────────────────────────────────────┘
```

## Why this shape

- **VA is constrained on purpose.** A small toolset means it can't accidentally do something dangerous or expensive. It can *think* and *note*, but not *act*. Senter decides what matters; Hermes acts.
- **Multimodal-native default.** OmniStep being text+voice+music in one model means the VA's "personality" is actually the model's behavior, not a stitched-together illusion. When you swap models, the VA's whole vibe changes — voice, music taste, conversational style. Eikon is the visual layer, model is the behavioral layer.
- **Evolutionary-radio as plug-in, not feature.** It's a sibling process the VA orchestrates. Decoupled from chat model. The radio can run ambient (pre-gen playlist) when GPU is busy (e.g. training) or live-generative when idle.
- **Curated catalog.** This isn't a "model browser." The catalog is a small, deliberate set of models you've hand-picked. Each entry is a recommendation, not an option. The user picks from your curation, not from "every model on HF."

## Eikon as identity

Each model in the catalog has an `eikon` field. The eikon is a Live2D sprite + a persona prompt + a voice. When you swap models, the VA's whole identity swaps. This is the "vibe conductor" pattern from the existing Omni VA work — the model is the brain, the eikon is the face, together they are the VA.

Default eikon: Omni VA (vendored from herm-tui's eikon package).
Other eikons: can be added to `VA/sprites/` and registered in the catalog.

## Evolutionary-radio coupling

The radio listens to:
- Which model the user is chatting with (for vibe matching)
- What the user types (NLP extract mood/genre)
- Which tracks the user skips vs. plays through
- Time of day, day of week
- The taste profile at `~/wiki/pet-curated/taste.yaml`

The radio generates:
- LoRA candidates (one per vibe cluster)
- Hourly playlist updates
- Weekly Ohm evolution runs

GPU policy:
- **Training active (e.g. Stage 1 SFT):** radio runs in ambient mode (pre-gen, no live generation)
- **Training idle:** radio can run live generative mode
- **Override:** user can force live-gen even during training (config flag)

## Why the catalog is hand-curated, not auto-scraped

The catalog is a deliberate choice. Each entry is a model you trust, paired with an eikon you vibe with, with a voice that fits. The user picks from your curation, not from "every model on HF." This makes the system opinionated and personal, not generic.

Candidates live in `models/suggested.yaml`. When you vet one, you move it to `models/curated.yaml`.

## Auxiliary model slot

The VA's main chat is OmniStep. The **auxiliary** model slot is for specialized tasks:
- Notebook curation (writing summaries to the wiki)
- Escalation target (when the VA needs to call out for help)
- Vision (if the main model is text-only)
- Music generation (if the main model is text-only)

Currently the auxiliary slot is for OmniSenter (the Qwen3-8B + Stage 1 SFT LoRA). Once Stage 4 (YaRN 256K) is done, OmniSenter becomes the VA's premium default and a new auxiliary replaces it.

## Radio ↔ wiki loop (the curation cycle)

```
1. User chats with VA
2. VA's curator agent reads chat, asks follow-up, takes notes
3. Notes go to ~/wiki/pet-curated/*.md
4. Radio bridge (radio_bridge.py sync) reads notes every 10 min
5. Bridge extracts music-relevant signals (vibes, moods)
6. Bridge updates ~/wiki/pet-curated/taste.yaml
7. Radio daemon reads taste.yaml to inform playlist generation
8. User plays/likes/skips tracks
9. Radio updates its internal state
10. On schedule (weekly), Ohm chain runs to evolve the radio's weights
11. Music gets better
12. User vibes more
13. GOTO 1
```

This is the cycle. It's slow, ambient, and self-improving. The visible artifact is the music. The invisible work is the curation + evolution.
