"""Exercise 6 — Load 3D Models (template)

Your task: place external 3D models into the room and make them
interactive.

Two GLB models are provided in exercises/assets/models/:
  - Angel.glb  — a statue (~1.9 units tall)
  - Swing.glb  — a playground swing (~1.8 units tall)

Run this file at any point to see your progress:

    python template.py

Complete the TODOs to load, position, scale, and animate the models.
"""

from pathlib import Path
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()

# Resolve the models directory relative to this script (works from any cwd)
MODELS_DIR = Path(__file__).resolve().parent.parent / 'assets' / 'models'


def load_glb(name, path):
    """Load a GLB model, keep its base-color texture, strip PBR shaders.

    GLB files carry PBR materials (metallic-roughness, normal maps) that
    need GLSL shaders macOS cannot compile.  This helper keeps the
    albedo (base-color) texture for visual fidelity while removing the
    shader-dependent parts so the fixed-function pipeline can render it
    — even when a DirectionalLight is in the scene.
    """
    from panda3d.core import TextureAttrib
    mdl = load_model(name, path=path)
    if mdl is None:
        print(f'warning: could not load model {name}')
        return None
    for np in mdl.findAllMatches('**/+GeomNode'):
        np.clearMaterial()
        np.setShaderOff(2)    # override DirectionalLight's auto-shader
        np.setLightOff(2)     # ignore scene lights (use flat shading)
        # Remove PBR textures but keep the base-color (albedo) texture
        node = np.node()
        for i in range(node.getNumGeoms()):
            ta = node.getGeomState(i).getAttrib(TextureAttrib)
            if ta:
                for j in range(ta.getNumOnStages()):
                    stage = ta.getOnStage(j)
                    tex = ta.getOnTexture(stage)
                    if 'Base Color' not in tex.getName():
                        np.setTextureOff(stage, 2)
    return mdl


# ---------------------------------------------------------------------------
# Room (reused from Exercise 3 — complete, do NOT change)
# ---------------------------------------------------------------------------

floor = Entity(
    model='quad', scale=(20, 20), rotation_x=90,
    color=color.dark_gray, texture='grass', collider='box',
)

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
    rotation_y=-90, color=color.white.tint(-0.05), texture='brick',
    collider='box',
)
right_wall = Entity(
    model='quad', scale=(20, 5), position=(10, 2.5, 0),
    rotation_y=90, color=color.white.tint(-0.05), texture='brick',
    collider='box',
)

Sky()
sun = DirectionalLight()
sun.look_at(Vec3(1, -1, -1))

# ---------------------------------------------------------------------------
# TODO 1: Load the Angel model
# ---------------------------------------------------------------------------
# Use load_glb() to load the model (keeps base-color texture, strips
# PBR shaders that macOS cannot compile).
#
# angel = Entity(
#     model=load_glb('Angel', path=MODELS_DIR),
#     scale=2,                  # scale up so it's about human height
#     position=(-3, 0, 5),     # place it against the far wall
# )
#
# Experiment with scale and position until the angel looks right in the room.
# Try rotating it:  rotation_y=180  to face the player.

# ---------------------------------------------------------------------------
# TODO 2: Load the Swing model
# ---------------------------------------------------------------------------
# swing = Entity(
#     model=load_glb('Swing', path=MODELS_DIR),
#     scale=2,
#     position=(4, 0, -3),     # place it on the other side
# )

# ---------------------------------------------------------------------------
# TODO 3: Animate the swing
# ---------------------------------------------------------------------------
# Make the swing rock back and forth using the update() function.
# Ursina calls update() every frame. You can use time.time() and
# math.sin() to create a smooth oscillation.
#
# import math
#
# def update():
#     if 'swing' in dir():
#         swing.rotation_z = math.sin(time.time() * 2) * 15
#
# The expression:
#   math.sin(time.time() * 2) — oscillates between -1 and +1
#   * 15                      — scales to +/-15 degrees

# ---------------------------------------------------------------------------
# TODO 4: Print model info on click
# ---------------------------------------------------------------------------
# Add a function that prints info about a model when you walk close to it.
# This uses the same proximity pattern from Exercise 4.
#
# def update():
#     # ... (keep swing animation above) ...
#     for name, obj in [('Angel', angel), ('Swing', swing)]:
#         d = distance(player.position, obj.position)
#         if d < 3:
#             obj.color = color.yellow    # highlight when near
#         else:
#             obj.color = color.white     # reset color

# ---------------------------------------------------------------------------
# TODO 5 (Bonus): Scale a model dynamically
# ---------------------------------------------------------------------------
# Let the player grow/shrink the angel with the up/down arrow keys.
#
# def input(key):
#     if key == 'up arrow':
#         angel.scale *= 1.1
#     elif key == 'down arrow':
#         angel.scale *= 0.9

# --- Player ----------------------------------------------------------------
player = FirstPersonController()
player.gravity = 0
player.cursor.visible = False
player.position = (3, 1, -1)    # near the swing
player.rotation_y = -45          # face the angel statue

app.run()
