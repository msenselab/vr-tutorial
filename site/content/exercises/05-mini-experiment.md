---
title: "Exercise 5: Mini Experiment"
description: "Build a complete experiment with state machine, trial sequencing, CSV logging, and EEG triggers"
weight: 5
---

## Learning Objectives

- Implement a **state machine** to control experiment flow.
- Build a **trial sequence** with conditions, repeats, and randomization.
- **Log data to CSV** at the end of each trial with timing and performance metrics.
- Send **mock EEG trigger codes** at key events.
- Use `invoke(fn, delay=N)` for timed transitions and `destroy(entity)` for scene cleanup.

## State Machine Diagram

Each trial cycles through four states. After all trials, the experiment ends.

```
INSTRUCTION --[SPACE]--> FIXATION --[1s]--> TASK --[all collected]--> FEEDBACK --[SPACE]--> next trial
                                              |                                                  |
                                              +------[ESC]------> FEEDBACK (escaped)             |
                                                                                                 v
                                                                                    (after last trial)
                                                                                         DONE
```

The `input()` method listens for SPACE and ESC. The state machine ensures each key press only has an effect in the correct state -- pressing SPACE during the TASK state does nothing.

## Key Concepts

### State Machine Pattern

Every psychology experiment is a state machine at its core. Each state defines what the participant sees and what inputs are valid. Transitions between states are triggered by events (key press, timer, task completion).

```
State           Entry Action                   Exit Trigger
-----------     ---------------------------    -------------------------
INSTRUCTION     Show trial info                SPACE pressed
FIXATION        Show "+", send trigger         1-second timer expires
TASK            Build room, enable player      All stars collected / ESC
FEEDBACK        Show results                   SPACE pressed
DONE            Show completion message        ESC quits app
```

### Trial Sequencing: Conditions x Repeats

Experimental designs cross conditions with repetitions. Here we have two conditions (easy = 1 star, hard = 3 stars) repeated twice each, yielding 4 trials:

```python
trials = []
for _ in range(2):  # repeats
    trials.append({'condition': 'easy', 'n_stars': 1})
    trials.append({'condition': 'hard', 'n_stars': 3})
random.shuffle(trials)
```

In a real experiment you might use Latin squares or counterbalancing, but the underlying structure is the same: build a list, shuffle or sort it, iterate through it.

### CSV Logging

Log one row per trial at the moment the trial ends. Record everything you need for analysis: trial number, condition, performance, and timing.

```python
self.csv_writer.writerow([
    trial_number, condition, n_stars, collected, duration, completed
])
self.csv_file.flush()  # write to disk immediately -- don't lose data on crash
```

Always call `flush()` after writing. If the experiment crashes mid-session, you want every completed trial safely on disk.

### Trigger Codes for EEG

EEG experiments need to mark the exact moment of key events in the continuous brain signal. A trigger code is a small integer sent to the EEG system via a hardware device (LabJack, parallel port, serial port).

In this exercise we use a mock function that prints to the console:

```python
TRIG_FIXATION  = 1
TRIG_TASK_START = 2
TRIG_COLLECT    = 3
TRIG_TRIAL_END  = 4

def send_trigger(code):
    print(f"  [TRIGGER] code={code} at {time.time():.3f}")
```

For a real experiment, replace the print with a hardware call. The trigger code constants stay the same -- only the function body changes.

### `invoke(fn, delay=N)` -- Timed Transitions

Ursina's `invoke()` schedules a function call after a delay (in seconds). Unlike `time.sleep()`, this does not freeze the application:

```python
invoke(self.start_task, delay=1)  # call start_task after 1 second
```

### `destroy(entity)` -- Cleanup Between Trials

When a trial ends, remove its entities before the next trial creates new ones:

```python
for e in self.stars:
    destroy(e)
for e in self.room_entities:
    destroy(e)
```

Compare with `entity.enabled = False` from Exercise 4, which hides but preserves. Here we destroy because each trial builds a fresh scene.

## Step-by-Step Instructions

Open `template.py` and read through the complete parts first -- `__init__`, `show_instruction()`, `show_done()`, `next_trial()`, and `input()`. Understand how the state machine is wired before filling in the missing methods.

Run the template as-is to confirm it starts without errors (it will show the instruction screen but nothing will happen when you press SPACE).

### TODO 1 -- Implement `show_fixation()`

This transitions from INSTRUCTION to FIXATION:

```python
def show_fixation(self):
    self.state = 'FIXATION'
    self.instruction_text.enabled = False
    self.fixation_text.enabled = True
    send_trigger(TRIG_FIXATION)
    invoke(self.start_task, delay=1)
```

Run and press SPACE. You should see `+` appear for 1 second.

### TODO 2 -- Implement `start_task()`

This sets up the entire trial scene:

```python
def start_task(self):
    self.state = 'TASK'
    self.fixation_text.enabled = False

    self.room_entities = build_room()
    trial = self.trials[self.current_trial]
    self.stars = spawn_stars(trial['n_stars'],
                            STAR_POSITIONS[:trial['n_stars']])
    self.score = 0

    self.player.enabled = True
    self.player.position = Vec3(0, 0, 0)
    self.player.rotation_y = 0
    mouse.locked = True

    self.score_text.text = f"Stars: 0/{trial['n_stars']}"
    self.score_text.enabled = True

    self.trial_start_time = time.time()
    send_trigger(TRIG_TASK_START)
```

### TODO 3 -- Implement Proximity Detection in `update()`

The same pattern from Exercise 4, adapted for the Experiment class:

```python
def update(self):
    if self.state != 'TASK':
        return

    trial = self.trials[self.current_trial]

    for star in self.stars:
        if star.enabled and distance(self.player.position,
                                     star.position) < 2:
            star.enabled = False
            self.score += 1
            self.score_text.text = (
                f"Stars: {self.score}/{trial['n_stars']}"
            )
            send_trigger(TRIG_COLLECT)

    if self.score >= trial['n_stars']:
        self.end_task(completed=True)
```

### TODO 4 -- Implement `end_task()`

Calculate timing, log to CSV, clean up the scene, and show feedback:

```python
def end_task(self, completed):
    duration = time.time() - self.trial_start_time
    trial = self.trials[self.current_trial]

    self.csv_writer.writerow([
        self.current_trial + 1,
        trial['condition'],
        trial['n_stars'],
        self.score,
        f"{duration:.3f}",
        completed,
    ])
    self.csv_file.flush()

    send_trigger(TRIG_TRIAL_END)

    for e in self.stars:
        destroy(e)
    for e in self.room_entities:
        destroy(e)
    self.stars = []
    self.room_entities = []

    self.player.enabled = False
    self.score_text.enabled = False
    mouse.locked = False

    self.show_feedback(trial, duration, completed)
```

The `destroy()` calls are critical -- without them, old walls and stars pile up across trials.

### TODO 5 -- Implement `show_feedback()`

Display the trial results:

```python
def show_feedback(self, trial, duration, completed):
    self.state = 'FEEDBACK'
    status = "Complete!" if completed else "Escaped"
    self.feedback_text.text = (
        f"{status}\n"
        f"Condition: {trial['condition']}\n"
        f"Stars: {self.score}/{trial['n_stars']}\n"
        f"Time: {duration:.1f}s\n\n"
        f"Press SPACE to continue"
    )
    self.feedback_text.enabled = True
```

After this, the experiment should be fully functional. Run all 4 trials, then check `experiment_data.csv`.

### TODO 6 (Bonus) -- Variable Fixation Duration

In real experiments, a fixed fixation duration lets participants anticipate the task onset. To prevent this, vary the duration randomly:

```python
delay = random.uniform(0.5, 1.5)
invoke(self.start_task, delay=delay)
```

## Connection to MazeWalker-Py

This exercise is a simplified version of `experiment.py` in the MazeWalker-Py project. The mapping is direct:

| Mini Experiment             | MazeWalker-Py                           |
|-----------------------------|-----------------------------------------|
| `Experiment` class          | `Experiment` class in experiment.py     |
| `self.state`                | `self.state` (same pattern)             |
| `self.trials` list          | Trial list from CSV/config file         |
| `build_room()`              | Maze generation from layout files       |
| `spawn_stars()`             | Goal placement in the maze              |
| `send_trigger()`            | LabJack trigger via hardware driver     |
| `experiment_data.csv`       | Structured data logging with timestamps |
| `show_fixation()`           | ITI / fixation phase with jitter        |
| `invoke(fn, delay=N)`       | Timed state transitions                 |
| `destroy(entity)`           | Scene teardown between trials           |

The key difference: MazeWalker-Py loads trial definitions from configuration files and uses real hardware for triggers. The architecture is the same.

## Hints

**Nothing happens when I press SPACE.** Check that `show_fixation()` does more than `pass`. The `input()` method calls it when SPACE is pressed in the INSTRUCTION state.

**The room does not appear after fixation.** Make sure `start_task()` calls `build_room()` and that `show_fixation()` calls `invoke(self.start_task, delay=1)`.

**Stars from previous trials are still visible.** In `end_task()`, you must destroy both `self.stars` and `self.room_entities` and reset both lists to `[]`.

**CSV file is empty or missing rows.** Make sure `self.csv_file.flush()` is called after `self.csv_writer.writerow()`.

## Builder Bonus Challenges

1. **Practice trial.** Add one practice trial (not logged to CSV) before the real trials begin.
2. **Variable fixation with logging.** Implement TODO 6 and add the fixation duration as an extra CSV column.
3. **Per-frame trajectory logging.** Open a second CSV file and log the player's position every frame during the TASK state.
4. **Timeout.** Add a maximum trial duration (e.g. 30 seconds). Call `end_task(completed=False)` automatically when time runs out.
5. **Counterbalanced order.** Accept a participant ID as a command-line argument and use it to select the trial order.

Next: [Capstone: MazeWalker-Py](/capstone/)
