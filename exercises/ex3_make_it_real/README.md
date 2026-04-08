# Exercise 3: Make It Real

## Learning goals

- Add colliders to prevent the player from walking through walls.
- Apply textures to surfaces for a more realistic appearance.
- Use a Sky entity to create an atmospheric background.
- Place a collectible object as a setup for interaction in Exercise 4.
- Adjust lighting to improve depth and texture visibility.

## Key concepts

### Why colliders matter

Without a `collider` parameter, entities are purely visual — the player walks straight through them. Adding `collider='box'` tells Ursina to create an invisible collision boundary that matches the entity's shape. Try removing the collider from one wall to see what happens: you can walk right through it.

```python
# Without collider — decoration only
wall = Entity(model='quad', scale=(20, 5), position=(0, 2.5, 10))

# With collider — solid barrier
wall = Entity(model='quad', scale=(20, 5), position=(0, 2.5, 10), collider='box')
```

### Built-in textures

Ursina ships with several textures you can reference by name:

| Texture name   | Appearance                  |
|----------------|-----------------------------|
| `'white_cube'` | Subtle white grid pattern   |
| `'brick'`      | Brick wall pattern          |
| `'grass'`      | Green grass pattern         |
| `'shore'`      | Sandy beach texture         |

You can combine `texture=` with `color=` to tint the texture:

```python
Entity(model='quad', texture='brick', color=color.white)         # neutral bricks
Entity(model='quad', texture='brick', color=color.orange.tint(-0.2))  # warm bricks
```

### Sky entity

`Sky()` wraps the entire scene in a panoramic background image. One line of code replaces the default black void with a blue sky and clouds, making even a simple scene feel immersive.

### Collectible placeholder

In this exercise the golden sphere is just a static entity — it looks like something you would want to pick up but it does not respond to the player yet. Exercise 4 adds proximity detection to make it interactive. Placing the entity now keeps this exercise focused on scene polish.

### Directional lighting

`DirectionalLight()` simulates sunlight. Point it with `look_at()` to control where the light comes from. Directional lighting adds subtle shading that makes textures and 3-D shapes more readable.

## Step-by-step instructions

Open `template.py` and run it to confirm the room from Exercise 2 loads correctly.

### TODO 1 — Add colliders to walls and floor

The front wall already has `collider='box'` as an example. Walk into it — you stop. Now walk into the back wall — you pass through. Add `collider='box'` to the back wall, left wall, right wall, and floor:

```python
# Add this parameter to each Entity that should be solid:
collider='box',
```

Test by walking into every wall. You should be blocked by all four.

### TODO 2 — Apply textures

Replace the `texture='white_cube'` on the floor and walls:

- **Floor:** change to `texture='grass'`
- **Walls:** change to `texture='brick'`

```python
floor = Entity(
    ...,
    texture='grass',    # was 'white_cube'
)
```

```python
front_wall = Entity(
    ...,
    texture='brick',    # was 'white_cube'
)
# Repeat for back_wall, left_wall, right_wall
```

### TODO 3 — Add a sky

Below the furniture section, add one line:

```python
Sky()
```

Run the scene — the black background is replaced with a panoramic sky.

### TODO 4 — Create a collectible sphere

Add a golden sphere somewhere in the room:

```python
collectible = Entity(
    model='sphere',
    color=color.yellow,
    position=(5, 1, 5),
    scale=0.7,
)
```

Walk up to it and look at it. For now it just sits there — Exercise 4 will make it respond when you get close.

### TODO 5 (optional) — Add lighting

Add a directional light to bring out the textures:

```python
sun = DirectionalLight()
sun.look_at(Vec3(1, -1, -1))
```

## What changed

| Before (Exercise 2)            | After (Exercise 3)                     |
|--------------------------------|----------------------------------------|
| Walk through every wall        | Colliders block movement               |
| White grid texture everywhere  | Grass floor, brick walls               |
| Black void background          | Panoramic sky                          |
| Nothing to interact with       | Golden sphere waiting in the corner    |
| Flat, uniform lighting         | Directional light adds depth           |

## Hints

<details>
<summary>I can still walk through a wall</summary>

Make sure you added `collider='box'` as a parameter inside the `Entity(...)` call, not after it. The comma matters — check that the parameter appears before the closing parenthesis.
</details>

<details>
<summary>The texture does not appear</summary>

Texture names are case-sensitive strings. Make sure you write `texture='brick'` (lowercase, in quotes). If a built-in texture does not load on your system, fall back to `texture='white_cube'` with a tinted `color=` to get a visual difference.
</details>

<details>
<summary>The scene is too dark / too bright</summary>

DirectionalLight adds light on top of the default ambient light. If the scene looks washed out, try pointing the light in a different direction: `sun.look_at(Vec3(-1, -1, 1))`. If it is too dark, you may also adjust `AmbientLight(color=color.rgba(100, 100, 100, 255))`.
</details>

## Challenges

When you have finished the main exercise, try these extensions:

1. **Custom texture from a file.** Download a `.png` texture and load it with `texture='path/to/your_texture.png'`. Place the image file next to your script.

2. **Different sky.** Try `Sky(color=color.light_gray)` for an overcast look, or experiment with `Sky(texture='sky_sunset')` if available.

3. **Multiple collectibles.** Place three or four spheres at different positions around the room using different colours:

   ```python
   for pos, col in [((5, 1, 5), color.yellow), ((-5, 1, -5), color.cyan), ((0, 1, 7), color.magenta)]:
       Entity(model='sphere', color=col, position=pos, scale=0.7)
   ```

4. **Ceiling.** Add a fifth quad above the room as a ceiling. Hint: `position=(0, 5, 0)` with `rotation_x=90` and `scale=(20, 20)`.
