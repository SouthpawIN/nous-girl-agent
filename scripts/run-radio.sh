#!/bin/bash
# run-radio.sh — start the Evolutionary Radio plugin (sibling process to the pet)
#
# Usage:
#   ./scripts/run-radio.sh start --vibe "chill lofi beats for coding"
#   ./scripts/run-radio.sh status
#   ./scripts/run-radio.sh skip
#   ./scripts/run-radio.sh stop
#
# This wraps the existing evolutionary-radio implementation, so all the
# feedback/GEPA/Darwin/Ohm logic in the upstream repo stays intact.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
RADIO_DIR="$REPO_ROOT/plugins/evolution-radio/upstream"

cd "$RADIO_DIR"

# Ensure venv exists
if [ ! -d "venv" ]; then
    echo "📦 Creating radio venv..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
fi

source venv/bin/activate

# Pass through to start_radio.sh which has auto-restart logic
exec ./start_radio.sh "$@"
