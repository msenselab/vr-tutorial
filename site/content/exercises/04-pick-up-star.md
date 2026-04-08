---
title: "Exercise 4: Pick Up the Star"
description: "Add proximity detection, HUD display, and gamepad input"
weight: 4
---

## Learning Objectives

- Use `update()` to run logic every frame (the game loop).
- Detect proximity between the player and objects with `distance()`.
- Display a HUD overlay with `Text(parent=camera.ui)`.
- Handle keyboard events with `input(key)`.
- Show and hide entities at runtime with `entity.enabled`.

## Key Concepts

### `update()` -- The Game Loop

Ursina calls `update()` once per frame (typically 60 times per second). Any logic you put inside this function runs continuously. This is where you check whether the player is near a star, whether a timer has expired, or whether a condition has been met.

```python
def update():
    # This code runs every single frame
    if distance(player.position, star.position) < 2:
        print('Close to the star!')
```

### `distance(a, b)` -- Proximity Detection

Ursina provides a built-in `distance()` function that calculates the Euclidean distance between two positions:

```python
if distance(player.position, star.position) < 2:
    star.enabled = False  # "collect" the star
```

The threshold (here `2`) controls how close the player must be. Smaller values require the player to walk right up to the object; larger values trigger from farther away.

### `entity.enabled` -- Show and Hide

Setting `entity.enabled = False` hides an entity and stops it from being processed. Setting it back to `True` brings it back. This is simpler and more efficient than creating and destroying entities at runtime:

```python
star.enabled = False   # star disappears
star.enabled = True    # star reappears (e.g. on game reset)
```

### `Text(parent=camera.ui)` -- HUD Overlay

A `Text` entity parented to `camera.ui` stays fixed on screen regardless of where the player looks:

```python
score_text = Text(
    text='Stars: 0/3',
    position=(-0.85, 0.45),
    scale=2,
    parent=camera.ui,
)
```

Position coordinates for UI elements range from roughly -0.9 to 0.9, with (0, 0) at the centre of the screen.

### `input(key)` -- Keyboard Events

Ursina calls `input(key)` whenever a key is pressed. The `key` parameter is a string like `'r'`, `'space'`, or `'escape'`:

```python
def input(key):
    if key == 'r':
        reset_game()
```

## Step-by-Step Instructions

Open `template.py` and run it. You should see the Exercise 3 room with three gold spheres. Walk around to confirm everything looks right -- the stars are visible but nothing happens when you approach them.

### TODO 1 -- Create the Score Display

Add a `score` variable and two Text entities above the player section:

```python
score = 0
score_text = Text(
    text=f'Stars: {score}/{len(stars)}',
    position=(-0.85, 0.45),
    scale=2,
    parent=camera.ui,
    color=color.white,
)

win_text = Text(
    text='Well done!',
    origin=(0, 0),
    scale=4,
    color=color.green,
    parent=camera.ui,
    enabled=False,
)
```

Run the script. You should see "Stars: 0/3" in the top-left corner.

### TODO 2 -- Loop Through Stars and Check Distance

Inside `update()`, loop through each star and check if the player is close enough:

```python
def update():
    global score
    for star in stars:
        if star.enabled and distance(player.position, star.position) < COLLECT_DISTANCE:
            # collection happens here (TODO 3)
            pass
```

The `global score` declaration is needed because you will modify `score` inside the function.

### TODO 3 -- Handle Collection

When the distance check passes, disable the star, increment the score, and update the HUD:

```python
            star.enabled = False
            score += 1
            score_text.text = f'Stars: {score}/{len(stars)}'
            print(f'Collected star! ({score}/{len(stars)})')
```

### TODO 4 -- Add Win Condition

After the for-loop (still inside `update()`), check whether all stars have been collected:

```python
    if score == len(stars):
        win_text.enabled = True
```

### TODO 5 (Bonus) -- Add Reset Function

Create a `reset_game()` function and wire it to the 'r' key:

```python
def reset_game():
    global score
    score = 0
    score_text.text = f'Stars: {score}/{len(stars)}'
    win_text.enabled = False
    for star in stars:
        star.enabled = True

def input(key):
    if key == 'r':
        reset_game()
```

## Solution Code

<details>
<summary>View full solution</summary>

```python
"""Exercise 4 -- Pick Up the Star (solution)"""

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()

# --- Room from Exercise 3 (complete) ----------------------------------------
floor = Entity(model='quad', scale=(20, 20), rotation_x=90,
               color=color.dark_gray, texture='grass', collider='box')
front_wall = Entity(model='quad', scale=(20, 5), position=(0, 2.5, 10),
                    rotation_y=0, color=color.white, texture='brick', collider='box')
back_wall = Entity(model='quad', scale=(20, 5), position=(0, 2.5, -10),
                   rotation_y=180, color=color.white, texture='brick', collider='box')
left_wall = Entity(model='quad', scale=(20, 5), position=(-10, 2.5, 0),
                   rotation_y=-90, color=color.white.tint(-0.05), texture='brick', collider='box')
right_wall = Entity(model='quad', scale=(20, 5), position=(10, 2.5, 0),
                    rotation_y=90, color=color.white.tint(-0.05), texture='brick', collider='box')
table = Entity(model='cube', scale=(2, 1, 2), position=(3, 0.5, 4),
               color=color.brown, texture='white_cube', collider='box')
lamp = Entity(model='sphere', scale=0.5, position=(3, 2.5, 4), color=color.yellow)
pillar = Entity(model='cylinder', scale=(1, 3, 1), position=(-6, 1.5, -6),
                color=color.light_gray, texture='white_cube', collider='box')
Sky()
sun = DirectionalLight()
sun.look_at(Vec3(1, -1, -1))

# --- Collectible stars -------------------------------------------------------
star_positions = [(5, 1, 5), (-5, 1, -5), (-3, 1, 7)]
stars = []
for pos in star_positions:
    star = Entity(model='sphere', color=color.gold, position=pos, scale=0.7)
    stars.append(star)

# --- Score display -----------------------------------------------------------
score = 0
score_text = Text(text=f'Stars: {score}/{len(stars)}', position=(-0.85, 0.45),
                  scale=2, parent=camera.ui, color=color.white)
win_text = Text(text='Well done!', origin=(0, 0), scale=4,
                color=color.green, parent=camera.ui, enabled=False)

# --- Player ------------------------------------------------------------------
player = FirstPersonController()
player.gravity = 0
player.position = (0, 1, 0)

COLLECT_DISTANCE = 2

def update():
    global score
    for star in stars:
        if star.enabled and distance(player.position, star.position) < COLLECT_DISTANCE:
            star.enabled = False
            score += 1
            score_text.text = f'Stars: {score}/{len(stars)}'
    if score == len(stars):
        win_text.enabled = True

def reset_game():
    global score
    score = 0
    score_text.text = f'Stars: {score}/{len(stars)}'
    win_text.enabled = False
    for star in stars:
        star.enabled = True

def input(key):
    if key == 'r':
        reset_game()

app.run()
```

</details>

## Gamepad Input with pygame

### Why pygame?

Panda3D (Ursina's rendering backend) does not always detect game controllers on macOS. The workaround is to use **pygame** as a sidecar: pygame polls the gamepad hardware, and you feed the axis values into Ursina's player each frame.

### The Pattern

```python
import pygame

pygame.init()
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0) if pygame.joystick.get_count() > 0 else None

def update():
    if joystick is None:
        return
    pygame.event.pump()            # process pygame events (non-blocking)
    lx = joystick.get_axis(0)      # left stick X
    ly = joystick.get_axis(1)      # left stick Y
    # ... apply deadzone, then move player ...
```

The critical line is `pygame.event.pump()` -- without it, pygame's internal event queue fills up and axis readings go stale.

### Demo Script

The `gamepad_demo.py` file in the exercise folder creates a simple scene and maps the left stick to movement and the right stick to camera look. If no gamepad is connected, keyboard and mouse controls still work.

<details>
<summary>View gamepad_demo.py</summary>

```python
"""Gamepad Demo: Using pygame joystick alongside Ursina"""

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import pygame

app = Ursina()

# Simple scene
Entity(model='quad', scale=20, rotation_x=90, color=color.dark_gray,
       texture='grass', collider='box')
for i in range(4):
    Entity(model='cube', position=(i * 3 - 4, 0.5, 5),
           color=color.random_color(), collider='box')
Entity(model='sphere', color=color.gold, position=(0, 1, 8), scale=0.7)
Sky()

player = FirstPersonController()
player.gravity = 0
player.position = (0, 1, 0)

# Initialize pygame joystick
pygame.init()
pygame.joystick.init()
joystick = None
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    print(f'Gamepad found: {joystick.get_name()}')
else:
    print('No gamepad detected. Use keyboard (WASD + mouse).')

status = Text(text='Gamepad: not connected', position=(-0.85, 0.45),
              scale=1.5, parent=camera.ui)
if joystick:
    status.text = f'Gamepad: {joystick.get_name()}'

DEADZONE = 0.2

def apply_deadzone(value):
    return 0 if abs(value) < DEADZONE else value

def update():
    if joystick is None:
        return
    pygame.event.pump()
    lx = apply_deadzone(joystick.get_axis(0))
    ly = apply_deadzone(joystick.get_axis(1))
    rx = apply_deadzone(joystick.get_axis(2))
    ry = apply_deadzone(joystick.get_axis(3))

    speed = 5 * time.dt
    player.position += player.forward * -ly * speed
    player.position += player.right * lx * speed
    look_speed = 2
    player.rotation_y += rx * look_speed
    camera.rotation_x = clamp(camera.rotation_x - ry * look_speed, -90, 90)
    status.text = f'L:({lx:.1f},{ly:.1f})  R:({rx:.1f},{ry:.1f})'

app.run()
```

</details>

This is the same pattern used in MazeWalker-Py for VR controller integration.

## Hints

**The score does not update.** Make sure you declared `global score` at the top of `update()`. Without it, Python creates a local variable instead of modifying the module-level `score`.

**Stars disappear immediately when the game starts.** Check that `COLLECT_DISTANCE` is not too large. Also verify the star positions are not at `(0, 1, 0)` -- that is where the player spawns.

**"Well done!" never appears.** The win check must be outside the for-loop but still inside `update()`.

## Challenges

1. **Collection sound.** Add `Audio('coin')` or `print_on_screen('Got one!')` for feedback.
2. **Animate the stars.** Make each star slowly rotate: `star.rotation_y += 50 * time.dt` inside `update()`.
3. **Add a timer.** Track collection time with `time.time()` and display it alongside the score.
4. **More stars.** Add 5 or 10 stars at random positions using `from random import uniform`.
5. **Shrinking collection radius.** Decrease `COLLECT_DISTANCE` after each pickup.

Next: [Exercise 5: Mini Experiment](/exercises/05-mini-experiment/)
