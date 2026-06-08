# Install & Run

> Full install coming. This is the scaffolding.

## Prerequisites

- Python 3.11+
- `uv` (Python package manager — `pip install uv`)
- A local model from `models/curated.yaml` (or an API key for `nous-portal` models)
- Optional: a Live2D model of your own (Omni VA default is shipped)

## Quick start

```bash
git clone https://github.com/SouthpawIN/nous-assistant-agent
cd nous-assistant-agent

# Install vtuber-core
cd vtuber-core
uv sync
cd ..

# Copy default config
cp vtuber-core/config_templates/conf.default.yaml conf.yaml

# Edit conf.yaml — point at your chosen model from models/curated.yaml
$EDITOR conf.yaml

# Run
cd vtuber-core
uv run run_server.py
```

The VA appears as a Live2D window. Right-click for menus, drag to move, double-click to chat.

## Adding a new model to the catalog

1. Edit `models/curated.yaml` (or copy from `models/suggested.yaml`)
2. Add the eikon sprite to `VA/sprites/<eikon-name>/`
3. Restart the server

## Running the evolutionary-radio plugin

The radio is a sibling process. Once the model is running:

```bash
# In another terminal
cd plugins/evolution-radio
python daemon/radio_daemon.py
```

It will detect the running model, pick the right music source based on the catalog, and start the perpetual loop.

## Running the Omni VA (Hermes profile)

The agent is a Hermes profile — headless, no UI. It reads the VA's chat logs and curates notes:

```bash
hermes profile create evolutionary-radio --template agent/profile-template.yaml
hermes run --profile evolutionary-radio
```

It writes to `~/wiki/pet-curated/`. Hermes main agent reads from there.

## GPU notes

- The VA + radio together need 1 GPU minimum (for the model). Darwin/APEX already use both 3090s.
- During active training (e.g. Stage 1 SFT), the radio automatically runs in ambient mode (pre-gen, no live generation). Override with `--force-live-gen` flag.
- If you want the VA to run on a different GPU than training, use `CUDA_VISIBLE_DEVICES=N` before launching.

## Troubleshooting

See `docs/TROUBLESHOOTING.md` (placeholder — full doc pending).
