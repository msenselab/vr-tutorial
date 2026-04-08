# Exercise 2: Build a Room

## Learning goals

- Understand the Ursina coordinate system (x, y, z).
- Position, rotate, and scale entities to form a 3-D space.
- Use quads as walls and floors by rotating them into place.
- Switch from EditorCamera to FirstPersonController for first-person navigation.

## Key concepts

### Coordinate system

Ursina uses a right-handed coordinate system:

| Axis | Direction            |
|------|----------------------|
| x    | right (+) / left (-) |
| y    | up (+) / down (-)    |
| z    | forward (+) / back (-) |

The origin `(0, 0, 0)` is the centre of the scene. A camera looking at the default view sees +x going right, +y going up, and +z going away from the viewer.

### Entity properties you will use

| Property   | What it controls                                      |
|------------|-------------------------------------------------------|
| `model`    | Shape — `'cube'`, `'sphere'`, `'cylinder'`, `'quad'`  |
| `position` | Location in 3-D space — `(x, y, z)`                   |
| `rotation` | Euler angles — `rotation_x`, `rotation_y`, `rotation_z` (degrees) |
| `scale`    | Size — a single number for uniform, or `(sx, sy, sz)` |
| `color`    | Colour — e.g. `color.brown`, `color.white.tint(-0.1)` |
| `texture`  | Surface pattern — `'white_cube'` gives a subtle grid  |

### Using quads as walls

A `'quad'` is a flat rectangular surface. By default its normal points toward `-z` (toward the camera). To build walls you rotate the quad so it faces the direction you need:

| Wall   | Position         | `rotation_y` | Why                              |
|--------|------------------|--------------|----------------------------------|
| Front  | `(0, 2.5, 10)`  | `0`          | Already faces -z (toward centre) |
| Back   | `(0, 2.5, -10)` | `180`        | Spin 180° to face +z             |
| Left   | `(-10, 2.5, 0)` | `-90`        | Spin -90° to face +x (right)     |
| Right  | `(10, 2.5, 0)`  | `90`         | Spin 90° to face -x (left)       |

All walls use `scale=(20, 5)` — 20 units wide and 5 units tall. Their y-position is 2.5 so the bottom edge sits on the floor at y=0.

### EditorCamera vs FirstPersonController

| Feature | EditorCamera | FirstPersonController |
|---------|-------------|----------------------|
| View    | Orbit around the scene | Look through the player's eyes |
| Movement | Right-click drag, scroll, middle-click | WASD keys, mouse look |
| Best for | Inspecting / debugging your scene | Walking through the scene |

## Step-by-step instructions

Open `template.py` in your editor and run it once to see the starting scene (a floor, two walls, and a table).

### TODO 1 — Left wall

Add a wall at x = -10 that faces right:

```python
left_wall = Entity(
    model='quad',
    scale=(20, 5),
    position=(-10, 2.5, 0),
    rotation_y=-90,
    color=color.white.tint(-0.15),
    texture='white_cube',
)
```

### TODO 2 — Right wall

Add a wall at x = +10 that faces left:

```python
right_wall = Entity(
    model='quad',
    scale=(20, 5),
    position=(10, 2.5, 0),
    rotation_y=90,
    color=color.white.tint(-0.15),
    texture='white_cube',
)
```

### TODO 3 — Lamp

Place a yellow sphere above the table:

```python
lamp = Entity(
    model='sphere',
    scale=0.5,
    position=(3, 2.5, 4),
    color=color.yellow,
)
```

### TODO 4 — Pillar

Place a gray cylinder in the back-left corner:

```python
pillar = Entity(
    model='cylinder',
    scale=(1, 3, 1),
    position=(-6, 1.5, -6),
    color=color.light_gray,
    texture='white_cube',
)
```

### TODO 5 — FirstPersonController

1. Comment out `EditorCamera()`.
2. Add the import at the top of the file:
   ```python
   from ursina.prefabs.first_person_controller import FirstPersonController
   ```
3. Add the player:
   ```python
   player = FirstPersonController()
   player.gravity = 0
   player.position = (0, 1, 0)
   ```

Walk around with WASD and look around with the mouse. Press Escape to release the cursor.

## Hints

<details>
<summary>Walls are invisible from behind</summary>

A quad is only visible from its front face. If a wall appears to be missing, you are looking at its back. Check the `rotation_y` value — it controls which direction the wall faces.
</details>

<details>
<summary>Objects sink into the floor</summary>

An entity's `position` refers to its centre. A cube with `scale=(2, 1, 2)` is 1 unit tall, so its centre must be at `y=0.5` to sit on the floor (y=0). A cylinder with `scale=(1, 3, 1)` is 3 units tall, so its centre goes at `y=1.5`.
</details>

<details>
<summary>FirstPersonController falls through the floor</summary>

Set `player.gravity = 0` for a flat scene without physics. Alternatively, add `collider='box'` to the floor entity so the player has something to stand on — but with gravity off this is not required.
</details>

## Challenges

When you have finished the main exercise, try these extensions:

1. **Add a doorway.** Replace one wall with two shorter wall segments that leave a gap in the middle. Hint: use two quads with `scale=(8, 5)` placed side by side with a gap between them.

2. **Change the room size.** Make the room 30 x 30 instead of 20 x 20. You will need to update the floor scale, wall positions, and wall widths.

3. **Add more furniture.** Place a bookshelf (tall thin cube), a rug (coloured quad on the floor), or a ceiling (another quad above the room). Experiment with different models, colours, and positions.

4. **Add a second room.** Duplicate and offset the walls to create two connected rooms with a shared doorway.
