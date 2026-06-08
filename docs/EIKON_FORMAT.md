# Eikon Format

The pet supports two eikon formats:

## v1 — Static PNG (current)

The simplest format. A single PNG, displayed as the pet's avatar.

```
pet/sprites/<eikon-name>/
├── README.md           (optional)
├── base.png            (default avatar)
├── manifest.json       (eikon metadata, optional)
└── states/             (per-state variants, optional)
    ├── idle/loop.mp4
    ├── listening/start.mp4
    ├── thinking/start.mp4
    ├── speaking/loop.mp4
    ├── working/start.mp4
    └── error/start.mp4
```

States follow the Herm eikon convention:
- `idle` — default resting state
- `listening` — user is speaking
- `thinking` — model is generating
- `speaking` — model has output
- `working` — model is in a tool loop
- `error` — something went wrong

States can be either a still image (`.png`) or a short video loop
(`.mp4`). If a state is missing, the base image is used.

## v2 — Live2D (planned upgrade)

To upgrade a v1 eikon to Live2D:

1. Source a Live2D model in Cubism 4 format (`.moc3` + textures)
2. Drop the files into `vtuber-core/live2d-models/<eikon-name>/`:
   ```
   vtuber-core/live2d-models/nous-girl/
   ├── nous-girl.moc3
   ├── nous-girl.model3.json
   ├── textures/
   │   └── *.png
   └── expressions/
       └── *.exp3.json
   ```
3. Update `vtuber-core/characters/nous-girl.yaml`:
   ```yaml
   character_config:
     live2d_model_name: "nous-girl"   # was: ""
     avatar_path: ""                   # was: "avatars/nous-girl.png"
   ```
4. Re-test the pet

## Brand constraints (Nous style)

When generating or commissioning new eikon sprites, follow the Nous
brand guide:

- **Color:** Monochrome B&W is the default. Cosmic variant (teal + gold
  nebula) is the exception, used for hero/banner art only.
- **Style:** Retro manga 70s shoujo line art, halftone grain, clean
  silhouettes, simple uncluttered backgrounds.
- **Mood:** Bright, studious, warm, curious. College-age energy.
- **Tagline:** "TOWARDS SELF-IMPROVEMENT" (optional, in the about menu).

The Nous Girl eikon shipped here was sourced from the eikon package
in herm-tui — a 48×24 braille-style rendering. It works for v1 but
should be upgraded to a proper Live2D for the v2 pet.
