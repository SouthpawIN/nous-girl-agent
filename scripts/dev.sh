#!/bin/bash
# dev.sh — Run everything: VA + radio + agent, with logs tailing
#
# Usage:
#   ./scripts/dev.sh               # all three, logs to /tmp/nous-assistant-*.log
#   ./scripts/dev.sh --no-agent    # VA + radio only
#   ./scripts/dev.sh --kill        # kill any running instances

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

if [ "$1" = "--kill" ]; then
    echo "🛑 Killing any running Omni VA processes..."
    pkill -f "uv run run_server.py" 2>/dev/null || true
    pkill -f "evolutionary-radio" 2>/dev/null || true
    pkill -f "radio_bridge" 2>/dev/null || true
    sleep 1
    echo "  ✅ Done"
    exit 0
fi

SKIP_AGENT=false
for arg in "$@"; do
    case $arg in
        --no-agent) SKIP_AGENT=true ;;
    esac
done

LOG_DIR="/tmp/nous-assistant-logs"
mkdir -p "$LOG_DIR"

echo "🎀 Omni VA dev environment"
echo "============================"
echo "  Logs: $LOG_DIR"
echo ""

# 1. VA
echo "🚀 Starting VA..."
nohup "$REPO_ROOT/scripts/run-VA.sh" > "$LOG_DIR/VA.log" 2>&1 &
PET_PID=$!
echo "  VA: PID $PET_PID, log: $LOG_DIR/VA.log"
sleep 3

# 2. Radio
echo "📻 Starting radio..."
nohup "$REPO_ROOT/scripts/run-radio.sh" start > "$LOG_DIR/radio.log" 2>&1 &
RADIO_PID=$!
echo "  radio: PID $RADIO_PID, log: $LOG_DIR/radio.log"
sleep 2

# 3. Radio bridge (sync loop, 10 min interval)
echo "🌉 Starting radio bridge (sync loop)..."
nohup bash -c 'while true; do python3 '"$REPO_ROOT"'/plugins/evolution-radio/radio_bridge.py sync; sleep 600; done' > "$LOG_DIR/bridge.log" 2>&1 &
BRIDGE_PID=$!
echo "  bridge: PID $BRIDGE_PID, log: $LOG_DIR/bridge.log"
sleep 1

# 4. Agent (optional)
if [ "$SKIP_AGENT" = false ]; then
    echo "🤖 Starting curator agent..."
    nohup "$REPO_ROOT/scripts/run-agent.sh" > "$LOG_DIR/agent.log" 2>&1 &
    AGENT_PID=$!
    echo "  agent: PID $AGENT_PID, log: $LOG_DIR/agent.log"
fi

echo ""
echo "✅ All services started. PIDs:"
echo "  VA:    $PET_PID"
echo "  radio:  $RADIO_PID"
echo "  bridge: $BRIDGE_PID"
[ "$SKIP_AGENT" = false ] && echo "  agent:  $AGENT_PID"
echo ""
echo "Tail logs with: tail -f $LOG_DIR/*.log"
echo "Kill all with: $REPO_ROOT/scripts/dev.sh --kill"
