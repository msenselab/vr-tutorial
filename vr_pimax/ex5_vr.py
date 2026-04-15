"""
ex5_vr.py — Mini Experiment  (Pimax Crystal VR version)
========================================================
Adapts Exercise 5 for the Pimax Crystal Super Q LED via SteamVR.

VR changes vs desktop version  (search "[VR]" to find every change)
--------------------------------------------------------------------
  [VR-1]  enable_vr() called before Ursina()          activates SteamVR rendering
  [VR-2]  VRPlayer replaces FirstPersonController      WASD only, no mouse look
  [VR-3]  mouse.locked calls removed                  irrelevant in VR
  [VR-4]  EyeTracker added                            gaze columns in CSV
  [VR-5]  gaze sampled at trial end + each collection gaze_x/y/z in output file

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

Output
------
  experiment_data_vr.csv
    trial, condition, n_stars, collected, duration_s, completed,
    gaze_x, gaze_y, gaze_z
    (gaze = HMD forward at trial end; replace with true gaze per GUIDE.md)
"""

import csv
import time
import random

from ursina import *
from vr_utils import enable_vr, VRPlayer, EyeTracker, VRControllerInput   # [VR-1,2,4]

# ---------------------------------------------------------------------------
# Trigger codes (mock — replace send_trigger() with hardware call)
# ---------------------------------------------------------------------------
TRIG_FIXATION   = 1
TRIG_TASK_START = 2
TRIG_COLLECT    = 3
TRIG_TRIAL_END  = 4


def send_trigger(code: int) -> None:
    """Mock trigger — replace body with LabJack/serial for real experiments."""
    print(f"  [TRIGGER] code={code} at {time.time():.3f}")


# ---------------------------------------------------------------------------
# Room builder  (unchanged from desktop)
# ---------------------------------------------------------------------------

def build_room():
    """Create the standard room. Returns list of room entities."""
    entities = []

    entities.append(Entity(
        model='quad', scale=(20, 20), rotation_x=90,
        color=color.dark_gray, texture='grass', collider='box',
    ))

    wall_specs = [
        (( 0,  2.5,  10),   0,    0),
        (( 0,  2.5, -10), 180,    0),
        ((-10, 2.5,   0), -90, -0.05),
        (( 10, 2.5,   0),  90, -0.05),
    ]
    for pos, rot_y, tint in wall_specs:
        entities.append(Entity(
            model='quad', scale=(20, 5), position=pos,
            rotation_y=rot_y, color=color.white.tint(tint),
            texture='brick', collider='box',
        ))

    Sky()
    return entities


# ---------------------------------------------------------------------------
# Star spawner  (unchanged from desktop)
# ---------------------------------------------------------------------------

STAR_POSITIONS = [Vec3(5, 1, 5), Vec3(-5, 1, -5), Vec3(-3, 1, 7)]


def spawn_stars(n: int, positions: list) -> list:
    return [
        Entity(model='sphere', color=color.yellow,
               position=positions[i], scale=0.7)
        for i in range(n)
    ]


# ---------------------------------------------------------------------------
# Experiment controller
# ---------------------------------------------------------------------------

class Experiment(Entity):
    """
    State-machine experiment controller.
    States: INSTRUCTION -> FIXATION -> TASK -> FEEDBACK -> DONE
    """

    def __init__(self):
        super().__init__()

        # Build trial list: 2 conditions x 2 repeats = 4 trials, randomised
        self.trials = []
        for _ in range(2):
            self.trials.append({'condition': 'easy', 'n_stars': 1})
            self.trials.append({'condition': 'hard', 'n_stars': 3})
        random.shuffle(self.trials)

        self.current_trial    = 0
        self.state            = 'INSTRUCTION'
        self.score            = 0
        self.stars            = []
        self.room_entities    = []
        self.trial_start_time = 0.0

        # [VR-4] Eye tracker
        self.eye  = EyeTracker()
        # Controller — shared VRControllerInput (VRPlayer also has one, but
        # we need a second instance here to track trigger edges for the state
        # machine independently of movement).
        self.ctrl = VRControllerInput()

        # CSV logging — [VR-5] gaze columns added at the end
        self.csv_file   = open('experiment_data_vr.csv', 'w', newline='')
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow([
            'trial', 'condition', 'n_stars', 'collected',
            'duration_s', 'completed',
            'gaze_x', 'gaze_y', 'gaze_z',   # [VR-5]
        ])

        # [VR-2] VRPlayer: movement without mouse look
        self.player = VRPlayer(speed=5.0)

        # UI — head-locked 2D overlay (works in VR as screen-space HUD)
        self.instruction_text = Text(text='', origin=(0, 0),          scale=2, parent=camera.ui)
        self.fixation_text    = Text(text='', origin=(0, 0),          scale=2, parent=camera.ui)
        self.score_text       = Text(text='', position=(-0.85, 0.45), scale=2, parent=camera.ui)
        self.feedback_text    = Text(text='', origin=(0, 0),          scale=2, parent=camera.ui)

        self.show_instruction()

    # -------------------------------------------------------------------------
    # State: INSTRUCTION
    # -------------------------------------------------------------------------

    def show_instruction(self):
        self.state = 'INSTRUCTION'
        trial = self.trials[self.current_trial]
        n     = trial['n_stars']
        self.instruction_text.text = (
            f"Trial {self.current_trial + 1} of {len(self.trials)}\n"
            f"Condition: {trial['condition']}  "
            f"({n} star{'s' if n > 1 else ''})\n\n"
            f"Press SPACE  (or controller trigger)  to start"
        )
        self.player.enabled = False
        # [VR-3] mouse.locked = False  <- removed; not relevant in VR

    # -------------------------------------------------------------------------
    # State: FIXATION
    # -------------------------------------------------------------------------

    def show_fixation(self):
        self.state = 'FIXATION'
        self.instruction_text.text = ''
        self.fixation_text.text    = '+'
        send_trigger(TRIG_FIXATION)
        invoke(self.start_task, delay=1)

    # -------------------------------------------------------------------------
    # State: TASK
    # -------------------------------------------------------------------------

    def start_task(self):
        self.state             = 'TASK'
        self.fixation_text.text = ''

        trial              = self.trials[self.current_trial]
        self.room_entities = build_room()
        self.stars         = spawn_stars(trial['n_stars'],
                                         STAR_POSITIONS[:trial['n_stars']])
        self.score         = 0

        self.player.enabled  = True
        self.player.position = Vec3(0, 0, 0)
        # [VR-3] mouse.locked = True  <- removed; HMD provides look direction

        self.score_text.text   = f"Stars: 0/{trial['n_stars']}"
        self.trial_start_time  = time.time()
        send_trigger(TRIG_TASK_START)

    # -------------------------------------------------------------------------
    # End task  (shared by completion and ESC)
    # -------------------------------------------------------------------------

    def end_task(self, completed: bool):
        duration = time.time() - self.trial_start_time
        trial    = self.trials[self.current_trial]
        gx, gy, gz = self.eye.sample()   # [VR-5] gaze at trial end

        self.csv_writer.writerow([
            self.current_trial + 1,
            trial['condition'],
            trial['n_stars'],
            self.score,
            f"{duration:.3f}",
            int(completed),
            gx, gy, gz,     # [VR-5]
        ])
        self.csv_file.flush()
        send_trigger(TRIG_TRIAL_END)

        for e in self.stars + self.room_entities:
            destroy(e)
        self.stars, self.room_entities = [], []

        self.player.enabled  = False
        self.score_text.text = ''
        # [VR-3] mouse.locked = False  <- removed

        self.show_feedback(trial, duration, completed)

    # -------------------------------------------------------------------------
    # State: FEEDBACK
    # -------------------------------------------------------------------------

    def show_feedback(self, trial, duration, completed):
        self.state = 'FEEDBACK'
        status     = "Complete!" if completed else "Escaped"
        self.feedback_text.text = (
            f"{status}\n"
            f"Condition: {trial['condition']}\n"
            f"Stars: {self.score}/{trial['n_stars']}\n"
            f"Time: {duration:.1f} s\n\n"
            f"Press SPACE  (or controller trigger)  to continue"
        )

    # -------------------------------------------------------------------------
    # Advance to next trial
    # -------------------------------------------------------------------------

    def next_trial(self):
        self.feedback_text.text = ''
        self.current_trial += 1
        if self.current_trial < len(self.trials):
            self.show_instruction()
        else:
            self.show_done()

    # -------------------------------------------------------------------------
    # State: DONE
    # -------------------------------------------------------------------------

    def show_done(self):
        self.state = 'DONE'
        self.instruction_text.text = (
            "Experiment complete!\n\n"
            "Data saved to  experiment_data_vr.csv\n"
            "Press ESC to exit"
        )
        self.csv_file.close()

    # -------------------------------------------------------------------------
    # Per-frame logic
    # -------------------------------------------------------------------------

    def update(self):
        # Controller trigger acts as SPACE for state transitions
        if self.ctrl.available and self.ctrl.trigger_just_pressed():
            if self.state == 'INSTRUCTION':
                self.show_fixation()
            elif self.state == 'FEEDBACK':
                self.next_trial()

        if self.state != 'TASK':
            return

        trial = self.trials[self.current_trial]
        for star in self.stars:
            if star.enabled and distance(self.player.position, star.position) < 2:
                star.enabled  = False
                self.score   += 1
                self.score_text.text = f"Stars: {self.score}/{trial['n_stars']}"
                send_trigger(TRIG_COLLECT)

        if self.score >= trial['n_stars']:
            self.end_task(completed=True)

    # -------------------------------------------------------------------------
    # Input handling
    # -------------------------------------------------------------------------

    def input(self, key):
        if key == 'space':
            if self.state == 'INSTRUCTION':
                self.show_fixation()
            elif self.state == 'FEEDBACK':
                self.next_trial()
        elif key == 'escape' and self.state == 'TASK':
            self.end_task(completed=False)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

enable_vr(render_scale=0.8)   # [VR-1] must be called BEFORE Ursina()
app = Ursina()
experiment = Experiment()
app.run()
