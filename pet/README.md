# Pet Launcher

This directory contains the pet-specific configuration that sits on top
of the vendored `vtuber-core/`.

## Layout

```
pet/
├── README.md          ← you are here
├── sprites/           ← Live2D eikons (one per eikon name in the catalog)
│   └── nous-girl/     ← default eikon — sprite, expressions, motions
├── menus/             ← right-click context menu definitions per eikon
└── launcher/          ← startup scripts (Python wrapper around vtuber-core)
```

## Running the pet

```bash
# From the repo root
cd vtuber-core
uv sync
cp config_templates/conf.default.yaml conf.yaml
# Edit conf.yaml — point at a model from models/curated.yaml
uv run run_server.py
```

The pet window appears. Right-click for menus, drag to move, double-click for chat.

## Swapping the eikon

The active eikon is determined by the model catalog entry's `eikon` field.
To swap eikons:

1. Add a new sprite directory under `pet/sprites/<name>/`
2. Add the eikon to the catalog entry
3. Restart the server

The Nous Girl eikon (default) is shipped in the eikon work — see the
`nous-girl` and `chizul` repos for the source sprites.

## Pet ↔ Agent coupling

The pet is the visual/auditory face of the model. The Nous Girl agent
(separate Hermes profile) is the headless curator that runs alongside.
See `agent/profile-template.yaml` for the agent's toolset.

The pet writes chat logs to `vtuber-core/chat_history/`. The agent reads
those logs to curate taste. No direct IPC needed — they share the filesystem.
