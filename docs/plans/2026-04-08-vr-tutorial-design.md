# VR Tutorial Design: From Screen to Scene

**Date:** 2026-04-08
**Format:** Half-day workshop (4-hour block, ~3.5h teaching)
**Delivery:** Slidev presentation slides + Hugo post-workshop reference site
**Reference project:** MazeWalker-Py (Ursina + pygame maze navigation for behavioral/EEG research)

---

## Audience

Mixed group of psychology/neuroscience researchers:
- **Builders:** Will design and code their own VR experiments
- **Runners:** Will set up, operate, and modify existing experiment code
- All have basic Python; none have 3D engine or VR experience
- Participants bring their own laptops (BYOL)

## Learning Outcomes

By the end, participants can:
1. Build a simple 3D environment from scratch using Ursina
2. Understand the MazeWalker-Py architecture well enough to adapt it
3. Wire up a complete experimental pipeline: trial sequencing, data logging, EEG triggers
4. See a clear path from desktop 3D to headset VR

## Pre-Workshop

- Install instructions distributed in advance: Python 3.11+, ursina, pygame, starter zip (exercise templates + assets)
- Fallback plan: participants who can't install follow the presenter; Hugo site has everything for self-study later

---

## Schedule Overview

```
Module 1: Welcome & Setup Check        (20 min)
Module 2: Ursina Fundamentals           (45 min)
         -- Break (15 min) --
Module 3: Adding Interaction & Input    (40 min)
Module 4: Experiment Paradigm Design    (45 min)
         -- Break (15 min) --
Module 5: Capstone -- MazeWalker-Py     (40 min)
Module 6: VR Roadmap & Wrap-up          (15 min)
                                   Total: ~3h55m
```

**Progression:** Basics (M1-2) -> Interaction (M3) -> Experiment layer (M4) -> Real system (M5) -> Next steps (M6)

---

## Module 1: Welcome & Setup Check (20 min)

### Goal
Everyone has a working environment and shared mental model.

### Content
- **5 min** -- Audience poll: coding experience, experiment types, VR exposure
- **5 min** -- Big picture: why Python for VR experiments? Landscape positioning (PsychoPy for 2D, Unity/Unreal for AAA, Ursina as the sweet spot -- lightweight, Pythonic, Panda3D under the hood)
- **10 min** -- Setup verification. Run hello-world script:

```python
from ursina import *
app = Ursina()
Entity(model='cube', color=color.orange, texture='white_cube')
EditorCamera()
app.run()
```

TAs help stragglers. If they see a cube, they're ready.

---

## Module 2: Ursina Fundamentals (45 min)

### Goal
Build a simple room from scratch -- walls, floor, textured objects, first-person camera.

### Content

**Lecture (10 min):** Core concepts
- Entity: position, rotation, scale, model, texture, color
- Coordinate system (y-up)
- Camera types: EditorCamera vs FirstPersonController

**Exercise 1: "Build a Room" (15 min)**
- Create a floor (quad, rotation_x=90)
- Add four walls with colors/textures
- Place 3D objects (cubes, spheres) as furniture
- Switch to FirstPersonController and walk around

**Lecture (10 min):** Collision, lighting, skybox
- `collider='box'` on walls -- can't walk through
- Skybox changes atmosphere
- Quick lighting overview

**Exercise 2: "Make It Real" (10 min)**
- Add colliders to all walls
- Load a custom texture (provided in starter zip)
- Add a Sky entity
- Place a collectible object (glowing sphere)

---

## Module 3: Adding Interaction & Input (40 min)

### Goal
Detect events, handle multiple input devices, bridge pygame into Ursina.

### Content

**Lecture (10 min):** Ursina's input model
- `input()` function, `held_keys`, `update()` loop
- The problem: Panda3D doesn't detect gamepads on macOS
- Solution: pygame as an input sidecar

**Demo (5 min):** Minimal pygame joystick polling alongside Ursina
- `pygame.event.pump()` as the non-blocking bridge
- Pattern: pygame reads hardware, feed values into Ursina's player/camera

**Exercise 3: "Pick Up the Star" (15 min)**
- Build on Exercise 2's room
- Proximity detection in `update()`: distance to collectible
- On collect: play sound, hide object, update score (Text on camera.ui)
- Bonus: keyboard shortcut to reset scene

**Lecture (10 min):** Input abstraction pattern
- One `get_input()` function for keyboard + gamepad
- MazeWalker-Py approach: deadzone, axis mapping, look speed
- Key takeaway: pygame fills a gap, not a replacement

---

## Module 4: Experiment Paradigm Design (45 min)

### Goal
Turn a 3D scene into a proper experiment with trials, timing, logging, and triggers.

### Content

**Lecture (15 min):** The experiment layer
- State machine: INSTRUCTION -> FIXATION -> TASK -> FEEDBACK -> next trial
- Trial sequencing: conditions list, randomization, repeats
- Data logging: per-frame trajectory vs per-trial summary, CSV, timestamps
- EEG/hardware triggers: trigger codes, LabJack, serial port alternatives
- Architecture diagram: how layers stack on Ursina

**Exercise 4: "Mini Experiment" (20 min)**

Skeleton-based exercise (provided template, participants fill in key parts):
- 2 conditions x 2 repeats = 4 trials:
  - Condition A: collect 1 star
  - Condition B: collect 3 stars
- Implement simplified state machine
- Randomize trial order
- Log to CSV: trial number, condition, duration, items collected
- Show fixation cross between trials
- Builder bonus: mock trigger function (`print(f"TRIGGER: {code}")`)

**Debrief (10 min)**
- Review what they built
- Map to real experiment requirements
- Discussion: what would you add for your own research?

Key takeaway: state machine + CSV logging + trigger pattern is the universal backbone. The 3D content is interchangeable.

---

## Module 5: Capstone -- MazeWalker-Py (40 min)

### Goal
See all pieces composed in a real experiment codebase. Modify it, don't just watch.

### Content

**Guided Tour (15 min):** Walk through architecture
- `experiment.py`: state machine (parallels to Exercise 4)
- `maze_renderer.py`: scene building from .maz data (same Entity patterns from Module 2)
- `trigger.py`: real LabJack triggers vs mock function
- pygame gamepad: exact pattern from Module 3
- Message: "You already understand every piece."

**Exercise 5: "Make It Yours" (20 min)**

Tiered by skill:
- **Runner track:** Change parameters -- move speed, repeats, trigger radius. Run experiment, inspect CSV output.
- **Builder track:** Add a feature -- countdown timer overlay, extra logged variable, or new trigger code.

All participants run a short 2-trial experiment on their laptops.

**Demo (5 min):** Trajectory visualization
- `plot_trajectory.py`: bird's-eye path plot, speed-over-time graph
- "This is what your data pipeline produces."

---

## Module 6: VR Roadmap & Wrap-up (15 min)

### Goal
Clear next steps. No one leaves wondering "how do I actually use VR?"

### Content

**The Path to Headset VR (8 min)**
- Panda3D's OpenXR / SteamVR plugin
- What changes: stereoscopic camera, head tracking replaces mouse look, controller tracking replaces gamepad
- What stays the same: scene building, state machine, data logging, triggers
- Side-by-side: desktop code vs VR-adapted code (~20 lines that change)
- Alternative paths: OpenHMD, WebXR for browser-based VR
- Honest take: when desktop 3D is enough vs when you need a headset

**Resources & Next Steps (5 min)**
- Hugo site: slides, exercises, solutions, starter code, MazeWalker-Py repo
- Recommended reading: Panda3D docs, Ursina cookbook, VR experiment design literature
- Community links
- Homework: take Exercise 4, swap in your own task, collect pilot data

**Q&A / Closing (2 min)**

---

## Deliverables

### For the Workshop
1. **Slidev presentation** -- one deck covering all 6 modules
2. **Starter zip** -- exercise templates, assets (textures, sounds), skeleton code for Exercise 4
3. **Pre-workshop install guide** -- step-by-step for macOS/Windows/Linux

### For the Hugo Site (post-workshop)
1. All slides (exported or embedded)
2. Exercise instructions with full solutions
3. MazeWalker-Py walkthrough guide
4. Install troubleshooting FAQ
5. VR extension resources and code examples
6. Links to reference materials and community

### Exercise Summary

| Exercise | Module | What they build | Key concepts |
|----------|--------|-----------------|--------------|
| 1: Build a Room | M2 | Textured room with FPC | Entity, model, texture, camera |
| 2: Make It Real | M2 | Colliders + skybox + collectible | Collision, Sky, scene polish |
| 3: Pick Up the Star | M3 | Proximity collection + score UI | update(), distance, UI overlay |
| 4: Mini Experiment | M4 | 2-condition trial experiment | State machine, CSV logging, randomization |
| 5: Make It Yours | M5 | Modified MazeWalker-Py | Real codebase navigation, parameter tuning |

---

## Design Decisions

- **Standalone exercises before capstone:** Less intimidating than diving into a large codebase. Builds confidence and vocabulary first.
- **Skeleton-based Exercise 4:** The densest exercise uses a provided template so runners can follow along without writing everything from scratch.
- **Tiered Exercise 5:** Builder/runner tracks let both audience segments engage meaningfully with the capstone.
- **pygame framed as input sidecar:** Avoids confusion about "two game engines." Clear message: Ursina renders, pygame polls hardware when Panda3D can't.
- **VR as roadmap, not hands-on:** Honest about what's taught. Shows the ~20-line diff so it feels achievable, not magical.
- **Slides drive the session:** Hugo site is post-workshop reference. Avoids split attention during the live session.
