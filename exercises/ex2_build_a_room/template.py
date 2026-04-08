"""Exercise 2 — Build a Room (template)

Your task: complete the TODOs below to build a 3-D room you can walk through.

The floor and two walls are provided so the scene is visible immediately.
Add the missing walls and furniture, then switch to FirstPersonController.

Run this file at any point to see your progress:

    python template.py
"""

from ursina import *

app = Ursina()

# ---------------------------------------------------------------------------
# Ursina coordinate system
#   x → right       (positive = right,   negative = left)
#   y → up          (positive = up,      negative = down)
#   z → forward     (positive = forward, negative = backward)
#
# A quad's default normal points toward -z (toward the camera).
# Rotating a quad with rotation_y changes which direction it faces.
# ---------------------------------------------------------------------------

# --- Floor (complete) ------------------------------------------------------
# A quad becomes a floor when rotated 90° around x so it lies flat.
floor = Entity(
    model='quad',
    scale=(20, 20),
    rotation_x=90,
    color=color.dark_gray,
    texture='white_cube',
)

# --- Walls -----------------------------------------------------------------
# Each wall is a 20-wide, 5-tall quad. Its y-centre is at 2.5 so it sits
# on the floor. The rotation_y value determines which way the wall faces.

# Front wall (complete) — at z=+10, faces back toward centre
front_wall = Entity(
    model='quad',
    scale=(20, 5),
    position=(0, 2.5, 10),
    rotation_y=0,
    color=color.white.tint(-0.1),
    texture='white_cube',
)

# Back wall (complete) — at z=-10, faces forward toward centre
back_wall = Entity(
    model='quad',
    scale=(20, 5),
    position=(0, 2.5, -10),
    rotation_y=180,
    color=color.white.tint(-0.1),
    texture='white_cube',
)

# TODO 1: Left wall
# The left wall sits at x=-10 and should face right (toward centre).
# Hint: position=(-10, 2.5, 0) and rotation_y=-90
# left_wall = Entity(
#     model='quad',
#     scale=???,
#     position=???,
#     rotation_y=???,
#     color=color.white.tint(-0.15),
#     texture='white_cube',
# )

# TODO 2: Right wall
# The right wall sits at x=+10 and should face left (toward centre).
# Hint: position=(10, 2.5, 0) and rotation_y=90
# right_wall = Entity(
#     model='quad',
#     scale=???,
#     position=???,
#     rotation_y=???,
#     color=color.white.tint(-0.15),
#     texture='white_cube',
# )

# --- Furniture -------------------------------------------------------------

# Table (complete) — a brown cube stretched into a tabletop shape
table = Entity(
    model='cube',
    scale=(2, 1, 2),
    position=(3, 0.5, 4),
    color=color.brown,
    texture='white_cube',
)

# TODO 3: Lamp
# Add a yellow sphere above the table to act as a lamp.
# Hint: model='sphere', scale=0.5, position=(3, 2.5, 4), color=color.yellow
# lamp = Entity(...)

# TODO 4: Pillar
# Add a gray cylinder standing near the back-left corner.
# Hint: model='cylinder', scale=(1, 3, 1), position=(-6, 1.5, -6)
# pillar = Entity(...)

# --- Camera / Player -------------------------------------------------------
# EditorCamera lets you orbit and inspect the scene with the mouse.
# Once your room looks right, replace it with FirstPersonController
# so you can walk through the room in first person.

EditorCamera()

# TODO 5: Switch to FirstPersonController
# 1. Comment out EditorCamera() above.
# 2. Add this import at the top of the file:
#        from ursina.prefabs.first_person_controller import FirstPersonController
# 3. Uncomment and complete the lines below:
# player = FirstPersonController()
# player.gravity = 0          # no falling in a flat scene
# player.position = (0, 1, 0) # start near centre

app.run()
