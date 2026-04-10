"""Exercise 2 — Build a Room (solution)

A complete 3-D room built from Ursina primitives:
  - Floor (quad laid flat)
  - Four walls (quads positioned and rotated to enclose the space)
  - Three pieces of furniture (cube table, sphere lamp, cylinder pillar)
  - FirstPersonController for walking through the scene
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
# A quad lies in the x-z plane when rotated 90° around x.
floor = Entity(
    model='quad',
    scale=(20, 20),
    rotation_x=90,
    color=color.dark_gray,
    texture='white_cube',
    collider='box',
)

# --- Walls -----------------------------------------------------------------
# Each wall is a quad (default: faces the camera, i.e. -z direction).
# We position and rotate them so they face inward.

# Front wall — sits at z=+10, faces back toward center (rotation_y=0)
front_wall = Entity(
    model='quad',
    scale=(20, 5),
    position=(0, 2.5, 10),
    rotation_y=0,
    color=color.white.tint(-0.1),
    texture='white_cube',
    collider='box',
)

# Back wall — sits at z=-10, faces forward toward center (rotation_y=180)
back_wall = Entity(
    model='quad',
    scale=(20, 5),
    position=(0, 2.5, -10),
    rotation_y=180,
    color=color.white.tint(-0.1),
    texture='white_cube',
    collider='box',
)

# Left wall — sits at x=-10, faces right toward center (rotation_y=-90)
left_wall = Entity(
    model='quad',
    scale=(20, 5),
    position=(-10, 2.5, 0),
    rotation_y=-90,
    color=color.white.tint(-0.15),
    texture='white_cube',
    collider='box',
)

# Right wall — sits at x=+10, faces left toward center (rotation_y=90)
right_wall = Entity(
    model='quad',
    scale=(20, 5),
    position=(10, 2.5, 0),
    rotation_y=90,
    color=color.white.tint(-0.15),
    texture='white_cube',
    collider='box',
)

# --- Furniture -------------------------------------------------------------

# Table — a brown cube stretched into a tabletop shape
table = Entity(
    model='cube',
    scale=(2, 1, 2),
    position=(3, 0.5, 4),
    color=color.brown,
    texture='white_cube',
    collider='box',
)

# Lamp — a yellow sphere hovering above the table
lamp = Entity(
    model='sphere',
    scale=0.5,
    position=(3, 2.5, 4),
    color=color.yellow,
)

# Pillar — a gray cylinder standing near the back-left corner
pillar = Entity(
    model='cylinder',
    scale=(1, 3, 1),
    position=(-6, 1.5, -6),
    color=color.light_gray,
    texture='white_cube',
    collider='box',
)

# --- Player ----------------------------------------------------------------
player = FirstPersonController()
player.gravity = 0       # flat scene, no need for falling
player.cursor.visible = False
player.position = (0, 1, 0)  # start near centre, slightly above floor

app.run()
