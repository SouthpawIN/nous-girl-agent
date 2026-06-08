# Multimodal Nous Girl (Omni VA) — Architecture & Wiring

> **Status:** 🟡 in progress · **Owner:** Agent 2 (this repo) · **Date:** 2026-06-08
>
> Chris wants the VA (Nous Girl, rebranded "Omni VA" per the Agent 1
> persona conventions) to generate **images, videos, AND music** via
> Discord, in addition to text + voice. This doc captures how that's
> wired together as of 2026-06-08.

## TL;DR

- **Today (2026-06-08):** the VA can route to **ComfyUI** (image + video)
  and **HeartMuLa** (music) as separate backends, plus a **DeepSeek** text
  backbone fallback. Catalog entries in `models/curated.yaml`.
- **Eventually:** the new **OmniStep** / **OmniSenter** models (per the
  architecture simplification) will do ALL of this natively in one
  model. The separate backends are the stand-in until those ship.

## The modality matrix

| What the user wants | Who handles it now | Model / backend | Status |
|---|---|---|---|
| Text chat (default) | Main model | `qwen-omni-3b` (Qwen 2.5 Omni 3B GGUF) | ✅ live |
| Voice (text → speech) | Edge TTS (fallback) | `edge-tts:en-US-AvaNeural` | ✅ live |
| Voice (in, real-time) | STT | `local:base` (Whisper) | ✅ live |
| Vision (image → text) | Main model | `qwen-omni-3b` (mmproj head) | ✅ live |
| Text (reliable fallback) | Auxiliary | `deepseek-text` (API) | 🟡 wired, needs key |
| Image generation | External backend | `comfyui-image-flux` (Flux) | 🟡 needs ComfyUI running |
| Video generation | External backend | `comfyui-video-ltx2` (LTX-2) | 🟡 needs ComfyUI running |
| Music generation | External backend | `heartmula-3b` (Suno-like) | 🟡 needs HeartMuLa installed |
| Music curation | Local playlist + radio | `evolutionary-radio` plugin | ✅ live |
| Speech input (low-latency) | Future | Nemotron 0.6B ASR | ⏳ Stage 2+ |
| Native music (ACE-Step) | Future | ACE-Step merge in OmniStep | ⏳ Stage 2+ |
| Native image/video | Future | OmniStep in-model | ⏳ Stage 2+ |

## Architecture diagram

```
                       ┌──────────────────────┐
   Discord  ────►      │   Omni VA (Nous Girl)│
                       │   ~/.hermes/profiles/│
                       │      nous-girl/      │
                       └──────────┬───────────┘
                                  │
            ┌─────────────────────┼─────────────────────┐
            │                     │                     │
       ┌────▼────┐          ┌─────▼─────┐         ┌─────▼─────┐
       │  TEXT   │          │  VISION   │         │  SPEECH   │
       │ default │          │  default  │         │  in/out  │
       │ qwen-   │          │  qwen-    │         │  Edge TTS│
       │ omni-3b │          │  omni-3b  │         │  + Whisper│
       └────┬────┘          └─────┬─────┘         └─────┬─────┘
            │                     │                     │
            │   when user asks:   │                     │
            │   "make a song..."  │                     │
            │   "draw me a..."    │                     │
            │   "make a video..." │                     │
            │                     │                     │
            └─────────┬───────────┴───────────┬─────────┘
                      │                       │
              ┌───────▼────────┐      ┌───────▼────────┐
              │    MUSIC GEN   │      │ IMAGE/VIDEO GEN│
              │                │      │                │
              │  heartmula-3b  │      │ comfyui:8188   │
              │  (Suno-like)   │      │  + Flux / LTX-2│
              │                │      │                │
              │  lyrics+tags   │      │  text prompt   │
              │  → full song   │      │  → image/video │
              └────────────────┘      └────────────────┘
                      │                       │
                      └───────────┬───────────┘
                                  │
                          ┌───────▼────────┐
                          │  FALLBACK TEXT │
                          │                │
                          │  deepseek-text │
                          │  (API) when    │
                          │  OmniStep      │
                          │  not enough    │
                          └────────────────┘
```

## How a user request flows

Example: user sends a Discord message: **"make me a chill lo-fi beat with a saxophone"**

1. **Discord bot** receives the message in the `nous-girl` hermes-agent
   profile
2. **Main model** (`qwen-omni-3b`) parses intent. Recognizes: music gen
   + style tags + genre. Possibly asks one clarifying question.
3. **Routes** to the `heartmula-3b` entry in `models/curated.yaml`:
   - Extracts genre tags: `[chill, lo-fi, saxophone]`
   - Extracts lyrics (or generates if user didn't provide)
   - Calls HeartMuLa via the `heartmula` skill
4. **HeartMuLa** generates the audio file, returns a URL or attachment
5. **VA** sends the audio back to Discord, along with a brief text reply

## What's wired where

### `models/curated.yaml` (this repo)
The source of truth for what the VA can serve. As of 2026-06-08:
- `qwen-omni-3b` (default, unchanged)
- `qwen35-35b-a3b` (text fallback, unchanged)
- `omni-step` (placeholder, updated with the new 4-block architecture)
- `omnisenter` (planned flagship, also updated)
- `qwen3-coder-30b`, etc. (others unchanged)
- **NEW** `heartmula-3b` (music gen)
- **NEW** `comfyui-image-flux` (image gen)
- **NEW** `comfyui-video-ltx2` (video gen)
- **NEW** `deepseek-text` (text backbone fallback)
- Auxiliary: `omnisenter-auxiliary` (the trained 8B SFT for notebook)

### `agent/profile-template.yaml` (this repo)
The curator profile (limited toolset). Now declares the
`generation_routing` block — image/video/music go to backends and
escalate to Hermes main or the VA Discord bot.

### `~/.hermes/profiles/nous-girl/config.yaml` (the Discord bot)
The VA itself. Already has `Darwin-28B-REASON` as the default model
(text) and `qwen3.6-35b-a3b` as the vision auxiliary. **TODO**: add
the `comfyui`, `heartmula`, and `deepseek` skills to its toolsets.

### Discord bot commands
The VA's Discord interface should expose intuitive commands:
- `/image <prompt>` — routes to `comfyui-image-flux`
- `/video <prompt>` — routes to `comfyui-video-ltx2`
- `/music <lyrics> <tags>` — routes to `heartmula-3b`
- `/text <prompt>` — uses main model (default)
- `/vision <image>` — uses main model's vision head

## Pre-flight: what needs to be running

| Backend | Port | Process | Status as of 2026-06-08 |
|---|---|---|---|
| llama-server (text, Darwin-28B) | :11500 | systemd `--user:llama-darwin` | ⏸️ stopped (training conflict) |
| llama-server (text, APEX-MTP) | :11501 | systemd `--user:llama-apex` | ⏸️ stopped (training conflict) |
| ComfyUI (image/video) | :8188 | `comfyui` command | 🟡 not installed yet |
| HeartMuLa (music) | n/a | `python -m heartmula.infer ...` | 🟡 not installed yet |
| Qwen-Omni-3B (default VA) | :8010+ | `llama-server --mmproj ...` | 🟡 not started |
| Stage 1 SFT training | n/a | PID 3884286 | ✅ RUNNING |
| Evolutionary Radio daemon | n/a | `plugins/evolution-radio/daemon/` | 🟡 needs restart |
| Discord gateway (nous-girl) | n/a | `~/.hermes/profiles/nous-girl/gateway.pid` | ✅ running |

**NOTE:** The training is using both RTX 3090s. The local LLM
servers (llama-darwin, llama-apex) are intentionally stopped per
AGENTS.md. ComfyUI + HeartMuLa would also need a GPU — they'll have
to wait until the training is done (or run on a third GPU if
available, but there are only 2).

## Open tasks

- [ ] Install ComfyUI (`comfyui` skill, `comfyui_setup.sh`)
- [ ] Install HeartMuLa (`heartmula` skill, 8GB+ VRAM)
- [ ] Pull a Flux model for image gen (~12GB)
- [ ] Pull LTX-2 for video gen (~10GB)
- [ ] Add `comfyui`, `heartmula` skills to the `nous-girl` Discord profile
- [ ] Add `DEEPSEEK_API_KEY` env var (or use local MiniMax M3 fallback)
- [ ] Wire the Discord bot to expose `/image`, `/video`, `/music` commands
- [ ] Smoke-test each backend with a tiny request
- [ ] Once OmniStep ships, retire the separate backends

## See also

- `AGENTS.md` — the architecture rule (Cosmos + Nemotron + 8B + ACE-Step)
- `models/curated.yaml` — the model catalog
- `agent/profile-template.yaml` — the curator profile
- `wiki-handoff/wiki_handoff.py` — how notes flow from VA → Hermes
- `plugins/evolution-radio/` — the existing music curator
- `~/.hermes/profiles/nous-girl/config.yaml` — the Discord bot config
- `../evolutionary-training/blog/the-omni-family.md` — the canonical
  naming convention for OmniStep / OmniSenter
