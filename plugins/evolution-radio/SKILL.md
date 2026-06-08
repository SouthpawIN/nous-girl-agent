---
name: evolution-radio
description: |
  Evolutionary radio with self-evolving playlists. Curates user taste,
  trains LoRAs, runs the Ohm chain for self-improvement. Perpetual
  background loop. Multi-modal (text + voice + music from a single
  forward pass when OmniStep is the model).
version: 0.1.0
metadata:
  hermes:
    tags: [radio, music, evolution, ohm, multi-modal]
---

# Evolution Radio

The OmniStep Evolution Radio is a perpetual playlist loop that:
- Watches what you engage with (chats, music, web, social)
- Builds playlists reflecting your taste
- Generates new tracks (HeartMuLa / ACE-Step / model-native)
- Trains LoRAs on what you like
- Feeds the **Ohm** evolutionary chain for self-improvement

It's a sibling process to the VA — decoupled from the chat model. The
radio runs ambient (pre-generated playlist) when GPU is busy (e.g.,
training), and switches to live-gen when idle.

## When to use

- The user asks to play music, queue a vibe, or just "start the radio"
- The user wants to discover new music curated to their taste
- The user wants to skip / like / dislike tracks
- The user wants to evolve the radio (force an Ohm run)

## Tools

| Tool | What it does |
|---|---|
| `radio:start` | Start the daemon |
| `radio:stop` | Stop the daemon |
| `radio:skip` | Skip the current track |
| `radio:like` | Like the current track (feeds taste profile + LoRA training) |
| `radio:dislike` | Dislike the current track (feeds taste profile) |
| `radio:status` | Get current playing state |
| `radio:queue` | Show upcoming queue |
| `radio:evolve` | Trigger an Ohm evolution step |
| `radio:sync` | Sync taste profile from the wiki |

## Voice

The radio doesn't have its own voice — it's ambient. The VA's
voice (Jenny/Ava via Edge TTS, or model-native if OmniStep) is what
the user hears when they talk to the agent. The radio is what they
hear in the background.

## Coupling to wiki

The radio reads `~/wiki/pet-curated/*.md` for music-relevant signals
(vibe keywords, mood mentions) and updates `~/wiki/pet-curated/taste.yaml`
with the aggregated taste profile. This is the "curation -> radio ->
curation" loop.

See `plugins/evolution-radio/radio_bridge.py` for the bridge module.
