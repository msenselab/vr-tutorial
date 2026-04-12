"""Exercise 7 — Maze Explorer (solution)

Procedurally generated maze experiment with trajectory logging:
  - Random maze via recursive backtracking (easy: 5x5, hard: 9x9)
  - State machine: INSTRUCTION -> FIXATION -> TASK -> FEEDBACK -> DONE
  - Player position logged every 0.1 s to trajectory.csv
  - Maze wall geometry saved to maze_walls.csv
  - Open visualize.ipynb after the experiment to plot trajectories

Controls during task:
  WASD        move
  Mouse       look around
  ESC         skip current trial
  Shift+Q     quit
"""

import atexit
import csv
import time
import random
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
CELL         = 4      # world-space units per maze cell
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
# Maze generation — recursive backtracking (DFS)
# ---------------------------------------------------------------------------

def generate_maze(rows: int, cols: int):
    """Return interior-wall boolean grids for a randomly carved maze.

    h_walls[r][c]  True => wall between row r and row r+1 at column c.
    v_walls[r][c]  True => wall between col c and col c+1 at row r.
    """
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


# ---------------------------------------------------------------------------
# Maze scene builder
# ---------------------------------------------------------------------------

def build_maze(rows: int, cols: int, h_walls, v_walls):
    """Instantiate Ursina wall entities.

    Returns:
        entities   -- list of Entity objects (pass to destroy() on teardown)
        wall_recs  -- list of (x, z, sx, sz) for the visualiser CSV
    """
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
    make_wall( 0,  -hh,  span_x, WALL_THICK)  # north
    make_wall( 0,   hh,  span_x, WALL_THICK)  # south
    make_wall(-hw,   0, WALL_THICK,  span_z)  # west
    make_wall( hw,   0, WALL_THICK,  span_z)  # east

    # Interior horizontal walls (east-west segments, between rows)
    for r in range(rows - 1):
        wz = (r - (rows - 1) / 2.0 + 0.5) * CELL
        for c in range(cols):
            if h_walls[r][c]:
                wx, _ = cell_center(r, c, rows, cols)
                make_wall(wx, wz, CELL + WALL_THICK, WALL_THICK)

    # Interior vertical walls (north-south segments, between columns)
    for r in range(rows):
        _, wz = cell_center(r, 0, rows, cols)
        for c in range(cols - 1):
            if v_walls[r][c]:
                wx = (c - (cols - 1) / 2.0 + 0.5) * CELL
                make_wall(wx, wz, WALL_THICK, CELL + WALL_THICK)

    # Floor
    floor = Entity(
        model='quad',
        scale=(cols * CELL, rows * CELL),
        rotation_x=90,
        color=color.dark_gray,
        texture='grass',
        collider='box',
    )
    entities.append(floor)

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

        # Open CSV files
        self._exp_file   = open('maze_experiment.csv', 'w', newline='')
        self._traj_file  = open('trajectory.csv',      'w', newline='')
        self._walls_file = open('maze_walls.csv',      'w', newline='')

        self._exp_w   = csv.writer(self._exp_file)
        self._traj_w  = csv.writer(self._traj_file)
        self._walls_w = csv.writer(self._walls_file)

        atexit.register(self._flush_all)

        self._exp_w.writerow([
            'trial', 'condition', 'rows', 'cols',
            'n_stars', 'collected', 'duration_s', 'completed',
        ])
        self._traj_w.writerow(['trial', 'time_s', 'x', 'z', 'event'])
        self._walls_w.writerow(['trial', 'x', 'z', 'sx', 'sz'])

        # Player (stays disabled until TASK phase)
        self.player = FirstPersonController(enabled=False)
        self.player.gravity = 0
        self.player.cursor.visible = False
        self.player.camera_pivot.y = 0.2   # lower camera height

        # Persistent scene elements
        Sky()
        sun = DirectionalLight()
        sun.look_at(Vec3(1, -1, -1))

        # HUD
        self.msg_text   = Text(text='', origin=(0, 0),          scale=2, parent=camera.ui)
        self.score_text = Text(text='', position=(-0.85, 0.45), scale=2, parent=camera.ui)

        self.show_instruction()

    # ------------------------------------------------------------------
    def show_instruction(self):
        self.state = 'INSTRUCTION'
        t = self.trials[self.current_trial]
        n = t['n_stars']
        self.msg_text.text = (
            f"Trial {self.current_trial + 1} of {len(self.trials)}\n"
            f"Condition: {t['condition']}  "
            f"({n} star{'s' if n > 1 else ''})\n\n"
            f"WASD — move     Mouse — look\n"
            f"ESC — skip trial\n\n"
            f"Press SPACE to start"
        )
        self.player.enabled = False
        mouse.locked = False

    # ------------------------------------------------------------------
    def show_fixation(self):
        self.state = 'FIXATION'
        self.msg_text.text = '+'
        send_trigger(TRIG_FIXATION)
        invoke(self.start_task, delay=1)

    # ------------------------------------------------------------------
    def start_task(self):
        self.state = 'TASK'
        self.msg_text.text = ''

        t = self.trials[self.current_trial]
        rows, cols = t['rows'], t['cols']

        # Generate and build maze
        h_walls, v_walls = generate_maze(rows, cols)
        self.room_ents, wall_recs = build_maze(rows, cols, h_walls, v_walls)

        # Log wall geometry for the visualiser
        for (wx, wz, sx, sz) in wall_recs:
            self._walls_w.writerow([self.current_trial + 1, wx, wz, sx, sz])
        self._walls_file.flush()

        # Spawn stars at random non-start cell centres
        all_cells  = [(r, c) for r in range(rows) for c in range(cols)
                      if (r, c) != (0, 0)]
        star_cells = random.sample(all_cells, t['n_stars'])
        self.stars = []
        for (r, c) in star_cells:
            sx, sz = cell_center(r, c, rows, cols)
            star = Entity(model='sphere', color=color.gold,
                          position=(sx, 1.0, sz), scale=0.7)
            self.stars.append(star)

        self.score = 0
        self.score_text.text = f"Stars: 0/{t['n_stars']}"

        # Place player at cell (0, 0)
        px, pz = cell_center(0, 0, rows, cols)
        self.player.position   = Vec3(px, 1.0, pz)
        self.player.rotation_y = 45
        self.player.enabled    = True
        mouse.locked = True

        self.trial_t0   = time.time()
        self._recording = True
        invoke(self._record_traj, delay=0.1)
        send_trigger(TRIG_TASK_START)

    # ------------------------------------------------------------------
    def _record_traj(self):
        if not self._recording:
            return
        self._traj_w.writerow([
            self.current_trial + 1,
            round(time.time() - self.trial_t0, 2),
            round(self.player.position.x, 2),
            round(self.player.position.z, 2),
            '',
        ])
        invoke(self._record_traj, delay=0.1)

    # ------------------------------------------------------------------
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

        self.player.enabled  = False
        self.score_text.text = ''
        mouse.locked = False

        self.show_feedback(t, duration, completed)

    # ------------------------------------------------------------------
    def show_feedback(self, trial, duration, completed):
        self.state = 'FEEDBACK'
        status = 'Complete!' if completed else 'Skipped'
        self.msg_text.text = (
            f"{status}\n"
            f"Condition: {trial['condition']}\n"
            f"Stars: {self.score}/{trial['n_stars']}\n"
            f"Time: {duration:.1f} s\n\n"
            f"Press SPACE to continue"
        )

    # ------------------------------------------------------------------
    def next_trial(self):
        self.msg_text.text = ''
        self.current_trial += 1
        if self.current_trial < len(self.trials):
            self.show_instruction()
        else:
            self.show_done()

    # ------------------------------------------------------------------
    def _flush_all(self):
        """Flush and close all CSV files — called on exit regardless of state."""
        for f in (self._exp_file, self._traj_file, self._walls_file):
            try:
                f.flush()
                f.close()
            except Exception:
                pass

    def show_done(self):
        self.state = 'DONE'
        self.msg_text.text = (
            "Experiment complete!\n\n"
            "Files saved:\n"
            "  maze_experiment.csv\n"
            "  trajectory.csv\n"
            "  maze_walls.csv\n\n"
            "Open visualize.ipynb to plot trajectories\n"
            "Press Shift+Q to exit"
        )
        for f in (self._exp_file, self._traj_file, self._walls_file):
            f.close()

    # ------------------------------------------------------------------
    def update(self):
        if self.state != 'TASK':
            return
        t = self.trials[self.current_trial]
        for star in self.stars:
            if star.enabled and distance(self.player.position, star.position) < COLLECT_DIST:
                star.enabled = False
                self.score  += 1
                t_s = round(time.time() - self.trial_t0, 2)
                self._traj_w.writerow([
                    self.current_trial + 1, t_s,
                    round(self.player.position.x, 2),
                    round(self.player.position.z, 2),
                    'collect',
                ])
                self.score_text.text = f"Stars: {self.score}/{t['n_stars']}"
                send_trigger(TRIG_COLLECT)
        if self.score >= t['n_stars']:
            self.end_task(completed=True)

    # ------------------------------------------------------------------
    def input(self, key):
        if key == 'space':
            if self.state == 'INSTRUCTION':
                self.show_fixation()
            elif self.state == 'FEEDBACK':
                self.next_trial()
        elif key == 'escape' and self.state == 'TASK':
            self.end_task(completed=False)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
app = Ursina()
experiment = Experiment()
app.run()
