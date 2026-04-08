"""Exercise 5 — Mini Experiment (template)

Your task: complete a state-machine experiment that runs multiple trials,
logs data to CSV, and sends mock EEG triggers.

The experiment flows through these states for each trial:

    INSTRUCTION --[SPACE]--> FIXATION --[1s]--> TASK --[all collected]--> FEEDBACK --[SPACE]--> next
                                                  |--[ESC]--> FEEDBACK (escaped)

Everything marked GIVEN is complete — do NOT change it.
Search for TODO to find the six parts you need to implement.

Run the finished experiment:
    python template.py
"""

import csv
import time
import random
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

# --- Mock trigger (simulates EEG trigger) ---------------------------------
# GIVEN — these constants and function are complete.

TRIG_FIXATION = 1
TRIG_TASK_START = 2
TRIG_COLLECT = 3
TRIG_TRIAL_END = 4


def send_trigger(code):
    """Mock trigger — replace with LabJack/serial for real experiments."""
    print(f"  [TRIGGER] code={code} at {time.time():.3f}")


# --- Room building (reused from Exercises 2-3) ----------------------------
# GIVEN — complete.

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
# GIVEN — complete.

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

    # --- GIVEN: __init__ is complete ------------------------------------------

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

        # UI elements
        self.instruction_text = Text(
            text='', origin=(0, 0), scale=2, parent=camera.ui,
        )
        self.fixation_text = Text(
            text='+', origin=(0, 0), scale=5, parent=camera.ui,
            enabled=False,
        )
        self.score_text = Text(
            text='', position=(-0.85, 0.45), scale=1.5, parent=camera.ui,
            enabled=False,
        )
        self.feedback_text = Text(
            text='', origin=(0, 0), scale=2, parent=camera.ui,
            enabled=False,
        )

        # Start the first trial
        self.show_instruction()

    # --- GIVEN: show_instruction is complete ----------------------------------

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
        self.instruction_text.enabled = True
        self.player.enabled = False
        mouse.locked = False

    # --- TODO 1: Implement show_fixation() ------------------------------------
    # This method transitions from INSTRUCTION to FIXATION.
    #
    # Steps:
    #   1. Set self.state to 'FIXATION'
    #   2. Hide the instruction text:  self.instruction_text.enabled = False
    #   3. Show the fixation cross:    self.fixation_text.enabled = True
    #   4. Send the fixation trigger:  send_trigger(TRIG_FIXATION)
    #   5. After a 1-second delay, call start_task:
    #          invoke(self.start_task, delay=1)
    #
    # The invoke() function is Ursina's way of scheduling a delayed call.

    def show_fixation(self):
        pass  # Replace with your implementation

    # --- TODO 2: Implement start_task() ---------------------------------------
    # This method transitions from FIXATION to TASK.
    #
    # Steps:
    #   1. Set self.state to 'TASK'
    #   2. Hide the fixation cross:  self.fixation_text.enabled = False
    #   3. Build the room:           self.room_entities = build_room()
    #   4. Get current trial info:   trial = self.trials[self.current_trial]
    #   5. Spawn stars for this trial:
    #          self.stars = spawn_stars(trial['n_stars'],
    #                                  STAR_POSITIONS[:trial['n_stars']])
    #   6. Reset score:              self.score = 0
    #   7. Enable and position the player:
    #          self.player.enabled = True
    #          self.player.position = Vec3(0, 0, 0)
    #          self.player.rotation_y = 0
    #          mouse.locked = True
    #   8. Update and show the score HUD:
    #          self.score_text.text = f"Stars: 0/{trial['n_stars']}"
    #          self.score_text.enabled = True
    #   9. Start the timer:          self.trial_start_time = time.time()
    #  10. Send the task trigger:    send_trigger(TRIG_TASK_START)

    def start_task(self):
        pass  # Replace with your implementation

    # --- TODO 3: Implement proximity detection in update() --------------------
    # This runs every frame. Only act when self.state == 'TASK'.
    #
    # Steps:
    #   1. If state is not 'TASK', return immediately
    #   2. Get current trial:  trial = self.trials[self.current_trial]
    #   3. Loop through self.stars — for each star:
    #       - If star.enabled AND distance(self.player.position,
    #                                      star.position) < 2:
    #           a. star.enabled = False
    #           b. self.score += 1
    #           c. Update score_text
    #           d. send_trigger(TRIG_COLLECT)
    #   4. After the loop, check if all stars collected:
    #       if self.score >= trial['n_stars']:
    #           self.end_task(completed=True)
    #
    # This is the same pattern you used in Exercise 4!

    def update(self):
        pass  # Replace with your implementation

    # --- TODO 4: Implement end_task() -----------------------------------------
    # This method is called when the trial ends (all stars collected or ESC).
    #
    # Parameters: completed (bool) — True if all stars found, False if escaped.
    #
    # Steps:
    #   1. Calculate duration:  duration = time.time() - self.trial_start_time
    #   2. Get trial info:      trial = self.trials[self.current_trial]
    #   3. Write a row to CSV:
    #          self.csv_writer.writerow([
    #              self.current_trial + 1,
    #              trial['condition'],
    #              trial['n_stars'],
    #              self.score,
    #              f"{duration:.3f}",
    #              completed,
    #          ])
    #          self.csv_file.flush()
    #   4. Send trial-end trigger:  send_trigger(TRIG_TRIAL_END)
    #   5. Destroy all stars and room entities:
    #          for e in self.stars:
    #              destroy(e)
    #          for e in self.room_entities:
    #              destroy(e)
    #          self.stars = []
    #          self.room_entities = []
    #   6. Disable the player and HUD:
    #          self.player.enabled = False
    #          self.score_text.enabled = False
    #          mouse.locked = False
    #   7. Show feedback:  self.show_feedback(trial, duration, completed)

    def end_task(self, completed):
        pass  # Replace with your implementation

    # --- TODO 5: Implement show_feedback() ------------------------------------
    # Display the trial results and wait for SPACE.
    #
    # Parameters: trial (dict), duration (float), completed (bool)
    #
    # Steps:
    #   1. Set self.state to 'FEEDBACK'
    #   2. Set feedback text — example format:
    #          status = "Complete!" if completed else "Escaped"
    #          self.feedback_text.text = (
    #              f"{status}\n"
    #              f"Condition: {trial['condition']}\n"
    #              f"Stars: {self.score}/{trial['n_stars']}\n"
    #              f"Time: {duration:.1f}s\n\n"
    #              f"Press SPACE to continue"
    #          )
    #   3. Show it:  self.feedback_text.enabled = True

    def show_feedback(self, trial, duration, completed):
        pass  # Replace with your implementation

    # --- GIVEN: next_trial is complete ----------------------------------------

    def next_trial(self):
        """Move to next trial or end the experiment."""
        self.feedback_text.enabled = False
        self.current_trial += 1
        if self.current_trial < len(self.trials):
            self.show_instruction()
        else:
            self.show_done()

    # --- GIVEN: show_done is complete -----------------------------------------

    def show_done(self):
        """Display completion message and close the CSV file."""
        self.state = 'DONE'
        self.instruction_text.text = (
            "Experiment complete!\n\n"
            "Data saved to experiment_data.csv\n"
            "Press ESC to exit"
        )
        self.instruction_text.enabled = True
        self.csv_file.close()

    # --- GIVEN: input is complete ---------------------------------------------

    def input(self, key):
        """Handle key presses for state transitions."""
        if key == 'space':
            if self.state == 'INSTRUCTION':
                self.show_fixation()
            elif self.state == 'FEEDBACK':
                self.next_trial()
        elif key == 'escape' and self.state == 'TASK':
            self.end_task(completed=False)


# --- TODO 6 (Bonus): Variable fixation duration -----------------------------
# In real experiments, the fixation duration varies to prevent anticipation.
#
# Modify show_fixation() to use a random delay:
#     delay = random.uniform(0.5, 1.5)
#     invoke(self.start_task, delay=delay)
#
# You could also log the fixation duration in the CSV by adding it as an
# extra column and storing it in self.fixation_duration before the invoke.


# --- Main -----------------------------------------------------------------
app = Ursina()
experiment = Experiment()
app.run()
