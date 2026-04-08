# Exercise 5: Mini Experiment

## Learning goals

- Implement a **state machine** to control experiment flow (the backbone of every experiment program).
- Build a **trial sequence** with conditions, repeats, and randomization.
- **Log data to CSV** at the end of each trial with timing and performance metrics.
- Send **mock EEG trigger codes** at key events (fixation onset, task start, collection, trial end).
- Use `invoke(fn, delay=N)` for timed transitions and `destroy(entity)` for scene cleanup.

## State machine diagram

Each trial cycles through four states. After all trials, the experiment ends.

```
INSTRUCTION --[SPACE]--> FIXATION --[1s]--> TASK --[all collected]--> FEEDBACK --[SPACE]--> next trial
                                              |                                                  |
                                              \------[ESC]------> FEEDBACK (escaped)             |
                                                                                                 v
                                                                                    (after last trial)
                                                                                         DONE
```

The `input()` method listens for SPACE and ESC. The state machine ensures each key press only has an effect in the correct state — pressing SPACE during the TASK state does nothing, for example.

## Key concepts

### State machine pattern

Every psychology experiment is a state machine at its core. Each state defines what the participant sees and what inputs are valid. Transitions between states are triggered by events (key press, timer, task completion). This pattern keeps your code organized: instead of tangled if-else chains, each state has its own method with clear entry conditions and exit actions.

```
State           Entry action                   Exit trigger
-----------     ---------------------------    -------------------------
INSTRUCTION     Show trial info                SPACE pressed
FIXATION        Show "+", send trigger         1-second timer expires
TASK            Build room, enable player       All stars collected / ESC
FEEDBACK        Show results                   SPACE pressed
DONE            Show completion message        ESC quits app
```

### Trial sequencing: conditions x repeats

Experimental designs cross conditions with repetitions. Here we have two conditions (easy = 1 star, hard = 3 stars) repeated twice each, yielding 4 trials. The trial list is built as a flat list of dictionaries and shuffled once at the start:

```python
trials = []
for _ in range(2):  # repeats
    trials.append({'condition': 'easy', 'n_stars': 1})
    trials.append({'condition': 'hard', 'n_stars': 3})
random.shuffle(trials)
```

This is the simplest form of randomization. In a real experiment you might use Latin squares or counterbalancing, but the underlying structure is the same: build a list, shuffle or sort it, iterate through it.

### CSV logging: what to record and when

Log one row per trial at the moment the trial ends (not during). Record everything you need for analysis: trial number, condition, performance, and timing. The CSV is opened once in `__init__`, flushed after each write, and closed in `show_done()`.

```python
self.csv_writer.writerow([
    trial_number, condition, n_stars, collected, duration, completed
])
self.csv_file.flush()  # write to disk immediately — don't lose data on crash
```

Always call `flush()` after writing. If the experiment crashes mid-session, you want every completed trial safely on disk.

### Trigger codes: what they are and why EEG needs them

EEG experiments need to mark the exact moment of key events in the continuous brain signal. A trigger code is a small integer sent to the EEG system via a hardware device (LabJack, parallel port, serial port). The EEG recording software logs the code alongside the brain data, allowing you to time-lock your analysis to specific events.

In this exercise we use a mock function that prints to the console:

```python
def send_trigger(code):
    print(f"  [TRIGGER] code={code} at {time.time():.3f}")
```

For a real experiment, you would replace the print with a hardware call. The trigger code constants stay the same — only the function body changes.

### `invoke(fn, delay=N)` — timed transitions

Ursina's `invoke()` schedules a function call after a delay (in seconds). This is how we implement the fixation period without blocking the main loop:

```python
invoke(self.start_task, delay=1)  # call start_task after 1 second
```

Unlike `time.sleep(1)`, this does not freeze the application. The engine continues rendering frames and processing input while waiting.

### `destroy(entity)` — cleanup between trials

When a trial ends, you must remove its entities from the scene before the next trial creates new ones. The `destroy()` function removes an entity completely:

```python
for e in self.stars:
    destroy(e)
for e in self.room_entities:
    destroy(e)
```

Compare this with `entity.enabled = False` from Exercise 4, which hides but preserves the entity. Here we destroy because each trial builds a fresh scene — there is no need to keep old entities around.

## Step-by-step instructions

Open `template.py` and read through the complete parts first — `__init__`, `show_instruction()`, `show_done()`, `next_trial()`, and `input()`. Understand how the state machine is wired before you start filling in the missing methods.

Run the template as-is to confirm it starts without errors (it will show the instruction screen but nothing will happen when you press SPACE, because the methods are empty).

### TODO 1 — Implement `show_fixation()`

This is the simplest state transition. When SPACE is pressed in the INSTRUCTION state, `input()` calls `show_fixation()`.

Your implementation should:

1. Set `self.state` to `'FIXATION'`.
2. Hide the instruction text.
3. Show the fixation cross (the `+` text element).
4. Send the fixation trigger.
5. Schedule `start_task` to run after 1 second.

```python
def show_fixation(self):
    self.state = 'FIXATION'
    self.instruction_text.enabled = False
    self.fixation_text.enabled = True
    send_trigger(TRIG_FIXATION)
    invoke(self.start_task, delay=1)
```

Run and press SPACE. You should see `+` appear for 1 second. Nothing happens after that yet — the next TODO will fix it.

### TODO 2 — Implement `start_task()`

This is the longest method. It sets up the entire trial scene.

Key steps:
- Set state to `'TASK'` and hide the fixation cross.
- Call `build_room()` and `spawn_stars()` to create the scene.
- Enable the player at the starting position.
- Show the score HUD and start the timer.
- Send the task-start trigger.

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

After this, pressing SPACE should show fixation, then the room appears with stars. You can walk around but cannot collect anything yet.

### TODO 3 — Implement proximity detection in `update()`

This is the same pattern from Exercise 4, adapted for the Experiment class.

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

Now you can collect stars, but the trial will not end properly until TODO 4 is done.

### TODO 4 — Implement `end_task()`

This method does four things: calculate timing, log to CSV, clean up the scene, and show feedback.

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

The `destroy()` calls are critical — without them, old walls and stars pile up across trials.

### TODO 5 — Implement `show_feedback()`

Display the trial results. This is straightforward text formatting.

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

After this, the experiment should be fully functional. Run all 4 trials, then check `experiment_data.csv` in the same folder.

### TODO 6 (Bonus) — Variable fixation duration

In real experiments, a fixed fixation duration lets participants anticipate the task onset, which contaminates EEG signals. To prevent this, vary the duration randomly.

In `show_fixation()`, replace the fixed delay:

```python
delay = random.uniform(0.5, 1.5)
invoke(self.start_task, delay=delay)
```

For extra credit, log the fixation duration in your CSV by adding a column and storing the value before the invoke.

## Connection to MazeWalker-Py

This exercise is a simplified version of `experiment.py` in the MazeWalker-Py project. The mapping is direct:

| Mini Experiment           | MazeWalker-Py                        |
|---------------------------|--------------------------------------|
| `Experiment` class        | `Experiment` class in experiment.py  |
| `self.state`              | `self.state` (same pattern)          |
| `self.trials` list        | Trial list from CSV/config file      |
| `build_room()`            | Maze generation from layout files    |
| `spawn_stars()`           | Goal placement in the maze           |
| `send_trigger()`          | LabJack trigger via hardware driver   |
| `experiment_data.csv`     | Structured data logging with timestamps |
| `show_fixation()`         | ITI / fixation phase with jitter     |
| `invoke(fn, delay=N)`     | Timed state transitions              |
| `destroy(entity)`         | Scene teardown between trials        |

The key difference: MazeWalker-Py loads trial definitions from configuration files and uses real hardware for triggers. The architecture is the same.

## Builder bonus

When the main exercise is complete, try these extensions:

1. **Practice trial.** Add one practice trial (not logged to CSV) before the real trials begin. Use a separate state `'PRACTICE'` or simply skip logging for trial index 0.

2. **Variable fixation with logging.** Implement TODO 6 and add the fixation duration as an extra CSV column. This is essential for EEG analysis — you need to know the exact fixation duration for each trial.

3. **Per-frame trajectory logging.** Open a second CSV file and log the player's position every frame during the TASK state: `trial, time, x, y, z`. This produces movement trajectory data that you can plot after the experiment.

4. **Timeout.** Add a maximum trial duration (e.g. 30 seconds). If the participant has not collected all stars within the time limit, call `end_task(completed=False)` automatically.

5. **Counterbalanced order.** Instead of random shuffle, implement an ABBA or Latin square design. Accept a participant ID as a command-line argument and use it to select the trial order.

## Hints

<details>
<summary>Nothing happens when I press SPACE</summary>

Check that `show_fixation()` does more than `pass`. The `input()` method (already complete) calls `show_fixation()` when SPACE is pressed in the INSTRUCTION state. If the method body is still `pass`, nothing will happen.
</details>

<details>
<summary>The room does not appear after fixation</summary>

Make sure `start_task()` calls `build_room()` and stores the result in `self.room_entities`. Also verify that `show_fixation()` calls `invoke(self.start_task, delay=1)` — if the invoke is missing, `start_task()` never runs.
</details>

<details>
<summary>Stars from previous trials are still visible</summary>

In `end_task()`, you must destroy both the stars and the room entities. Check that you are calling `destroy(e)` in a loop for both `self.stars` and `self.room_entities`, and that you reset the lists to `[]` afterward.
</details>

<details>
<summary>CSV file is empty or missing rows</summary>

Make sure `self.csv_file.flush()` is called after `self.csv_writer.writerow()`. Also check that `end_task()` is actually being called — if `update()` never detects that all stars are collected, the trial never ends.
</details>

<details>
<summary>The experiment crashes after the last trial</summary>

The `show_done()` method calls `self.csv_file.close()`. If you try to write to the CSV after closing it, Python will raise an error. Make sure `end_task()` writes data before `show_done()` is reached (which it should, since `next_trial()` only calls `show_done()` after incrementing the trial counter).
</details>
