---
title: "Exercises"
description: "Hands-on coding exercises from screen to scene"
weight: 2
---

Five progressive exercises take you from a first 3D window to a complete experiment paradigm. Each builds on the previous one, so work through them in order.

## Exercise Overview

| #  | Exercise                                          | What You Learn                                                     | Duration |
|----|---------------------------------------------------|--------------------------------------------------------------------|----------|
| 1  | [Hello Ursina](/exercises/01-hello-ursina/)        | Verify setup; create your first 3D scene with a cube               | 10 min   |
| 2  | [Build a Room](/exercises/02-build-a-room/)        | Construct a room from primitives; position, rotate, and scale      | 25 min   |
| 3  | [Make It Real](/exercises/03-make-it-real/)        | Add colliders, textures, lighting, and a skybox                    | 20 min   |
| 4  | [Pick Up the Star](/exercises/04-pick-up-star/)   | Proximity detection, HUD display, keyboard events, gamepad input   | 25 min   |
| 5  | [Mini Experiment](/exercises/05-mini-experiment/) | State machine, trial sequencing, CSV logging, EEG triggers         | 35 min   |

## Prerequisites

- **Exercise 1**: Python 3.11+ and `pip install ursina pygame` completed (see [Setup Guide](/setup/))
- **Exercises 2-4**: Understanding of Exercise 1 concepts
- **Exercise 5**: Comfortable with Python classes and dictionaries

## How to Use Templates and Solutions

Each exercise folder (in the repository) contains:

- **`template.py`** -- a starting point with scaffolding and TODO comments. Work through the TODOs in order.
- **`solution.py`** -- a complete reference implementation. Use it to check your work or if you get stuck.

The recommended workflow:

1. Read the exercise page on this site first to understand the concepts.
2. Open `template.py` and run it to see the starting state.
3. Complete the TODOs one at a time, running the script after each change.
4. Compare your result with `solution.py` when you finish.

If you fall behind during the workshop, you can always start the next exercise from its template -- each template includes all the completed code from previous exercises.

## Builder vs Runner Tracks

- **Builders**: complete all TODOs and attempt the challenge extensions at the end of each exercise.
- **Runners**: focus on TODOs 1-3 in each exercise, run the solutions to understand the output, and read through the remaining code with the explanations on this site.
