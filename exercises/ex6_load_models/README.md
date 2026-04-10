# Exercise 6 — Load 3D Models

## What you will learn

- Load external `.glb` (glTF) models into an Ursina scene
- Position, scale, and rotate imported models
- Animate a model with a sine-wave oscillation
- Detect proximity to a model and change its appearance
- Scale models dynamically with keyboard input

## Background

### GLB models on macOS

GLB files use PBR (physically based rendering) materials that require GLSL shaders macOS cannot compile. The template includes a `load_glb()` helper that strips PBR textures and shaders so the geometry renders with flat colors via the fixed-function pipeline. You lose the original textures but gain a visible, coloured 3D shape.

### Loading models

Ursina supports `.glb`, `.gltf`, `.obj`, and `.blend` formats. Use `load_model()` with the model name and directory path. For GLB files on macOS, use the `load_glb()` wrapper provided in the template:

```python
from pathlib import Path

MODELS_DIR = Path(__file__).resolve().parent.parent / 'assets' / 'models'

angel = Entity(
    model=load_glb('Angel', path=MODELS_DIR),
    scale=2,
    position=(-3, 0, 5),
    color=color.light_gray,
)
```

`Path(__file__).resolve().parent.parent` navigates from the script's directory up to `exercises/`, then into `assets/models/`. This works regardless of which directory you run the script from. The `scale` parameter uniformly resizes the model.

### Model orientation

Models from different tools may face different directions. Use `rotation_y` to turn them:

```python
angel.rotation_y = 180   # face the opposite direction
```

### Animation with sine waves

`math.sin()` produces a smooth oscillation between -1 and +1. Multiply by an angle to create rocking motion:

```python
import math

def update():
    swing.rotation_z = math.sin(time.time() * 2) * 15
```

- `time.time() * 2` controls the speed (higher = faster)
- `* 15` controls the amplitude (degrees of rotation)

## Provided models

| Model | File | Approximate size (at scale=1) |
|-------|------|-------------------------------|
| Angel statue | `assets/models/Angel.glb` | 1.4 x 1.9 x 0.6 units |
| Playground swing | `assets/models/Swing.glb` | 1.9 x 1.8 x 1.0 units |

At `scale=2`, both models are roughly human-sized within the room.

## Step-by-step instructions

### TODO 1 — Load the Angel model

Uncomment and adjust the Entity call. Start with `scale=2` and tweak until it looks right:

```python
angel = Entity(
    model=load_glb('Angel', path=MODELS_DIR),
    scale=2,
    position=(-3, 0, 5),
    rotation_y=180,
    color=color.light_gray,
)
```

### TODO 2 — Load the Swing model

Same pattern, different position and color:

```python
swing = Entity(
    model=load_glb('Swing', path=MODELS_DIR),
    scale=2,
    position=(4, 0, -3),
    color=color.brown,
)
```

### TODO 3 — Animate the swing

Add `import math` at the top, then create an `update()` function:

```python
def update():
    swing.rotation_z = math.sin(time.time() * 2) * 15
```

The swing should rock gently back and forth.

### TODO 4 — Proximity highlighting

Extend `update()` to change a model's color when the player is nearby:

```python
for name, obj in [('Angel', angel), ('Swing', swing)]:
    d = distance(player.position, obj.position)
    if d < 3:
        obj.color = color.yellow
    else:
        obj.color = color.white
```

### TODO 5 (Bonus) — Dynamic scaling

Add an `input(key)` function to resize the angel interactively:

```python
def input(key):
    if key == 'up arrow':
        angel.scale *= 1.1
    elif key == 'down arrow':
        angel.scale *= 0.9
```

## Expected result

- Two 3D models placed in the room
- The swing rocks back and forth continuously
- Models highlight yellow when you walk close
- Arrow keys grow and shrink the angel

## Troubleshooting

<details>
<summary>Model does not appear</summary>

Make sure you use `load_model('Angel', path=MODELS_DIR)`, not a raw file path string. The `MODELS_DIR` variable at the top of the script resolves the correct directory. Check that `Angel.glb` and `Swing.glb` exist in `exercises/assets/models/`.
</details>

<details>
<summary>Model appears but is black</summary>

Make sure you use `load_glb()` (not `load_model()` directly). The `load_glb()` helper strips PBR materials that macOS cannot render. Also set a `color=` on the Entity so the geometry is visible.
</details>

<details>
<summary>Model is too big or too small</summary>

Adjust `scale`. The models are about 1-2 units at `scale=1`. Try `scale=2` for human-sized in the tutorial room. Use `print(entity.bounds.size)` to see the exact dimensions.
</details>

## Going further

1. **Find more models.** Download free `.glb` models from [Sketchfab](https://sketchfab.com/features/free-3d-models) or [poly.pizza](https://poly.pizza/). Place them in `assets/models/` and load them the same way.
2. **Combine with Exercise 4.** Replace the gold sphere collectibles with 3D models — collect angel statues instead of spheres.
3. **Add colliders.** Give a model a collider so the player cannot walk through it: `angel.collider = 'box'`.
