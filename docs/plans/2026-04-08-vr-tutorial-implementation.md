# VR Tutorial Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a complete half-day VR tutorial with exercises, Slidev slides, Hugo reference site, and learner step-by-step guide.

**Architecture:** Monorepo with three main areas: `exercises/` (Python code with templates + solutions), `slides/` (Slidev presentation), and `site/` (Hugo static site for post-workshop reference). Exercise code progresses from simple Ursina basics to a full experiment paradigm, with MazeWalker-Py as the capstone reference.

**Tech Stack:** Python 3.11+ (ursina, pygame), Slidev (Vue-based slides), Hugo (static site generator), pnpm

---

### Task 1: Project Scaffolding

**Files:**
- Create: `README.md`
- Create: `.gitignore`
- Create: directory structure

**Step 1: Initialize git and create directory structure**

```bash
cd /Users/strongway/_git/vr-tutorial
git init
mkdir -p exercises/{ex1_hello_ursina,ex2_build_a_room,ex3_make_it_real,ex4_pick_up_star,ex5_mini_experiment}
mkdir -p exercises/assets/{textures,sounds}
mkdir -p slides
mkdir -p site
```

**Step 2: Create .gitignore**

```gitignore
# Python
__pycache__/
*.pyc
*.pyo
.venv/
venv/

# Node
node_modules/
dist/

# Hugo
site/public/
site/resources/

# Slidev
slides/dist/

# OS
.DS_Store
Thumbs.db

# Data output
*.csv
data/
```

**Step 3: Create README.md**

Write a comprehensive README covering:
- Tutorial title and purpose
- Audience description
- Schedule overview (6 modules)
- Pre-workshop setup instructions (Python, ursina, pygame install)
- Repository structure explanation
- How to run exercises
- How to run slides locally
- How to run the Hugo site locally
- Link to MazeWalker-Py reference project
- License

**Step 4: Commit scaffolding**

```bash
git add -A
git commit -m "feat: initial project scaffolding with directory structure and README"
```

---

### Task 2: Exercise 1 — Hello Ursina (Setup Check)

**Files:**
- Create: `exercises/ex1_hello_ursina/hello_cube.py`
- Create: `exercises/ex1_hello_ursina/README.md`

**Step 1: Write hello_cube.py**

The simplest possible Ursina script — verifies install works. Shows a colored cube with EditorCamera (orbit with right-click, zoom with scroll).

```python
from ursina import *

app = Ursina()
Entity(model='cube', color=color.orange, texture='white_cube')
EditorCamera()
app.run()
```

**Step 2: Write exercise README**

Step-by-step instructions:
1. What this exercise does
2. How to run it: `python hello_cube.py`
3. What you should see (orange cube, orbit camera)
4. Try changing: color, model (sphere, cylinder), position
5. Troubleshooting: common install issues

**Step 3: Verify it runs**

```bash
cd exercises/ex1_hello_ursina && python hello_cube.py
```

**Step 4: Commit**

```bash
git add exercises/ex1_hello_ursina/
git commit -m "feat: add Exercise 1 — Hello Ursina setup check"
```

---

### Task 3: Exercise 2 — Build a Room

**Files:**
- Create: `exercises/ex2_build_a_room/template.py` (starter with TODOs)
- Create: `exercises/ex2_build_a_room/solution.py` (complete version)
- Create: `exercises/ex2_build_a_room/README.md`

**Step 1: Write solution.py**

Complete working room with:
- Floor (quad, rotation_x=90, scaled, textured)
- 4 walls (quads, positioned and rotated to form a room)
- 3 furniture items (cube table, sphere lamp, cylinder pillar)
- FirstPersonController to walk around
- Proper coordinate setup (y-up, walls at correct positions)

**Step 2: Write template.py**

Same structure but with TODO comments where participants fill in:
- Wall positions and rotations (2 walls given, 2 as TODO)
- Furniture placement (1 given, 2 as TODO)
- Switch from EditorCamera to FirstPersonController (TODO)

**Step 3: Write exercise README**

Step-by-step guide:
1. Learning goals
2. Key concepts: Entity, position, rotation, scale, model, texture
3. Ursina coordinate system diagram (y-up)
4. Instructions for each TODO
5. Hints section
6. "What to try next" challenges

**Step 4: Verify solution runs**

```bash
cd exercises/ex2_build_a_room && python solution.py
```

**Step 5: Commit**

```bash
git add exercises/ex2_build_a_room/
git commit -m "feat: add Exercise 2 — Build a Room with template and solution"
```

---

### Task 4: Exercise 3 — Make It Real

**Files:**
- Create: `exercises/ex3_make_it_real/template.py`
- Create: `exercises/ex3_make_it_real/solution.py`
- Create: `exercises/ex3_make_it_real/README.md`
- Add: `exercises/assets/textures/` (brick, wood, stone textures — use ursina built-ins)

**Step 1: Write solution.py**

Builds on Exercise 2's room, adding:
- `collider='box'` on all walls and floor
- Custom textures on walls (brick) and floor (wood) — use ursina built-in textures
- Sky entity for atmosphere
- A collectible glowing sphere (Entity with color, scale animation or emissive look)
- Ambient light adjustment
- Player height and gravity settings on FirstPersonController

**Step 2: Write template.py**

Starts from completed Exercise 2 room. TODOs for:
- Adding colliders to walls
- Applying textures (texture name provided, participant assigns them)
- Adding Sky()
- Creating the collectible sphere with position

**Step 3: Write exercise README**

Step-by-step:
1. Learning goals: collision, textures, skybox
2. Why colliders matter (walk-through-walls demo)
3. Ursina's built-in textures list
4. How Sky() works
5. Instructions for each TODO
6. Challenge: try different sky textures, add more objects

**Step 4: Verify solution runs**

**Step 5: Commit**

```bash
git add exercises/ex3_make_it_real/ exercises/assets/
git commit -m "feat: add Exercise 3 — Make It Real with colliders, textures, skybox"
```

---

### Task 5: Exercise 4 — Pick Up the Star

**Files:**
- Create: `exercises/ex4_pick_up_star/template.py`
- Create: `exercises/ex4_pick_up_star/solution.py`
- Create: `exercises/ex4_pick_up_star/README.md`

**Step 1: Write solution.py**

Builds on Exercise 3's room, adding:
- Multiple collectible stars (3 spheres at different positions)
- `update()` function with proximity detection (distance calculation)
- On collect: disable/hide the star, play built-in sound, increment score
- Score display as Text entity on `camera.ui`
- Win condition: all stars collected → show congratulations text
- Bonus: 'r' key to reset scene

Key code pattern (proximity detection):
```python
def update():
    for star in stars:
        if star.enabled:
            dist = distance(player.position, star.position)
            if dist < 2:
                star.enabled = False
                score += 1
                # update UI
```

**Step 2: Write template.py**

Provides the room + stars already placed. TODOs:
- Write the distance check in update()
- Handle collection (disable star, update score)
- Create the score Text element
- Bonus: add reset function

**Step 3: Write exercise README**

Step-by-step:
1. Learning goals: update loop, proximity detection, UI text
2. How `update()` works in Ursina (called every frame)
3. Distance calculation explanation
4. Ursina's `distance()` helper
5. Text on camera.ui for HUD elements
6. Instructions for each TODO
7. Pygame input demo section: show how `pygame.event.pump()` + joystick would plug in here

**Step 4: Write pygame_input_demo.py**

Standalone script showing pygame joystick alongside Ursina:
- Initializes pygame joystick
- Reads axes in update()
- Moves player with gamepad
- Includes deadzone handling
- Works as a reference, not an exercise

**Step 5: Verify solution runs**

**Step 6: Commit**

```bash
git add exercises/ex4_pick_up_star/
git commit -m "feat: add Exercise 4 — Pick Up the Star with proximity detection and pygame demo"
```

---

### Task 6: Exercise 5 — Mini Experiment

**Files:**
- Create: `exercises/ex5_mini_experiment/template.py`
- Create: `exercises/ex5_mini_experiment/solution.py`
- Create: `exercises/ex5_mini_experiment/README.md`

**Step 1: Write solution.py**

Full mini-experiment with:
- State machine: INSTRUCTION → FIXATION → TASK → FEEDBACK → next trial
- 2 conditions (1 star vs 3 stars) × 2 repeats = 4 trials, randomized
- Fixation cross (Text '+' centered, 1 second)
- Instruction screen with "Press SPACE to start"
- Feedback screen showing trial results
- CSV logging: trial, condition, duration, stars_collected, completed
- Mock trigger function: `send_trigger(code)` → prints to console
- Trial timing with `time.time()`
- End screen with summary

Key architecture:
```python
class Experiment(Entity):
    def __init__(self):
        super().__init__()
        self.state = 'INSTRUCTION'
        self.trials = [{'condition': 'A', 'n_stars': 1}, ...] * 2
        random.shuffle(self.trials)
        self.current_trial = 0
        # ... setup UI, CSV writer

    def update(self):
        if self.state == 'INSTRUCTION': ...
        elif self.state == 'FIXATION': ...
        elif self.state == 'TASK': ...
        elif self.state == 'FEEDBACK': ...
```

**Step 2: Write template.py**

Provides:
- Full room setup (reused from Exercise 3)
- Experiment class skeleton with states defined
- Trial list creation (done)
- CSV file setup (done)
- TODOs:
  - Implement state transitions in update()
  - Add fixation cross display/hide
  - Add star spawning based on condition
  - Add collection logic (reuse from Exercise 4)
  - Write trial data to CSV
  - Add mock trigger calls

**Step 3: Write exercise README**

Step-by-step:
1. Learning goals: state machine, trial sequencing, data logging
2. State machine diagram (text-based)
3. Why this pattern matters for experiments
4. CSV logging basics
5. What trigger codes are and why they matter for EEG
6. Instructions for each TODO (most detailed README)
7. How this maps to MazeWalker-Py's experiment.py
8. Builder bonus: add practice trial, variable fixation duration

**Step 4: Verify solution runs**

**Step 5: Commit**

```bash
git add exercises/ex5_mini_experiment/
git commit -m "feat: add Exercise 5 — Mini Experiment with state machine and CSV logging"
```

---

### Task 7: Slidev Presentation Setup

**Files:**
- Create: `slides/package.json`
- Create: `slides/slides.md`
- Copy: slidev-theme components/layouts

**Step 1: Initialize Slidev project**

```bash
cd /Users/strongway/_git/vr-tutorial/slides
pnpm init
pnpm add -D @slidev/cli @slidev/theme-seriph slidev-theme-academic
```

**Step 2: Apply slidev-theme skill**

Use the slidev-theme skill to copy components and layouts.

**Step 3: Create slides.md**

Structure following the 6-module design:
- Title slide
- Module 1: Welcome (audience poll, landscape, setup check)
- Module 2: Ursina Fundamentals (concepts, Exercise 1-2)
- Break slide
- Module 3: Interaction & Input (input model, pygame, Exercise 3)
- Module 4: Experiment Paradigm (state machine, logging, Exercise 4)
- Break slide
- Module 5: Capstone (MazeWalker-Py tour, Exercise 5)
- Module 6: VR Roadmap (headset path, resources)

Include code blocks, diagrams (mermaid), and exercise instruction slides.

**Step 4: Verify slides run**

```bash
cd slides && pnpm dev
```

**Step 5: Commit**

```bash
git add slides/
git commit -m "feat: add Slidev presentation with all 6 modules"
```

---

### Task 8: Hugo Site Setup

**Files:**
- Create: `site/` Hugo project
- Create: content pages for each exercise
- Create: setup guide page
- Create: resources page

**Step 1: Initialize Hugo site**

```bash
cd /Users/strongway/_git/vr-tutorial
hugo new site site
cd site
git submodule add https://github.com/theNewDynamic/gohugo-theme-ananke themes/ananke
```

Configure `hugo.toml` with tutorial title, theme, menu structure.

**Step 2: Create content structure**

```
site/content/
├── _index.md                    # Landing page: tutorial overview
├── setup/
│   └── _index.md               # Pre-workshop install guide
├── exercises/
│   ├── _index.md               # Exercise overview
│   ├── 01-hello-ursina.md      # Exercise 1
│   ├── 02-build-a-room.md      # Exercise 2
│   ├── 03-make-it-real.md      # Exercise 3
│   ├── 04-pick-up-star.md      # Exercise 4
│   └── 05-mini-experiment.md   # Exercise 5
├── capstone/
│   └── _index.md               # MazeWalker-Py walkthrough
├── vr-roadmap/
│   └── _index.md               # Path to headset VR
└── resources/
    └── _index.md               # Links, reading, community
```

**Step 3: Write setup guide page**

Pre-workshop install instructions:
- Python 3.11+ install (per platform)
- Create virtual environment
- `pip install ursina pygame`
- Verify with hello_cube.py
- Troubleshooting FAQ
- Download starter zip link

**Step 4: Write exercise pages**

Each exercise page includes:
- Learning objectives
- Key concepts with explanations
- Step-by-step instructions (adapted from exercise READMEs)
- Code snippets (template and solution)
- Screenshots/expected output descriptions
- "What you learned" summary
- Link to next exercise

**Step 5: Write capstone page**

MazeWalker-Py walkthrough:
- Architecture overview
- File-by-file guide
- How tutorial concepts map to real code
- Runner track and builder track instructions

**Step 6: Write VR roadmap page**

- Desktop 3D vs headset VR comparison
- Panda3D OpenXR path
- Code diff: desktop → VR
- When to use which approach

**Step 7: Write resources page**

- Documentation links
- Recommended reading
- Community resources
- Related projects

**Step 8: Verify site builds**

```bash
cd site && hugo server -D
```

**Step 9: Commit**

```bash
git add site/
git commit -m "feat: add Hugo site with exercise guides, setup instructions, and resources"
```

---

### Task 9: Pre-Workshop Starter Package

**Files:**
- Create: `starter/` directory with exercise templates + assets
- Create: `starter/INSTALL.md`
- Create: `starter/requirements.txt`

**Step 1: Create starter directory**

```
starter/
├── INSTALL.md           # Setup instructions
├── requirements.txt     # pip install -r requirements.txt
├── ex1_hello_ursina/
│   └── hello_cube.py
├── ex2_build_a_room/
│   └── template.py
├── ex3_make_it_real/
│   └── template.py
├── ex4_pick_up_star/
│   └── template.py
├── ex5_mini_experiment/
│   └── template.py
└── assets/
    ├── textures/
    └── sounds/
```

This is a curated subset: templates only (no solutions), plus assets.

**Step 2: Write INSTALL.md**

Concise install instructions for participants:
1. Install Python 3.11+
2. Create venv
3. `pip install -r requirements.txt`
4. Run `python ex1_hello_ursina/hello_cube.py` to verify
5. Troubleshooting section

**Step 3: Write requirements.txt**

```
ursina>=7.0.0
pygame
```

**Step 4: Commit**

```bash
git add starter/
git commit -m "feat: add pre-workshop starter package with templates and install guide"
```

---

### Task 10: Final Polish and Integration Check

**Step 1: Verify all exercises run**

Run each solution.py to confirm they work.

**Step 2: Cross-reference README, site, and slides**

Ensure schedule, exercise names, and descriptions are consistent across all three.

**Step 3: Update README with final structure**

Add the actual directory tree and any final links.

**Step 4: Final commit**

```bash
git add -A
git commit -m "docs: final polish — cross-reference consistency and verification"
```
