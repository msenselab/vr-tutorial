"""Exercise 5 — Mini Experiment (solution)

A complete mini-experiment demonstrating:
  - State machine: INSTRUCTION -> FIXATION -> TASK -> FEEDBACK -> next trial
  - Trial sequencing: 2 conditions x 2 repeats, randomized
  - CSV data logging with per-trial metrics
  - Mock EEG trigger codes at key events
  - Scene build-up and teardown between trials
"""

import csv
import time
import random
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

# --- Mock trigger (simulates EEG trigger) ---------------------------------
TRIG_FIXATION = 1
TRIG_TASK_START = 2
TRIG_COLLECT = 3
TRIG_TRIAL_END = 4


def send_trigger(code):
    """Mock trigger — replace with LabJack/serial for real experiments."""
    print(f"  [TRIGGER] code={code} at {time.time():.3f}")


# --- Room building (reused from Exercises 2-3) ----------------------------
def build_room():
    """Create the standard room. Returns list of room entities."""
    entities = []

    floor = Entity(
        model='quad', scale=(20, 20), rotation_x=90,
        color=color.dark_gray, texture='grass', collider='box',
    )
    entities.append(floor)

    # Front wall
    entities.append(Entity(
        model='quad', scale=(20, 5), position=(0, 2.5, 10),
        rotation_y=0, color=color.white, texture='brick', collider='box',
    ))
    # Back wall
    entities.append(Entity(
        model='quad', scale=(20, 5), position=(0, 2.5, -10),
        rotation_y=180, color=color.white, texture='brick', collider='box',
    ))
    # Left wall
    entities.append(Entity(
        model='quad', scale=(20, 5), position=(-10, 2.5, 0),
        rotation_y=-90, color=color.white.tint(-0.05), texture='brick',
        collider='box',
    ))
    # Right wall
    entities.append(Entity(
        model='quad', scale=(20, 5), position=(10, 2.5, 0),
        rotation_y=90, color=color.white.tint(-0.05), texture='brick',
        collider='box',
    ))

    Sky()
    return entities


# --- Star spawning --------------------------------------------------------
STAR_POSITIONS = [Vec3(5, 1, 5), Vec3(-5, 1, -5), Vec3(-3, 1, 7)]


def spawn_stars(n, positions):
    """Spawn n stars at given positions. Returns list of star entities."""
    stars = []
    for i in range(n):
        star = Entity(
            model='sphere', color=color.yellow,
            position=positions[i], scale=0.7,
        )
        stars.append(star)
    return stars


# --- Experiment class -----------------------------------------------------
class Experiment(Entity):
    """State-machine experiment controller.

    States: INSTRUCTION -> FIXATION -> TASK -> FEEDBACK -> (next or DONE)
    """

    def __init__(self):
        super().__init__()

        # Build trial list: 2 conditions x 2 repeats = 4 trials
        self.trials = []
        for _ in range(2):
            self.trials.append({'condition': 'easy', 'n_stars': 1})
            self.trials.append({'condition': 'hard', 'n_stars': 3})
        random.shuffle(self.trials)

        self.current_trial = 0
        self.state = 'INSTRUCTION'
        self.score = 0
        self.stars = []
        self.room_entities = []
        self.trial_start_time = 0

        # CSV logging
        self.csv_file = open('experiment_data.csv', 'w', newline='')
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow([
            'trial', 'condition', 'n_stars', 'collected', 'duration_s',
            'completed',
        ])

        # Player (disabled until task phase)
        self.player = FirstPersonController(enabled=False)
        self.player.gravity = 0
        self.player.cursor.visible = False

        # UI elements
        self.instruction_text = Text(
            text='', origin=(0, 0), scale=2, parent=camera.ui,
        )
        self.fixation_text = Text(
            text='', origin=(0, 0), scale=2, parent=camera.ui,
        )
        self.score_text = Text(
            text='', position=(-0.85, 0.45), scale=2, parent=camera.ui,
        )
        self.feedback_text = Text(
            text='', origin=(0, 0), scale=2, parent=camera.ui,
        )

        # Start the first trial
        self.show_instruction()

    # --- State: INSTRUCTION ---------------------------------------------------

    def show_instruction(self):
        """Display trial info and wait for SPACE."""
        self.state = 'INSTRUCTION'
        trial = self.trials[self.current_trial]
        n = trial['n_stars']
        self.instruction_text.text = (
            f"Trial {self.current_trial + 1} of {len(self.trials)}\n"
            f"Condition: {trial['condition']} "
            f"({n} star{'s' if n > 1 else ''})\n\n"
            f"Press SPACE to start"
        )
        self.player.enabled = False
        mouse.locked = False

    # --- State: FIXATION ------------------------------------------------------

    def show_fixation(self):
        """Show fixation cross for 1 second, then proceed to task."""
        self.state = 'FIXATION'
        self.instruction_text.text = ''
        self.fixation_text.text = '+'
        send_trigger(TRIG_FIXATION)
        invoke(self.start_task, delay=1)

    # --- State: TASK ----------------------------------------------------------

    def start_task(self):
        """Build the room, spawn stars, enable the player."""
        self.state = 'TASK'
        self.fixation_text.text = ''

        # Build room and spawn stars for this trial
        self.room_entities = build_room()
        trial = self.trials[self.current_trial]
        self.stars = spawn_stars(trial['n_stars'],
                                STAR_POSITIONS[:trial['n_stars']])
        self.score = 0

        # Enable player at starting position
        self.player.enabled = True
        self.player.position = Vec3(0, 0, 0)
        self.player.rotation_y = 0
        mouse.locked = True

        # HUD
        self.score_text.text = f"Stars: 0/{trial['n_stars']}"

        # Timing
        self.trial_start_time = time.time()
        send_trigger(TRIG_TASK_START)

    # --- End task (shared by completion and escape) ---------------------------

    def end_task(self, completed):
        """Log data, clean up the scene, and show feedback."""
        duration = time.time() - self.trial_start_time
        trial = self.trials[self.current_trial]

        # Write CSV row
        self.csv_writer.writerow([
            self.current_trial + 1,
            trial['condition'],
            trial['n_stars'],
            self.score,
            f"{duration:.3f}",
            completed,
        ])
        self.csv_file.flush()

        send_trigger(TRIG_TRIAL_END)

        # Destroy room and stars
        for e in self.stars:
            destroy(e)
        for e in self.room_entities:
            destroy(e)
        self.stars = []
        self.room_entities = []

        # Disable player and HUD
        self.player.enabled = False
        self.score_text.text = ''
        mouse.locked = False

        self.show_feedback(trial, duration, completed)

    # --- State: FEEDBACK ------------------------------------------------------

    def show_feedback(self, trial, duration, completed):
        """Display trial results and wait for SPACE."""
        self.state = 'FEEDBACK'
        status = "Complete!" if completed else "Escaped"
        self.feedback_text.text = (
            f"{status}\n"
            f"Condition: {trial['condition']}\n"
            f"Stars: {self.score}/{trial['n_stars']}\n"
            f"Time: {duration:.1f}s\n\n"
            f"Press SPACE to continue"
        )

    # --- Advance to next trial ------------------------------------------------

    def next_trial(self):
        """Move to next trial or end the experiment."""
        self.feedback_text.text = ''
        self.current_trial += 1
        if self.current_trial < len(self.trials):
            self.show_instruction()
        else:
            self.show_done()

    # --- State: DONE ----------------------------------------------------------

    def show_done(self):
        """Display completion message and close the CSV file."""
        self.state = 'DONE'
        self.instruction_text.text = (
            "Experiment complete!\n\n"
            "Data saved to experiment_data.csv\n"
            "Press ESC to exit"
        )
        self.csv_file.close()

    # --- Per-frame logic (TASK state only) ------------------------------------

    def update(self):
        """Check star proximity during the TASK state."""
        if self.state != 'TASK':
            return

        trial = self.trials[self.current_trial]

        for star in self.stars:
            if star.enabled and distance(self.player.position,
                                         star.position) < 2:
                star.enabled = False
                self.score += 1
                self.score_text.text = (
                    f"Stars: {self.score}/{trial['n_stars']}"
                )
                send_trigger(TRIG_COLLECT)

        # All stars collected — trial complete
        if self.score >= trial['n_stars']:
            self.end_task(completed=True)

    # --- Input handling -------------------------------------------------------

    def input(self, key):
        """Handle key presses for state transitions."""
        if key == 'space':
            if self.state == 'INSTRUCTION':
                self.show_fixation()
            elif self.state == 'FEEDBACK':
                self.next_trial()
        elif key == 'escape' and self.state == 'TASK':
            self.end_task(completed=False)


# --- Main -----------------------------------------------------------------
app = Ursina()
experiment = Experiment()
app.run()
