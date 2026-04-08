"""Exercise 4 — Pick Up the Star (solution)

Builds on the Exercise 3 room by adding:
  - Three collectible gold stars at different positions
  - A HUD score counter displayed on camera.ui
  - Proximity detection in update() to collect nearby stars
  - A win condition that shows "Well done!" when all stars are collected
  - A reset function (press 'r') to restart the collection
"""

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()

# ---------------------------------------------------------------------------
# Coordinate system reminder
#   x -> right
#   y -> up
#   z -> forward (into the screen)
# ---------------------------------------------------------------------------

# --- Floor -----------------------------------------------------------------
floor = Entity(
    model='quad',
    scale=(20, 20),
    rotation_x=90,
    color=color.dark_gray,
    texture='grass',
    collider='box',
)

# --- Walls -----------------------------------------------------------------

front_wall = Entity(
    model='quad',
    scale=(20, 5),
    position=(0, 2.5, 10),
    rotation_y=0,
    color=color.white,
    texture='brick',
    collider='box',
)

back_wall = Entity(
    model='quad',
    scale=(20, 5),
    position=(0, 2.5, -10),
    rotation_y=180,
    color=color.white,
    texture='brick',
    collider='box',
)

left_wall = Entity(
    model='quad',
    scale=(20, 5),
    position=(-10, 2.5, 0),
    rotation_y=-90,
    color=color.white.tint(-0.05),
    texture='brick',
    collider='box',
)

right_wall = Entity(
    model='quad',
    scale=(20, 5),
    position=(10, 2.5, 0),
    rotation_y=90,
    color=color.white.tint(-0.05),
    texture='brick',
    collider='box',
)

# --- Furniture -------------------------------------------------------------

table = Entity(
    model='cube',
    scale=(2, 1, 2),
    position=(3, 0.5, 4),
    color=color.brown,
    texture='white_cube',
    collider='box',
)

lamp = Entity(
    model='sphere',
    scale=0.5,
    position=(3, 2.5, 4),
    color=color.yellow,
)

pillar = Entity(
    model='cylinder',
    scale=(1, 3, 1),
    position=(-6, 1.5, -6),
    color=color.light_gray,
    texture='white_cube',
    collider='box',
)

# --- Sky & Lighting --------------------------------------------------------
Sky()

sun = DirectionalLight()
sun.look_at(Vec3(1, -1, -1))

# --- Collectible stars -----------------------------------------------------
# Three gold spheres placed around the room for the player to collect.
star_positions = [
    (5, 1, 5),     # near front-right corner
    (-5, 1, -5),   # near back-left corner
    (-3, 1, 7),    # near front-left area
]

stars = []
for pos in star_positions:
    star = Entity(
        model='sphere',
        color=color.gold,
        position=pos,
        scale=0.7,
    )
    stars.append(star)

# --- Score display (HUD) --------------------------------------------------
score = 0
score_text = Text(
    text=f'Stars: {score}/{len(stars)}',
    position=(-0.85, 0.45),
    scale=2,
    parent=camera.ui,
    color=color.white,
)

# --- Win text (hidden until all stars collected) ---------------------------
win_text = Text(
    text='Well done!',
    origin=(0, 0),
    scale=4,
    color=color.green,
    parent=camera.ui,
    enabled=False,
)

# --- Player ----------------------------------------------------------------
player = FirstPersonController()
player.gravity = 0
player.position = (0, 1, 0)

# --- Game logic ------------------------------------------------------------
COLLECT_DISTANCE = 2  # how close the player must be to collect a star


def update():
    """Called every frame. Check proximity to each star."""
    global score
    for star in stars:
        if star.enabled and distance(player.position, star.position) < COLLECT_DISTANCE:
            star.enabled = False
            score += 1
            score_text.text = f'Stars: {score}/{len(stars)}'
            print(f'Collected star! ({score}/{len(stars)})')

    if score == len(stars):
        win_text.enabled = True


def reset_game():
    """Re-enable all stars and reset the score."""
    global score
    score = 0
    score_text.text = f'Stars: {score}/{len(stars)}'
    win_text.enabled = False
    for star in stars:
        star.enabled = True
    print('Game reset!')


def input(key):
    """Handle keyboard events."""
    if key == 'r':
        reset_game()


app.run()
