"""
gaze_demo.py — Eye Gaze Recording Demo  (Pimax Crystal VR)
===========================================================
Static room with 7 coloured target objects for gaze validation.

Controls
--------
  SPACE        start / stop recording
  ESC          quit (data saved automatically on stop)

Output
------
PS C:\Users\PC\Documents\GitHub\vr-tutorial\vr_pimax\eye_tracking_demo> & c:/Users/PC/Documents/GitHub/vr-tutorial/.venv/Scripts/python.exe c:/Users/PC/Documents/GitHub/vr-tutorial/vr_pimax/eye_tracking_demo/gaze_demo.py
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
[EyeTracker] Mode: pyopenxr worker launched — waiting for FOCUSED state...
[EyeTracker]   (gaze data will be live once SteamVR session is ready)
:pnmimage:png(warning): iCCP: known incorrect sRGB profile
[EyeWorker] XR_EXT_eye_gaze_interaction not available in this runtime.
[EyeWorker] Make sure SteamVR is running and the headset is connected.
:prc(warning): changing type for ConfigVariable textures-power-2 from enum to string.
Replicating left eye
[VR] Fallback init: P3DOpenVR initialized from Python module.
[VRController] Ready (reusing base.openvr.vr_system).
os: Windows
development mode: True
application successfully started
info: changed aspect ratio: 1.778 -> 1.778
[VRController] Found 2 controller(s): [1, 2]
:display:windisplay(warning): Could not find icon filename textures/ursina.ico
PS C:\Users\PC\Documents\GitHub\vr-tutorial\vr_pimax\eye_tracking_demo> 
  gaze_YYYYMMDD_HHMMSS.csv
  Columns: time_s, gaze_x, gaze_y, gaze_z, pupil_size_mm, head_x, head_y, head_z

Run gaze_analysis.py after the session to plot trajectories and heatmaps.
"""

import csv
import time
import datetime

from ursina import *
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vr_utils import enable_vr, VRPlayer, EyeTracker, VRHud   # noqa: E402

# ---------------------------------------------------------------------------
# Target objects — placed around the room at various angles / heights
# ---------------------------------------------------------------------------

TARGETS = [
    {'pos': ( 0.0, 1.6,  7.0), 'color': color.red,     'label': 'front'},
    {'pos': ( 5.0, 1.6,  5.0), 'color': color.blue,    'label': 'front-right'},
    {'pos': (-5.0, 1.6,  5.0), 'color': color.green,   'label': 'front-left'},
    {'pos': ( 7.0, 2.5,  0.0), 'color': color.yellow,  'label': 'right'},
    {'pos': (-7.0, 2.5,  0.0), 'color': color.orange,  'label': 'left'},
    {'pos': ( 0.0, 4.0,  6.0), 'color': color.cyan,    'label': 'high-front'},
    {'pos': ( 0.0, 1.6, -7.0), 'color': color.magenta, 'label': 'behind'},
]

SAMPLE_HZ = 90          # recording rate (samples/s)
ROOM_HALF = 10          # room half-extent (metres)


def _build_scene():
    ents = []
    # Floor
    ents.append(Entity(
        model='quad', scale=(ROOM_HALF * 2, ROOM_HALF * 2),
        rotation_x=90, color=color.dark_gray, texture='grass', collider='box',
    ))
    # Four walls
    wall_specs = [
        ((0, 2.5,  ROOM_HALF),   0),
        ((0, 2.5, -ROOM_HALF), 180),
        ((-ROOM_HALF, 2.5, 0), -90),
        (( ROOM_HALF, 2.5, 0),  90),
    ]
    for pos, ry in wall_specs:
        ents.append(Entity(
            model='quad', scale=(ROOM_HALF * 2, 5), position=pos,
            rotation_y=ry, color=color.white, texture='brick', collider='box',
        ))
    Sky()
    sun = DirectionalLight(shadows=False)
    sun.look_at(Vec3(1, -1, -1))
    AmbientLight(color=color.rgba(0.35, 0.35, 0.35, 1))

    # Target spheres
    for t in TARGETS:
        e = Entity(model='sphere', color=t['color'],
                   position=t['pos'], scale=0.55)
        ents.append(e)

    return ents


# ---------------------------------------------------------------------------
# Demo controller
# ---------------------------------------------------------------------------

class GazeDemo(Entity):

    def __init__(self):
        super().__init__()

        self.state       = 'IDLE'
        self.eye         = EyeTracker()
        self._ents       = _build_scene()

        # Player spawned 8 m behind the room centre, facing forward
        self.player = VRPlayer(speed=7.0)
        self.player.teleport_to(Vec3(0, 1.6, -8))
        self.player.enabled = True

        # CSV state
        self._csv_file   = None
        self._csv_w      = None
        self._t0         = 0.0
        self._n_samples  = 0
        self._filename   = ''
        self._next_t     = 0.0
        self._interval   = 1.0 / SAMPLE_HZ

        # VR HUD
        self._hud        = VRHud(distance=2.5, panel_scale=0.06)
        self.msg_text    = Text('', origin=(0, 0),        scale=2.0, parent=self._hud)
        self.status_text = Text('', position=(-8.5, 4.5), scale=1.2, parent=self._hud)
        self.gaze_text   = Text('', position=(-8.5, -4.5),scale=1.0, parent=self._hud)

        self._show_idle()

    # ------------------------------------------------------------------

    def _show_idle(self):
        self.state = 'IDLE'
        self.msg_text.text = (
            'Gaze Recording Demo\n\n'
            'Seven coloured spheres surround you.\n'
            'Look at each one in turn.\n\n'
            'Press  SPACE  to start recording.\n'
            'Press  SPACE  again to stop & save.\n'
            'Press  ESC   to quit.'
        )
        self.status_text.text = 'Status: IDLE'
        self.gaze_text.text   = ''

    def _start_recording(self):
        self.state = 'RECORDING'
        ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        # Save next to the script
        out_dir = os.path.dirname(os.path.abspath(__file__))
        self._filename  = os.path.join(out_dir, f'gaze_{ts}.csv')
        self._csv_file  = open(self._filename, 'w', newline='')
        self._csv_w     = csv.writer(self._csv_file)
        self._csv_w.writerow([
            'time_s', 'gaze_x', 'gaze_y', 'gaze_z', 'pupil_size_mm',
            'head_x', 'head_y', 'head_z',
        ])
        self._t0        = time.perf_counter()
        self._n_samples = 0
        self._next_t    = self._t0
        self.msg_text.text    = ''
        self.status_text.text = 'Recording: ON  [0 samples]'

    def _stop_recording(self):
        self.state = 'DONE'
        if self._csv_file:
            self._csv_file.flush()
            self._csv_file.close()
            self._csv_file = None
        short_name = os.path.basename(self._filename)
        self.msg_text.text = (
            f'Saved  {self._n_samples}  samples\n\n'
            f'File:  {short_name}\n\n'
            'Run  gaze_analysis.py  to visualise.\n\n'
            'Press  ESC  to quit.'
        )
        self.status_text.text = f'Done  [{self._n_samples} samples]'
        self.gaze_text.text   = ''

    # ------------------------------------------------------------------

    def update(self):
        now = time.perf_counter()
        gx, gy, gz, pupil_mm = self.eye.sample_with_pupil()
        hp = self.player.position

        # Always show live gaze vector in HUD
        self.gaze_text.text = f'Gaze  {gx:+.3f}  {gy:+.3f}  {gz:+.3f}  Pupil {pupil_mm:.1f}mm'

        if self.state != 'RECORDING':
            return

        if now < self._next_t:
            return

        t_s = round(now - self._t0, 4)
        self._csv_w.writerow([
            t_s,
            round(gx, 5), round(gy, 5), round(gz, 5), round(pupil_mm, 2),
            round(hp.x, 3), round(hp.y, 3), round(hp.z, 3),
        ])
        self._n_samples += 1
        self._next_t += self._interval

        # Update counter display once per second
        if self._n_samples % SAMPLE_HZ == 0:
            self.status_text.text = f'Recording: ON  [{self._n_samples} samples]'

    def input(self, key):
        if key == 'space':
            if self.state == 'IDLE':
                self._start_recording()
            elif self.state == 'RECORDING':
                self._stop_recording()
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
demo = GazeDemo()
app.run()
