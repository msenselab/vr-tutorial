"""Exercise 3 — Make It Real (solution)

Builds on the Exercise 2 room by adding:
  - Colliders on every surface (walls, floor, furniture) so you can't walk through them
  - Textures on walls and floor for a more realistic look
  - A Sky entity for atmospheric background
  - A golden collectible sphere (placeholder for Exercise 4 interaction)
  - Directional lighting for better depth and shadows
"""

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()

# ---------------------------------------------------------------------------
# Coordinate system reminder
#   x → right
#   y → up
#   z → forward (into the screen)
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
# Each wall has collider='box' so the player cannot walk through,
# and texture='brick' for a realistic surface.

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

# Table
table = Entity(
    model='cube',
    scale=(2, 1, 2),
    position=(3, 0.5, 4),
    color=color.brown,
    texture='white_cube',
    collider='box',
)

# Lamp — yellow sphere hovering above the table
lamp = Entity(
    model='sphere',
    scale=0.5,
    position=(3, 2.5, 4),
    color=color.yellow,
)

# Pillar — gray cylinder in the back-left corner
pillar = Entity(
    model='cylinder',
    scale=(1, 3, 1),
    position=(-6, 1.5, -6),
    color=color.light_gray,
    texture='white_cube',
    collider='box',
)

# --- Sky -------------------------------------------------------------------
Sky()

# --- Collectible sphere ----------------------------------------------------
# A golden sphere hovering in the room. In Exercise 4 we will add proximity
# detection so the player can "pick it up."
collectible = Entity(
    model='sphere',
    color=color.yellow,
    position=(5, 1, 5),
    scale=0.7,
)

# --- Lighting --------------------------------------------------------------
# A directional light improves depth perception and makes textures pop.
sun = DirectionalLight()
sun.look_at(Vec3(1, -1, -1))

# --- Player ----------------------------------------------------------------
player = FirstPersonController()
player.gravity = 0            # flat scene, no falling
player.cursor.visible = False
player.position = (0, 1, 0)   # start near centre, slightly above floor

app.run()
