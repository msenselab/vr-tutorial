"""Maze Practice — 4 trials, no triggers

A simplified version of the maze experiment for practice runs.
  - 4 easy trials, each with 1 star to collect
  - No EEG triggers
  - No block rest screens
  - Player position logged every 0.1 s to trajectory.csv

Controls:
  WASD        move
  Mouse       look around
  ESC         skip current trial
  Shift+Q     quit
"""

import atexit
import csv
import time as pytime
import random
from datetime import datetime
from pathlib import Path
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

_RUN_DIR = Path(__file__).parent / f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
_RUN_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR = _RUN_DIR

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
CELL         = 5
WALL_HEIGHT  = 5
WALL_THICK   = 0.32
COLLECT_DIST = 2

EASY_ROWS, EASY_COLS = 6, 6
HARD_ROWS, HARD_COLS = 6, 6


def make_star(x: float, z: float) -> Entity:
    root = Entity(position=(x, 1.1, z))
    Entity(
        parent=root,
        model='quad',
        texture='white_cube',
        color=color.gold,
        scale=0.9,
        billboard=True,
        double_sided=True,
    )
    Entity(
        parent=root,
        model='quad',
        texture='white_cube',
        color=color.yellow,
        scale=0.55,
        rotation_z=45,
        billboard=True,
        double_sided=True,
    )
    return root


# ---------------------------------------------------------------------------
# Maze generation — recursive backtracking (DFS)
# ---------------------------------------------------------------------------

def generate_maze(rows: int, cols: int):
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
    return (
        (c - (cols - 1) / 2.0) * CELL,
        (r - (rows - 1) / 2.0) * CELL,
    )


def build_maze(rows: int, cols: int, h_walls, v_walls):
    entities  = []
    wall_recs = []
    hw = cols * CELL / 2.0
    hh = rows * CELL / 2.0

    def make_wall(x, z, sx, sz):
        entities.append(Entity(
            model='cube',
            position=(x, WALL_HEIGHT / 2, z),
            scale=(sx, WALL_HEIGHT, sz),
            color=color.light_gray,
            texture='grass',
            collider='box',
        ))
        wall_recs.append((x, z, sx, sz))

    span_x = cols * CELL + WALL_THICK
    span_z = rows * CELL + WALL_THICK
    make_wall( 0,  -hh,  span_x, WALL_THICK)
    make_wall( 0,   hh,  span_x, WALL_THICK)
    make_wall(-hw,   0, WALL_THICK,  span_z)
    make_wall( hw,   0, WALL_THICK,  span_z)

    for r in range(rows - 1):
        wz = (r - (rows - 1) / 2.0 + 0.5) * CELL
        for c in range(cols):
            if h_walls[r][c]:
                wx, _ = cell_center(r, c, rows, cols)
                make_wall(wx, wz, CELL + WALL_THICK, WALL_THICK)

    for r in range(rows):
        _, wz = cell_center(r, 0, rows, cols)
        for c in range(cols - 1):
            if v_walls[r][c]:
                wx = (c - (cols - 1) / 2.0 + 0.5) * CELL
                make_wall(wx, wz, WALL_THICK, CELL + WALL_THICK)

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

class Practice(Entity):
    """State machine: INSTRUCTION -> FIXATION -> TASK -> FEEDBACK -> DONE."""

    @staticmethod
    def _build_trials():
        trials = [
            {'condition': 'easy', 'rows': EASY_ROWS, 'cols': EASY_COLS, 'n_stars': 1},
            {'condition': 'easy', 'rows': EASY_ROWS, 'cols': EASY_COLS, 'n_stars': 1},
            {'condition': 'hard', 'rows': HARD_ROWS, 'cols': HARD_COLS, 'n_stars': 3},
            {'condition': 'hard', 'rows': HARD_ROWS, 'cols': HARD_COLS, 'n_stars': 3},
        ]
        random.shuffle(trials)
        return trials

    def __init__(self):
        super().__init__()

        self.trials        = self._build_trials()
        self.current_trial = 0
        self.state         = 'INSTRUCTION'
        self.score         = 0
        self.stars         = []
        self.room_ents     = []
        self.trial_t0      = 0.0
        self._traj_timer   = 0.0

        # CSV output
        self._exp_file  = open(DATA_DIR / 'maze_practice.csv', 'w', newline='')
        self._traj_file = open(DATA_DIR / 'trajectory.csv',    'w', newline='')
        self._wall_file = open(DATA_DIR / 'maze_walls.csv',    'w', newline='')

        self._exp_w  = csv.writer(self._exp_file)
        self._traj_w = csv.writer(self._traj_file)
        self._wall_w = csv.writer(self._wall_file)

        atexit.register(self._flush_all)

        self._exp_w.writerow([
            'trial', 'condition', 'n_stars', 'collected', 'duration_s', 'completed',
        ])
        self._traj_w.writerow(['trial', 'time_s', 'x', 'z', 'event'])
        self._wall_w.writerow(['trial', 'x', 'z', 'sx', 'sz'])

        # Player
        self.player = FirstPersonController(enabled=False)
        self.player.gravity = 1
        self.player.cursor.visible = False
        self.player.speed = 6
        self.player.mouse_sensitivity = Vec2(60, 60)
        camera.clip_plane_near = 0.005

        Sky()
        AmbientLight(color=color.rgba(1, 1, 1, 1))

        self.msg_text   = Text(text='', origin=(0, 0),          scale=2, parent=camera.ui)
        self.score_text = Text(text='', position=(-0.85, 0.45), scale=2, parent=camera.ui)

        self.show_instruction()

    # ------------------------------------------------------------------
    def show_instruction(self):
        self.state = 'INSTRUCTION'
        t = self.trials[self.current_trial]
        n = t['n_stars']
        self.msg_text.text = (
            f"Practice Trial {self.current_trial + 1} of {len(self.trials)}\n"
            f"Condition: {t['condition']}  ({n} star{'s' if n > 1 else ''})\n\n"
            f"Find all the stars and walk up to them.\n\n"
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
        invoke(self.start_task, delay=1)

    # ------------------------------------------------------------------
    def start_task(self):
        self.state = 'TASK'
        self.msg_text.text = ''

        t = self.trials[self.current_trial]
        rows, cols = t['rows'], t['cols']

        h_walls, v_walls = generate_maze(rows, cols)
        self.room_ents, wall_recs = build_maze(rows, cols, h_walls, v_walls)
        for (wx, wz, sx, sz) in wall_recs:
            self._wall_w.writerow([self.current_trial + 1, wx, wz, sx, sz])

        all_cells  = [(r, c) for r in range(rows) for c in range(cols)
                      if (r, c) != (0, 0)]
        star_cells = random.sample(all_cells, t['n_stars'])
        self.stars = []
        for (r, c) in star_cells:
            sx, sz = cell_center(r, c, rows, cols)
            self.stars.append(make_star(sx, sz))

        self.score = 0
        self.score_text.text = f"Stars: 0/{t['n_stars']}"

        px, pz = cell_center(0, 0, rows, cols)
        self.player.position   = Vec3(px, 2.0, pz)
        self.player.rotation_y = 45
        self.player.enabled    = True
        mouse.locked = True

        self.trial_t0    = pytime.time()
        self._traj_timer = 0.0

    # ------------------------------------------------------------------
    def _record_traj(self):
        self._traj_w.writerow([
            self.current_trial + 1,
            round(pytime.time() - self.trial_t0, 2),
            round(self.player.position.x, 2),
            round(self.player.position.z, 2),
            '',
        ])

    # ------------------------------------------------------------------
    def end_task(self, completed: bool):
        duration = pytime.time() - self.trial_t0
        t = self.trials[self.current_trial]

        self._exp_w.writerow([
            self.current_trial + 1, t['condition'], t['n_stars'],
            self.score, f'{duration:.3f}', int(completed),
        ])
        self._exp_file.flush()
        self._traj_file.flush()
        self._wall_file.flush()

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
        # If quit mid-trial, save a partial row so the data isn't lost
        if self.state == 'TASK':
            try:
                duration = pytime.time() - self.trial_t0
                t = self.trials[self.current_trial]
                self._exp_w.writerow([
                    self.current_trial + 1, t['condition'], t['n_stars'],
                    self.score, f'{duration:.3f}', 0,
                ])
            except Exception:
                pass
        for f in (self._exp_file, self._traj_file, self._wall_file):
            try:
                f.flush()
                f.close()
            except Exception:
                pass

    def show_done(self):
        self.state = 'DONE'
        self.msg_text.text = (
            "Practice complete!\n\n"
            "Files saved:\n"
            "  maze_practice.csv\n"
            "  trajectory.csv\n"
            "  maze_walls.csv\n\n"
            "Press Shift+Q to exit"
        )
        for f in (self._exp_file, self._traj_file, self._wall_file):
            f.close()

    # ------------------------------------------------------------------
    def update(self):
        if self.state != 'TASK':
            return
        # Trajectory recording: accumulate time, write every 0.1 s
        self._traj_timer += time.dt
        if self._traj_timer >= 0.1:
            self._traj_timer -= 0.1
            self._record_traj()
        t = self.trials[self.current_trial]
        player_pos = self.player.position
        for star in self.stars:
            if star.enabled:
                star.rotation_y += 60 * time.dt
            if star.enabled and distance(player_pos, star.position) < COLLECT_DIST:
                star.enabled = False
                self.score  += 1
                t_s = round(pytime.time() - self.trial_t0, 2)
                self._traj_w.writerow([
                    self.current_trial + 1, t_s,
                    round(self.player.position.x, 2),
                    round(self.player.position.z, 2),
                    f"collect_{self.score}",
                ])
                self.score_text.text = f"Stars: {self.score}/{t['n_stars']}"
        if self.score >= t['n_stars']:
            self.end_task(completed=True)

    # ------------------------------------------------------------------
    def input(self, key):
        if key == 'space':
            if self.state == 'INSTRUCTION':
                self.show_fixation()
            elif self.state == 'FEEDBACK':
                self.next_trial()
        elif key == 'left mouse down' and self.state == 'TASK':
            mouse.locked = True
        elif key == 'escape' and self.state == 'TASK':
            self.end_task(completed=False)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
app = Ursina()
practice = Practice()
app.run()
