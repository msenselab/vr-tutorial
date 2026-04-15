---
title: "Capstone: MazeWalker-Py"
description: "A walkthrough of a production experiment built with the same tools"
weight: 3
---

## Project Overview

[MazeWalker-Py](https://github.com/msenselab/MazeWalker-Py) is a maze-navigation experiment for EEG and behavioural research. Participants navigate virtual mazes using a gamepad while brain activity is recorded. It is built with Ursina, pygame, and the same architectural patterns you learned in this tutorial.

The capstone module connects everything you have built to a real research codebase. The goal is not to memorize the code but to recognize familiar patterns and understand how they scale.

## Architecture

```
mazewalker-py/
├── experiment.py       # State machine (like Exercise 5)
├── maze_renderer.py    # Scene building (like Exercises 2-3)
├── trigger.py          # EEG triggers via LabJack (like mock triggers in Exercise 5)
├── config.py           # Experiment parameters and trial definitions
├── data_logger.py      # CSV/JSON logging with timestamps
├── gamepad.py          # Pygame joystick input (like gamepad_demo.py)
└── main.py             # Entry point
```

## File-by-File Guide

### experiment.py -- The State Machine

This is the heart of the project. Like your Exercise 5 `Experiment` class, it manages:

- **States**: WELCOME, INSTRUCTION, FIXATION, NAVIGATION, FEEDBACK, BREAK, DONE
- **Transitions**: timed (fixation), event-driven (goal reached), and user-initiated (key press)
- **Trial management**: loading trial definitions, tracking the current trial, advancing to the next

The state machine is more elaborate than Exercise 5 (it has break periods and welcome screens) but the core pattern is identical: a `self.state` variable, methods for each state, and an `input()` handler that routes key presses based on the current state.

**Maps to**: Exercise 5's `Experiment` class

### maze_renderer.py -- Scene Building

This module generates 3D maze environments from layout data. Instead of hard-coded wall positions (like Exercises 2-3), it reads a maze definition (grid of walls and paths) and programmatically creates Entity objects:

- Walls are quads positioned and rotated based on grid coordinates
- The floor is a textured quad
- Goal objects are placed at specific locations
- Everything uses colliders for solid boundaries

The rendering logic is more general than what you built by hand, but each wall is still an `Entity(model='quad', collider='box', ...)` -- exactly the same primitives.

**Maps to**: Exercises 2-3 room building, Exercise 5's `build_room()` function

### trigger.py -- EEG Triggers

This module sends trigger codes through a LabJack device (a USB DAQ used in many EEG labs). The interface is the same as Exercise 5's mock triggers:

```python
# Exercise 5 (mock)
def send_trigger(code):
    print(f"[TRIGGER] code={code}")

# MazeWalker-Py (real hardware)
def send_trigger(code):
    labjack.setFIOState(trigger_pin, 1)   # pin HIGH
    time.sleep(0.005)                      # 5 ms pulse
    labjack.setFIOState(trigger_pin, 0)   # pin LOW
```

The trigger constants are defined the same way. Swapping between mock and real triggers requires changing one import -- the rest of the experiment code is untouched.

**Maps to**: Exercise 5's `send_trigger()` and `TRIG_*` constants

### gamepad.py -- Pygame Input

This module wraps pygame's joystick API with deadzone handling and axis mapping. It uses the exact pattern from Exercise 4's `gamepad_demo.py`:

1. Initialize pygame and detect the joystick.
2. Call `pygame.event.pump()` every frame.
3. Read axis values and apply deadzone filtering.
4. Feed movement values into the player entity.

**Maps to**: Exercise 4's `gamepad_demo.py`

### config.py and data_logger.py

These handle trial definitions (loaded from files instead of hard-coded) and data output (structured CSV/JSON with timestamps for every event). The principles match Exercise 5's CSV logging, but with more columns and richer metadata.

## How Tutorial Concepts Map to Real Code

| Tutorial Concept                | Exercise | MazeWalker-Py Equivalent              |
|---------------------------------|----------|----------------------------------------|
| `Entity(model='quad', ...)`     | 2-3      | Procedural wall generation             |
| `collider='box'`               | 3        | Collision on all maze walls            |
| `texture='brick'`              | 3        | Custom maze textures                   |
| `FirstPersonController`        | 2-5      | Custom player controller with gamepad  |
| `distance()` proximity check   | 4-5      | Goal detection in maze                 |
| `entity.enabled` / `destroy()` | 4-5      | Scene teardown between trials          |
| State machine (`self.state`)   | 5        | Extended state machine in experiment.py|
| `csv.writer` logging           | 5        | Structured data logging                |
| `send_trigger()` mock          | 5        | LabJack hardware triggers              |
| `invoke(fn, delay=N)`          | 5        | Timed fixation and inter-trial intervals|
| `pygame.joystick`              | 4        | Gamepad module for navigation          |

## Runner Track: What to Configure

If you are running experiments (not writing code), here is what you would typically change:

- **Participant ID and session number** -- passed as command-line arguments
- **Number of trials and conditions** -- defined in the config file
- **Maze layouts** -- selected by condition in the trial definition
- **Trigger port/channel** -- set in the trigger configuration
- **Data output directory** -- specified at launch

You do not need to modify Python code for routine data collection.

## Builder Track: What to Extend

If you are developing experiments, consider these starting points:

- **New maze types** -- create additional layout files and add them to the trial definitions.
- **New metrics** -- add columns to the data logger (e.g., path efficiency, head direction changes).
- **New stimuli** -- add objects to the maze renderer (e.g., landmarks, distractors).
- **New input modalities** -- integrate eye tracking or additional sensors through the same sidecar pattern used for the gamepad.
- **VR headset support** -- see the [VR Roadmap](/vr-roadmap/) for how to adapt the rendering pipeline.
