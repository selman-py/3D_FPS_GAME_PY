from gc import collect
from direct.gui.DirectGuiGlobals import DESTROY
from ursina import *
from ursina.color import clear
from ursina.prefabs.first_person_controller import FirstPersonController
from random import randint
from mermi import *
from direct.actor.Actor import Actor
from ursina.shaders import basic_lighting_shader as bls, colored_lights_shader as cls
from collider_setup import *
from playsound import playsound
from threading import Thread
import time
from ursina.prefabs.ursfx import ursfx
from ursina.prefabs.health_bar import HealthBar
from effects import Effects
from Smoke_effect import Smoke_effect
from particle import *
from Smoke_Particle import *
from collect import *

physics_entities = []
Entity.default_shader = bls

class CustomSky(Entity):
    def __init__(self):
        super().__init__(
            parent=scene,
            model="sphere",
            texture="sunset.hdr",
            double_sided=True,
            scale=3000,
            shader=cls
        )

class Enemy(Entity):
    enemy_list = []

    def __init__(self, move_speed=0.1, collider_speed=1, **kwargs):
        super().__init__(model=None, scale=.7, y=0, collider="box", **kwargs)
        self.actor = Actor("assets/guardian12.glb")
        self.actor.reparentTo(self)
        self.actor.setPlayRate(0.71, 'Walk')
        self.collider = BoxCollider(self, size=(1, 3, 1))
        self.shader = cls
        self.health_bar = Entity(parent=self, y=2, model='cube',color=color.green,  world_scale=(.7, .1, .1))
        self.max_hp = 100
        self.hp = self.max_hp
        self.speed = move_speed
        self.collider_speed = collider_speed
        Enemy.enemy_list.append(self)

    def update(self):
        dist = distance_xz(self, player)

        if dist < 0.8:
            self.speed = 0

        elif dist <= 2:
            print_on_screen("BUSTED")
            if self.actor.getCurrentAnim() == None:
                self.actor.play("attack")

        elif dist > 2:
            if self.actor.getCurrentAnim() == None:
                self.actor.play("Walk")
                self.speed = 4

        elif dist > 1:
            self.speed = 4

        self.look_at_2d(player.position, 'y')
        hit_info = raycast(self.world_position + Vec3(0, 1, 0), self.forward, 30, ignore=(self,))
        if hit_info.entity == player:
            if dist > 2:
                self.position += self.forward * time.dt * 5
        self.position += self.forward * time.dt * self.speed

        for enemy in Enemy.enemy_list:
            if enemy == self:
                continue

            if distance_xz(self, enemy) < 1:
                self.position -= self.forward * time.dt * self.collider_speed

        for b in Mermi.ball_list:
            if distance(b, self) < 1:
                self.hit_enemy()
                Mermi.ball_list.remove(b)
                destroy(b)
                break

        for b in physics_entities:
            if b not in physics_entities:
                continue

            # Prevent damage from Smoke
            if hasattr(b, 'smoke_effect') and b.smoke_effect:
                continue

            if distance(b, self) < 2:
                invoke(self.hit_enemy, delay=1.7)

        self.rotation_y += 180

    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, value):
        self._hp = value
        if value <= 0:
            return
        self.health_bar.world_scale_x = self.hp / self.max_hp * 1.5
        self.health_bar.world_scale_x /= 1.5
        self.health_bar.alpha = 1

    def hit_enemy(self):
        self.hp -= 10
        if self.hp < 75:
            self.health_bar.color = color.orange
        if self.hp <= 0:
            self.z = -25


class Collect(Entity):
    text = None
    icon = None
    count = 0

    def __init__(self, player, model='bomba', collider='box', **kwargs):
        super().__init__(model=model, collider=collider, **kwargs)

        self.not_collected = True

        self.x = random.randint(-50, 50)
        self.y = 0.1
        self.z = random.randint(-50, 50)

        self.color = color.yellow
        self.shader = bls
        self.player = player
        self.check_collision()

    @staticmethod
    def gui():
        Collect.icon = Entity(parent=camera.ui, model="bomba", scale=0.5, color=color.yellow,y=0.2, x=-0.7, shader=bls)
        Collect.text = Text(str(Collect.count), scale=2, x=Collect.icon.x - 0.02, y=0.1)

    def check_collision(self):
        while self.intersects():
            self.x = random.randint(-50, 50)

    def update(self):
        if distance_xz(self, self.player) < 1.5 and self.not_collected:
            self.animate_scale(0.1, duration=1)

            pos = self.screen_position + Vec2(0, 0.45)
            new_collect = Entity(parent=camera.ui, model="bomba", scale=0.05, color=color.yellow, position=pos,
                                 shader=bls, unlit=True)
            new_collect.animate_position(Vec2(-.8, 0), duration=1, curve=curve.linear)
            destroy(new_collect, delay=1)

            self.not_collected = False
            Collect.count += 1
            Collect.text.text = str(Collect.count)

            a = Audio("sounds/collect.mp3", autoplay=False, auto_destroy=True)
            a.play()

            destroy(self)


class PhysicsEntity(Entity):
    def __init__(self, model='bomba', collider='box', **kwargs):
        super().__init__(model=model, **kwargs)
        self.velocity = Vec3(1, 0, 0)
        physics_entities.append(self)

    def update(self):
        if self.intersects():
            self.stop()
            return

        self.velocity = lerp(self.velocity, Vec3(0), time.dt)
        self.velocity += Vec3(0, -1, 0) * time.dt * 5
        self.position += (self.velocity + Vec3(0, -1, 0)) * time.dt

    def stop(self):
        self.velocity = Vec3(0, 0, 0)

    def throw(self, direction, force):
        self.velocity = direction * force


def play_sound_with_delay(sound_file, delay):
    time.sleep(delay)
    playsound(sound_file)


def input(key):
    global selected_weapon

    if  key == '1':
        a = Audio("sounds/glock_pull_sound.mp3", autoplay=False, auto_destroy=False)
        a.play()
        selected_weapon = 'gun'
        gun.visible = True
        Smoke.visible = False
        bomba.visible = False
        scope_gun.visible = False
        camera.fov = 90

    elif selected_weapon == 'scope_gun' and key == 'right mouse down':
        a = Audio("sounds/Scope_zoom.mp3", autoplay=False, auto_destroy=False)
        a.play()
        selected_weapon = 'gun'
        gun.visible = True
        Smoke.visible = False
        bomba.visible = False
        scope_gun.visible = False
        camera.fov = 90

    elif gun.visible == True and key == "right mouse down":
        a = Audio("sounds/Scope_zoom.mp3", autoplay=False, auto_destroy=False)
        a.play()
        selected_weapon = 'scope_gun'
        gun.visible = False
        bomba.visible = False
        Smoke.visible = False
        scope_gun.visible = True
        camera.fov = 50

    elif key == '2':
        a = Audio("sounds/Bomba_pini.mp3", autoplay=False, auto_destroy=False)
        a.play()
        selected_weapon = 'bomba'
        bomba.visible = True
        gun.visible = False
        Smoke.visible = False
        scope_gun.visible = False
        camera.fov = 90

    elif key == '3':
        a = Audio("sounds/Bomba_pini.mp3", autoplay=False, auto_destroy=True)
        a.play()
        selected_weapon = 'Smoke'
        bomba.visible = False
        gun.visible = False
        Smoke.visible = True
        scope_gun.visible = False
        camera.fov = 90

    if key == 'left mouse down':
        if selected_weapon == 'gun':
            shoot_gun()
        elif selected_weapon == 'scope_gun':
            shoot_Scope()
        elif selected_weapon == 'bomba' and Collect.count != 0:
            Collect.count -= 1
            e = PhysicsEntity(model='bomba', velocity=Vec3(0), scale=1,
                              position=player.position + Vec3(0, 1.5, 0) + player.forward, collider='box')
            e.velocity = (camera.forward + Vec3(0, .5, 0)) * 15
            invoke(Particle.move, e, delay=2)
            invoke(generate_particle, e, delay=2)

        elif selected_weapon == 'Smoke':
            e = PhysicsEntity(model='Smoke', velocity=Vec3(0), scale=1,
                              position=player.position + Vec3(0, 1.5, 0) + player.forward, collider='box')
            e.velocity = (camera.forward + Vec3(0, .5, 0)) * 15
            e.smoke_effect = True  # This ensures it's smoke and not damaging
            invoke(Particle_Smoke.move, e, delay=0.5)
            invoke(generate_Smoke_particle, e, delay=0.5)
            destroy(e, delay=10)

def generate_particle(entity):
    if selected_weapon == 'bomba':
        p = Effects(parent=entity, position=entity.position, file=r'effects\dust.ptf')
        p.scale = 3
        a = Audio("sounds/cannon.wav", autoplay=False, auto_destroy=True)
        a.play()


def generate_Smoke_particle(entity):
    if selected_weapon == 'Smoke':
        p = Smoke_effect(parent=entity, position=entity.position, file=r'effects\Smoke_dust.ptf')
        p.scale = 3
        a = Audio("sounds/cannon.wav", autoplay=False, auto_destroy=True)
        a.play()
        p.opacity = 0.1


def shoot_gun():
    if not gun.on_cooldown:
        gun.on_cooldown = True
        gun.muzzle_flash.enabled = True
        ursfx([(0.0, 0.0), (0.1, 0.9), (0.15, 0.75), (0.3, 0.14), (0.6, 0.0)], volume=0.5, wave='noise',
              pitch=random.uniform(-13, -12), pitch_change=-12, speed=3.0)
        invoke(gun.muzzle_flash.disable, delay=.05)
        invoke(setattr, gun, 'on_cooldown', False, delay=.15)

        dir = camera.forward + Vec3(0, 0.01, 0)
        pos = player.position + player.forward + Vec3(0, 1.6, 0)
        ball = Mermi(pos=pos, speed=15, dir=dir, rot=player.rotation)
        ball.shader = bls


def shoot_Scope():
    if not scope_gun.on_cooldown:
        scope_gun.on_cooldown = True
        scope_gun.muzzle_flash.enabled = True
        ursfx([(0.0, 0.0), (0.1, 0.9), (0.15, 0.75), (0.3, 0.14), (0.6, 0.0)], volume=0.5, wave='noise',
              pitch=random.uniform(-13, -12), pitch_change=-12, speed=3.0)
        invoke(scope_gun.muzzle_flash.disable, delay=.05)
        invoke(setattr, scope_gun, 'on_cooldown', False, delay=.15)

        dir = camera.forward + Vec3(0, 0.01, 0)
        pos = player.position + player.forward + Vec3(0, 1.6, 0)
        ball = Mermi(pos=pos, speed=22, dir=dir, rot=player.rotation)
        ball.shader = bls


app = Ursina(borderless=False)

gun = Entity(model='gun3', parent=camera, position=(.5, -.25, .25), scale=(.3, .2, 1), origin_z=-.5,
             on_cooldown=False, visible=False)
gun.muzzle_flash = Entity(parent=gun, z=8, y=1, x=5, world_scale=.5, model='quad', color=color.yellow,
                          enabled=False)

scope_gun = Entity(model='Scope.glb', parent=camera, zoom=3, position=(0, 0, 0), scale=(1, 1, 1), origin_z=-.5,
                   on_cooldown=False, visible=False)

scope_gun.muzzle_flash = Entity(parent=gun, z=8, y=1, x=5, world_scale=.5, model='quad', color=color.yellow,
                                enabled=False)

player = FirstPersonController(x=-10, origin_y=-.55, z=4, speed=5)

bomba = Entity(model='bomba', parent=camera, position=(.5, -.25, .25), scale=(.3, .2, 1), origin_z=-.5,
               visible=False)

Smoke = Entity(model='Smoke', parent=camera, position=(.5, -.25, .25), scale=(.3, .2, 1), origin_z=-.5,
               visible=False)

a = Audio("sounds/grass_step.mp3", autoplay=False, auto_destroy=False)

for i in range(10):
    Collect(player=player, y=1)
Collect.gui()

DirectionalLight().look_at(Vec3(1, -1, -1))

def update():
    if held_keys["w"] or held_keys["a"] or held_keys["s"] or held_keys["d"]:
        if not a.playing:
            a.play()
    else:
        a.stop()



sky = CustomSky()

arena = Entity(model="map8", scale=350, y=-34.5)

bg = Entity(model="quad", parent=camera.ui, texture="Fps_game_bg", scale=(1.5, 1))

ground = Entity(model="plane", scale=300, y=0, texture="grass", color=color.lime)
ground_box = Entity(model="plane", scale=300, y=-1.5, collider="box")

selected_weapon = None

enemies = [Enemy(x=x * 20, anim_speed=0.5, move_speed=0.1, collider_speed=0.05) for x in range(6)]

setup_scene("assets\colliders.json", 350)

app.enableParticles()
app.run()
