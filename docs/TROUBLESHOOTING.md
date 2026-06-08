# Troubleshooting

## Common issues

### VA won't start: "conf.yaml not found"

```
cp vtuber-core/config_templates/conf.default.yaml vtuber-core/conf.yaml
$EDITOR vtuber-core/conf.yaml
```

### VA won't start: "module 'open_llm_vtuber' not found"

The vtuber-core deps aren't installed. Run:

```bash
cd vtuber-core && uv sync
```

### VA can't reach the model

Check that a model is actually running:

```bash
# If using llama.cpp directly
curl http://localhost:<port>/health

# Check the conf.yaml has the right api_base URL
```

### Radio: "mpv not found"

```bash
sudo apt install mpv    # Debian/Ubuntu
brew install mpv        # macOS
```

### Radio: stuck or loop audio

```bash
# Kill stuck mpv/ffplay processes
pkill mpv
pkill ffplay

# Then restart
./scripts/run-radio.sh start
```

### Curator agent: "no profile 'evolutionary-radio'"

```bash
hermes profile create evolutionary-radio --template agent/profile-template.yaml
```

### Notes not appearing in ~/wiki/pet-curated/

Check that the directory exists and is writable:

```bash
mkdir -p ~/wiki/pet-curated/escalations
ls -la ~/wiki/pet-curated/
```

### GPU contention between training and the VA

The VA is GPU-light (it serves as the LLM client; the actual inference
happens in the local model server). The model server itself uses VRAM.

If you have active training running on both GPUs:

1. Stop training first, OR
2. Run the VA against a small model (qwen-omni-3b at 1.96GB), OR
3. Use an API model (set `api_key_env: NOUS_API_KEY` in the catalog)

### The VA's eikon doesn't appear / is invisible

Check that the Live2D model path in `characters/nous-assistant.yaml` is valid.
For v1 (static PNG), the `avatar_path: avatars/nous-assistant.png` should be
present — verify with `ls vtuber-core/avatars/`.

### The radio won't autostart tracks

The radio needs at least one playable source. Check:

1. Is the model in `models/curated.yaml` reachable? (LLM client)
2. Is ACE-Step installed? (`pip install -e ~/projects/ACE-Step`)
3. Or is the `playlists/default.json` populated?

If the queue is empty and live-gen is failing, the radio will idle.

### Wiki handoff: "Permission denied" writing to ~/wiki/

```bash
chmod -R u+w ~/wiki/pet-curated/
```

### Surface Duo / mobile: voice doesn't auto-play

The TTS file is generated and delivered as a voice bubble in the chat
platform. The user needs to tap to play on mobile. There's no
auto-play on mobile due to platform restrictions.

## Getting more help

- Open an issue: https://github.com/SouthpawIN/nous-assistant-agent/issues
- Check the upstream Open-LLM-VTuber docs: vtuber-core/doc/
- Read the radio upstream: https://github.com/SouthpawIN/evolutionary-radio
