# Model Format

The VA's `models/curated.yaml` references GGUF files for local models.
Here's what you need to know.

## Supported backends

| backend        | file format   | where it runs                         |
|----------------|---------------|---------------------------------------|
| `llama.cpp`    | `.gguf`       | local, spawned by llama-server        |
| `ollama`       | (internal)    | local, ollama daemon                  |
| `openai-compat`| any           | any OpenAI-compatible HTTP endpoint   |
| `nous-portal`  | (cloud)       | https://api.nous.research/v1          |

## GGUF (local, llama.cpp)

Most local models in the catalog are GGUF quantizations. Place the
`.gguf` file at the path in `model_path` and the VA will spawn a
`llama-server` instance pointing at it.

Recommended layout:

```
~/Models/storage/gguf/
├── <model-name>/
│   ├── <model-name>-Q4_K_M.gguf
│   └── mmproj-<model-name>-Q8_0.gguf  (if multimodal)
```

Or for a single-file model:

```
~/Models/storage/gguf/
└── <model-name>.gguf
```

### Multimodal models

Multimodal models (like Qwen2.5-Omni) need a `mmproj` (multimodal
projector) file in addition to the main GGUF. The `mmproj_path` field
in the catalog entry points to it.

## Recommended quantization

- **Q4_K_M:** good default. ~4 bits per weight, balanced quality/size.
- **Q5_K_M:** slightly higher quality, ~5 bits per weight.
- **Q8_0:** near-original quality, ~8 bits per weight. For small models.
- **Q2_K:** tiny, but quality loss. Only for testing.

For the VA (interactive use), **Q4_K_M** is the sweet spot.

## Context size

The catalog doesn't currently set `--ctx-size` per model. To set it,
edit the `conf.yaml` in `vtuber-core/` after running `./scripts/install.sh`.

The model_path field can be a directory containing multiple files (e.g.
when using safetensors + tokenizer) — but for GGUF, a single file is
most common.

## Memory budget

The VA runs the model on GPU. Memory needed per model:

| model                | GGUF size | VRAM needed (Q4_K_M) |
|----------------------|-----------|----------------------|
| Qwen2.5-Omni-3B      | 1.96GB    | ~4GB                 |
| Darwin-28B           | 15.4GB    | ~17GB                |
| APEX-MTP (35B-A3B)   | 16.1GB    | ~18GB                |
| Qwen3.5-35B-A3B      | 18.3GB    | ~20GB                |
| Qwen3-Coder-30B-A3B  | 17.3GB    | ~19GB                |

For a single 24GB RTX 3090, models up to ~20B total / ~3B active fit
comfortably. Larger models (24B+, dense) need both GPUs.

## Downloading a model

The catalog is just a manifest — it doesn't auto-download. To add a
new model, you can:

1. Use `huggingface-cli` to download the GGUF:
   ```bash
   huggingface-cli download <org>/<model>-GGUF \
       --include "<model>-Q4_K_M.gguf" \
       --local-dir ~/Models/storage/gguf/<model>
   ```
2. Edit `models/curated.yaml` to add an entry pointing at the new file.
3. Set `default: true` if you want it to be the launch default.
