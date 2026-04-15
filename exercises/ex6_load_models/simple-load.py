import math
from pathlib import Path
from ursina import *

app = Ursina()

# Resolve the models directory relative to this script (works from any cwd)
MODELS_DIR = Path(__file__).resolve().parent.parent / 'assets' / 'models'

angel = Entity(
    model=load_model('troy', path=MODELS_DIR),
    scale=2,
    position=(0, 0, 0),
    rotation_y=180,
)

swing = Entity(
    model=load_model('Swing', path=MODELS_DIR),
    scale=1,
    position=(4, 0, 3),
)

app.run()
