---
title: "Exercise 6: Load 3D Models"
description: "Import GLB models, strip PBR shaders for macOS, animate and interact"
weight: 6
---

## Learning Objectives

- Load external `.glb` models into an Ursina scene using `load_model()`.
- Understand why GLB files need special handling on macOS (PBR vs fixed-function pipeline).
- Position, scale, and rotate imported models in 3D space.
- Animate a model with a sine-wave oscillation.
- Detect player proximity and change a model's appearance.

## Background

### GLB and PBR Materials

GLB (binary glTF) is the standard format for 3D models on the web and in game engines. Each GLB file packages geometry, textures, and PBR (physically based rendering) material descriptions into a single file.

PBR materials include:

| Texture | Purpose |
|---------|---------|
| **Base Color** (albedo) | The surface color/pattern |
| **Metallic-Roughness** | How shiny or matte the surface is |
| **Normal Map** | Surface detail without extra geometry |

The problem on macOS: Ursina's auto-shader (GLSL 130) cannot compile on macOS OpenGL 2.1. When a `DirectionalLight` is in the scene, the failed shader makes GLB models go black.

### The `load_glb()` Helper

The template provides a `load_glb()` function that:

1. Loads the model geometry and textures with `load_model()`
2. Strips PBR-only textures (metallic-roughness, normal maps)
3. Keeps the **base-color texture** so the model looks correct
4. Sets `setShaderOff(2)` and `setLightOff(2)` with priority 2 to override the scene's auto-shader

```python
angel = Entity(
    model=load_glb('Angel', path=MODELS_DIR),
    scale=2,
    position=(-3, 0, 5),
)
```

The room walls still receive `DirectionalLight` lighting normally — only the GLB models bypass it.

### Model Path Resolution

Models are stored in `exercises/assets/models/`. The template resolves the path relative to the script file so it works from any working directory:

```python
MODELS_DIR = Path(__file__).resolve().parent.parent / 'assets' / 'models'
```

### Sine-Wave Animation

`math.sin()` produces smooth oscillation between -1 and +1:

```python
def update():
    swing.rotation_z = math.sin(time.time() * 2) * 15
```

- `time.time() * 2` — speed (higher = faster rocking)
- `* 15` — amplitude (degrees of rotation)

## Provided Models

| Model | File | Size at scale=1 |
|-------|------|-----------------|
| Angel statue | `Angel.glb` | ~1.4 x 1.9 x 0.6 units |
| Playground swing | `Swing.glb` | ~1.9 x 1.8 x 1.0 units |

At `scale=2`, both are roughly human-sized in the 20x20 room.

## Step-by-Step Instructions

### TODO 1 — Load the Angel

```python
angel = Entity(
    model=load_glb('Angel', path=MODELS_DIR),
    scale=2,
    position=(-3, 0, 5),
    rotation_y=180,
)
```

### TODO 2 — Load the Swing

```python
swing = Entity(
    model=load_glb('Swing', path=MODELS_DIR),
    scale=2,
    position=(4, 0, -3),
)
```

### TODO 3 — Animate the Swing

```python
import math

def update():
    swing.rotation_z = math.sin(time.time() * 2) * 15
```

### TODO 4 — Proximity Highlighting

```python
for name, obj in [('Angel', angel), ('Swing', swing)]:
    d = distance(player.position, obj.position)
    if d < 3:
        obj.color = color.yellow
    else:
        obj.color = color.white
```

### TODO 5 (Bonus) — Dynamic Scaling

```python
def input(key):
    if key == 'up arrow':
        angel.scale *= 1.1
    elif key == 'down arrow':
        angel.scale *= 0.9
```

## Troubleshooting

### Model does not appear

Make sure you use `load_glb()` (not `load_model()` directly). Check that `Angel.glb` and `Swing.glb` exist in `exercises/assets/models/`.

### Model appears black

This happens when `DirectionalLight` applies its auto-shader. The `load_glb()` helper prevents this with `setShaderOff(2)`. If you loaded the model with plain `load_model()`, switch to `load_glb()`.

### Model is too big or too small

Adjust `scale`. Use `print(entity.bounds.size)` to see exact dimensions.

## Going Further

1. **Find more models.** Download free `.glb` models from [Sketchfab](https://sketchfab.com/features/free-3d-models) or [poly.pizza](https://poly.pizza/). Place them in `assets/models/` and load them the same way.
2. **Combine with Exercise 4.** Replace the gold sphere collectibles with 3D model collectibles.
3. **Add colliders.** Give a model a collider so the player cannot walk through it: `angel.collider = 'box'`.
