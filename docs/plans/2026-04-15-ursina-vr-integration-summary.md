# Ursina + VR Device Integration Summary (2026-04-15)

This note summarizes how the project currently connects Ursina with Pimax/SteamVR devices, what has been fixed, and what problems are still open.

## Integration Architecture

Current runtime chain:

Pimax headset -> Pimax Play -> SteamVR runtime -> OpenVR Python binding -> panda3d-openvr -> Panda3D/Ursina app

Files involved:

- `vr_pimax/ex7_vr.py`: VR experiment state machine and data logging
- `vr_pimax/vr_utils.py`: VR initialization, controller input, movement, and gaze proxy
- `pyproject.toml`: Python dependencies (including OpenVR packages)

## Environment and Dependency Decisions

- Python environment is project-local virtualenv: `.venv`
- Correct VR package names are:
  - `panda3d-openvr`
  - `openvr`
- `panda3dopenvr` (no hyphen) is not a valid PyPI distribution name.

## What Was Fixed

1. OpenVR startup no longer relies only on aux-display auto-loading.
- Added fallback initialization in `vr_utils.py`:
  - If `base.openvr` is missing after Ursina starts, initialize `P3DOpenVR()` directly.
- Result: app can initialize VR path even when Panda does not auto-load `p3openvr` module.

2. Controller initialization robustness improved.
- Reuse `base.openvr.vr_system` when available.
- Keep direct `openvr.init(...)` as fallback.
- Added device re-scan for controller reconnect cases.

3. Controller axis selection improved.
- Supports both left and right hands.
- Auto-selects strongest movement axis for non-standard mappings.

4. Keyboard movement fallback added.
- Uses both Ursina `held_keys` and raw Panda key polling.
- Helps when mirror-window focus handling is inconsistent.

5. Fixation-to-task transition robustness added in `ex7_vr.py`.
- Added watchdog fallback in `update()` so FIXATION always advances to TASK after ~1s.

## Current Observed Status

From latest logs:

- VR fallback initialization succeeds (`P3DOpenVR initialized`)
- Two controllers are detected
- Left/right movement axes are selected (`rAxis[0]`)
- No recurring OpenVR interface 105 failure in the latest successful runs

## Current Problems (Open)

1. Locomotion can still appear non-responsive in some runs.
- Symptom: keyboard and/or controller appear connected but character does not move.
- Most likely causes:
  - Input focus mismatch at runtime
  - Axis values near zero despite detected controllers
  - Movement gated by experiment state (movement only active in TASK)

2. Non-blocking warnings still appear.
- `win-size` float-to-int warning
- texture profile (`iCCP`) warning
- missing icon warning (`textures/ursina.ico`)
- `textures-power-2` type warning

These do not currently indicate hard failure of experiment execution.

## Practical Run Checklist

1. Start Pimax Play and ensure headset is ready.
2. Start SteamVR and wait for green status.
3. Run from project venv using absolute interpreter path.
4. In experiment, press SPACE/trigger to pass INSTRUCTION and FIXATION.
5. Test movement only after TASK starts.
6. If no movement:
- Click mirror window once (focus)
- Re-test keyboard WASD
- Re-test both controller sticks

## Recommended Next Debug Step

If movement is still intermittent, add temporary runtime prints for:

- current experiment `state`
- `kb_x/kb_z`
- left and right stick `(x, y)`
- final `dx/dz` after combination

This will isolate whether the issue is input acquisition or movement application.
