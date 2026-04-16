"""
gaze_calibration.py — Eye Tracking Calibration Scene  (Pimax Crystal VR)
=========================================================================
Shows 9 calibration targets in a 3×3 angular grid at fixed distance.
The user looks at each sphere in turn; gaze samples are recorded during
a fixed window per target.

Controls
--------
  SPACE / Trigger   start calibration
  ESC               quit at any time

Output
------
  calib_YYYYMMDD_HHMMSS.csv
  Columns: trial_n, phase, time_s,
           target_yaw_deg, target_pitch_deg,
           target_wx, target_wy, target_wz,
           gaze_x, gaze_y, gaze_z, pupil_mm

Calibration grid (all angles relative to straight-ahead +Z)
------------------------------------------------------------
  Yaw:    -20 °,  0 °, +20 °   (left, centre, right)
  Pitch:  +15 °,  0 °, -15 °   (up, eye-level, down)
  Radius:  5 m
PS C:\Users\PC\Documents\GitHub\vr-tutorial> & c:/Users/PC/Documents/GitHub/vr-tutorial/.venv/Scripts/python.exe c:/Users/PC/Documents/GitHub/vr-tutorial/vr_pimax/eye_tracking_demo/gaze_calibration.py
info: Using primary monitor: Monitor(x=0, y=0, width=2560, height=1440, width_mm=597, height_mm=336, name='\\\\.\\DISPLAY2', is_primary=True)
:prc(warning): Invalid integer value for ConfigVariable win-size: 1152.0
:prc(warning): Invalid integer value for ConfigVariable win-size: 2048.0
Known pipe types:
  wglGraphicsPipe
(4 aux display modules not yet loaded.)
set window position: Vec2(256, 144)
:prc(warning): changing default value for ConfigVariable paste-emit-keystrokes from '1' to '0'.
:pnmimage:png(warning): iCCP: known incorrect sRGB profile
package_folder: C:\Users\PC\Documents\GitHub\vr-tutorial\.venv\Lib\site-packages\ursina
asset_folder: c:\Users\PC\Documents\GitHub\vr-tutorial\vr_pimax\eye_tracking_demo
[EyeTracker] Mode: pyopenxr worker will start after VR init.
:prc(warning): changing type for ConfigVariable textures-power-2 from enum to string.
Replicating left eye
[VR] Fallback init: P3DOpenVR initialized from Python module.
[VRController] Ready (reusing base.openvr.vr_system).
os: Windows
development mode: True
application successfully started
info: changed aspect ratio: 1.778 -> 1.778
[EyeTracker] pyopenxr worker launched.
:display:windisplay(warning): Could not find icon filename textures/ursina.ico
[EyeWorker] Available extensions (16):
  XR_EXT_debug_utils
  XR_EXT_eye_gaze_interaction
  XR_EXT_hand_joints_motion_range
  XR_EXT_hand_tracking
  XR_FB_display_refresh_rate
  XR_KHR_D3D11_enable
  XR_KHR_D3D12_enable
  XR_KHR_composition_layer_depth
  XR_KHR_opengl_enable
  XR_KHR_visibility_mask
  XR_KHR_vulkan_enable
  XR_KHR_vulkan_enable2
  XR_KHR_win32_convert_performance_counter_time
  XR_PIMAX_custom_interface
  XR_VARJO_foveated_rendering
  XR_VARJO_quad_views
[EyeWorker] Using OpenGL session binding.
[EyeWorker] get_system_properties ext chain unavailable; proceeding.
Exception ignored on calling ctypes callback function: <function _create_wgl_context.<locals>.<lambda> at 0x0000018DA8649440>
Traceback (most recent call last):
  File "c:\Users\PC\Documents\GitHub\vr-tutorial\vr_pimax\eye_tracking_demo\..\eye_tracking_demo\eye_worker.py", line 60, in <lambda>
    _wnd_proc = WNDPROC(lambda h, m, w, l: _def(h, m, w, l))
                                           ^^^^^^^^^^^^^^^^
ctypes.ArgumentError: argument 4: OverflowError: int too long to convert
Exception ignored on calling ctypes callback function: <function _create_wgl_context.<locals>.<lambda> at 0x0000018DA8649440>
Traceback (most recent call last):
  File "c:\Users\PC\Documents\GitHub\vr-tutorial\vr_pimax\eye_tracking_demo\..\eye_tracking_demo\eye_worker.py", line 60, in <lambda>
    _wnd_proc = WNDPROC(lambda h, m, w, l: _def(h, m, w, l))
                                           ^^^^^^^^^^^^^^^^
ctypes.ArgumentError: argument 4: OverflowError: int too long to convert
Exception ignored on calling ctypes callback function: <function _create_wgl_context.<locals>.<lambda> at 0x0000018DA8649440>
Traceback (most recent call last):
  File "c:\Users\PC\Documents\GitHub\vr-tutorial\vr_pimax\eye_tracking_demo\..\eye_tracking_demo\eye_worker.py", line 60, in <lambda>
    _wnd_proc = WNDPROC(lambda h, m, w, l: _def(h, m, w, l))
                                           ^^^^^^^^^^^^^^^^
ctypes.ArgumentError: argument 4: OverflowError: int too long to convert
Exception ignored on calling ctypes callback function: <function _create_wgl_context.<locals>.<lambda> at 0x0000018DA8649440>
Traceback (most recent call last):
  File "c:\Users\PC\Documents\GitHub\vr-tutorial\vr_pimax\eye_tracking_demo\..\eye_tracking_demo\eye_worker.py", line 60, in <lambda>
    _wnd_proc = WNDPROC(lambda h, m, w, l: _def(h, m, w, l))
                                           ^^^^^^^^^^^^^^^^
ctypes.ArgumentError: argument 4: OverflowError: int too long to convert
[EyeWorker] Unhandled error: The given graphics device is not in a valid state. The graphics device could be lost or initialized without meeting graphics requirements.
:text(warning): No definition in  for character U+25cf
:text(warning): No definition in  for character U+25cf
:text(warning): No definition in  for character U+25cf
:text(warning): No definition in  for character U+25cf
:text(warning): No definition in  for character U+25cf
:text(warning): No definition in  for character U+25cf
:text(warning): No definition in  for character U+25cf
:text(warning): No definition in  for character U+25cf
:text(warning): No definition in  for character U+25cf
Use analyse_calibration.py (or gaze_analysis.py) to visualise accuracy.
PS C:\Users\PC\Documents\GitHub\vr-tutorial> & c:/Users/PC/Documents/GitHub/vr-tutorial/.venv/Scripts/python.exe c:/Users/PC/Documents/GitHub/vr-tutorial/vr_pimax/eye_tracking_demo/gaze_demo.py
info: Using primary monitor: Monitor(x=0, y=0, width=2560, height=1440, width_mm=597, height_mm=336, name='\\\\.\\DISPLAY2', is_primary=True)
:prc(warning): Invalid integer value for ConfigVariable win-size: 1152.0
:prc(warning): Invalid integer value for ConfigVariable win-size: 2048.0
Known pipe types:
  wglGraphicsPipe
(4 aux display modules not yet loaded.)
set window position: Vec2(256, 144)
:prc(warning): changing default value for ConfigVariable paste-emit-keystrokes from '1' to '0'.
:pnmimage:png(warning): iCCP: known incorrect sRGB profile
package_folder: C:\Users\PC\Documents\GitHub\vr-tutorial\.venv\Lib\site-packages\ursina
asset_folder: c:\Users\PC\Documents\GitHub\vr-tutorial\vr_pimax\eye_tracking_demo
[EyeTracker] Mode: pyopenxr worker will start after VR init.
:pnmimage:png(warning): iCCP: known incorrect sRGB profile
:prc(warning): changing type for ConfigVariable textures-power-2 from enum to string.
Replicating left eye
[VR] Fallback init: P3DOpenVR initialized from Python module.
[VRController] Ready (reusing base.openvr.vr_system).
os: Windows
development mode: True
application successfully started
info: changed aspect ratio: 1.778 -> 1.778
[EyeTracker] pyopenxr worker launched.
[VRController] Found 2 controller(s): [1, 2]
:display:windisplay(warning): Could not find icon filename textures/ursina.ico
[EyeWorker] Available extensions (16):
  XR_EXT_debug_utils
  XR_EXT_eye_gaze_interaction
  XR_EXT_hand_joints_motion_range
  XR_EXT_hand_tracking
  XR_FB_display_refresh_rate
  XR_KHR_D3D11_enable
  XR_KHR_D3D12_enable
  XR_KHR_composition_layer_depth
  XR_KHR_opengl_enable
  XR_KHR_visibility_mask
  XR_KHR_vulkan_enable
  XR_KHR_vulkan_enable2
  XR_KHR_win32_convert_performance_counter_time
  XR_PIMAX_custom_interface
  XR_VARJO_foveated_rendering
  XR_VARJO_quad_views
[EyeWorker] Using OpenGL session binding.
[EyeWorker] get_system_properties ext chain unavailable; proceeding.
Exception ignored on calling ctypes callback function: <function _create_wgl_context.<locals>.<lambda> at 0x0000025F5EF49440>
Traceback (most recent call last):
  File "c:\Users\PC\Documents\GitHub\vr-tutorial\vr_pimax\eye_tracking_demo\..\eye_tracking_demo\eye_worker.py", line 60, in <lambda>
    _wnd_proc = WNDPROC(lambda h, m, w, l: _def(h, m, w, l))
                                           ^^^^^^^^^^^^^^^^
ctypes.ArgumentError: argument 4: OverflowError: int too long to convert
Exception ignored on calling ctypes callback function: <function _create_wgl_context.<locals>.<lambda> at 0x0000025F5EF49440>
Traceback (most recent call last):
  File "c:\Users\PC\Documents\GitHub\vr-tutorial\vr_pimax\eye_tracking_demo\..\eye_tracking_demo\eye_worker.py", line 60, in <lambda>
    _wnd_proc = WNDPROC(lambda h, m, w, l: _def(h, m, w, l))
                                           ^^^^^^^^^^^^^^^^
ctypes.ArgumentError: argument 4: OverflowError: int too long to convert
Exception ignored on calling ctypes callback function: <function _create_wgl_context.<locals>.<lambda> at 0x0000025F5EF49440>
Traceback (most recent call last):
  File "c:\Users\PC\Documents\GitHub\vr-tutorial\vr_pimax\eye_tracking_demo\..\eye_tracking_demo\eye_worker.py", line 60, in <lambda>
    _wnd_proc = WNDPROC(lambda h, m, w, l: _def(h, m, w, l))
                                           ^^^^^^^^^^^^^^^^
ctypes.ArgumentError: argument 4: OverflowError: int too long to convert
Exception ignored on calling ctypes callback function: <function _create_wgl_context.<locals>.<lambda> at 0x0000025F5EF49440>
Traceback (most recent call last):
  File "c:\Users\PC\Documents\GitHub\vr-tutorial\vr_pimax\eye_tracking_demo\..\eye_tracking_demo\eye_worker.py", line 60, in <lambda>
    _wnd_proc = WNDPROC(lambda h, m, w, l: _def(h, m, w, l))
                                           ^^^^^^^^^^^^^^^^
ctypes.ArgumentError: argument 4: OverflowError: int too long to convert
[EyeWorker] Unhandled error: The given graphics device is not in a valid state. The graphics device could be lost or initialized without meeting graphics requirements.
"""

import csv
import datetime
import math
import os
import random
import sys
import time

from ursina import *
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vr_utils import enable_vr, VRPlayer, EyeTracker, VRHud  # noqa: E402

# ---------------------------------------------------------------------------
# Calibration parameters
# ---------------------------------------------------------------------------

CALIB_RADIUS    = 5.0    # metres from player to target sphere
DWELL_DURATION  = 0.6    # seconds: target visible, gaze settles — not recorded
RECORD_DURATION = 1.5    # seconds: gaze recorded to CSV
BLANK_DURATION  = 0.35   # seconds: blank interval between targets
SAMPLE_HZ       = 90     # max recording rate

TARGET_YAWS     = [-20.0,  0.0,  20.0]   # horizontal angles (deg)
TARGET_PITCHES  = [ 15.0,  0.0, -15.0]   # vertical   angles (deg, +up)

PLAYER_EYE_POS  = Vec3(0, 1.6, 0)        # player eye height at origin


def _angle_to_world(origin: Vec3, yaw_deg: float, pitch_deg: float,
                    radius: float) -> Vec3:
    """
    Convert angular offsets from the +Z axis to a world-space point.
    Ursina world: +X right, +Y up, +Z forward.
    """
    yr = math.radians(yaw_deg)
    pr = math.radians(pitch_deg)
    x  = math.sin(yr) * math.cos(pr)
    y  = math.sin(pr)
    z  = math.cos(yr) * math.cos(pr)
    return Vec3(origin.x + x * radius,
                origin.y + y * radius,
                origin.z + z * radius)


def _build_target_list(origin: Vec3) -> list[dict]:
    """Build all 9 targets and randomise their presentation order."""
    targets = []
    for yaw in TARGET_YAWS:
        for pitch in TARGET_PITCHES:
            wp = _angle_to_world(origin, yaw, pitch, CALIB_RADIUS)
            targets.append({'yaw': yaw, 'pitch': pitch, 'world': wp})
    random.shuffle(targets)
    return targets


# ---------------------------------------------------------------------------
# Calibration controller
# ---------------------------------------------------------------------------

class GazeCalibration(Entity):

    INTRO  = 'INTRO'
    DWELL  = 'DWELL'
    RECORD = 'RECORD'
    BLANK  = 'BLANK'
    DONE   = 'DONE'

    def __init__(self):
        super().__init__()

        # Eye tracker — real gaze if pyopenxr worker available, else head proxy
        self.eye = EyeTracker()

        # Player locked at calibration position (no locomotion needed)
        self.player = VRPlayer(speed=0.0)
        self.player.teleport_to(PLAYER_EYE_POS)
        self.player.enabled = False

        self._targets = _build_target_list(PLAYER_EYE_POS)
        self._n       = len(self._targets)
        self._idx     = 0
        self._phase   = self.INTRO
        self._phase_t = 0.0

        # Recording state
        self._csv_file      = None
        self._csv_w         = None
        self._n_samples     = 0
        self._filename      = ''
        self._next_sample_t = 0.0
        self._interval      = 1.0 / SAMPLE_HZ

        # --- 3D scene ---
        # Minimal room: just a floor so the space feels anchored
        Entity(
            model='quad', scale=(30, 30), rotation_x=90,
            color=color.dark_gray, position=(0, 0, 0),
        )
        AmbientLight(color=color.rgba(0.45, 0.45, 0.45, 1))
        sun = DirectionalLight(shadows=False)
        sun.look_at(Vec3(1, -1, 1))

        # Single sphere repositioned per target
        self._sphere = Entity(
            model='sphere', color=color.white,
            scale=0.35, enabled=False,
        )
        # Thin ring around sphere (faces the player) for easier fixation
        self._ring = Entity(
            model='circle', color=color.yellow,
            scale=0.55, enabled=False,
        )
        # Small centre dot
        self._dot = Entity(
            model='sphere', color=color.black,
            scale=0.05, enabled=False,
        )

        # --- VR HUD ---
        self._hud        = VRHud(distance=2.5, panel_scale=0.06)
        self.msg_text    = Text('', origin=(0, 0),         scale=2.0, parent=self._hud)
        self.status_text = Text('', position=(-8.5, 4.5),  scale=1.2, parent=self._hud)
        self.gaze_text   = Text('', position=(-8.5, -4.5), scale=1.0, parent=self._hud)

        self._show_intro()

    # ------------------------------------------------------------------ scene helpers

    def _place_target(self, t: dict):
        wp = t['world']
        self._sphere.position = wp
        self._sphere.enabled  = True
        # Ring and dot face back toward the player
        self._ring.position   = wp
        self._ring.look_at(PLAYER_EYE_POS)
        self._ring.enabled    = True
        self._dot.position    = Vec3(wp.x, wp.y, wp.z)
        self._dot.look_at(PLAYER_EYE_POS)
        self._dot.enabled     = True

    def _hide_target(self):
        self._sphere.enabled = False
        self._ring.enabled   = False
        self._dot.enabled    = False

    # ------------------------------------------------------------------ phase transitions

    def _show_intro(self):
        self._phase = self.INTRO
        self._hide_target()
        self.msg_text.text = (
            'Eye Tracking Calibration\n\n'
            f'{self._n} targets will appear one at a time.\n\n'
            'Keep your HEAD STILL.\n'
            'Move only your EYES to look at\n'
            'each sphere when it appears.\n\n'
            'Green = recording  |  White = settling\n\n'
            'Press  SPACE  to begin.'
        )
        self.status_text.text = 'Status: READY'
        self.gaze_text.text   = ''

    def _start_calibration(self):
        ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        out_dir = os.path.dirname(os.path.abspath(__file__))
        self._filename  = os.path.join(out_dir, f'calib_{ts}.csv')
        self._csv_file  = open(self._filename, 'w', newline='')
        self._csv_w     = csv.writer(self._csv_file)
        self._csv_w.writerow([
            'trial_n', 'phase', 'time_s',
            'target_yaw_deg', 'target_pitch_deg',
            'target_wx', 'target_wy', 'target_wz',
            'gaze_x', 'gaze_y', 'gaze_z', 'pupil_mm',
        ])
        self._n_samples = 0
        self._idx       = 0
        self.msg_text.text = ''
        self._begin_dwell(0)

    def _begin_dwell(self, idx: int):
        t = self._targets[idx]
        self._place_target(t)
        self._sphere.color = color.white   # white = settling
        self._phase   = self.DWELL
        self._phase_t = time.perf_counter()
        self.status_text.text = (
            f'Point  {idx + 1} / {self._n}\n'
            'Look at the sphere...'
        )

    def _begin_record(self):
        self._sphere.color = color.lime    # green = recording
        self._phase   = self.RECORD
        self._phase_t = time.perf_counter()
        self._next_sample_t = self._phase_t
        self.status_text.text = (
            f'Point  {self._idx + 1} / {self._n}\n'
            'Recording  \u25cf'
        )

    def _begin_blank(self):
        self._hide_target()
        self._phase   = self.BLANK
        self._phase_t = time.perf_counter()
        self.status_text.text = ''

    def _finish(self):
        self._phase = self.DONE
        self._hide_target()
        if self._csv_file:
            self._csv_file.flush()
            self._csv_file.close()
            self._csv_file = None
        self.msg_text.text = (
            'Calibration complete!\n\n'
            f'{self._n_samples} samples recorded\n\n'
            f'File: {os.path.basename(self._filename)}\n\n'
            'Press  ESC  to quit.'
        )
        self.status_text.text = f'Done  [{self._n_samples} samples]'
        self.gaze_text.text   = ''

    # ------------------------------------------------------------------ update

    def update(self):
        # Must be called every frame — launches worker after panda3d-openvr is ready
        if hasattr(self.eye, '_launch_worker_deferred'):
            self.eye._launch_worker_deferred()

        now = time.perf_counter()
        gx, gy, gz, pupil_mm = self.eye.sample_with_pupil()

        # Live gaze readout in HUD (shown during calibration, not during intro/done)
        if self._phase not in (self.INTRO, self.DONE):
            self.gaze_text.text = (
                f'Gaze  {gx:+.3f}  {gy:+.3f}  {gz:+.3f}  '
                f'Pupil {pupil_mm:.1f} mm'
            )

        # Gentle pulsing animation on the active sphere
        if self._sphere.enabled:
            pulse = 0.35 + 0.06 * math.sin(now * 5.0)
            self._sphere.scale = pulse

        # --- phase state machine ---
        elapsed = now - self._phase_t

        if self._phase == self.DWELL:
            if elapsed >= DWELL_DURATION:
                self._begin_record()

        elif self._phase == self.RECORD:
            # Record at SAMPLE_HZ
            if now >= self._next_sample_t:
                t  = self._targets[self._idx]
                wp = t['world']
                self._csv_w.writerow([
                    self._idx + 1,
                    'record',
                    round(now, 5),
                    t['yaw'],
                    t['pitch'],
                    round(wp.x, 4), round(wp.y, 4), round(wp.z, 4),
                    round(gx, 5), round(gy, 5), round(gz, 5),
                    round(pupil_mm, 3),
                ])
                self._n_samples    += 1
                self._next_sample_t += self._interval

            if elapsed >= RECORD_DURATION:
                self._idx += 1
                if self._idx >= self._n:
                    self._finish()
                else:
                    self._begin_blank()

        elif self._phase == self.BLANK:
            if elapsed >= BLANK_DURATION:
                self._begin_dwell(self._idx)

    # ------------------------------------------------------------------ input

    def input(self, key):
        if key == 'space' and self._phase == self.INTRO:
            self._start_calibration()
        elif key == 'escape':
            if self._csv_file:
                try:
                    self._csv_file.flush()
                    self._csv_file.close()
                except Exception:
                    pass
            application.quit()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

enable_vr(render_scale=0.8)
app = Ursina()
calib = GazeCalibration()
app.run()
