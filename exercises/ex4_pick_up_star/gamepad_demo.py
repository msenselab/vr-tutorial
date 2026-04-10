"""
Gamepad Demo: Using pygame joystick alongside Ursina

This script demonstrates how to use pygame for gamepad/joystick input
when Panda3D (Ursina's backend) does not reliably detect controllers
on macOS.

Pattern: pygame polls hardware -> feed values into Ursina player

This is a reference script, not an exercise. Plug in a gamepad and run:

    python gamepad_demo.py

If no gamepad is detected, keyboard + mouse controls still work (WASD).
"""

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import pygame

app = Ursina()

# --- Simple scene for testing movement ------------------------------------
Entity(model='quad', scale=20, rotation_x=90, color=color.dark_gray,
       texture='grass', collider='box')

# Reference objects so you can see yourself moving
for i in range(4):
    Entity(model='cube', position=(i * 3 - 4, 0.5, 5),
           color=color.random_color(), collider='box')

Entity(model='sphere', color=color.gold, position=(0, 1, 8), scale=0.7)

Sky()

# --- Player ----------------------------------------------------------------
player = FirstPersonController()
player.gravity = 0
player.cursor.visible = False
player.position = (0, 1, 0)

# --- Initialize pygame joystick -------------------------------------------
pygame.init()
pygame.joystick.init()
joystick = None

if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    print(f'Gamepad found: {joystick.get_name()}')
else:
    print('No gamepad detected. Use keyboard (WASD + mouse).')

# --- HUD status text -------------------------------------------------------
status = Text(
    text='Gamepad: not connected',
    position=(-0.85, 0.45),
    scale=0.75,
    parent=camera.ui,
)

if joystick:
    status.text = f'Gamepad: {joystick.get_name()}'

# --- Deadzone threshold ----------------------------------------------------
DEADZONE = 0.2


def apply_deadzone(value):
    """Zero out axis values below the deadzone threshold."""
    return 0 if abs(value) < DEADZONE else value


def update():
    """Called every frame. Read gamepad axes and move the player."""
    if joystick is None:
        return

    # Process pygame events (non-blocking — required each frame)
    pygame.event.pump()

    # Left stick: movement (strafe + forward/back)
    lx = apply_deadzone(joystick.get_axis(0))  # left/right
    ly = apply_deadzone(joystick.get_axis(1))  # forward/back

    # Right stick: camera look (yaw + pitch)
    rx = apply_deadzone(joystick.get_axis(2))  # yaw
    ry = apply_deadzone(joystick.get_axis(3))  # pitch

    # Move player relative to facing direction
    speed = 5 * time.dt
    player.position += player.forward * -ly * speed
    player.position += player.right * lx * speed

    # Rotate camera
    look_speed = 2
    player.rotation_y += rx * look_speed
    camera.rotation_x = clamp(camera.rotation_x - ry * look_speed, -90, 90)

    # Update HUD with current axis values
    status.text = f'L:({lx:.1f},{ly:.1f})  R:({rx:.1f},{ry:.1f})'


app.run()
