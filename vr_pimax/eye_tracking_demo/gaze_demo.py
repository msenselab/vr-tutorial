"""
gaze_demo.py - Eye Gaze Recording Demo (Pimax Crystal VR)
==========================================================
Static room with 7 colored target objects for gaze validation.

Controls
--------
  SPACE        start / stop recording
  ESC          quit (data saved automatically on stop)

Output
------
  gaze_YYYYMMDD_HHMMSS.csv
  Columns: time_s, gaze_x, gaze_y, gaze_z, pupil_size_mm, head_x, head_y, head_z

Run gaze_analysis.py after the session to plot trajectories and heatmaps.
"""

import csv
import datetime
import os
import sys
import time

from ursina import *

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vr_utils import EyeTracker, VRHud, VRPlayer, enable_vr  # noqa: E402


TARGETS = [
    {'pos': (0.0, 1.6, 7.0), 'color': color.red, 'label': 'front'},
    {'pos': (5.0, 1.6, 5.0), 'color': color.blue, 'label': 'front-right'},
    {'pos': (-5.0, 1.6, 5.0), 'color': color.green, 'label': 'front-left'},
    {'pos': (7.0, 2.5, 0.0), 'color': color.yellow, 'label': 'right'},
    {'pos': (-7.0, 2.5, 0.0), 'color': color.orange, 'label': 'left'},
    {'pos': (0.0, 4.0, 6.0), 'color': color.cyan, 'label': 'high-front'},
    {'pos': (0.0, 1.6, -7.0), 'color': color.magenta, 'label': 'behind'},
]

SAMPLE_HZ = 90
ROOM_HALF = 10


def _build_scene():
    ents = []
    ents.append(Entity(
        model='quad',
        scale=(ROOM_HALF * 2, ROOM_HALF * 2),
        rotation_x=90,
        color=color.dark_gray,
        texture='grass',
        collider='box',
    ))

    wall_specs = [
        ((0, 2.5, ROOM_HALF), 0),
        ((0, 2.5, -ROOM_HALF), 180),
        ((-ROOM_HALF, 2.5, 0), -90),
        ((ROOM_HALF, 2.5, 0), 90),
    ]
    for pos, ry in wall_specs:
        ents.append(Entity(
            model='quad',
            scale=(ROOM_HALF * 2, 5),
            position=pos,
            rotation_y=ry,
            color=color.white,
            texture='brick',
            collider='box',
        ))

    Sky()
    sun = DirectionalLight(shadows=False)
    sun.look_at(Vec3(1, -1, -1))
    AmbientLight(color=color.rgba(0.35, 0.35, 0.35, 1))

    for t in TARGETS:
        ents.append(Entity(model='sphere', color=t['color'], position=t['pos'], scale=0.55))

    return ents


class GazeDemo(Entity):
    def __init__(self):
        super().__init__()

        self.state = 'IDLE'
        self.eye = EyeTracker()
        self._ents = _build_scene()

        self.player = VRPlayer(speed=7.0)
        self.player.teleport_to(Vec3(0, 1.6, -8))
        self.player.enabled = True

        self._csv_file = None
        self._csv_w = None
        self._t0 = 0.0
        self._n_samples = 0
        self._filename = ''
        self._next_t = 0.0
        self._interval = 1.0 / SAMPLE_HZ

        self._hud = VRHud(distance=2.5, panel_scale=0.06)
        self.msg_text = Text('', origin=(0, 0), scale=2.0, parent=self._hud)
        self.status_text = Text('', position=(-8.5, 4.5), scale=1.2, parent=self._hud)
        self.gaze_text = Text('', position=(-8.5, -4.5), scale=1.0, parent=self._hud)

        self._show_idle()

    def _show_idle(self):
        self.state = 'IDLE'
        self.msg_text.text = (
            'Gaze Recording Demo\n\n'
            'Seven colored spheres surround you.\n'
            'Look at each one in turn.\n\n'
            'Press SPACE to start recording.\n'
            'Press SPACE again to stop and save.\n'
            'Press ESC to quit.'
        )
        self.status_text.text = 'Status: IDLE'
        self.gaze_text.text = ''

    def _start_recording(self):
        if hasattr(self.eye, 'real_gaze_ready') and not self.eye.real_gaze_ready():
            self.msg_text.text = (
                'Real eye tracking is not ready yet.\n\n'
                'Wait until OpenXR session is FOCUSED\n'
                'and eye state is READY.\n\n'
                'Then press SPACE again.'
            )
            self.status_text.text = 'Status: WAITING_FOR_EYE_TRACKING'
            return

        self.state = 'RECORDING'
        ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        out_dir = os.path.dirname(os.path.abspath(__file__))
        self._filename = os.path.join(out_dir, f'gaze_{ts}.csv')
        self._csv_file = open(self._filename, 'w', newline='')
        self._csv_w = csv.writer(self._csv_file)
        self._csv_w.writerow([
            'time_s', 'gaze_x', 'gaze_y', 'gaze_z', 'pupil_size_mm',
            'head_x', 'head_y', 'head_z',
        ])
        self._t0 = time.perf_counter()
        self._n_samples = 0
        self._next_t = self._t0
        self.msg_text.text = ''
        self.status_text.text = 'Recording: ON  [0 samples]'

    def _stop_recording(self):
        self.state = 'DONE'
        if self._csv_file:
            self._csv_file.flush()
            self._csv_file.close()
            self._csv_file = None
        short_name = os.path.basename(self._filename)
        self.msg_text.text = (
            f'Saved {self._n_samples} samples\n\n'
            f'File: {short_name}\n\n'
            'Run gaze_analysis.py to visualize.\n\n'
            'Press ESC to quit.'
        )
        self.status_text.text = f'Done [{self._n_samples} samples]'
        self.gaze_text.text = ''

    def update(self):
        if hasattr(self.eye, '_launch_worker_deferred'):
            self.eye._launch_worker_deferred()

        now = time.perf_counter()
        gx, gy, gz, pupil_mm = self.eye.sample_with_pupil()
        hp = self.player.position

        if hasattr(self.eye, 'real_gaze_ready') and self.state == 'IDLE':
            eye_state = 'READY' if self.eye.real_gaze_ready() else 'NOT_READY'
            self.status_text.text = f'Status: IDLE  Eye:{eye_state}'

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


enable_vr(render_scale=0.8)
app = Ursina()
demo = GazeDemo()
app.run()
