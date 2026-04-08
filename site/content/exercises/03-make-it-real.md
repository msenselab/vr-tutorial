---
title: "Exercise 3: Make It Real"
description: "Add colliders, textures, skybox, and lighting to the room"
weight: 3
---

## Learning Objectives

- Add colliders to prevent the player from walking through walls.
- Apply textures to surfaces for a more realistic appearance.
- Use a Sky entity to create an atmospheric background.
- Place a collectible object as setup for interaction in Exercise 4.
- Adjust lighting to improve depth and texture visibility.

## Key Concepts

### Why Colliders Matter

Without a `collider` parameter, entities are purely visual -- the player walks straight through them. Adding `collider='box'` tells Ursina to create an invisible collision boundary that matches the entity's shape.

```python
# Without collider -- decoration only
wall = Entity(model='quad', scale=(20, 5), position=(0, 2.5, 10))

# With collider -- solid barrier
wall = Entity(model='quad', scale=(20, 5), position=(0, 2.5, 10), collider='box')
```

### Built-in Textures

Ursina ships with several textures you can reference by name:

| Texture name   | Appearance                  |
|----------------|-----------------------------|
| `'white_cube'` | Subtle white grid pattern   |
| `'brick'`      | Brick wall pattern          |
| `'grass'`      | Green grass pattern         |
| `'shore'`      | Sandy beach texture         |

You can combine `texture=` with `color=` to tint the texture:

```python
Entity(model='quad', texture='brick', color=color.white)              # neutral bricks
Entity(model='quad', texture='brick', color=color.orange.tint(-0.2))  # warm bricks
```

### Sky Entity

`Sky()` wraps the entire scene in a panoramic background image. One line of code replaces the default black void with a blue sky and clouds, making even a simple scene feel immersive.

### Directional Lighting

`DirectionalLight()` simulates sunlight. Point it with `look_at()` to control where the light comes from. Directional lighting adds subtle shading that makes textures and 3D shapes more readable.

## Step-by-Step Instructions

Open `template.py` and run it to confirm the room from Exercise 2 loads correctly.

### TODO 1 -- Add Colliders to Walls and Floor

The front wall already has `collider='box'` as an example. Walk into it -- you stop. Now walk into the back wall -- you pass through. Add `collider='box'` to the back wall, left wall, right wall, and floor:

```python
collider='box',
```

Test by walking into every wall. You should be blocked by all four.

### TODO 2 -- Apply Textures

Replace the `texture='white_cube'` on the floor and walls:

- **Floor:** change to `texture='grass'`
- **Walls:** change to `texture='brick'`

### TODO 3 -- Add a Sky

Below the furniture section, add one line:

```python
Sky()
```

The black background is replaced with a panoramic sky.

### TODO 4 -- Create a Collectible Sphere

Add a golden sphere somewhere in the room:

```python
collectible = Entity(
    model='sphere',
    color=color.yellow,
    position=(5, 1, 5),
    scale=0.7,
)
```

Walk up to it and look at it. For now it just sits there -- Exercise 4 will make it respond when you get close.

### TODO 5 (Optional) -- Add Lighting

Add a directional light to bring out the textures:

```python
sun = DirectionalLight()
sun.look_at(Vec3(1, -1, -1))
```

## What Changed

| Before (Exercise 2)            | After (Exercise 3)                     |
|--------------------------------|----------------------------------------|
| Walk through every wall        | Colliders block movement               |
| White grid texture everywhere  | Grass floor, brick walls               |
| Black void background          | Panoramic sky                          |
| Nothing to interact with       | Golden sphere waiting in the corner    |
| Flat, uniform lighting         | Directional light adds depth           |

## Solution Code

<details>
<summary>View full solution</summary>

```python
"""Exercise 3 -- Make It Real (solution)"""

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()

# --- Floor -----------------------------------------------------------------
floor = Entity(
    model='quad', scale=(20, 20), rotation_x=90,
    color=color.dark_gray, texture='grass', collider='box',
)

# --- Walls (all with collider='box' and texture='brick') -------------------
front_wall = Entity(
    model='quad', scale=(20, 5), position=(0, 2.5, 10),
    rotation_y=0, color=color.white, texture='brick', collider='box',
)
back_wall = Entity(
    model='quad', scale=(20, 5), position=(0, 2.5, -10),
    rotation_y=180, color=color.white, texture='brick', collider='box',
)
left_wall = Entity(
    model='quad', scale=(20, 5), position=(-10, 2.5, 0),
    rotation_y=-90, color=color.white.tint(-0.05), texture='brick', collider='box',
)
right_wall = Entity(
    model='quad', scale=(20, 5), position=(10, 2.5, 0),
    rotation_y=90, color=color.white.tint(-0.05), texture='brick', collider='box',
)

# --- Furniture -------------------------------------------------------------
table = Entity(
    model='cube', scale=(2, 1, 2), position=(3, 0.5, 4),
    color=color.brown, texture='white_cube', collider='box',
)
lamp = Entity(model='sphere', scale=0.5, position=(3, 2.5, 4), color=color.yellow)
pillar = Entity(
    model='cylinder', scale=(1, 3, 1), position=(-6, 1.5, -6),
    color=color.light_gray, texture='white_cube', collider='box',
)

# --- Sky -------------------------------------------------------------------
Sky()

# --- Collectible sphere ----------------------------------------------------
collectible = Entity(
    model='sphere', color=color.yellow, position=(5, 1, 5), scale=0.7,
)

# --- Lighting --------------------------------------------------------------
sun = DirectionalLight()
sun.look_at(Vec3(1, -1, -1))

# --- Player ----------------------------------------------------------------
player = FirstPersonController()
player.gravity = 0
player.position = (0, 1, 0)

app.run()
```

</details>

## Hints

**I can still walk through a wall.** Make sure you added `collider='box'` as a parameter inside the `Entity(...)` call, not after it. The comma matters.

**The texture does not appear.** Texture names are case-sensitive strings. Make sure you write `texture='brick'` (lowercase, in quotes).

**The scene is too dark or too bright.** Try pointing the light in a different direction: `sun.look_at(Vec3(-1, -1, 1))`.

## Challenges

1. **Custom texture from a file.** Download a `.png` texture and load it with `texture='path/to/your_texture.png'`.
2. **Different sky.** Try `Sky(color=color.light_gray)` for an overcast look.
3. **Multiple collectibles.** Place three or four spheres at different positions with different colours.
4. **Ceiling.** Add a fifth quad above the room: `position=(0, 5, 0)` with `rotation_x=90` and `scale=(20, 20)`.

Next: [Exercise 4: Pick Up the Star](/exercises/04-pick-up-star/)
