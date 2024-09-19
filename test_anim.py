from ursina import *
from ursina.shaders import basic_lighting_shader
from ursina.prefabs.first_person_controller import FirstPersonController as FPS

Entity.default_shader = basic_lighting_shader




app = Ursina(borderless=False)
Sky()

arena = Entity(model="map8", scale=350, y=-34.5)

bg = Entity(model="quad", parent=camera.ui, texture="Fps_game_bg", scale=(1.5, 1))

ground = Entity(model="plane", scale=300, y=0, texture="grass", color=color.lime)
ground_box = Entity(model="plane", scale=300, y=-1.5, collider="box")

EditorCamera()

app.run()
