#!/bin/bash
# run-VA.sh — start the Omni VA (Open-LLM-VTuber desktop client)
#
# Usage:
#   ./scripts/run-VA.sh                # uses curated.yaml default model
#   ./scripts/run-VA.sh --character nous-assistant
#   ./scripts/run-VA.sh --model-id qwen-omni-3b

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
VTUBER_DIR="$REPO_ROOT/vtuber-core"

cd "$VTUBER_DIR"

# Ensure deps are installed
if [ ! -d ".venv" ]; then
    echo "📦 Installing vtuber-core deps (uv sync)..."
    uv sync
fi

# Copy default config if missing
if [ ! -f "conf.yaml" ]; then
    echo "📝 Creating conf.yaml from default template..."
    cp config_templates/conf.default.yaml conf.yaml
    echo ""
    echo "⚠️  Please edit conf.yaml to point at your chosen model."
    echo "   See $REPO_ROOT/models/curated.yaml for available entries."
    exit 1
fi

# Launch
echo "🎀 Starting Omni VA..."
exec uv run run_server.py "$@"
