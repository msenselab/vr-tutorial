---
title: "Exercise 2: Build a Room"
description: "Construct a 3D room from primitives with first-person navigation"
weight: 2
---

## Learning Objectives

- Understand the Ursina coordinate system (x, y, z).
- Position, rotate, and scale entities to form a 3D space.
- Use quads as walls and floors by rotating them into place.
- Switch from EditorCamera to FirstPersonController for first-person navigation.

## Key Concepts

### Coordinate System

Ursina uses a right-handed coordinate system:

| Axis | Direction                |
|------|--------------------------|
| x    | right (+) / left (-)     |
| y    | up (+) / down (-)        |
| z    | forward (+) / back (-)   |

The origin `(0, 0, 0)` is the centre of the scene.

### Entity Properties

| Property     | What It Controls                                        |
|--------------|---------------------------------------------------------|
| `model`      | Shape -- `'cube'`, `'sphere'`, `'cylinder'`, `'quad'`   |
| `position`   | Location in 3D space -- `(x, y, z)`                     |
| `rotation`   | Euler angles -- `rotation_x`, `rotation_y`, `rotation_z` (degrees) |
| `scale`      | Size -- a single number for uniform, or `(sx, sy, sz)`  |
| `color`      | Colour -- e.g. `color.brown`, `color.white.tint(-0.1)`  |
| `texture`    | Surface pattern -- `'white_cube'` gives a subtle grid   |

### Using Quads as Walls

A `'quad'` is a flat rectangular surface. By default its normal points toward `-z` (toward the camera). To build walls you rotate the quad so it faces the direction you need:

| Wall  | Position           | `rotation_y` | Why                                  |
|-------|--------------------|--------------|--------------------------------------|
| Front | `(0, 2.5, 10)`    | `0`          | Already faces -z (toward centre)     |
| Back  | `(0, 2.5, -10)`   | `180`        | Spin 180 degrees to face +z          |
| Left  | `(-10, 2.5, 0)`   | `-90`        | Spin -90 degrees to face +x (right)  |
| Right | `(10, 2.5, 0)`    | `90`         | Spin 90 degrees to face -x (left)    |

All walls use `scale=(20, 5)` -- 20 units wide and 5 units tall. Their y-position is 2.5 so the bottom edge sits on the floor at y=0.

### EditorCamera vs FirstPersonController

| Feature  | EditorCamera                     | FirstPersonController              |
|----------|----------------------------------|------------------------------------|
| View     | Orbit around the scene           | Look through the player's eyes     |
| Movement | Right-click drag, scroll, middle-click | WASD keys, mouse look         |
| Best for | Inspecting / debugging your scene | Walking through the scene         |

## Step-by-Step Instructions

Open `template.py` in your editor and run it once to see the starting scene (a floor, two walls, and a table).

### TODO 1 -- Left Wall

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

### TODO 2 -- Right Wall

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

### TODO 3 -- Lamp

Place a yellow sphere above the table:

```python
lamp = Entity(
    model='sphere',
    scale=0.5,
    position=(3, 2.5, 4),
    color=color.yellow,
)
```

### TODO 4 -- Pillar

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

### TODO 5 -- FirstPersonController

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

## Template Code

The template provides a floor, front wall, back wall, and a table. You fill in the missing walls, furniture, and player controller.

<details>
<summary>View full template</summary>

```python
"""Exercise 2 -- Build a Room (template)

Your task: complete the TODOs below to build a 3-D room you can walk through.
"""

from ursina import *

app = Ursina()

# --- Floor (complete) -------------------------------------------------------
floor = Entity(
    model='quad',
    scale=(20, 20),
    rotation_x=90,
    color=color.dark_gray,
    texture='white_cube',
)

# --- Walls (front and back complete, left and right are TODOs) ---------------

front_wall = Entity(
    model='quad',
    scale=(20, 5),
    position=(0, 2.5, 10),
    rotation_y=0,
    color=color.white.tint(-0.1),
    texture='white_cube',
)

back_wall = Entity(
    model='quad',
    scale=(20, 5),
    position=(0, 2.5, -10),
    rotation_y=180,
    color=color.white.tint(-0.1),
    texture='white_cube',
)

# TODO 1: Left wall
# TODO 2: Right wall

# --- Furniture ---------------------------------------------------------------
table = Entity(
    model='cube',
    scale=(2, 1, 2),
    position=(3, 0.5, 4),
    color=color.brown,
    texture='white_cube',
)

# TODO 3: Lamp
# TODO 4: Pillar

# --- Camera / Player ---------------------------------------------------------
EditorCamera()
# TODO 5: Switch to FirstPersonController

app.run()
```

</details>

## Solution Code

<details>
<summary>View full solution</summary>

```python
"""Exercise 2 -- Build a Room (solution)"""

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()

# --- Floor -----------------------------------------------------------------
floor = Entity(
    model='quad',
    scale=(20, 20),
    rotation_x=90,
    color=color.dark_gray,
    texture='white_cube',
    collider='box',
)

# --- Walls -----------------------------------------------------------------
front_wall = Entity(
    model='quad', scale=(20, 5), position=(0, 2.5, 10),
    rotation_y=0, color=color.white.tint(-0.1),
    texture='white_cube', collider='box',
)
back_wall = Entity(
    model='quad', scale=(20, 5), position=(0, 2.5, -10),
    rotation_y=180, color=color.white.tint(-0.1),
    texture='white_cube', collider='box',
)
left_wall = Entity(
    model='quad', scale=(20, 5), position=(-10, 2.5, 0),
    rotation_y=-90, color=color.white.tint(-0.15),
    texture='white_cube', collider='box',
)
right_wall = Entity(
    model='quad', scale=(20, 5), position=(10, 2.5, 0),
    rotation_y=90, color=color.white.tint(-0.15),
    texture='white_cube', collider='box',
)

# --- Furniture -------------------------------------------------------------
table = Entity(
    model='cube', scale=(2, 1, 2), position=(3, 0.5, 4),
    color=color.brown, texture='white_cube', collider='box',
)
lamp = Entity(
    model='sphere', scale=0.5, position=(3, 2.5, 4),
    color=color.yellow,
)
pillar = Entity(
    model='cylinder', scale=(1, 3, 1), position=(-6, 1.5, -6),
    color=color.light_gray, texture='white_cube', collider='box',
)

# --- Player ----------------------------------------------------------------
player = FirstPersonController()
player.gravity = 0
player.position = (0, 1, 0)

app.run()
```

</details>

## Hints

**Walls are invisible from behind.** A quad is only visible from its front face. If a wall appears to be missing, you are looking at its back. Check the `rotation_y` value.

**Objects sink into the floor.** An entity's `position` refers to its centre. A cube with `scale=(2, 1, 2)` is 1 unit tall, so its centre must be at `y=0.5` to sit on the floor (y=0). A cylinder with `scale=(1, 3, 1)` is 3 units tall, so its centre goes at `y=1.5`.

**FirstPersonController falls through the floor.** Set `player.gravity = 0` for a flat scene without physics.

## Challenges

1. **Add a doorway.** Replace one wall with two shorter wall segments that leave a gap in the middle.
2. **Change the room size.** Make the room 30 x 30 instead of 20 x 20. Update floor scale, wall positions, and wall widths.
3. **Add more furniture.** Place a bookshelf (tall thin cube), a rug (coloured quad on the floor), or a ceiling (another quad above the room).
4. **Add a second room.** Duplicate and offset the walls to create two connected rooms with a shared doorway.

Next: [Exercise 3: Make It Real](/exercises/03-make-it-real/)
