"""Exercise 3 — Make It Real (template)

Your task: enhance this room so it feels like a real environment.

The room from Exercise 2 is already built below — floor, four walls,
furniture, and first-person controls all work. Run it now to confirm:

    python template.py

Then complete the five TODOs to add colliders, textures, a sky, a
collectible sphere, and lighting.
"""

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()

# ---------------------------------------------------------------------------
# The room from Exercise 2 (complete — do NOT change the structure)
# ---------------------------------------------------------------------------

# --- Floor -----------------------------------------------------------------
floor = Entity(
    model='quad',
    scale=(20, 20),
    rotation_x=90,
    color=color.dark_gray,
    texture='white_cube',
    # TODO 1a: Add  collider='box'  to the floor (prevents falling through)
)

# --- Walls -----------------------------------------------------------------

# Front wall — collider already added as an example
front_wall = Entity(
    model='quad',
    scale=(20, 5),
    position=(0, 2.5, 10),
    rotation_y=0,
    color=color.white.tint(-0.1),
    texture='white_cube',
    collider='box',       # <-- this one is done for you
)

# Back wall
back_wall = Entity(
    model='quad',
    scale=(20, 5),
    position=(0, 2.5, -10),
    rotation_y=180,
    color=color.white.tint(-0.1),
    texture='white_cube',
    # TODO 1b: Add  collider='box'  here
)

# Left wall
left_wall = Entity(
    model='quad',
    scale=(20, 5),
    position=(-10, 2.5, 0),
    rotation_y=-90,
    color=color.white.tint(-0.15),
    texture='white_cube',
    # TODO 1c: Add  collider='box'  here
)

# Right wall
right_wall = Entity(
    model='quad',
    scale=(20, 5),
    position=(10, 2.5, 0),
    rotation_y=90,
    color=color.white.tint(-0.15),
    texture='white_cube',
    # TODO 1d: Add  collider='box'  here
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

# Lamp
lamp = Entity(
    model='sphere',
    scale=0.5,
    position=(3, 2.5, 4),
    color=color.yellow,
)

# Pillar
pillar = Entity(
    model='cylinder',
    scale=(1, 3, 1),
    position=(-6, 1.5, -6),
    color=color.light_gray,
    texture='white_cube',
    collider='box',
)

# --- TODO 2: Add textures -------------------------------------------------
# Replace the wall and floor textures above to make the room look realistic.
#
# Try changing the floor's  texture='white_cube'  to  texture='grass'
# and each wall's  texture='white_cube'  to  texture='brick'
#
# Ursina built-in texture names include:
#   'white_cube'  — subtle grid (already used)
#   'brick'       — brick pattern
#   'grass'       — grass pattern
#   'shore'       — sandy beach
#
# Hint: you can also tint textures by combining  texture=  with  color=

# --- TODO 3: Add a sky -----------------------------------------------------
# Add a single line to wrap the scene in a panoramic sky background:
#
# Sky()

# --- TODO 4: Create a collectible sphere -----------------------------------
# Place a golden sphere somewhere in the room. This is a preview —
# in Exercise 4 you will make it interactive.
#
# Hint:
# collectible = Entity(
#     model='sphere',
#     color=color.yellow,
#     position=(5, 1, 5),
#     scale=0.7,
# )

# --- TODO 5 (optional): Add lighting --------------------------------------
# A directional light adds depth and makes textures more visible.
#
# sun = DirectionalLight()
# sun.look_at(Vec3(1, -1, -1))

# --- Player ----------------------------------------------------------------
player = FirstPersonController()
player.gravity = 0            # flat scene, no falling
player.position = (0, 1, 0)   # start near centre, slightly above floor

app.run()
