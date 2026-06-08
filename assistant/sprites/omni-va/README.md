# Omni VA eikon — VA avatar
# Source: eikon package nous (vendored from herm-tui/node_modules/eikon/eikons/nous)

## Files
- `base.png` (98KB) — default avatar, used for the VA window and as the catalog default
- `manifest.json` — eikon manifest with state references
- `states/` — per-state variants (idle, listening, thinking, speaking, working, error)

## Live2D upgrade path
The current eikon is a static PNG, suitable for v1 of the VA. To upgrade to
Live2D (for animated expressions, mouse-tracking eye movement, click animations):

1. Source a Live2D model in Cubism 4 format
2. Drop the `.moc3` + textures + `*.model3.json` into `vtuber-core/live2d-models/nous-assistant/`
3. Update `vtuber-core/characters/nous-assistant.yaml` `live2d_model_name` to `nous-assistant`
4. Re-test

## Vibe
Warm, studious, college-age energy. Cosmic variant friendly (the existing Nous
brand uses monochrome with teal/gold cosmic accents).
