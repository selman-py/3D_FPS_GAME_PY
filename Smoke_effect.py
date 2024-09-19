from ursina import *
from direct.particles.Particles import Particles
from direct.particles.ParticleEffect import ParticleEffect
from panda3d.core import Filename
from panda3d.core import Point3
from direct.showbase.DirectObject import DirectObject
from direct.particles.ForceGroup import ForceGroup
from panda3d.physics import LinearSourceForce, LinearDistanceForce
from panda3d.core import *
import time
from ursina.shaders import lit_with_shadows_shader as lit
import unreal


class Smoke_effect(Entity):

    def __init__(self, position=Vec3(0, 0, 0), file='effects/Smoke_dust.ptf', life=4, deathtime=25, parent=None, force=None):
        super().__init__(position=position)
        self.stoptime = time.time() + life
        self.effect = ParticleEffect()
        self.effect.loadConfig(file)
        self.life = life
        self.deathtime = deathtime
        self.shader = lit
        self.force = force
        if parent == None:
            self.effect.start(parent=self, renderParent=self)
        else:
            self.effect.start(parent=parent, renderParent=self)
        return

    def update(self):
        if time.time() > self.stoptime:
            self.effect.soft_stop()
            invoke(self.die, delay=self.deathtime)

        return

    def die(self):
        destroy(self)
        return


if __name__ == "__main__":
    from ursina.shaders import basic_lighting_shader, lit_with_shadows_shader as lit

    Entity.default_shader = basic_lighting_shader

    app = Ursina()

    ground = Entity(model="plane", scale=200, texture="grass")

    cannon = Entity(model="cannon")

    ball = Entity(model="sphere", z=-0.5, y=0.75, scale=0.45, color=color.dark_gray)


    def input(key):
        if key == "x up":
            create_explosion(cannon.position)


    def create_explosion(position):
        # https://soundbible.com/909-Cannon.html
        a = Audio("sounds/cannon.wav", autoplay=False, auto_destroy=True)
        a.play()

        fire_ball(cannon.forward * -50 + Vec3(0, 5, 0))
        fire = Smoke_effect(position=position, file=r'effects\fire_sphere.ptf')
        fire.scale_z = 1
        fire.rotation_y = 180
        fire.rotation_x = -11
        fire.y += 0.7
        fire.z -= 0.7

        smoke = Smoke_effect(parent=cannon, position=position, file=r'effects\Smoke_dust.ptf')
        smoke.z += 1
        smoke.y += 1
        smoke.scale = 3
        return


    def fire_ball(final_pos):
        # pre_position = cannon.position
        cannon.shake(duration=0.3, magnitude=10, direction=(0, 0, 1))
        # invoke(setattr(cannon, "position", pre_position), delay=0.3)
        ball.position = Vec3(0, 0.7, 0.5)
        ball.animate_position(final_pos, duration=3, curve=curve.linear)


    EditorCamera()
    Sky(texture="sky_sunset")

    app.enableParticles()
    app.run()
