#!/bin/bash
# install.sh — One-shot setup for the Nous Girl agent + pet + radio
#
# Usage:
#   ./scripts/install.sh                    # full install
#   ./scripts/install.sh --no-radio         # skip the radio plugin
#   ./scripts/install.sh --no-pet           # skip the pet (just the agent + radio)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
VTUBER_DIR="$REPO_ROOT/vtuber-core"
RADIO_DIR="$REPO_ROOT/plugins/evolution-radio/upstream"
NOTES_DIR="${HOME}/wiki/pet-curated"

SKIP_RADIO=false
SKIP_PET=false
for arg in "$@"; do
    case $arg in
        --no-radio) SKIP_RADIO=true ;;
        --no-pet)   SKIP_PET=true ;;
    esac
done

echo "🎀 Nous Girl agent — install"
echo "============================"
echo ""

# 1. System deps
echo "📦 Checking system dependencies..."
MISSING=""
for cmd in python3 uv mpv git; do
    if ! command -v "$cmd" &> /dev/null; then
        MISSING="$MISSING $cmd"
    fi
done
if [ -n "$MISSING" ]; then
    echo "  ❌ Missing:$MISSING"
    echo "     Install with:"
    echo "       sudo apt install python3 mpv git   # Debian/Ubuntu"
    echo "       pip install uv                     # uv (Python pkg mgr)"
    exit 1
fi
echo "  ✅ python3, uv, mpv, git all present"
echo ""

# 2. vtuber-core deps (the pet)
if [ "$SKIP_PET" = false ]; then
    echo "📦 Installing vtuber-core deps (uv sync)..."
    cd "$VTUBER_DIR"
    if [ ! -d ".venv" ]; then
        uv sync
    fi
    if [ ! -f "conf.yaml" ]; then
        echo "  📝 Creating conf.yaml from default template..."
        cp config_templates/conf.default.yaml conf.yaml
        echo "  ⚠️  Edit conf.yaml to point at a model from $REPO_ROOT/models/curated.yaml"
    fi
    cd "$REPO_ROOT"
    echo "  ✅ vtuber-core ready"
    echo ""
fi

# 3. radio deps
if [ "$SKIP_RADIO" = false ]; then
    echo "📦 Installing radio deps..."
    cd "$RADIO_DIR"
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
        deactivate
    fi
    cd "$REPO_ROOT"
    echo "  ✅ radio ready"
    echo ""
fi

# 4. notes dir
echo "📂 Setting up notes directory..."
mkdir -p "$NOTES_DIR/escalations"
if [ ! -f "$NOTES_DIR/taste.yaml" ]; then
    cat > "$NOTES_DIR/taste.yaml" <<EOF
created_at: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
last_updated: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
music:
  likes: []
  skips: []
  vibes: []
visuals:
  aesthetics: []
  color_palettes: []
topics:
  active: []
  recurring: []
projects:
  active: []
  completed: []
EOF
fi
echo "  ✅ $NOTES_DIR ready"
echo ""

# 5. Hermes profile (agent)
if command -v hermes &> /dev/null; then
    if ! hermes profile list 2>/dev/null | grep -q "evolutionary-radio"; then
        echo "📝 Registering evolutionary-radio profile with Hermes..."
        hermes profile create evolutionary-radio --template "$REPO_ROOT/agent/profile-template.yaml"
    fi
    echo "  ✅ evolutionary-radio profile ready"
else
    echo "  ⚠️  Hermes CLI not found — install separately, then run:"
    echo "       hermes profile create evolutionary-radio --template agent/profile-template.yaml"
fi
echo ""

# 6. Done
echo "🎀 Install complete!"
echo ""
echo "Next steps:"
echo "  1. Edit $REPO_ROOT/models/curated.yaml — pick which models to enable"
echo "  2. Edit $VTUBER_DIR/conf.yaml — point at a model from the catalog"
echo "  3. (Optional) Customize $REPO_ROOT/pet/sprites/nous-girl/"
echo "  4. Start the pet:    $REPO_ROOT/scripts/run-pet.sh"
echo "  5. Start the radio:  $REPO_ROOT/scripts/run-radio.sh start"
echo "  6. Start the agent:  $REPO_ROOT/scripts/run-agent.sh"
echo ""
echo "Or run them all:       $REPO_ROOT/scripts/dev.sh"
