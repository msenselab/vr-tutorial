from ursina import *

app = Ursina()
Entity(model='cube', color=color.orange, texture='white_cube')
EditorCamera()

def update():
    speed = 5 * time.dt
    if held_keys['w']: camera.position += camera.forward * speed
    if held_keys['s']: camera.position -= camera.forward * speed
    if held_keys['a']: camera.position -= camera.right * speed
    if held_keys['d']: camera.position += camera.right * speed

app.run()
