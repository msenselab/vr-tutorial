"""
ex7_vr.py — Maze Explorer  (Pimax Crystal VR version)
======================================================
Adapts Exercise 7 for the Pimax Crystal Super Q LED via SteamVR.

VR changes vs desktop version  (search "[VR]" to find every change)
--------------------------------------------------------------------
  [VR-1]  enable_vr() called before Ursina()          activates SteamVR rendering
  [VR-2]  VRPlayer replaces FirstPersonController      WASD only, no mouse look
  [VR-3]  mouse.locked calls removed                  irrelevant in VR
  [VR-4]  EyeTracker added                            gaze sampled every 0.1 s
  [VR-5]  gaze_x/y/z columns in trajectory_vr.csv    matches trajectory sample rate
  [VR-6]  camera_pivot.y line removed                 VR uses real HMD height

State machine (unchanged from desktop)
---------------------------------------
  INSTRUCTION --[SPACE]--> FIXATION --[1 s]--> TASK --[all stars]--> FEEDBACK
                                                  |                       |
                                                  +--[ESC]--> FEEDBACK    +--> next trial / DONE

Controls
--------
  WASD          move
  HMD           look (headset tracking — no mouse needed)
  SPACE         advance state  OR  remap controller trigger in SteamVR Input
  ESC           skip current trial
  Shift+Q       quit

Output files
------------
  maze_experiment_vr.csv   per-trial summary (same as desktop)
  trajectory_vr.csv        position + gaze every 0.1 s during task  [VR-5]
  maze_walls.csv           wall geometry for visualiser (unchanged)

Open  exercises/ex7_maze_explorer/visualize.ipynb  after the run to
plot trajectories — it reads trajectory.csv; update the filename to
trajectory_vr.csv in the first cell.
"""

import atexit
import csv
import time
import random

from ursina import *
from vr_utils import enable_vr, VRPlayer, EyeTracker, VRControllerInput, VRHud   # [VR-1,2,4]

# ---------------------------------------------------------------------------
# Constants  (unchanged)
# ---------------------------------------------------------------------------
CELL         = 4
WALL_HEIGHT  = 5
WALL_THICK   = 0.3
COLLECT_DIST = 2

TRIG_FIXATION   = 1
TRIG_TASK_START = 2
TRIG_COLLECT    = 3
TRIG_TRIAL_END  = 4


def send_trigger(code: int) -> None:
    """Mock EEG trigger — replace with serial/LabJack for real experiments."""
    print(f'  [TRIGGER] code={code}  t={time.time():.3f}')


# ---------------------------------------------------------------------------
# Maze generation — recursive backtracking DFS  (unchanged)
# ---------------------------------------------------------------------------

def generate_maze(rows: int, cols: int):
    """Return interior-wall boolean grids for a randomly carved maze."""
    h_walls = [[True] * cols       for _ in range(rows - 1)]
    v_walls = [[True] * (cols - 1) for _ in range(rows)]
    visited = [[False] * cols      for _ in range(rows)]

    def dfs(r, c):
        visited[r][c] = True
        dirs = [(1, 0, 'S'), (-1, 0, 'N'), (0, 1, 'E'), (0, -1, 'W')]
        random.shuffle(dirs)
        for dr, dc, d in dirs:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc]:
                if   d == 'S': h_walls[r][c]     = False
                elif d == 'N': h_walls[r - 1][c] = False
                elif d == 'E': v_walls[r][c]     = False
                elif d == 'W': v_walls[r][c - 1] = False
                dfs(nr, nc)

    dfs(0, 0)
    return h_walls, v_walls


def cell_center(r, c, rows, cols):
    """World-space (x, z) of cell (r, c) centre."""
    return (
        (c - (cols - 1) / 2.0) * CELL,
        (r - (rows - 1) / 2.0) * CELL,
    )


def center_spawn_cell(rows: int, cols: int) -> tuple[int, int]:
    """Return the cell closest to the geometric center of the maze."""
    best = (0, 0)
    best_dist = float('inf')
    for r in range(rows):
        for c in range(cols):
            x, z = cell_center(r, c, rows, cols)
            dist = x * x + z * z
            if dist < best_dist:
                best_dist = dist
                best = (r, c)
    return best


# ---------------------------------------------------------------------------
# Maze scene builder  (unchanged)
# ---------------------------------------------------------------------------

def build_maze(rows: int, cols: int, h_walls, v_walls):
    """Instantiate Ursina wall entities."""
    entities  = []
    wall_recs = []
    hw = cols * CELL / 2.0
    hh = rows * CELL / 2.0

    def make_wall(x, z, sx, sz):
        e = Entity(
            model='cube',
            position=(x, WALL_HEIGHT / 2, z),
            scale=(sx, WALL_HEIGHT, sz),
            color=color.light_gray,
            texture='white_cube',
            collider='box',
        )
        entities.append(e)
        wall_recs.append((x, z, sx, sz))

    # Outer boundary
    span_x = cols * CELL + WALL_THICK
    span_z = rows * CELL + WALL_THICK
    make_wall( 0,  -hh,  span_x, WALL_THICK)   # north
    make_wall( 0,   hh,  span_x, WALL_THICK)   # south
    make_wall(-hw,   0, WALL_THICK,  span_z)   # west
    make_wall( hw,   0, WALL_THICK,  span_z)   # east

    # Interior horizontal walls
    for r in range(rows - 1):
        wz = (r - (rows - 1) / 2.0 + 0.5) * CELL
        for c in range(cols):
            if h_walls[r][c]:
                wx, _ = cell_center(r, c, rows, cols)
                make_wall(wx, wz, CELL + WALL_THICK, WALL_THICK)

    # Interior vertical walls
    for r in range(rows):
        _, wz = cell_center(r, 0, rows, cols)
        for c in range(cols - 1):
            if v_walls[r][c]:
                wx = (c - (cols - 1) / 2.0 + 0.5) * CELL
                make_wall(wx, wz, WALL_THICK, CELL + WALL_THICK)

    # Floor
    entities.append(Entity(
        model='quad',
        scale=(cols * CELL, rows * CELL),
        rotation_x=90,
        color=color.dark_gray,
        texture='grass',
        collider='box',
    ))

    return entities, wall_recs


# ---------------------------------------------------------------------------
# Experiment controller
# ---------------------------------------------------------------------------

class Experiment(Entity):
    """State machine: INSTRUCTION -> FIXATION -> TASK -> FEEDBACK -> DONE."""

    _TRIAL_DEFS = [
        {'condition': 'easy', 'rows': 4, 'cols': 4, 'n_stars': 1},
        {'condition': 'easy', 'rows': 4, 'cols': 4, 'n_stars': 1},
        {'condition': 'hard', 'rows': 6, 'cols': 6, 'n_stars': 3},
        {'condition': 'hard', 'rows': 6, 'cols': 6, 'n_stars': 3},
    ]

    def __init__(self):
        super().__init__()

        self.trials        = list(self._TRIAL_DEFS)
        random.shuffle(self.trials)
        self.current_trial = 0
        self.state         = 'INSTRUCTION'
        self.score         = 0
        self.stars         = []
        self.room_ents     = []
        self._recording    = False
        self.trial_t0      = 0.0
        self.fixation_t0   = None
        self.fixation_mono_t0 = None
        self._ctrl_available_cached = False
        self._ctrl_next_poll_t = 0.0
        self._ctrl_poll_interval = 0.25
        self._stall_threshold_s = 0.8
        self._stall_clear_after_s = 2.0
        self._stall_msg_until = 0.0
        self._stall_count = 0
        self._last_update_mono = time.perf_counter()

        # [VR-4] Eye tracker
        self.eye  = EyeTracker()
        self.ctrl = VRControllerInput()
        self._ctrl_available_cached = self.ctrl.available

        # CSV files — [VR-5] trajectory has extra gaze columns
        self._exp_file   = open('maze_experiment_vr.csv', 'w', newline='')
        self._traj_file  = open('trajectory_vr.csv',      'w', newline='')
        self._walls_file = open('maze_walls.csv',          'w', newline='')

        self._exp_w   = csv.writer(self._exp_file)
        self._traj_w  = csv.writer(self._traj_file)
        self._walls_w = csv.writer(self._walls_file)

        atexit.register(self._flush_all)

        self._exp_w.writerow([
            'trial', 'condition', 'rows', 'cols',
            'n_stars', 'collected', 'duration_s', 'completed',
        ])
        self._traj_w.writerow([
            'trial', 'time_s', 'x', 'z', 'event',
            'gaze_x', 'gaze_y', 'gaze_z',   # [VR-5]
        ])
        self._walls_w.writerow(['trial', 'x', 'z', 'sx', 'sz'])

        # [VR-2] VRPlayer instead of FirstPersonController.
        # Bumped for maze cell scale (CELL=4) so locomotion feels responsive.
        self.player = VRPlayer(speed=9.0)
        # [VR-6] Removed: self.player.camera_pivot.y = 0.2
        #         In VR the real HMD position sets the camera height.

        # Persistent scene elements
        Sky()
        sun = DirectionalLight(shadows=False)
        sun.look_at(Vec3(1, -1, -1))
        AmbientLight(color=color.rgba(0.3, 0.3, 0.3, 1))

        # HUD — parented to VRHud so text appears in the headset.
        # camera.ui is desktop-only in panda3d-openvr; text must be in 3D scene.
        # Positions are ~10× the camera.ui values because panel_scale=0.06 shrinks
        # the coordinate space (±8 units × 0.06 ≈ ±48 cm at 2 m from HMD).
        self._hud       = VRHud()
        self.msg_text   = Text(text='', origin=(0, 0),         scale=2,   parent=self._hud)
        self.score_text = Text(text='', position=(-8.5, 4.5),  scale=2,   parent=self._hud)
        self.ctrl_text  = Text(text='', position=(-8.5, 3.5),  scale=1.2, parent=self._hud)
        self.warn_text  = Text(text='', position=(-8.5, 2.8),  scale=1.0, color=color.orange, parent=self._hud)

        self.show_instruction()

    # -------------------------------------------------------------------------
    # State: INSTRUCTION
    # -------------------------------------------------------------------------

    def show_instruction(self):
        self.state = 'INSTRUCTION'
        t = self.trials[self.current_trial]
        n = t['n_stars']
        self.msg_text.text = (
            f"Trial {self.current_trial + 1} of {len(self.trials)}\n"
            f"Condition: {t['condition']}  "
            f"({n} star{'s' if n > 1 else ''})\n\n"
            f"WASD — move     HMD — look\n"
            f"ESC — skip trial\n\n"
            f"Press SPACE  (or controller trigger)  to start"
        )
        self.player.enabled = False
        self.ctrl_text.text = f"Controller: {'OK' if self._controller_available(force=True) else 'WAITING'}"
        # [VR-3] mouse.locked = False  <- removed

    def _controller_available(self, force: bool = False) -> bool:
        """Poll controller connection at low frequency to keep frame loop smooth."""
        now = time.perf_counter()
        if force or now >= self._ctrl_next_poll_t:
            self._ctrl_available_cached = self.ctrl.poll_connection()
            self._ctrl_next_poll_t = now + self._ctrl_poll_interval
        return self._ctrl_available_cached

    def _handle_stall(self, frame_gap: float) -> None:
        """Show warning and reduce polling rates after a long-frame stall."""
        self._stall_count += 1
        self._stall_msg_until = time.perf_counter() + self._stall_clear_after_s
        self.warn_text.text = f"Warning: long frame {frame_gap:.2f}s (stall #{self._stall_count})"
        print(
            f"[STALL] gap={frame_gap:.3f}s state={self.state} trial={self.current_trial + 1}"
        )

        # Back off controller polling to reduce pressure during unstable periods.
        self._ctrl_poll_interval = min(1.0, self._ctrl_poll_interval + 0.1)
        try:
            self.ctrl.set_reconnect_interval(max(1.0, self._ctrl_poll_interval * 2.0))
        except Exception:
            pass
        try:
            self.player.set_controller_poll_interval(self._ctrl_poll_interval)
        except Exception:
            pass

    # -------------------------------------------------------------------------
    # State: FIXATION
    # -------------------------------------------------------------------------

    def show_fixation(self):
        self.state         = 'FIXATION'
        self.msg_text.text = '+'
        self.fixation_t0   = time.time()
        self.fixation_mono_t0 = time.perf_counter()
        send_trigger(TRIG_FIXATION)
        # Keep delayed invoke, but update() has a monotonic watchdog fallback.
        invoke(self.start_task, delay=1)

    # -------------------------------------------------------------------------
    # State: TASK
    # -------------------------------------------------------------------------

    def start_task(self):
        # Guard against double entry when invoke() and watchdog fire close together.
        if self.state != 'FIXATION':
            return

        self.state         = 'TASK'
        self.fixation_t0   = None
        self.fixation_mono_t0 = None
        self.msg_text.text = ''

        t = self.trials[self.current_trial]
        rows, cols = t['rows'], t['cols']

        h_walls, v_walls = generate_maze(rows, cols)
        self.room_ents, wall_recs = build_maze(rows, cols, h_walls, v_walls)

        # Log wall geometry for the visualiser
        for (wx, wz, sx, sz) in wall_recs:
            self._walls_w.writerow([self.current_trial + 1, wx, wz, sx, sz])
        self._walls_file.flush()

        # Register walls for locomotion collision blocking.
        self.player.set_collision_rects(wall_recs, radius=0.52)

        # Spawn stars at random non-start cells
        all_cells  = [(r, c) for r in range(rows) for c in range(cols)
                      if (r, c) != (0, 0)]
        star_cells = random.sample(all_cells, t['n_stars'])
        self.stars = []
        for (r, c) in star_cells:
            sx, sz = cell_center(r, c, rows, cols)
            self.stars.append(
                Entity(model='sphere', color=color.gold,
                       position=(sx, 1.0, sz), scale=0.7)
            )

        self.score = 0
        self.score_text.text = f"Stars: 0/{t['n_stars']}"

        # Place player at the maze center-adjacent cell.
        spawn_r, spawn_c = center_spawn_cell(rows, cols)
        px, pz = cell_center(spawn_r, spawn_c, rows, cols)
        self.player.teleport_to(Vec3(px, 1.0, pz))
        self.player.enabled  = True
        self.ctrl_text.text = f"Controller: {'OK' if self._controller_available(force=True) else 'WAITING'}"
        # [VR-3] mouse.locked = True  <- removed; HMD provides look direction
        # [VR-2] rotation_y = 45     <- removed; HMD controls orientation

        self.trial_t0   = time.time()
        self._recording = True
        invoke(self._record_traj, delay=0.1)
        send_trigger(TRIG_TASK_START)

    # -------------------------------------------------------------------------
    # Trajectory + gaze recorder  (runs every 0.1 s during TASK)
    # -------------------------------------------------------------------------

    def _record_traj(self):
        if not self._recording:
            return
        gx, gy, gz = self.eye.sample()   # [VR-4] sample gaze
        self._traj_w.writerow([
            self.current_trial + 1,
            round(time.time() - self.trial_t0, 2),
            round(self.player.position.x, 2),
            round(self.player.position.z, 2),
            '',
            gx, gy, gz,   # [VR-5]
        ])
        invoke(self._record_traj, delay=0.1)

    # -------------------------------------------------------------------------
    # End task
    # -------------------------------------------------------------------------

    def end_task(self, completed: bool):
        self._recording = False
        duration = time.time() - self.trial_t0
        t = self.trials[self.current_trial]

        self._exp_w.writerow([
            self.current_trial + 1, t['condition'],
            t['rows'], t['cols'], t['n_stars'],
            self.score, f'{duration:.3f}', int(completed),
        ])
        self._exp_file.flush()
        self._traj_file.flush()
        send_trigger(TRIG_TRIAL_END)

        for e in self.stars + self.room_ents:
            destroy(e)
        self.stars, self.room_ents = [], []
        self.player.set_collision_rects([], radius=0.52)

        self.player.enabled  = False
        self.score_text.text = ''
        self.ctrl_text.text = f"Controller: {'OK' if self._controller_available(force=True) else 'WAITING'}"
        # [VR-3] mouse.locked = False  <- removed

        self.show_feedback(t, duration, completed)

    # -------------------------------------------------------------------------
    # State: FEEDBACK
    # -------------------------------------------------------------------------

    def show_feedback(self, trial, duration, completed):
        self.state = 'FEEDBACK'
        status     = 'Complete!' if completed else 'Skipped'
        self.msg_text.text = (
            f"{status}\n"
            f"Condition: {trial['condition']}\n"
            f"Stars: {self.score}/{trial['n_stars']}\n"
            f"Time: {duration:.1f} s\n\n"
            f"Press SPACE  (or controller trigger)  to continue"
        )
        self.ctrl_text.text = f"Controller: {'OK' if self._controller_available(force=True) else 'WAITING'}"

    # -------------------------------------------------------------------------
    # Advance to next trial
    # -------------------------------------------------------------------------

    def next_trial(self):
        self.msg_text.text = ''
        self.current_trial += 1
        if self.current_trial < len(self.trials):
            self.show_instruction()
        else:
            self.show_done()

    # -------------------------------------------------------------------------
    # Flush / close all CSV files on exit
    # -------------------------------------------------------------------------

    def _flush_all(self):
        for f in (self._exp_file, self._traj_file, self._walls_file):
            try:
                f.flush()
                f.close()
            except Exception:
                pass

    # -------------------------------------------------------------------------
    # State: DONE
    # -------------------------------------------------------------------------

    def show_done(self):
        self.state = 'DONE'
        self.msg_text.text = (
            "Experiment complete!\n\n"
            "Files saved:\n"
            "  maze_experiment_vr.csv\n"
            "  trajectory_vr.csv  (position + gaze every 0.1 s)\n"
            "  maze_walls.csv\n\n"
            "Open visualize.ipynb to plot trajectories\n"
            "  (update filename to trajectory_vr.csv in cell 1)\n\n"
            "Press Shift+Q to exit"
        )
        for f in (self._exp_file, self._traj_file, self._walls_file):
            try:
                f.close()
            except Exception:
                pass

    # -------------------------------------------------------------------------
    # Per-frame logic
    # -------------------------------------------------------------------------

    def update(self):
        now = time.perf_counter()
        frame_gap = now - self._last_update_mono
        self._last_update_mono = now
        if frame_gap >= self._stall_threshold_s:
            self._handle_stall(frame_gap)
        elif now >= self._stall_msg_until:
            self.warn_text.text = ''

        ctrl_ok = self._controller_available()
        self.ctrl_text.text = f"Controller: {'OK' if ctrl_ok else 'WAITING'}"

        # VR runtimes can occasionally miss delayed invoke callbacks.
        # Watchdog ensures FIXATION always advances to TASK after ~1s.
        if self.state == 'FIXATION' and self.fixation_mono_t0 is not None:
            if (time.perf_counter() - self.fixation_mono_t0) >= 1.1:
                self.start_task()

        # Controller trigger acts as SPACE for state transitions
        if ctrl_ok and self.ctrl.trigger_just_pressed():
            if self.state == 'INSTRUCTION':
                self.show_fixation()
            elif self.state == 'FIXATION':
                # Manual override if timer/invoke is delayed.
                self.start_task()
            elif self.state == 'FEEDBACK':
                self.next_trial()

        if self.state != 'TASK':
            return
        t = self.trials[self.current_trial]
        for star in self.stars:
            if star.enabled and distance(self.player.position, star.position) < COLLECT_DIST:
                star.enabled  = False
                self.score   += 1
                t_s = round(time.time() - self.trial_t0, 2)
                gx, gy, gz = self.eye.sample()   # [VR-4] gaze at collection
                self._traj_w.writerow([
                    self.current_trial + 1, t_s,
                    round(self.player.position.x, 2),
                    round(self.player.position.z, 2),
                    'collect',
                    gx, gy, gz,   # [VR-5]
                ])
                self.score_text.text = f"Stars: {self.score}/{t['n_stars']}"
                send_trigger(TRIG_COLLECT)
        if self.score >= t['n_stars']:
            self.end_task(completed=True)

    # -------------------------------------------------------------------------
    # Input handling
    # -------------------------------------------------------------------------

    def input(self, key):
        if key == 'space':
            if self.state == 'INSTRUCTION':
                self.show_fixation()
            elif self.state == 'FIXATION':
                self.start_task()
            elif self.state == 'FEEDBACK':
                self.next_trial()
        elif key == 'escape' and self.state == 'TASK':
            self.end_task(completed=False)
        elif key == 'q' and held_keys['shift']:
            application.quit()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

enable_vr(render_scale=0.8)   # [VR-1] must be called BEFORE Ursina()
app = Ursina()
experiment = Experiment()
app.run()
