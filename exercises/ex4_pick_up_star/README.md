# Exercise 4: Pick Up the Star

## Learning goals

- Use `update()` to run logic every frame (the game loop).
- Detect proximity between the player and objects with `distance()`.
- Display a HUD overlay with `Text(parent=camera.ui)`.
- Handle keyboard events with `input(key)`.
- Show and hide entities at runtime with `entity.enabled`.

## Key concepts

### `update()` — the game loop

Ursina calls `update()` once per frame (typically 60 times per second). Any logic you put inside this function runs continuously. This is where you check whether the player is near a star, whether a timer has expired, or whether a condition has been met.

```python
def update():
    # This code runs every single frame
    if distance(player.position, star.position) < 2:
        print('Close to the star!')
```

### `distance(a, b)` — proximity detection

Ursina provides a built-in `distance()` function that calculates the Euclidean distance between two positions. Use it to detect when the player is close enough to an object:

```python
if distance(player.position, star.position) < 2:
    star.enabled = False  # "collect" the star
```

The threshold (here `2`) controls how close the player must be. Smaller values require the player to walk right up to the object; larger values trigger from farther away.

### `entity.enabled` — show and hide without destroying

Setting `entity.enabled = False` hides an entity and stops it from being processed. Setting it back to `True` brings it back. This is simpler and more efficient than creating and destroying entities at runtime:

```python
star.enabled = False   # star disappears
star.enabled = True    # star reappears (e.g. on game reset)
```

### `Text(parent=camera.ui)` — HUD overlay

A `Text` entity parented to `camera.ui` stays fixed on screen regardless of where the player looks. This is how you display scores, instructions, and status messages:

```python
score_text = Text(
    text='Stars: 0/3',
    position=(-0.85, 0.45),
    scale=1,
    parent=camera.ui,
)
```

Position coordinates for UI elements range from roughly -0.9 to 0.9, with (0, 0) at the centre of the screen.

### `input(key)` — keyboard events

Ursina calls `input(key)` whenever a key is pressed. The `key` parameter is a string like `'r'`, `'space'`, or `'escape'`:

```python
def input(key):
    if key == 'r':
        reset_game()
```

## Step-by-step instructions

Open `template.py` and run it. You should see the Exercise 3 room with three gold spheres. Walk around to confirm everything looks right — the stars are visible but nothing happens when you approach them.

### TODO 1 — Create the score display

Add a `score` variable and two Text entities above the player section:

```python
score = 0
score_text = Text(
    text=f'Stars: {score}/{len(stars)}',
    position=(-0.85, 0.45),
    scale=1,
    parent=camera.ui,
    color=color.white,
)

win_text = Text(
    text='Well done!',
    origin=(0, 0),
    scale=2,
    color=color.green,
    parent=camera.ui,
    enabled=False,
)
```

Run the script. You should see "Stars: 0/3" in the top-left corner.

### TODO 2 — Loop through stars and check distance

Inside `update()`, loop through each star and check if the player is close enough:

```python
def update():
    global score
    for star in stars:
        if star.enabled and distance(player.position, star.position) < COLLECT_DISTANCE:
            # collection happens here (TODO 3)
            pass
```

The `global score` declaration is needed because you will modify `score` inside the function. The `star.enabled` check prevents collecting a star that is already hidden.

### TODO 3 — Handle collection

When the distance check passes, disable the star, increment the score, and update the HUD:

```python
            star.enabled = False
            score += 1
            score_text.text = f'Stars: {score}/{len(stars)}'
            print(f'Collected star! ({score}/{len(stars)})')
```

Run and walk up to a star. It should disappear and the counter should update.

### TODO 4 — Add win condition

After the for-loop (still inside `update()`), check whether all stars have been collected:

```python
    if score == len(stars):
        win_text.enabled = True
```

Collect all three stars to see the "Well done!" message appear on screen.

### TODO 5 (Bonus) — Add reset function

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

Collect all stars, see "Well done!", press 'r', and all stars reappear with the score back to 0.

## Gamepad input

### Why pygame?

Panda3D (Ursina's rendering backend) does not always detect game controllers on macOS. The workaround is to use **pygame** as a sidecar: pygame polls the gamepad hardware, and you feed the axis values into Ursina's player each frame.

### The pattern

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

The critical line is `pygame.event.pump()` — without it, pygame's internal event queue fills up and axis readings go stale.

### Demo script

See `gamepad_demo.py` in this folder for a complete working example. It creates a simple scene and maps the left stick to movement and the right stick to camera look. If no gamepad is connected, keyboard and mouse controls still work via FirstPersonController.

This is the same pattern used in MazeWalker-Py for VR controller integration.

## Hints

<details>
<summary>The score does not update</summary>

Make sure you declared `global score` at the top of `update()`. Without it, Python creates a local variable instead of modifying the module-level `score`.
</details>

<details>
<summary>Stars disappear immediately when the game starts</summary>

Check that `COLLECT_DISTANCE` is not too large. A value of 2 means the player must be within 2 units. If you set it to 20, the player starts close enough to collect everything instantly. Also verify the star positions are not at `(0, 1, 0)` — that is where the player spawns.
</details>

<details>
<summary>"Well done!" never appears</summary>

The win check must be outside the for-loop but still inside `update()`. If it is inside the loop, it only checks after each individual star rather than after all stars have been processed. Also verify that `win_text` was created with `enabled=False` so it starts hidden.
</details>

## Challenges

When you have finished the main exercise, try these extensions:

1. **Collection sound.** Add `Audio('coin')` or `print_on_screen('Got one!')` inside the collection block to give auditory or visual feedback.

2. **Animate the stars.** Make each star slowly rotate by adding `star.rotation_y += 50 * time.dt` inside `update()` before the distance check.

3. **Add a timer.** Track how long it takes to collect all stars using `time.time()`. Display the elapsed time alongside the score.

4. **More stars.** Add 5 or 10 stars at random positions: `from random import uniform` then `position=(uniform(-8, 8), 1, uniform(-8, 8))`.

5. **Shrinking collection radius.** Make each successive star harder to collect by decreasing `COLLECT_DISTANCE` after each pickup.
