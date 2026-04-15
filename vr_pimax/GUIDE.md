# Running VR Experiments on Pimax Crystal Super Q LED

Step-by-step guide for running Exercise 5 and Exercise 7 in the Pimax Crystal
Super Q LED headset via SteamVR and `panda3d-openvr`.

---

## Contents

1. [Prerequisites](#1-prerequisites)
2. [Installation](#2-installation)
3. [SteamVR Controller Remapping](#3-steamvr-controller-remapping)
4. [Startup Sequence](#4-startup-sequence-every-session)
5. [Running Exercise 5](#5-running-exercise-5-mini-experiment)
6. [Running Exercise 7](#6-running-exercise-7-maze-explorer)
7. [Output Data Files](#7-output-data-files)
8. [Eye Tracking](#8-eye-tracking)
9. [Performance Settings](#9-performance-settings)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Prerequisites

### Hardware

| Item | Requirement |
|------|-------------|
| Headset | Pimax Crystal Super Q LED |
| Connection | USB (wired, plugged in) |
| PC | Windows 10/11, GPU with DisplayPort or USB-C DP Alt Mode |

### Software

| Software | Version | Where to get |
|----------|---------|--------------|
| Pimax Play | 1.43.9 (your version) | Pimax website |
| SteamVR | latest | Steam → Library → Tools |
| Python | 3.11 | python.org |
| uv | latest | `pip install uv` |

---

## 2. Installation

### Step 1 — Activate the project virtual environment

Open a terminal in the `vr-tutorial` folder and run:

```bash
# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### Step 2 — Install the VR rendering plugin

```bash
pip install panda3d-openvr
```

### Step 3 — Verify the installation

```bash
python -c "import p3openvr; print('panda3d-openvr OK')"
```

You should see `panda3d-openvr OK`.  If you see an import error, check that
your Python version is 3.11 and that the virtual environment is active.

### Step 4 — (Optional) Install pyopenxr for true eye gaze

The experiments run fine without this.  Install it only when you are ready
to upgrade from the HMD-proxy gaze to true per-eye gaze (see §8).

```bash
pip install pyopenxr
```

---

## 3. SteamVR Controller Remapping

The experiments use the **keyboard** for input (WASD to move, SPACE to
advance between states).  You can map your Pimax controller buttons to
these keyboard keys inside SteamVR — no code changes needed.

### Step-by-step

1. Launch SteamVR.
2. In the SteamVR status window, click the **hamburger menu** (≡) →
   **Devices** → **Controller Settings**.
3. Click **Manage Controller Bindings**.
4. Select your controller and click **Edit this Binding**.
5. Map the following:

| Controller input | Keyboard key | Purpose |
|-----------------|--------------|---------|
| Right trigger   | `Space`      | Advance state / start trial |
| Left joystick   | `W A S D`    | Move forward / back / left / right |

6. Click **Save Personal Binding**.

After this, you can run the full experiment with only the headset and
controllers — no keyboard required.

---

## 4. Startup Sequence (every session)

Follow these steps in order before running any experiment script.

```
Step 1 — Connect the Pimax Crystal via USB

Step 2 — Launch Pimax Play 1.43.9
          Wait until the device status shows green / "Ready"

Step 3 — Launch SteamVR  (from inside Pimax Play, or Steam → SteamVR)
          Wait until the SteamVR status window shows all green icons

Step 4 — Put on the headset
          You should see the SteamVR home environment inside the headset

Step 5 — Run your experiment script (see §5 or §6)
          The VR view switches to the experiment automatically
```

> **Important:** Always start SteamVR before running the Python script.
> If the script starts before SteamVR is ready, panda3d-openvr will fall
> back to a regular desktop window and VR rendering will not activate.

---

## 5. Running Exercise 5 (Mini Experiment)

### What the experiment does

A 4-trial star-collection task:

- 2 conditions (easy = 1 star, hard = 3 stars) × 2 repeats, randomised
- State machine: Instruction → Fixation → Task → Feedback → next trial
- Mock EEG trigger codes printed to the terminal at key events

### How to run

```bash
cd vr-tutorial
.venv\Scripts\activate        # Windows
python vr_pimax/ex5_vr.py
```

### In-headset flow

| What you see | Action |
|--------------|--------|
| Instruction screen with trial info | Press SPACE (or controller trigger) |
| Fixation cross `+` for 1 second | Wait |
| Room with yellow stars | WASD to walk, collect all stars by proximity |
| Feedback screen | Press SPACE to continue |
| After 4 trials: completion screen | Press ESC to exit |

### Output

`experiment_data_vr.csv` is saved in the folder where you ran the script.

---

## 6. Running Exercise 7 (Maze Explorer)

### What the experiment does

A 4-trial procedurally generated maze:

- 2 conditions (easy = 4×4 maze, hard = 6×6 maze) × 2 repeats, randomised
- Player position logged every 0.1 s alongside gaze direction
- Maze wall geometry saved for trajectory visualisation

### How to run

```bash
cd vr-tutorial
.venv\Scripts\activate        # Windows
python vr_pimax/ex7_vr.py
```

### In-headset flow

| What you see | Action |
|--------------|--------|
| Instruction screen | Press SPACE (or controller trigger) |
| Fixation cross `+` for 1 second | Wait |
| Maze with a gold star | WASD to navigate; find and approach the star |
| Feedback screen | Press SPACE to continue |
| After 4 trials: completion screen | Press Shift+Q to exit |

### Visualising trajectories after the run

The existing notebook works with the VR data — just update the filename:

1. Open `exercises/ex7_maze_explorer/visualize.ipynb`
2. In the first cell, change `trajectory.csv` to `trajectory_vr.csv`
3. Run all cells

---

## 7. Output Data Files

### Exercise 5 — `experiment_data_vr.csv`

| Column | Description |
|--------|-------------|
| `trial` | Trial number (1-based) |
| `condition` | `easy` or `hard` |
| `n_stars` | Number of stars in this trial |
| `collected` | Stars collected before trial ended |
| `duration_s` | Trial duration in seconds |
| `completed` | 1 = all stars collected, 0 = ESC pressed |
| `gaze_x` | Gaze direction X at trial end |
| `gaze_y` | Gaze direction Y at trial end |
| `gaze_z` | Gaze direction Z at trial end |

### Exercise 7 — `trajectory_vr.csv`

Sampled every 0.1 s during the task, plus one row per star collection.

| Column | Description |
|--------|-------------|
| `trial` | Trial number (1-based) |
| `time_s` | Seconds since trial start |
| `x` | Player X position |
| `z` | Player Z position |
| `event` | Empty for regular samples; `collect` at star collection |
| `gaze_x` | Gaze direction X |
| `gaze_y` | Gaze direction Y |
| `gaze_z` | Gaze direction Z |

### Exercise 7 — `maze_experiment_vr.csv`

One row per trial: condition, maze size, stars collected, duration, completed.

### Exercise 7 — `maze_walls.csv`

Wall positions for the trajectory visualiser notebook (unchanged from
desktop version).

---

## 8. Eye Tracking

### Current state

The scripts record **HMD forward vector** as a gaze proxy.  This gives you
the direction the participant's head is pointing — a useful baseline and
sufficient for many head-referenced analyses.

The CSV columns `gaze_x / gaze_y / gaze_z` are already in place in both
output files.

### Upgrading to true per-eye gaze

When you are ready to integrate the Crystal's built-in eye tracker, there
are two paths.

#### Option A — Pimax PGEE SDK (recommended)

1. Download the Pimax Eye Tracking SDK from the Pimax developer portal.
2. Install it and note the Python package name (typically `PimaxEyeTracker`).
3. In `vr_utils.py`, replace the `EyeTracker.sample()` method:

```python
# Replace the sample() method in EyeTracker with this:
def sample(self) -> tuple[float, float, float]:
    data = self._et.get_gaze_data()
    # data fields depend on SDK version; common names shown below
    return (
        round(data.combined_gaze_x, 4),
        round(data.combined_gaze_y, 4),
        round(data.combined_gaze_z, 4),
    )
```

And in `EyeTracker.__init__()`:

```python
from PimaxEyeTracker import PimaxEyeTracker
self._et = PimaxEyeTracker()
self._et.open()
self._ok = True
```

No changes are needed in `ex5_vr.py` or `ex7_vr.py` — they call
`self.eye.sample()` and will automatically use the real gaze data.

#### Option B — pyopenxr (XR_EXT_eye_gaze_interaction)

Works if SteamVR exposes the eye gaze extension for your device.

```python
import xr

# In EyeTracker.__init__():
self._instance = xr.create_instance(
    xr.InstanceCreateInfo(
        enabled_extension_names=[xr.EXT_EYE_GAZE_INTERACTION_EXTENSION_NAME],
    )
)
self._ok = True

# In EyeTracker.sample():
# Access gaze via xr.locate_space with EyeGazerPoseSPACE
# See pyopenxr documentation for full example
```

---

## 9. Performance Settings

The Crystal Super Q LED has a very high native resolution.  If you see
frame drops or judder, try these settings in order.

### In `vr_utils.py` — lower render scale

```python
# Default is 0.8.  Lower further if needed.
enable_vr(render_scale=0.7)   # or 0.6
```

### In Pimax Play

| Setting | Recommended value |
|---------|------------------|
| Render Quality | Normal (not High or Ultra) |
| Refresh rate | 72 Hz or 90 Hz |
| Smart Smoothing | On (reduces judder if frames drop) |
| FOV | Normal (reduces GPU load vs. Large) |

### In SteamVR

| Setting | Recommended value |
|---------|------------------|
| Render Resolution | Custom → 80% |
| Motion Smoothing | Enabled |

---

## 10. Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| Experiment opens as a desktop window (no VR) | SteamVR not running when script started | Close script, start SteamVR, run again |
| `ImportError: No module named 'p3openvr'` | Plugin not installed | `pip install panda3d-openvr` |
| `[EyeTracker] WARNING: base.openvr not found` | `enable_vr()` not called before `Ursina()` | Check that `enable_vr(...)` is the first line before `app = Ursina()` |
| Black screen inside headset | SteamVR not fully initialised | Wait for all SteamVR icons to turn green, then run the script |
| Very low frame rate / judder | Resolution too high | Lower `render_scale` to 0.7 or reduce Pimax Play Render Quality |
| Player falls through the floor | Gravity not disabled | Confirm `self.player.gravity = 0` is set in `VRPlayer.__init__()` |
| WASD does not move the player | Script not in focus | Click the SteamVR desktop mirror window, or remap WASD to controller stick via SteamVR Input |
| CSV file not saved on crash | Flush not called | Both scripts call `atexit.register(self._flush_all)` — data up to the last completed trial is safe |
| Instruction text invisible in headset | UI rendering issue | Try reducing `Text` scale or repositioning `origin` |
