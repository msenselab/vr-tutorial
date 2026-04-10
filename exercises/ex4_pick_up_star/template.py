"""Exercise 4 — Pick Up the Star (template)

Your task: make the stars collectible.

The room from Exercise 3 is complete below — colliders, textures, sky,
lighting, and three gold stars are already placed. Run it now to confirm:

    python template.py

You can see the stars but nothing happens when you walk up to them.
Complete the TODOs to add a score counter, proximity detection, a win
condition, and a reset function.
"""

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()

# ---------------------------------------------------------------------------
# The room from Exercise 3 (complete — do NOT change the structure)
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

# --- TODO 1: Create the score display -------------------------------------
# Add a Text entity on camera.ui to show how many stars have been collected.
#
# You will need a global variable to track the score:
#   score = 0
#
# Then create the text:
#   score_text = Text(
#       text=f'Stars: {score}/{len(stars)}',
#       position=(-0.85, 0.45),
#       scale=1,
#       parent=camera.ui,
#       color=color.white,
#   )
#
# Also create a hidden win message for later:
#   win_text = Text(
#       text='Well done!',
#       origin=(0, 0),
#       scale=2,
#       color=color.green,
#       parent=camera.ui,
#       enabled=False,
#   )

# --- Player ----------------------------------------------------------------
player = FirstPersonController()
player.gravity = 0
player.cursor.visible = False
player.position = (0, 1, 0)

# --- Game logic ------------------------------------------------------------
COLLECT_DISTANCE = 2  # how close the player must be to collect a star


def update():
    """Called every frame. Check proximity to each star."""
    # TODO 2: Loop through stars and check distance to player
    # For each star, if it is still enabled and close enough, collect it.
    #
    # Hint — the structure looks like:
    #   global score
    #   for star in stars:
    #       if star.enabled and distance(player.position, star.position) < COLLECT_DISTANCE:
    #           # TODO 3: Handle collection
    #           #   - Disable the star:  star.enabled = False
    #           #   - Increment score:   score += 1
    #           #   - Update the HUD:    score_text.text = f'Stars: {score}/{len(stars)}'
    #           pass
    #
    # TODO 4: Check win condition
    #   if score == len(stars):
    #       win_text.enabled = True
    pass


# --- TODO 5 (Bonus): Add reset function -----------------------------------
# Create a reset_game() function that:
#   - Sets score back to 0
#   - Updates score_text
#   - Hides win_text
#   - Re-enables all stars (loop through stars, set star.enabled = True)
#
# Then create an input(key) function that calls reset_game() when 'r' is
# pressed:
#
#   def input(key):
#       if key == 'r':
#           reset_game()


app.run()
