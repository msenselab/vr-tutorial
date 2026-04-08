# Exercise 1 — Hello Ursina

## Learning goal

Verify that Ursina is installed correctly and that your system can open a 3-D window. If you see a spinning orange cube, you are ready for the rest of the tutorial.

## How to run

```bash
python hello_cube.py
```

A window should open within a few seconds.

## What you should see

An orange textured cube floating in the centre of a dark scene.

**Camera controls (EditorCamera):**

- **Right-click + drag** — orbit around the cube
- **Scroll wheel** — zoom in / out
- **Middle-click + drag** — pan

## Try it yourself

Once the cube appears, close the window, edit `hello_cube.py`, and experiment:

1. **Change the colour** — replace `color.orange` with `color.red`, `color.azure`, or `color.lime`.
2. **Change the model** — replace `'cube'` with `'sphere'`, `'cylinder'`, or `'cone'`.
3. **Move the entity** — add a `position` argument: `position=(2, 1, 0)`.
4. **Add a second entity** — duplicate the `Entity(...)` line, give the copy a different model or colour, and offset its position so the two objects don't overlap.

## Key concepts

| Concept | What it does |
|---------|-------------|
| `Ursina()` | Creates the application and opens a window. |
| `Entity` | The basic building block of every Ursina scene — anything visible (or invisible) in the world is an Entity. |
| `EditorCamera()` | Adds an orbit camera so you can inspect the scene with the mouse. |
| `app.run()` | Starts the game loop (rendering, input, updates). Nothing appears until this is called. |

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: No module named 'ursina'` | Ursina is not installed. Run `pip install ursina` (use the same Python environment you launch the script with). |
| Window opens and immediately closes | Check the terminal for error messages. A common cause is a missing dependency — re-run `pip install ursina` to make sure everything is in place. |
| Black window / no cube visible | Your GPU driver may need updating, or the default shader is unsupported. Try adding `window.render_mode = 'wireframe'` before `app.run()` to test. |
| Display-related errors on a headless server | Ursina needs a display. If you are running over SSH, use X-forwarding (`ssh -X`) or work on a machine with a monitor attached. |
