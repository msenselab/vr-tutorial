from ursina import *

app = Ursina()
Entity(model='cube', color=color.orange, texture='white_cube')
EditorCamera()
app.run()
