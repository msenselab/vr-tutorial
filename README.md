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

## License

MIT
