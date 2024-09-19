from ursina import *
from ursina.shaders import basic_lighting_shader as bls


class Collect(Entity):
    text = None
    icon = None
    count = 0

    def __init__(self, player, model='sphere', collider='box', **kwargs):
        super().__init__(model=model, collider=collider, **kwargs)

        self.not_collected = True

        self.x = random.randint(-50, 50)
        self.z = random.randint(-50, 50)

        self.color = color.yellow
        self.shader = bls
        self.player = player
        self.check_collision()

    @staticmethod
    def gui():
        Collect.icon = Entity(parent=camera.ui, model="sphere", scale=0.05, color=color.yellow, x=-0.8, shader=bls)
        Collect.text = Text("0", scale=2, x=Collect.icon.x - 0.02, y=0.1)

    def check_collision(self):
        while self.intersects():
            self.x = random.randint(-50, 50)

    def update(self):
        if distance_xz(self, self.player) < 1.5 and self.not_collected:
            self.animate_scale(0.1, duration=1)

            pos = self.screen_position + Vec2(0, 0.45)
            new_collect = Entity(parent=camera.ui, model="sphere", scale=0.05, color=color.yellow, position=pos,
                                 shader=bls, unlit=True)
            new_collect.animate_position(Vec2(-.8, 0), duration=1, curve=curve.linear)
            destroy(new_collect, delay=1)

            self.not_collected = False
            Collect.count += 1
            Collect.text.text = str(Collect.count)

            a = Audio("sounds/coin.mp3", autoplay=False, auto_destroy=True)
            a.play()

            destroy(self)


if __name__ == "__main__":
    from ursina.shaders import lit_with_shadows_shader, basic_lighting_shader as bls

    Entity.default_shader = lit_with_shadows_shader

    from ursina.prefabs.first_person_controller import FirstPersonController

    app = Ursina()

    player = FirstPersonController()


    a = Audio("sounds/footstep.wav", autoplay=False, auto_destroy=False)

    ground = Entity(model='plane', scale=100, texture='white_cube', texture_scale=Vec2(32), collider='box')

    for i in range(100):
        e = Entity(model="cube", y=1)
        e.x = random.randint(-50, 50)
        e.z = random.randint(-50, 50)

    for i in range(10):
        Collect(player=player, y=1)
    Collect.gui()

    DirectionalLight().look_at(Vec3(1, -1, -1))

    Sky()


    def update():
        if held_keys["w"] or held_keys["a"] or held_keys["s"] or held_keys["d"]:
            if not a.playing:
                a.play()
            else:
                a.stop()


    app.run()