# Exercise 7 — Maze Explorer

## Learning goal

Build a complete first-person maze experiment from scratch. You will:

- Generate random mazes using a depth-first search algorithm
- Build a 3-D maze with walls and a floor using Ursina `Entity` objects
- Implement a multi-state experiment loop (Instruction → Fixation → Task → Feedback)
- Record player position and events to CSV files every 0.1 s
- Visualise trajectories and trial outcomes in a Jupyter notebook

---

## Files in this folder

| File | Purpose |
|------|---------|
| `template.py` | Your starting point — fill in the 6 TODO sections |
| `maze_practice_solution.py` | A complete reference implementation to compare against |
| `visualize.ipynb` | Jupyter notebook that plots trajectories after you run the experiment |

Each run of the experiment creates a timestamped subfolder, e.g.:

```
ex7_maze_explorer/
  run_20260415_143022/
    maze_practice.csv
    trajectory.csv
    maze_walls.csv
```

| File | Contents |
|------|---------|
| `maze_practice.csv` | One row per trial: condition, stars collected, duration |
| `trajectory.csv` | Player position sampled every 0.1 s, plus star-collection events |
| `maze_walls.csv` | Wall geometry for each trial (needed by the notebook) |

This means re-running the experiment never overwrites old data. The notebook always loads the most recent run automatically.

---

## How to run

### Step 1 — Run the experiment

```bash
python template.py
```

A 3-D window opens. Use the controls below to navigate each maze trial.

**Controls:**

| Key | Action |
|-----|--------|
| `WASD` | Move forward / left / back / right |
| Mouse | Look around |
| `SPACE` | Start trial / confirm feedback screen |
| `ESC` | Skip the current trial |
| `Shift + Q` | Quit |

### Step 2 — Visualise results

After at least one trial has been completed, open the notebook:

```bash
jupyter notebook visualize.ipynb
```

Then run all cells (Kernel → Restart & Run All). Two plots are produced:

1. **Top-down maze map** — shows walls, your path, start/end positions, and star collection points for each trial.
2. **Position over time** — x and z coordinates plotted against time, with gold dashed lines marking each star collected.

A `trajectory_plot.png` is also saved in this folder.

---

## Your task — 6 TODOs in `template.py`

Search the file for `TODO` to find each part. Here is a summary:

### TODO 1 — `show_fixation()`

Transition to the FIXATION state: set `self.state`, show a `+` cross, and schedule `start_task` to run after 1 second using `invoke(self.start_task, delay=1)`.

### TODO 2 — `start_task()`

The biggest method. It must:
- Generate a maze with `generate_maze(rows, cols)`
- Build it in 3-D with `build_maze(...)` and log every wall to `maze_walls.csv`
- Place stars in random cells (never the start cell `(0, 0)`)
- Reset the score HUD
- Teleport the player to cell `(0, 0)` and enable mouse lock
- Start the trial timer

### TODO 3 — `_record_traj()`

Write one row to `trajectory.csv` with the trial number, elapsed time, and the player's x/z position.

### TODO 4 — `update()`

Called every frame. Accumulate `time.dt` and call `_record_traj()` every 0.1 s. Spin each active star, check whether the player is within `COLLECT_DIST` of any star, log a collection event, and call `end_task(completed=True)` when all stars are collected.

### TODO 5 — `end_task(completed)`

Write the trial summary row to `maze_practice.csv`, destroy all maze and star entities, disable the player, and call `show_feedback(...)`.

### TODO 6 — `show_feedback(trial, duration, completed)`

Set state to FEEDBACK and display a summary message (Condition, stars collected, time) with a "Press SPACE to continue" prompt.

---

## Key concepts

| Concept | Explanation |
|---------|-------------|
| **Recursive backtracking (DFS)** | The maze generator visits every cell once in a random order, knocking down walls as it goes. The result is always a perfect maze — exactly one path between any two cells. |
| **`h_walls` / `v_walls`** | Two 2-D arrays that track which walls still exist. `h_walls[r][c]` is the horizontal wall *below* row `r` at column `c`. `v_walls[r][c]` is the vertical wall to the *right* of cell `(r, c)`. |
| **`cell_center(r, c, rows, cols)`** | Converts a grid cell `(row, col)` into a world-space `(x, z)` position, centred on the whole maze. |
| **State machine** | The experiment uses a simple string variable `self.state` to track which phase it is in: `'INSTRUCTION'`, `'FIXATION'`, `'TASK'`, `'FEEDBACK'`, `'DONE'`. Each method transitions to the next state. |
| **`invoke(fn, delay=t)`** | Ursina's way of scheduling a function call after `t` seconds without blocking the game loop. |
| **`atexit.register(...)`** | Registers a cleanup function that saves any in-progress data even if the window is closed mid-trial. |

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Stars do not disappear when touched | Make sure `update()` checks `star.enabled` before comparing distance, and sets `star.enabled = False` on collection. |
| `maze_walls.csv not found` in the notebook | You need to complete TODO 2 so `maze_walls.csv` is written. Alternatively, the notebook will skip wall drawing and still show the trajectory. |
| Window freezes on fixation cross | TODO 1 is missing the `invoke(self.start_task, delay=1)` call — without it, the experiment gets stuck waiting. |
| `KeyError` or `IndexError` when accessing trial data | Check that `self.current_trial` is a valid index. It should only be incremented inside `next_trial()`. |
| Maze walls overlap or look wrong | The wall placement maths in `build_maze` is GIVEN and correct. If you see visual glitches, check that you are not accidentally calling `build_maze` more than once per trial. |
| CSV files are empty after running | The files are only flushed on `end_task()` or on exit via `_flush_all()`. Make sure you finish or skip each trial rather than force-quitting the process. |
