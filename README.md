# From Screen to Scene: Building VR Experiments with Python

A half-day workshop for psychology and neuroscience researchers who want to build and run VR experiments using Python. No 3D or VR experience required — just bring basic Python skills and curiosity.

## What You Will Learn

This tutorial walks you through building interactive 3D environments with the [Ursina](https://www.ursinaengine.org/) game engine and handling gamepad input via [pygame](https://www.pygame.org/). By the end, you will have built a complete experiment paradigm from scratch and understand how to extend it for your own research.

## Who Is This For?

The workshop serves two roles that exist in every lab:

- **Builders** — researchers who design and code experiments. You will learn to create 3D scenes, add physics and interaction, and structure a full experiment with trials, conditions, and data logging.
- **Runners** — research assistants and technicians who set up and operate experiments. You will learn how the software works, how to configure parameters, and how to troubleshoot common issues.

Both roles work through the same exercises; depth of engagement differs.

## Schedule

| Time       | Module                              | Duration |
|------------|-------------------------------------|----------|
| 09:00      | M1: Welcome & Setup Check           | 20 min   |
| 09:20      | M2: Ursina Fundamentals             | 45 min   |
| 10:05      | Break                               | 20 min   |
| 10:25      | M3: Interaction & Input             | 40 min   |
| 11:05      | M4: Experiment Paradigm Design      | 45 min   |
| 11:50      | Q&A & Hands-on                      | 10 min   |
| 12:00      | Lunch                               | 60 min   |
| 13:00      | M5: Capstone — MazeWalker-Py        | 45 min   |
| 13:45      | M6: VR Roadmap                      | 25 min   |
| 14:10      | Break                               | 20 min   |
| 14:30      | M7: Beyond Primitives (3D Models)   | 30 min   |
| 15:00      | Wrap-up & Homework                  | 15 min   |

Total: ~6 hours including breaks and lunch.

## Pre-Workshop Setup

Please complete these steps **before** the workshop.

### 1. Install Python 3.11 and uv

Download **Python 3.11** from [python.org](https://www.python.org/downloads/release/python-3119/) (not 3.12+ — panda3d requires 3.11). Then install [uv](https://docs.astral.sh/uv/getting-started/installation/) (a fast Python package manager):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh   # macOS/Linux
# or: pip install uv
```

### 2. Create a virtual environment

```bash
cd vr-tutorial
uv venv
source .venv/bin/activate    # macOS/Linux
.venv\Scripts\activate       # Windows
```

### 3. Install dependencies

```bash
uv pip install ursina pygame
```

### 4. Verify your setup

```bash
python exercises/ex1_hello_ursina/hello_cube.py
```

You should see a window with a spinning cube. If so, you are ready.

## Repository Structure

```
vr-tutorial/
├── README.md                  # You are here
├── .gitignore
├── docs/plans/                # Design documents and planning notes
├── exercises/                 # Hands-on coding exercises
│   ├── ex1_hello_ursina/      # Setup check and first scene
│   ├── ex2_build_a_room/      # Constructing a 3D room
│   ├── ex3_make_it_real/      # Colliders, textures, and skybox
│   ├── ex4_pick_up_star/      # Interaction and gamepad input
│   ├── ex5_mini_experiment/   # State machine and data logging
│   └── assets/                # Shared textures and sounds
│       ├── textures/
│       └── sounds/
├── slides/                    # Slidev presentation
├── site/                      # Hugo documentation site
└── starter/                   # Pre-workshop starter package
```

## Exercises

| #  | Exercise            | What You Learn                                           |
|----|---------------------|----------------------------------------------------------|
| 1  | Hello Ursina        | Verify setup; create your first 3D scene with a cube     |
| 2  | Build a Room        | Construct a room from primitives; position and scale      |
| 3  | Make It Real        | Add colliders, textures, lighting, and a skybox           |
| 4  | Pick Up the Star    | Proximity detection, score UI, and pygame gamepad input   |
| 5  | Mini Experiment     | Trial state machine, conditions, timing, and CSV logging  |
| 6  | Load 3D Models      | Import GLB models, animate, proximity highlight           |

Each exercise folder contains a `template.py` (starting point) and a `solution.py` (reference implementation).

## Running Things

### Exercises

```bash
source .venv/bin/activate
python exercises/ex1_hello_ursina/hello_cube.py
```

### Slides (Slidev)

```bash
cd slides
pnpm install
pnpm dev
```

Opens at `http://localhost:3030`.

### Documentation site (Hugo)

```bash
cd site
hugo server
```

Opens at `http://localhost:1313`.

## Capstone: MazeWalker-Py

The capstone module uses [MazeWalker-Py](https://github.com/msenselab/MazeWalker-Py) as a reference project — a complete maze-navigation experiment built with the same stack. You will study its architecture and extend parts of it during Module 5.

---

## VR Setup — Pimax Crystal + SteamVR + Ursina

This section covers everything needed to run the VR experiment scripts in `vr_pimax/`.

### How It Works

Ursina does not natively support VR headsets. VR rendering is added through a chain of software layers:

```
Pimax Crystal headset
    └── Pimax Play (device driver, must be running)
        └── SteamVR (OpenVR runtime, must be running)
            └── openvr Python package (reads controller state from SteamVR)
            └── panda3d-openvr (hooks into Panda3D/Ursina to render stereo frames)
                └── Ursina app (your experiment code)
```

`panda3d-openvr` registers itself as a Panda3D **auxiliary display** (`aux-display p3openvr`). When Ursina starts, Panda3D hands each rendered frame to the OpenVR compositor, which reprojects and displays it in the headset with lens correction and tracking applied.

### Python Packages

All dependencies are declared in `pyproject.toml`. Install everything with:

```bash
cd vr-tutorial
uv venv                          # create .venv (Python 3.11 required)
.venv\Scripts\activate           # Windows
uv pip install -e .              # install all packages from pyproject.toml
```

Key packages and what they do:

| Package | Version | Purpose |
|---------|---------|---------|
| `ursina` | <8 | 3D scene, entities, UI, game loop |
| `panda3d` | latest | Rendering engine underneath Ursina |
| `panda3d-openvr` | latest | Stereo VR rendering bridge between Panda3D and SteamVR |
| `openvr` | latest | Python bindings for OpenVR — reads controller axes and buttons |
| `pygame` | latest | Gamepad input for non-VR desktop exercises |
| `matplotlib` | latest | Plotting trajectory data after experiments |
| `jupyter` | latest | Running analysis notebooks |

Verify VR packages after install:

```bash
python -c "import p3openvr; print('panda3d-openvr OK')"
python -c "import openvr; print('openvr OK')"
```

### Startup Sequence (every session)

Follow this order every time before running a VR script:

```
1. Connect the Pimax Crystal via USB

2. Launch Pimax Play
   Wait until the device shows green / "Ready"

3. Launch SteamVR  (from inside Pimax Play, or Steam → Library → Tools → SteamVR)
   Wait until all icons in the SteamVR status window are green

4. Put on the headset
   You should see the SteamVR home environment inside the headset

5. Activate the Python environment
   .venv\Scripts\activate

6. Run your experiment script (see below)
   The VR view switches to the experiment automatically
```

> **Important:** The Python script must start *after* SteamVR is fully ready. If SteamVR is not running when the script starts, `panda3d-openvr` falls back to a regular desktop window and VR rendering is not activated.

### How to Activate VR Rendering in an Ursina Script

Two lines are all that is required. They must appear **before** `Ursina()` is called:

```python
from vr_utils import enable_vr

enable_vr(render_scale=0.8)   # must be called BEFORE Ursina()
app = Ursina()
```

`enable_vr()` sets two Panda3D config variables:

```
aux-display p3openvr                    ← tells Panda3D to load the VR display module
openvr-render-size-multiplier 0.8       ← render at 80 % of native resolution
```

`render_scale=0.8` is recommended for the Crystal Super Q LED — its native resolution is very high and 80 % gives smooth frame rates with no visible quality loss. Lower to `0.7` or `0.6` if you see judder.

### Controls in VR

| Input | Action |
|-------|--------|
| **Left thumbstick** | Move forward / back / strafe left / right |
| **Right thumbstick left/right** | Snap turn 30° (replaces mouse look) |
| **Right trigger** | Advance experiment state (same as SPACE) |
| **WASD keys** | Move (same as left thumbstick — both work simultaneously) |
| **ESC** | Skip current trial |
| **Shift+Q** | Quit |

Mouse look is not used in VR — the headset provides head orientation automatically.

### VR Experiment Scripts

| Script | Purpose |
|--------|---------|
| `vr_pimax/maze_experiment.py` | **Main experiment** — procedurally generated maze, trajectory + gaze logging |
| `vr_pimax/demo.py` | Demo — 4-trial star collection, useful for testing the VR setup |
| `vr_pimax/probe.py` | Diagnostic tool — verifies keyboard and controller input are working |
| `vr_pimax/vr_utils.py` | Shared VR utilities (`enable_vr`, `VRPlayer`, `VRControllerInput`, `EyeTracker`) |

Run from the repo root (so relative imports work):

```bash
cd vr-tutorial
.venv\Scripts\activate
python vr_pimax/maze_experiment.py
```

### Output Files

**ex7_vr.py** writes three CSV files in the folder where the script is run:

| File | Contents |
|------|---------|
| `maze_experiment_vr.csv` | One row per trial: condition, maze size, stars collected, duration |
| `trajectory_vr.csv` | Position + gaze direction every 0.1 s during each trial |
| `maze_walls.csv` | Wall geometry for the trajectory visualiser notebook |

To visualise trajectories after a run:

```bash
cd exercises/ex7_maze_explorer
jupyter notebook visualize.ipynb
```
Change `trajectory.csv` to `trajectory_vr.csv` in the first cell, then run all cells.

### vr_utils.py — Public API

```python
from vr_utils import enable_vr, VRPlayer, VRControllerInput, EyeTracker

# Configure VR before Ursina starts
enable_vr(render_scale=0.8)
app = Ursina()

# First-person player: WASD + left thumbstick locomotion, right thumbstick snap turn
player = VRPlayer(speed=9.0)
player.set_collision_rects(wall_rects, radius=0.52)
player.teleport_to(Vec3(0, 1.0, 0))
player.enabled = True

# Read controller input directly
ctrl = VRControllerInput()
x, y = ctrl.get_thumbstick('left')   # (-1..1, -1..1)
val  = ctrl.get_trigger('right')     # 0..1
pressed = ctrl.trigger_just_pressed('right')  # True on rising edge, per-frame accurate

# Gaze proxy (HMD forward direction; see GUIDE.md to upgrade to true eye tracking)
eye = EyeTracker()
gx, gy, gz = eye.sample()
```

### Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Experiment opens as a desktop window | SteamVR not running when script started | Close script → start SteamVR → run again |
| `ImportError: No module named 'p3openvr'` | Package not installed | `uv pip install panda3d-openvr` |
| `[VRController] Init failed` | SteamVR not running | Start SteamVR first |
| Black screen in headset | SteamVR not fully initialised | Wait for all SteamVR status icons to turn green |
| Player passes through walls | Collision rects not registered | Call `player.set_collision_rects(wall_rects)` after building the maze |
| Movement non-responsive | Experiment state is not TASK | Movement is only active when `player.enabled = True` |
| WASD does not work | Mirror window not focused | Click the SteamVR desktop mirror window once |
| Controller does not move player | Wrong hand / axis | Left thumbstick controls locomotion; right thumbstick is snap turn only |
| Very low frame rate | Resolution too high | Lower `render_scale` to `0.7`; reduce Pimax Play Render Quality to Normal |

### Performance Settings

If you see frame drops or judder:

1. Lower render scale: `enable_vr(render_scale=0.7)` or `0.6`
2. In **Pimax Play**: Render Quality → Normal, Refresh Rate → 72 Hz, Smart Smoothing → On, FOV → Normal
3. In **SteamVR**: Settings → Video → Custom Resolution → 80 %

---

## License

MIT
