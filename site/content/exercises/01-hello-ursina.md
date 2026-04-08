---
title: "Exercise 1: Hello Ursina"
description: "Verify your setup and create your first 3D scene"
weight: 1
---

## Learning Objectives

- Confirm that Ursina is installed correctly and can open a 3D window.
- Understand the minimal structure of an Ursina application.
- Experiment with Entity properties to build intuition about the engine.

## The Code

Create a file called `hello_cube.py` (or use the one from the repository):

```python
from ursina import *

app = Ursina()
Entity(model='cube', color=color.orange, texture='white_cube')
EditorCamera()
app.run()
```

Run it:

```bash
python hello_cube.py
```

## What to Expect

A window opens showing an orange cube with a subtle grid texture. The background is dark.

**Camera controls (EditorCamera):**

| Action              | Effect            |
|---------------------|-------------------|
| Right-click + drag  | Orbit around cube |
| Scroll wheel        | Zoom in/out       |
| Middle-click + drag | Pan the view      |

## Key Concepts

| Concept         | What It Does                                                                  |
|-----------------|-------------------------------------------------------------------------------|
| `Ursina()`      | Creates the application and opens a window.                                   |
| `Entity`        | The basic building block of every Ursina scene. Anything visible (or invisible) in the world is an Entity. |
| `EditorCamera()` | Adds an orbit camera so you can inspect the scene with the mouse.            |
| `app.run()`     | Starts the game loop (rendering, input, updates). Nothing appears until this is called. |

These four lines are the skeleton of every Ursina program. All subsequent exercises build on this structure.

## Try It Yourself

Close the window, edit `hello_cube.py`, and experiment:

1. **Change the colour.** Replace `color.orange` with `color.red`, `color.azure`, or `color.lime`.

2. **Change the model.** Replace `'cube'` with `'sphere'`, `'cylinder'`, or `'cone'`.

3. **Move the entity.** Add a `position` argument: `position=(2, 1, 0)`.

4. **Add a second entity.** Duplicate the `Entity(...)` line, give the copy a different model or colour, and offset its position so the two objects do not overlap.

```python
# Example: two objects side by side
Entity(model='cube', color=color.orange, texture='white_cube', position=(-1, 0, 0))
Entity(model='sphere', color=color.azure, position=(1, 0, 0))
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: No module named 'ursina'` | Run `pip install ursina` in your virtual environment. |
| Window opens and immediately closes | Check terminal for errors. Re-run `pip install ursina`. |
| Black window / no cube visible | Update your GPU driver, or test with `window.render_mode = 'wireframe'` before `app.run()`. |
| Display errors on a headless server | Ursina needs a display. Use X-forwarding (`ssh -X`) or a machine with a monitor. |

Once you see the cube, you are ready for [Exercise 2: Build a Room](/exercises/02-build-a-room/).
