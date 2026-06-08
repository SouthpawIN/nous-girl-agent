# Omni VA — Local Auxiliary Model Architecture

> **One local model. Three personas. Eight deployment tiers.**

The **Omni VA (Omni Virtual Assistant)** is a single local llama.cpp server
running on the "other" GPU that powers the entire desktop companion stack:

- **Nous Girl** — the VA face, warm/studious persona
- **OmniStep** — the omni-modal model (vision + audio + text)
- **Omni Evolution Radio** — the perpetual music curator

Different system prompts over the same OpenAI-compatible endpoint.

---

## Why this design

| Constraint | Why it matters |
|---|---|
| Always-on | VA must be available 24/7 without spinning up |
| Low VRAM | Must not steal from main model or training |
| Wake-on-ping | Idle-kill after 30 min so other workloads can use VRAM |
| 1M context | Long-running agentic sessions span days of context |
| Vision-capable | For multimodal Nous Girl (Discord, screen-share, image understanding) |
| MoE efficiency | Active 3B per token of 35B total → 11× smaller VRAM than dense 35B |

The model is `mudler/Carnice-Qwen3.6-MoE-35B-A3B-APEX-MTP` I-Nano variant
(`qwen35moe` arch, hybrid Mamba-2 / Gated Delta Net + Transformer, 30 active
experts, 11.68GB on disk).

---

## The tier cascade

Local server main + Carnice aux, scaling down by VRAM, all hitting
**256K context minimum** and **30 t/s minimum**:

| Tier | VRAM | RAM | Main | Aux (always Carnice) | Status |
|------|------|-----|------|----------------------|--------|
| **T1 — Top** | 32GB+ | 64GB+ | Darwin 28B Reason @ 1M | Carnice 1M | planned |
| **T2 — High** | 24GB | 64GB+ | Darwin 28B Reason @ 1M | Carnice 1M (offloaded) | ✅ measured 11 t/s |
| **T3 — Mid** | 16GB | 32GB+ | Darwin 28B Reason @ 512K | Carnice 1M | measured 11.6 t/s |
| **T4 — Standard** | 12GB | 32GB+ | Darwin 28B Reason @ 256K | Carnice 1M | ✅ measured 15.7 t/s |
| **T5 — PrismEagle** | 16GB | 32GB+ | PrismEagle 27B w/ MTP @ 512K | Carnice 1M | pending download |
| **T6 — Darwin Apex** | 12GB | 32GB+ | Darwin 36B Apex (MTP/NextN) experts offloaded | Carnice 1M | pending build |
| **T7 — Low** | 8GB | 32GB+ | Darwin 36B Apex, most experts CPU @ 256K | Carnice 1M | pending build |
| **T8 — API + recommended aux** | n/a | 32GB+ | API (DeepSeek, Minimax, Nemo, Qwen, etc.) | Qwen2.5-3B / Phi-3 / etc. | docs only |

**Priorities:** aux 1M / 30 t/s first, then scale main down. **Floor:** 256K / 30 t/s. **Below 30 t/s = scale down context or scale up model.**

**Auto-aux fallback:** if Carnice won't fit beside the main (combined VRAM > 24GB), main serves aux duties too at 1M.

### Measured Carnice I-Nano speeds (RTX 3090, 24GB)

| Context | I-Nano (Q2) | I-Compact (Q4_K_M) | Note |
|---------|-------------|--------------------|------|
| 256K    | **15.7 t/s** (with thinking) / 11.3 t/s (no-think) | 12.1 t/s | sweet spot |
| 512K    | 11.6 t/s | not tested | KV cache bandwidth-bound |
| 1M      | failed to start in 5 min | not tested | needs more startup time |

**Conclusion:** Carnice I-Nano at **256K** is the practical tier for current
hardware. To hit 1M / 30 t/s we need either more VRAM (A100/H100) or a
smaller aux model (Qwen3-4B).

---

## Smart vision routing

When the main model is vision-capable (heuristic: `minimax*`, `qwen*vl*`,
`qwen*omni*`, `gpt-4*`, `claude-3-opus*`, `gemini-*`, `*vision*`),
Hermes routes vision aux to the main. Otherwise it falls back to the
Carnice aux (always has vision via Qwen3-Omni lineage).

Configured in `~/.hermes/config.yaml`:

```yaml
auxiliary:
  vision:
    provider: nous
    model: minimax/minimax-m3      # main (has vision)
    base_url: https://inference-api.nousresearch.com/v1
  web_extract: { provider: custom, base_url: http://127.0.0.1:8082/v1 }
  compression:  { provider: custom, base_url: http://127.0.0.1:8082/v1 }
  # ... all other tasks → Carnice via :8082
  default: carnice-35a3b
  _omni_va:
    model_path: /home/sovthpaw/Models/storage/gguf/Carnice-35A3B-APEX-MTP-GGUF/...
    service: omni-va.service
    binary: llama.cpp-atomic (MTP/NextN-capable)
    architecture: qwen35moe hybrid (Mamba-2 + Transformer)
    kv_cache: q4_0
    moe_offload: --cpu-moe
    notes: MTP draft path blocked by hybrid arch
```

---

## Architecture: hybrid Mamba + Transformer

The Carnice model uses the `qwen35moe` architecture — a hybrid stack:

- **41 layers** total
- **Recurrent state (RS)** buffer: ~63MB per sequence (constant size, **NOT** context-dependent)
- **KV cache** for transformer layers: ~1.4GB at 256K q4_0
- **Mamba-2 / Gated Delta Net** in some layers for O(1) memory per token
- **30 active experts per token** (out of ~256 total)

**Why this matters:** the recurrent state means **memory does not grow
linearly with context length** for the linear-attention layers. Only the
transformer-layer KV cache grows. At 1M context the model is feasible
where pure-transformer 35B would not be.

**Gotcha:** MTP/NextN speculative decoding is **blocked** by the hybrid
arch — recurrent state doesn't support partial sequence removal. The 30
t/s comes from MoE offload + q4_0 KV cache + constant-size RS, not from
draft speculation.

---

## Service definition

`~/.config/systemd/user/omni-va.service`

```ini
[Service]
Environment="LLAMA_SERVER=/home/sovthpaw/projects/LLM-Infra/llama.cpp-atomic/build/bin/llama-server"
Environment="LLAMA_LIB_DIR=/home/sovthpaw/projects/LLM-Infra/llama.cpp-atomic/build/bin"
Environment="LLAMA_SERVER_EXTRA_ARGS=--cpu-moe -c 1048576 -ctk q4_0 -ctv q4_0 --flash-attn on"
Environment="IDLE_KILL_SECS=1800"
Environment="STARTUP_TIMEOUT=300"

ExecStart=/home/sovthpaw/bin/llama-proxy 8082 9082 0 \
  /home/sovthpaw/Models/storage/gguf/Carnice-35A3B-APEX-MTP-GGUF/Carnice-Qwen3.6-MoE-35B-A3B-APEX-MTP-I-Nano.gguf

Restart=always
```

**Atomic fork requirement:** main `llama.cpp` does **NOT** have MTP/NextN
code for Qwen35Moe. The atomic fork (`llama.cpp-atomic` branch
`b1-mtp-qwen-rebase`) does. **Must set `LD_LIBRARY_PATH` to the atomic
fork's `build/bin` directory** or you'll get
`undefined symbol: llama_context_nextn_seq_rm`.

The proxy script at `~/bin/llama-proxy` now supports `LLAMA_SERVER` and
`LLAMA_LIB_DIR` env vars (env-driven, defaults to main llama.cpp).

---

## Operational commands

```bash
# Start / stop
systemctl --user start omni-va.service
systemctl --user stop omni-va.service    # also kills the backend, frees VRAM
systemctl --user status omni-va.service

# Logs
tail -f /tmp/omni-va.log

# Manual wake-up test
curl -X POST http://127.0.0.1:8082/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"carnice-35a3b","messages":[{"role":"user","content":"hi"}],"max_tokens":20}'

# Speed test
curl -X POST http://127.0.0.1:8082/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"carnice-35a3b","messages":[{"role":"user","content":"list the alphabet"}],"max_tokens":500,"chat_template_kwargs":{"enable_thinking":false}}' \
  | jq '.timings | {predicted_n, predicted_ms, tps: (.predicted_n / .predicted_ms * 1000)}'
```

---

## Open questions / next steps

1. **1M context / 30 t/s** — needs either more VRAM (A100 40GB+) or a
   smaller aux model (Qwen3-4B at 256K for fast contexts, Carnice for
   long). For now we ship at 256K / 15 t/s.

2. **MTP/NextN** — blocked by hybrid arch. Path forward: investigate
   if the atomic fork's `nextn` path can be adapted for the recurrent
   layers, or wait for upstream llama.cpp Mamba-aware spec decoding.

3. **PrismEagle 27B (T5)** — not yet on disk. Available on HF as
   `Ex0bit/Qwen3.6-27B-PRISM-EAGLE3`. To download, add to the
   `tier-cascade.md` script.

4. **Darwin 36B Apex (T6/T7)** — also not yet built. The plan was to
   Darwin-merge the 35A3B APEX-MTP with a 36B parent. Until then, the
   on-disk 17.3GB `Qwen3.6-35B-A3B-APEX-MTP-I-Compact.gguf` is the
   closest stand-in.

5. **Persona switching** — three system prompts (Nous Girl, OmniStep,
   Omni Evolution Radio) over the same endpoint. Implementation: a
   small router proxy that prepends the system prompt based on a
   request header (`X-Persona: nous-girl | omnistep | radio`).

---

## See also

- `wiki/entities/omni-va-carnice-35a3b.md` — model entity doc
- `wiki/concepts/omni-va-architecture.md` — conceptual overview
- `evolutionary-training/AGENTS.md` — architecture rule
- `evolutionary-training/blog/the-omni-family.md` — model family taxonomy
- `nous-girl-agent/docs/MULTIMODAL.md` — multimodal wiring
- `hermes-agent` skill: `auxiliary-model-config.md`, `llama-auto-start-proxy.md`
