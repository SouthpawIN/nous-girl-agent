#!/bin/bash
# run-agent.sh — start the Nous Girl curator agent (headless Hermes profile)
#
# Usage:
#   ./scripts/run-agent.sh
#   ./scripts/run-agent.sh --once     # run curation once and exit
#
# This is the headless curator that runs alongside the pet.
# Toolset: web search, web fetch, file write (notes only), social media.
# Writes to ~/wiki/pet-curated/ for Hermes main to consume.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
NOTES_DIR="${HOME}/wiki/pet-curated"

mkdir -p "$NOTES_DIR"

# First-time setup: register the profile with Hermes
if ! hermes profile list 2>/dev/null | grep -q "evolutionary-radio"; then
    echo "📝 Registering evolutionary-radio profile with Hermes..."
    hermes profile create evolutionary-radio --template "$REPO_ROOT/agent/profile-template.yaml"
fi

echo "🎀 Starting Nous Girl curator agent..."
echo "   Notes will be written to: $NOTES_DIR"
echo ""

hermes run --profile evolutionary-radio "$@"
