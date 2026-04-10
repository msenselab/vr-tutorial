"""Exercise 6 — Load 3D Models (solution)

Demonstrates loading external GLB models into an Ursina scene:
  - Loading .glb files with Entity(model=...)
  - Positioning, scaling, and rotating imported models
  - Animating a model (swing rocking via sine wave)
  - Proximity-based highlighting
  - Dynamic scaling with keyboard input
"""

import math
from pathlib import Path
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()


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

# Resolve the models directory relative to this script (works from any cwd)
MODELS_DIR = Path(__file__).resolve().parent.parent / 'assets' / 'models'

# ---------------------------------------------------------------------------
# Room (reused from Exercise 3)
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

# --- Load 3D models -------------------------------------------------------

angel = Entity(
    model=load_glb('Angel', path=MODELS_DIR),
    scale=2,
    position=(0, 2, 5),
)

swing = Entity(
    model=load_glb('Swing', path=MODELS_DIR),
    scale=2,
    position=(0, 2, -3),
    rotation_y=180,
)

# --- HUD -------------------------------------------------------------------
info_text = Text(
    text='',
    position=(-0.85, 0.45),
    scale=0.1,
    parent=camera.ui,
    color=color.white,
)

# --- Player ----------------------------------------------------------------
player = FirstPersonController()
player.gravity = 0
player.cursor.visible = False
player.position = (3, 1, -1)    # near the swing
player.rotation_y = -45          # face the angel statue

# --- Per-frame logic -------------------------------------------------------

HIGHLIGHT_DISTANCE = 3

def update():
    # Animate the swing: rock back and forth
    swing.rotation_z = math.sin(time.time() * 2) * 15

    # Proximity highlighting
    near_name = ''
    for name, obj in [('Angel', angel), ('Swing', swing)]:
        d = distance(player.position, obj.position)
        if d < HIGHLIGHT_DISTANCE:
            obj.color = color.yellow
            near_name = f'{name}  (pos={obj.position}, scale={obj.scale_x:.1f})'
        else:
            obj.color = color.white

    info_text.text = near_name


def input(key):
    # Scale the angel with arrow keys
    if key == 'up arrow':
        angel.scale *= 1.1
    elif key == 'down arrow':
        angel.scale *= 0.9


app.run()
