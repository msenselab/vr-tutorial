---
theme: academic
title: "From Screen to Scene: Building VR Experiments with Python"
info: Half-day workshop for researchers
drawings:
  persist: false
transition: slide-left
mdc: true
---

<div class="h-full flex flex-col justify-center items-center text-center">
  <h1 class="text-4xl font-bold mb-2">From Screen to Scene</h1>
  <h2 class="text-2xl text-gray-600 mb-6">Building VR Experiments with Python</h2>
  <p class="text-lg text-gray-500 mb-4">A hands-on workshop for researchers</p>
  <p class="text-lg"><strong>Chunyu Qu, Artyom Zinchenko</strong> & <strong>Zhuanghua Shi</strong></p>
  <p class="text-base text-gray-500">LMU Munich &middot; April 2026</p>
  <p class="text-sm text-gray-400 mt-2">Erasmus+ KA210-VET &middot; <a href="https://xr4vet.eu">xr4vet.eu</a></p>
  <div class="flex items-center justify-center gap-8 mt-6">
    <img src="/images/lmu-logo.png" class="h-12" />
    <img src="/images/comu-logo.png" class="h-12" />
    <img src="/images/eu-cofunded.png" class="h-10" />
  </div>
</div>

<!--
Welcome everyone. This workshop takes you from zero 3D experience to building a complete VR experiment paradigm in about four hours. Everything runs in Python — no Unity, no C#, no game-dev background needed.
-->

---
layout: pgTwoColumn
leftWidth: 50
rightWidth: 50
---

::title::
Workshop Overview

::left-title::
Morning

::left::

- **09:00** M1: Welcome & Setup Check
- **09:20** M2: Ursina Fundamentals
- **10:05** Break (20 min)
- **10:25** M3: Interaction & Input
- **11:05** M4: Experiment Paradigm Design
- **11:50** Q&A & Hands-on
- **12:00** Lunch (60 min)

::right-title::
Afternoon

::right::

- **13:00** M5: Capstone -- MazeWalker-Py
- **13:40** M6: VR Roadmap
- **13:55** M7: Beyond Primitives
- **14:10** Unity VR in Research (Artyom)
- **15:10** Wrap-up & Homework

**Two tracks**: *Builders* (design & code) · *Runners* (configure & operate)

<!--
Full-day workshop split across morning and afternoon. Artyom presents Unity VR in the afternoon for participants interested in the Unity ecosystem.
-->

---
layout: section
---

# Module 1
## Welcome & Setup Check

<!--
Let's start by getting to know the room and making sure everyone's environment works.
-->

---

# Who's in the Room?

Quick poll -- raise your hand:

<v-clicks>

- Who has written a PsychoPy experiment?
- Who has used Unity or Unreal?
- Who has never touched 3D programming?
- Who has a gamepad plugged in right now?

</v-clicks>

> This workshop assumes **basic Python** (variables, functions, classes). No 3D or VR experience needed.

<!--
This helps me calibrate the pace. Most participants will fall into the "basic Python, no 3D" camp, which is exactly the target audience.
-->

---
layout: pgTwoColumn
leftWidth: 55
rightWidth: 45
---

::title::
The Landscape: Why Ursina?

::left::

| Tool       | Language | VR Ready | Science Use      |
|------------|----------|----------|------------------|
| PsychoPy   | Python   | Limited  | Gold standard 2D |
| Unity      | C#       | Full     | Dominant in VR   |
| **Ursina** | Python   | Via Panda3D | **Sweet spot** |
| Vizard     | Python   | Full     | Commercial       |

::right::

<comBlock title="Why Ursina?" bgColor="bg-blue-50" border="left" borderColor="border-blue-400">

- Pure Python -- reuse your analysis skills
- Built on Panda3D -- production-grade 3D engine
- ~20 extra lines to go from desktop to headset VR

</comBlock>

<!--
PsychoPy is great for 2D but limited for 3D navigation tasks. Unity is powerful but requires C# and a steep learning curve. Ursina gives us Python simplicity with real 3D capability.
-->

---
layout: pgTwoColumn
leftWidth: 50
rightWidth: 50
---

::title::
Setup Check

::left::

Run this in your terminal:

```bash
cd vr-tutorial
source venv/bin/activate
python exercises/ex1_hello_ursina/hello_cube.py
```

A window with a **spinning orange cube**. Middle-click to orbit, scroll to zoom.

If it works -- you are ready.

::right::

```python
from ursina import *

app = Ursina()
Entity(model='cube',
       color=color.orange,
       texture='white_cube')
EditorCamera()
app.run()
```

<!--
Let's take two minutes. Run hello_cube.py. If you see a cube in a window, give me a thumbs up. If you get an error, raise your hand and we'll debug together.
-->

---

# Architecture Overview

<div class="flex flex-col gap-0 max-w-2xl mx-auto mt-4">
  <div class="bg-blue-100 border border-blue-300 rounded-t-lg px-6 py-3 text-center">
    <div class="font-bold text-blue-800">Your Experiment Logic</div>
    <div class="text-sm text-blue-600">trials, conditions, data logging</div>
  </div>
  <div class="bg-green-100 border-x border-green-300 px-6 py-3 text-center">
    <div class="font-bold text-green-800">Ursina Engine</div>
    <div class="text-sm text-green-600">Entity, Camera, Lighting, Colliders</div>
  </div>
  <div class="flex">
    <div class="flex-1 bg-orange-100 border border-orange-300 px-4 py-3 text-center">
      <div class="font-bold text-orange-800">Panda3D</div>
      <div class="text-sm text-orange-600">3D backend</div>
    </div>
    <div class="flex-1 bg-purple-100 border border-purple-300 px-4 py-3 text-center">
      <div class="font-bold text-purple-800">pygame</div>
      <div class="text-sm text-purple-600">gamepad input</div>
    </div>
  </div>
  <div class="bg-gray-200 border border-gray-400 rounded-b-lg px-6 py-3 text-center">
    <div class="font-bold text-gray-700">Python + OpenGL</div>
  </div>
</div>

<div class="mt-4 text-center text-sm">

Three layers: **Ursina** (rendering, physics) · **pygame** (gamepad input) · **Your code** (experiment logic, trials, data)

</div>

<!--
Think of this as a layer cake. Ursina handles all the 3D rendering. Pygame handles hardware input that Ursina's backend doesn't cover well on all platforms. Your experiment logic sits on top.
-->

---
layout: section
---

# Module 2
## Ursina Fundamentals

<!--
Now let's learn the building blocks. Everything in Ursina is an Entity.
-->

---
layout: pgTwoColumn
leftWidth: 55
rightWidth: 45
---

::title::
The Entity: Everything Is One

::left::

```python
from ursina import *

app = Ursina()

cube = Entity(
    model='cube',
    color=color.orange,
    texture='white_cube',
    position=(0, 1, 0),
    scale=(2, 1, 1),
    rotation=(0, 45, 0),
    collider='box',
)

app.run()
```

::right::

An Entity = **model** + **position** + **appearance** + optional **physics**

<comBlock bgColor="bg-gray-50" border="left" borderColor="border-gray-400">

Walls, floors, furniture, collectibles, even the player -- they're all Entities with different properties.

</comBlock>

<!--
Entity is the one class to rule them all. Walls, floors, furniture, collectibles, even the player -- they're all Entities with different properties.
-->

---
layout: pgTwoColumn
leftWidth: 45
rightWidth: 55
---

::title::
Coordinate System

::left::

<img src="/images/coordinate-system.svg" class="w-full" />

::right::

- **x** -- right (+) / left (-)
- **y** -- up (+) / down (-)
- **z** -- forward (+) / back (-)

`position=(3, 0.5, 4)` means: 3 right, 0.5 up, 4 forward

> Ursina uses a **Y-up, right-handed** coordinate system (same as Panda3D)

<!--
This is the most important diagram today. When you place an object, you need to think in these three axes. Y is up -- different from some 2D frameworks where Y is often down.
-->

---
layout: pgTwoColumn
leftWidth: 50
rightWidth: 50
---

::title::
Entity Properties at a Glance

::left::

| Property   | Example              |
|------------|----------------------|
| `model`    | `'cube'`, `'sphere'` |
| `color`    | `color.orange`       |
| `texture`  | `'brick'`, `'grass'` |
| `position` | `(0, 1, 0)`         |
| `scale`    | `(2, 1, 1)` or `0.5`|

::right::

| Property   | Example              |
|------------|----------------------|
| `rotation` | `(0, 45, 0)`        |
| `collider` | `'box'`, `'mesh'`   |
| `parent`   | `camera.ui`         |
| `enabled`  | `True` / `False`    |

<comBlock bgColor="bg-gray-50" border="left" borderColor="border-gray-400">

`model` and `position` are the minimum; everything else has sensible defaults.

</comBlock>

<!--
These are the properties you will use in every exercise. model and position are the minimum; everything else has sensible defaults.
-->

---
layout: pgComparison
leftColor: bg-blue-50
rightColor: bg-green-50
---

::title::
Cameras: Two Modes

::left-title::
EditorCamera

::left::

Orbit, zoom, pan -- great for **building**

```python
EditorCamera()
# middle-click orbit, scroll zoom
```

- Free orbit movement
- No physics
- Use for scene building & debugging

::right-title::
FirstPersonController

::right::

WASD + mouse look -- great for **experiments**

```python
from ursina.prefabs.first_person_controller \
    import FirstPersonController

player = FirstPersonController()
player.gravity = 0
player.position = (0, 1, 0)
```

- Gravity + collision
- Use for participant navigation

<!--
EditorCamera is for building and debugging. FirstPersonController is what your participants will use -- it gives you WASD walking and mouse look out of the box.
-->

---
layout: pgTwoColumn
leftWidth: 50
rightWidth: 50
---

::title::
Exercise 1: Build a Room (15 min)

::left-title::
Steps

::left::

1. Open `exercises/ex2_build_a_room/template.py`
2. Create a floor (a flat quad)
3. Add four walls (position + rotate quads)
4. Place at least 3 furniture items
5. Add a `FirstPersonController` and walk around

::right-title::
Key Hint

::right::

A flat floor = `quad` with `rotation_x=90`

```python
floor = Entity(
    model='quad',
    scale=(20, 20),
    rotation_x=90,
    color=color.dark_gray,
    texture='white_cube'
)
```

<!--
Open the template file. The TODO comments tell you what to build. Start with the floor, then add walls one at a time. Remember: a quad faces -z by default, so you need to rotate walls to face inward.
-->

---
layout: pgTwoColumn
leftWidth: 50
rightWidth: 50
---

::title::
Exercise 2: Make It Real (10 min)

::left-title::
Steps

::left::

1. Open `exercises/ex3_make_it_real/template.py`
2. Add `collider='box'` to walls and furniture
3. Replace plain colors with textures: `'brick'`, `'grass'`
4. Add `Sky()` for atmosphere
5. Add `DirectionalLight()` for depth

::right-title::
Before vs After

::right::

| Without                | With                     |
|------------------------|--------------------------|
| Walk through walls     | Solid walls block you    |
| Flat gray surfaces     | Brick walls, grass floor |
| Black void background  | Sky dome                 |

<!--
This exercise is quick -- just adding polish. Colliders are the most important part: without them, walls are just decoration. Textures and sky make a huge difference for immersion.
-->

---
layout: center
---

# Break

20 minutes -- Back at **10:25**

<!--
Take a break. Stretch, get coffee. When you come back, we'll add interaction and gamepad input.
-->

---
layout: section
---

# Module 3
## Adding Interaction & Input

<!--
So far our scene is pretty but static. Let's make things happen when the player does something.
-->

---
layout: pgTwoColumn
leftWidth: 55
rightWidth: 45
---

::title::
Ursina's Input Model

::left::

```python
# 1. update() — every frame (~60 fps)
def update():
    if held_keys['w']:
        player.y += time.dt

# 2. input(key) — once per press/release
def input(key):
    if key == 'space':
        jump()

# 3. Entity methods — scoped
class Player(Entity):
    def update(self):
        pass
    def input(self, key):
        pass
```

::right::

| Method      | Use case              |
|-------------|-----------------------|
| `update()`  | Continuous movement   |
| `input()`   | Discrete actions      |
| `held_keys` | Sustained key holding |

<comBlock bgColor="bg-blue-50" border="left" borderColor="border-blue-400">

`update()` runs 60x/s -- for proximity checks. `input()` fires once -- for trial triggers.

</comBlock>

<!--
update runs 60 times per second -- use it for continuous checks like proximity detection. input fires once per keypress -- use it for discrete actions like starting a trial or jumping.
-->

---
layout: pgTwoColumn
leftWidth: 55
rightWidth: 45
---

::title::
The Pygame Sidecar Pattern (Optional)

::left::

**Problem:** Panda3D has unreliable gamepad support on **macOS**.

**Solution:** Use pygame alongside Ursina for joystick input.

```python
import pygame

pygame.init()
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0) \
    if pygame.joystick.get_count() > 0 \
    else None

DEADZONE = 0.2
```

::right::

```python
def update():
    if joystick is None:
        return
    pygame.event.pump()

    # Left stick: movement
    lx = joystick.get_axis(0)
    ly = joystick.get_axis(1)

    if abs(lx) > DEADZONE:
        player.position += \
          player.right * lx * 5 * time.dt
    if abs(ly) > DEADZONE:
        player.position += \
          player.forward * -ly * 5 * time.dt
```

<!--
The key insight: pygame and Ursina can coexist in the same process. Pygame handles only the gamepad; Ursina handles everything else. Call pygame.event.pump() every frame to keep it alive.
-->

---
layout: pgTwoColumn
leftWidth: 45
rightWidth: 55
---

::title::
Gamepad Integration: Full Pattern

::left::

<img src="/images/gamepad-axes.svg" class="w-full" />

::right::

```python
def update():
    if not joystick: return
    pygame.event.pump()

    # Left stick → movement
    lx = apply_deadzone(js.get_axis(0))
    ly = apply_deadzone(js.get_axis(1))
    # Right stick → camera
    rx = apply_deadzone(js.get_axis(2))
    ry = apply_deadzone(js.get_axis(3))

    speed = 5 * time.dt
    player.position += player.forward * -ly * speed
    player.position += player.right * lx * speed
    player.rotation_y += rx * 2
    camera.rotation_x = clamp(
        camera.rotation_x - ry * 2, -90, 90)
```

<!--
This is the complete gamepad pattern. Left stick controls movement relative to facing direction. Right stick controls the camera. The apply_deadzone function zeros out small axis values to prevent drift.
-->

---
layout: pgTwoColumn
leftWidth: 50
rightWidth: 50
---

::title::
Exercise 3: Pick Up the Star (15 min)

::left-title::
Steps

::left::

1. Open `exercises/ex4_pick_up_star/template.py`
2. Create 3 gold star entities at different positions
3. Add a score counter on the HUD (`Text` on `camera.ui`)
4. In `update()`, check distance to each star
5. When close enough: hide star, increment score
6. Show "Well done!" when all collected

::right-title::
Key Pattern: Proximity Detection

::right::

```python
COLLECT_DISTANCE = 2

def update():
    for star in stars:
        if star.enabled and \
           distance(player.position,
                    star.position) \
           < COLLECT_DISTANCE:
            star.enabled = False
            score += 1
```

Same pattern for "participant reached the target" in a navigation task.

<!--
This is the interaction pattern you will use in real experiments: check distance each frame, trigger an event when a threshold is crossed.
-->

---

# Input Abstraction

Why abstract input? So experiments work with keyboard **and** gamepad:

```python
class InputManager:
    """Unified input: keyboard or gamepad."""

    def get_movement(self):
        if self.joystick:
            return (self.get_axis(0), self.get_axis(1))
        return (
            held_keys['d'] - held_keys['a'],
            held_keys['w'] - held_keys['s'],
        )

    def get_action(self, key):
        if self.joystick and self.joystick.get_button(0):
            return True
        return key == 'space'
```

Same experiment code works on desktop and in the lab.

<!--
This abstraction layer means you write your experiment logic once and it works with whatever input device the participant uses.
-->

---
layout: section
---

# Module 4
## Experiment Paradigm Design

<!--
Now we move from game-like interaction to real experiment structure. This is where we add trials, conditions, timing, and data logging.
-->

---

# The Experiment Layer

Your 3D scene is the **stimulus**. On top of it, you need:

<v-clicks>

- **State machine** -- what phase of the trial are we in?
- **Trial sequencing** -- condition, repeats, randomization
- **Timing** -- fixation duration, response windows, ITI
- **Data logging** -- what happened, when, under which condition
- **Triggers** -- event markers for EEG/fMRI synchronization

</v-clicks>

> Ursina handles the *scene*. You handle the *experiment*.

<!--
Think of it as two layers: the 3D world that participants see and interact with, and the experiment logic that controls what they see and records what they do.
-->

---

# State Machine

Every trial follows a sequence of states:

<img src="/images/trial-timeline.svg" class="w-full mt-2 mb-4" />

Each state controls:
- What the participant **sees** (text, scene, fixation cross)
- What **input** is accepted (SPACE to advance, ESC to skip)
- What gets **logged** (triggers, timestamps — red markers below the timeline)

<!--
This state machine is the backbone of any trial-based experiment. The participant reads instructions, sees a fixation cross, performs the task, and gets feedback. Then we repeat for the next trial.
-->

---
layout: pgTwoColumn
leftWidth: 55
rightWidth: 45
---

::title::
Implementing the State Machine

::left::

```python
class Experiment(Entity):
    def __init__(self):
        super().__init__()
        self.state = 'INSTRUCTION'
        self.current_trial = 0
        # ... setup trials, UI, player

    def input(self, key):
        if key == 'space':
            if self.state == 'INSTRUCTION':
                self.show_fixation()
            elif self.state == 'FEEDBACK':
                self.next_trial()
        elif key == 'escape' \
                and self.state == 'TASK':
            self.end_task(completed=False)

    def update(self):
        if self.state != 'TASK':
            return
        # Check proximity, collect stars...
```

::right::

<comBlock title="Key Idea" bgColor="bg-blue-50" border="left" borderColor="border-blue-400">

Subclassing `Entity` gives you `update()` and `input()` scoped to the experiment.

</comBlock>

The `state` variable controls which code path runs -- clean separation of concerns.

<!--
By making the experiment an Entity, Ursina automatically calls its update and input methods each frame.
-->

---
layout: pgTwoColumn
leftWidth: 50
rightWidth: 50
---

::title::
Trial Sequencing

::left::

```python
# Define conditions and build trial list
trials = []
for _ in range(2):  # 2 repeats
    trials.append(
      {'condition': 'easy', 'n_stars': 1})
    trials.append(
      {'condition': 'hard', 'n_stars': 3})

random.shuffle(trials)
```

**For real experiments:** use balanced Latin squares, blocked randomization, or counterbalancing as needed.

::right::

| Trial | Condition | Stars |
|-------|-----------|-------|
| 1     | hard      | 3     |
| 2     | easy      | 1     |
| 3     | easy      | 1     |
| 4     | hard      | 3     |

The pattern: build a list of dicts, shuffle, iterate.

<!--
Each trial is a dictionary with its parameters. You build the full list upfront, shuffle it, then step through one at a time.
-->

---
layout: pgTwoColumn
leftWidth: 55
rightWidth: 45
---

::title::
Data Logging

::left::

```python
import csv

csv_file = open('experiment_data.csv',
                'w', newline='')
writer = csv.writer(csv_file)
writer.writerow([
    'trial', 'condition', 'n_stars',
    'collected', 'duration_s', 'completed'
])

# At the end of each trial:
writer.writerow([
    trial_number,
    trial['condition'],
    trial['n_stars'],
    score,
    f"{duration:.3f}",
    completed,
])
csv_file.flush()
```

::right::

**What to record:**
- Trial number & condition
- Stimulus parameters
- Response & accuracy
- Reaction time / duration
- Timestamps

<comBlock label="Important" bgColor="bg-yellow-50" border="left" borderColor="border-yellow-400">

Always `flush()` after each trial -- if the program crashes, you keep the data.

</comBlock>

<!--
CSV is the simplest and most portable format. One row per trial, columns for everything you might want to analyze later.
-->

---
layout: pgTwoColumn
leftWidth: 55
rightWidth: 45
---

::title::
EEG Triggers

::left::

```python
# Define trigger codes
TRIG_FIXATION   = 1
TRIG_TASK_START = 2
TRIG_COLLECT    = 3
TRIG_TRIAL_END  = 4

def send_trigger(code):
    """Replace with LabJack/serial
    for real experiments."""
    print(f"[TRIGGER] code={code} "
          f"at {time.time():.3f}")
```

::right::

Send at key moments:

```python
send_trigger(TRIG_FIXATION)
send_trigger(TRIG_TASK_START)
send_trigger(TRIG_COLLECT)
send_trigger(TRIG_TRIAL_END)
```

<comBlock bgColor="bg-gray-50" border="left" borderColor="border-gray-400">

**In production:** replace `print` with a hardware call (LabJack, parallel port, serial). The trigger points stay the same.

</comBlock>

<!--
For EEG experiments, you need millisecond-accurate event markers. We mock them with print statements today, but the architecture is identical to a real setup.
-->

---
layout: pgTwoColumn
leftWidth: 50
rightWidth: 50
---

::title::
Exercise 4: Mini Experiment (20 min)

::left-title::
Steps

::left::

1. Open `exercises/ex5_mini_experiment/template.py`
2. Define 2 conditions (easy/hard) x 2 repeats
3. Implement state machine: INSTRUCTION → FIXATION → TASK → FEEDBACK
4. Log each trial to CSV
5. Add mock triggers at key events
6. Run it -- complete all 4 trials and check CSV

::right-title::
Two Tracks

::right::

<comBlock title="Builder Track" bgColor="bg-blue-50" border="left" borderColor="border-blue-400">

Implement from the template hints

</comBlock>

<comBlock title="Runner Track" bgColor="bg-green-50" border="left" borderColor="border-green-400">

Read the solution, modify parameters (add a condition, change timing)

</comBlock>

<!--
This is the big one. You're building a real experiment paradigm from scratch. The template has the structure laid out -- you fill in the state transitions and data logging.
-->

---

# Debrief: Mapping to Real Experiments

| Workshop concept       | Real experiment equivalent         |
|------------------------|------------------------------------|
| Collect stars          | Navigate to target / reach object  |
| Easy vs hard condition | Set size, distance, distractor load |
| Proximity detection    | Response zone / collision trigger  |
| CSV data logging       | Behavioral data file               |
| Mock triggers          | EEG/fMRI event markers             |
| State machine          | Trial sequence controller          |

The architecture scales: swap the 3D task, keep the experiment logic.

<!--
Everything we did today with stars and rooms is a stand-in for real experimental manipulations. The state machine, data logging, and trigger architecture don't change when you switch to a different task.
-->

---
layout: center
---

# Q&A & Hands-on

Catch up on exercises, ask questions, explore

---
layout: center
---

# Lunch Break

Back at **13:00**

<!--
Enjoy your lunch. This afternoon we'll look at a complete production experiment, VR headsets, and 3D models.
-->

---
layout: section
---

# Module 5
## Capstone: MazeWalker-Py

<!--
Let's see what a complete, production-quality experiment looks like using the same stack you've been learning.
-->

---
layout: pgTwoColumn
leftWidth: 50
rightWidth: 50
---

::title::
MazeWalker-Py: Architecture

::left::

```
mazewalker-py/
├── experiment.py
├── maze_renderer.py
├── input_manager.py
├── trigger.py
├── config.yaml
├── conditions.csv
└── data/
```

::right::

- **experiment.py** -- state machine + trials
- **maze_renderer.py** -- Ursina scene
- **input_manager.py** -- gamepad + keyboard
- **trigger.py** -- EEG interface (LabJack)
- **config.yaml** -- all parameters
- **conditions.csv** -- trial list

Same patterns you learned today, at production scale.

<!--
MazeWalker-Py is a real experiment used in research. Let's look at how it's organized.
-->

---

# Your Code vs MazeWalker-Py

| Your Exercise 5                  | MazeWalker-Py                       |
|----------------------------------|--------------------------------------|
| State machine in one file        | Separate `experiment.py`             |
| Hard-coded conditions            | External `conditions.csv`            |
| Room from code                   | `maze_renderer.py` reads layout data |
| `print()` triggers               | `trigger.py` with LabJack driver     |
| Keyboard only                    | `input_manager.py` (keyboard + pad)  |
| CSV logging inline               | Dedicated logging with trajectories  |

**The patterns are identical.** The production version separates concerns into files and uses configuration files instead of hard-coded values.

<!--
Compare these side by side. The experiment logic is the same state machine. The difference is organization.
-->

---
layout: pgTwoColumn
leftWidth: 50
rightWidth: 50
---

::title::
Key Files Walkthrough

::left::

**experiment.py** -- the state machine:

```python
class MazeExperiment(Entity):
    states = ['INSTRUCTION', 'FIXATION',
              'NAVIGATION', 'FEEDBACK',
              'DONE']
    # Same pattern as your Exercise 5
```

**maze_renderer.py** -- builds from data:

```python
def build_maze(layout):
    for row, col in layout:
        Entity(model='cube',
               position=(col, 0.5, row),
               texture='brick',
               collider='box')
```

::right::

**trigger.py** -- hardware abstraction:

```python
class Trigger:
    def send(self, code):
        if self.device:
            self.device.write(code)
        else:
            print(f"[MOCK] {code}")
```

<comBlock bgColor="bg-gray-50" border="left" borderColor="border-gray-400">

Each file has a single responsibility. You can test each piece independently.

</comBlock>

<!--
experiment.py manages state. maze_renderer.py builds the visual scene. trigger.py abstracts the hardware.
-->

---
layout: pgTwoColumn
leftWidth: 50
rightWidth: 50
---

::title::
Exercise 5: Make It Yours (20 min)

::left-title::
Builder Track

::left::

Pick one:

- Add a third condition (medium: 2 stars)
- Add a time limit per trial (30s, auto-end)
- Log player position every 0.5s (trajectory)
- Add a practice trial before real trials

::right-title::
Runner Track

::right::

Explore and configure:

- Read through MazeWalker-Py code on GitHub
- Change `config.yaml` parameters (maze size, time limits)
- Run the experiment and examine output data

<!--
Choose the track that matches your role. Builders: extend your Exercise 4. Runners: explore MazeWalker-Py and practice configuring an experiment you didn't write.
-->

---
layout: pgTwoColumn
leftWidth: 50
rightWidth: 50
---

::title::
Data Visualization: Trajectory Plots

::left::

```python
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('trajectory.csv')

plt.figure(figsize=(8, 8))
for trial in df.trial.unique():
    t = df[df.trial == trial]
    plt.plot(t.x, t.z, alpha=0.6,
             label=f'Trial {trial}')

plt.xlabel('X position')
plt.ylabel('Z position')
plt.title('Navigation Trajectories')
plt.legend()
plt.axis('equal')
plt.show()
```

::right::

Trajectory data reveals **strategy** -- not just whether they succeeded, but *how* they moved.

<comBlock bgColor="bg-blue-50" border="left" borderColor="border-blue-400">

You can analyze:
- Path efficiency
- Hesitation points
- Strategy differences between conditions

</comBlock>

<!--
This is why 3D experiments are interesting for research. You don't just get reaction times -- you get full movement trajectories.
-->

---
layout: section
---

# Module 6
## VR Roadmap & Wrap-up

<!--
Final module. Let's talk about what changes when you move from desktop 3D to actual VR headsets.
-->

---
layout: pgComparison
leftColor: bg-blue-50
rightColor: bg-orange-50
---

::title::
Desktop 3D vs Headset VR

::left-title::
What Stays the Same

::left::

- Entity-based scene construction
- Experiment state machine
- Trial sequencing & data logging
- Trigger architecture
- Python as the main language

::right-title::
What Changes

::right::

- Mouse + keyboard → **hand controllers + head tracking**
- Monitor at 60 Hz → **headset at 90 Hz** (per eye)
- `FirstPersonController` → **VR camera rig** (stereo)
- Must **manage comfort** (motion sickness)
- Need **OpenXR runtime**

::callout::

~90% of your code stays the same. The scene, experiment logic, and data logging are identical.

<!--
The good news: about 90% of your code stays the same. What changes is the camera setup and the input device.
-->

---

# The VR Diff: ~20 Lines

```python
# Desktop version (what you built today)
from ursina import *
player = FirstPersonController()

# VR version (Panda3D OpenXR)
from ursina import *
from ursina.xr import VRPlayer  # hypothetical — use Panda3D OpenXR

player = VRPlayer()
player.hand_left.on_grip = grab_object
player.hand_right.on_trigger = interact
```

The core change:

```diff
- player = FirstPersonController()
+ player = VRPlayer()
+ player.ipd = 0.063          # interpupillary distance
+ player.tracking_origin = 'floor'
+ player.render_stereo = True  # one pass per eye
```

Everything else -- your room, your stars, your state machine -- **unchanged**.

<!--
This is the payoff of using a Python 3D engine. When you're ready for VR, you swap the camera and input code.
-->

---
layout: section
---

# Module 7
## Beyond Primitives: 3D Models

<!--
So far we've built everything from cubes and quads. Let's look at how to bring realistic 3D models into your experiments.
-->

---
layout: pgTwoColumn
leftWidth: 50
rightWidth: 50
---

::title::
Sourcing 3D Models

::left-title::
Free Model Libraries

::left::

- **Sketchfab** -- largest library, CC licensed
- **Poly Haven** -- all CC0, no attribution
- **Objaverse** -- 800K+ models, research use

> Prefer **.glb** (single file, textures embedded) over .obj

::right-title::
AI Generation

::right::

- **Meshy.ai** -- text → 3D in ~2 min, free tier
- **Tripo3D** -- fast, has a Python API
- **HuggingFace TripoSR** -- local, needs GPU

Pipeline: prompt → generate → preview → download .glb

> AI models for **prototyping**; curated models for final stimuli.

<!--
For a workshop setting, Meshy is the easiest to demo -- no GPU, no install, just a browser. For production experiments, curated models give you more control over visual consistency.
-->

---
layout: pgTwoColumn
leftWidth: 50
rightWidth: 50
---

::title::
Loading Models in Ursina

::left-title::
Code

::left::

```python
# Load a .glb model
chair = Entity(
    model='assets/chair.glb',
    scale=0.5,
    position=(2, 0, 3),
    rotation=(0, 90, 0),
    collider='box',
)

# Load a .obj model
table = Entity(
    model='assets/table.obj',
    texture='assets/table_diffuse.png',
    scale=1.0,
)
```

::right-title::
Gotchas

::right::

- **Scale varies wildly** between sources -- always check and adjust
- Some models face -Z -- use `rotation_y=180`
- **.glb** embeds textures; **.obj** needs .mtl + texture files alongside
- Place models in an `assets/` folder

<comBlock bgColor="bg-gray-50" border="left" borderColor="border-gray-400">

Same Entity API you already know -- just pass a file path instead of `'cube'` or `'sphere'`.

</comBlock>

<!--
The beauty of Ursina: loading a complex 3D model uses the exact same Entity class you've been using all workshop. model='cube' becomes model='assets/chair.glb' and everything else stays the same.
-->

---
layout: pgTwoColumn
leftWidth: 50
rightWidth: 50
---

::title::
Exercise 6: Add a 3D Model (15 min)

::left-title::
Builder Track

::left::

1. Open your room from Exercise 1/2
2. Load `assets/table.glb` into the scene
3. Adjust scale and position until it fits
4. Add `collider='box'` so the player can't walk through
5. Load a second model (`assets/lamp.glb`)

::right-title::
Runner Track

::right::

- Browse the provided models in `assets/`
- Swap different models, compare scale/rotation
- Bonus: visit meshy.ai, generate a model from a text prompt, download .glb, load it

<comBlock bgColor="bg-green-50" border="left" borderColor="border-green-400">

We provide 3-4 pre-downloaded .glb models in the starter package -- no account signup needed.

</comBlock>

<!--
The starter package includes a few .glb models so you can get started immediately. If you have time and want to try AI generation, Meshy gives you 5 free models per day.
-->


---
layout: pgTwoColumn
leftWidth: 50
rightWidth: 50
---

::title::
Resources

::left-title::
Documentation

::left::

- Ursina: [ursinaengine.org](https://www.ursinaengine.org/)
- Panda3D: [panda3d.org](https://www.panda3d.org/)
- pygame: [pygame.org/docs](https://www.pygame.org/docs/)
- Panda3D OpenXR plugin documentation

::right-title::
This Workshop

::right::

- GitHub: `github.com/msenselab/vr-tutorial`
- All exercises with templates and solutions
- Slides available online
- MazeWalker-Py source code and examples
- PsychoPy-to-Ursina migration notes

<!--
All the code and slides are on GitHub. The exercises have both templates and solutions.
-->

---

# Homework

Adapt the exercises for your own research question:

<v-clicks>

1. **Change the task** -- replace star collection with your paradigm
2. **Add your conditions** -- define meaningful experimental manipulations
3. **Design the CSV** -- what dependent variables will you analyze?
4. **Add trajectory logging** -- record position every N milliseconds
5. **Add 3D models** -- replace primitives with realistic assets
6. **Test with a colleague** -- have someone else run your experiment

</v-clicks>

> The best way to learn is to build something you actually need.

<!--
The workshop gave you the architecture. Now fill it with your own research question. Start small -- get one trial working, then scale up.
-->

---

<div class="h-full flex flex-col justify-center items-center text-center">
  <h1 class="text-4xl font-bold mb-2">Thank You!</h1>
  <h2 class="text-2xl text-gray-500 mb-6">Questions?</h2>
  <p class="text-lg"><strong>Chunyu Qu</strong> · chunyu.qu@psy.lmu.de</p>
  <p class="text-lg"><strong>Zhuanghua Shi</strong> · strongway@psy.lmu.de</p>
  <p class="text-base text-gray-500 mt-2">LMU Munich</p>
  <p class="text-sm text-gray-400 mt-4">Workshop materials: <code>github.com/msenselab/vr-tutorial</code></p>
  <p class="text-sm text-gray-400 mt-1">Erasmus+ KA210-VET · <a href="https://xr4vet.eu">xr4vet.eu</a></p>
  <div class="flex items-center justify-center gap-8 mt-6">
    <img src="/images/lmu-logo.png" class="h-12" />
    <img src="/images/comu-logo.png" class="h-12" />
    <img src="/images/eu-cofunded.png" class="h-10" />
  </div>
</div>

<!--
Thank you for your time and attention. I'm happy to take questions now, and you can always reach me by email or open an issue on the GitHub repository.
-->
