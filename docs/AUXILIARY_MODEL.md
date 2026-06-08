# Auxiliary model wiring

The VA has a **primary** model slot (the one you chat with) and an **auxiliary** model slot (for specialized tasks). The catalog in `models/curated.yaml` distinguishes them:

- **Main model** — `models[].default: true` is the launch default
- **Auxiliary model** — `auxiliaries[]` entries are loaded as escalation / notebook / vision / music targets

## Why two slots?

A small text LLM is great for chat, but you sometimes need:
- **A vision model** when the main one is text-only
- **A music generation model** when the main one can't sing
- **An escalation target** when the chat model says "I don't know" too often
- **A notebook curator** that summarizes chats into the wiki

The auxiliary slot handles all of these.

## Current wiring

In `vtuber-core/conf.nous-assistant.yaml`, the VA is configured with two `llm_configs`:

| Slot | Provider | Model | Use |
|---|---|---|---|
| Primary | `llama_cpp_omnistep` | OmniStep (Qwen2.5-Omni-3B) | Chat, default voice, vision |
| Auxiliary | `llama_cpp_omnisenter` | OmniSenter (Qwen3-8B + Stage 1 LoRA) | Notebook curation, escalation |

The VA's right-click menu can switch which `llm_provider` is active at runtime.

## To add a new auxiliary

1. Add an entry to `auxiliaries:` in `models/curated.yaml`
2. Add a matching `llm_configs.<name>` block in `conf.yaml` (or `conf.nous-assistant.yaml`)
3. Reference it from the `agent_settings.basic_memory_agent.llm_provider` field, or from a sub-agent

## To use OmniSenter as primary

When Stage 1 SFT finishes (~50-60h from now), the OmniSenter GGUF + LoRA adapter will be at:
- GGUF: `~/Models/storage/gguf/omnisenter/omnisenter-stage1-Q4_K_M.gguf`
- Adapter: `~/projects/evolutionary-training/training-output/omnisenter-sft-20260606_213858/checkpoint-N/`

Set `default: true` on the `omnisenter-auxiliary` entry in `models/curated.yaml` to make it the launch default, and update `conf.yaml` to point at it.

## Why a llama-server sidecar?

The VA is a *client*. It speaks the OpenAI API to whatever's serving. The model servers (`llama-server`, `ollama`, `vllm`) handle the actual inference. This separation means:
- You can swap the model without restarting the VA
- You can run the model on a different machine than the VA
- The radio plugin can read the same model server for vision/music

The `base_url` in each `llm_configs.*` block points at the model server's OpenAI-compatible endpoint.
