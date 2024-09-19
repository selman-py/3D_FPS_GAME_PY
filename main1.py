from ursina import *
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
from particle import *

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

        # Health properties
        self.max_hp = 100
        self.hp = self.max_hp

        # Health bar setup
        self.health_bar = Entity(parent=self, y=2, model='cube', color=color.red, world_scale=(1.5, 0.1, 0.1))

        self.speed = move_speed
        self.collider_speed = collider_speed

        Enemy.enemy_list.append(self)

    def update(self):
        dist = distance_xz(self, player)

        if dist < 0.8:
            self.speed = 0

        elif dist <= 2:
            print_on_screen("BUSTED")
            if self.actor.getCurrentAnim() is None:
                self.actor.play("attack")

        elif dist > 2:
            if self.actor.getCurrentAnim() is None:
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
                self.hit_enemy(34)  # Gun deals 34 damage per shot (100/34 ~= 3 shots to kill)

        for b in physics_entities:
            if b not in physics_entities:
                continue
            if distance(b, self) < 2:
                self.hit_enemy(100)  # Bomb deals 100 damage (1 shot to kill)

        self.rotation_y += 180

    def hit_enemy(self, damage):
        # Reduce enemy health
        self.hp -= damage

        # Update health bar
        self.health_bar.world_scale_x = (self.hp / self.max_hp) * 1.5

        # If the enemy's health drops to 0 or below, move it out of the scene
        if self.hp <= 0:
            self.visible = False
            self.health_bar.visible = False
            self.z = -25

class PhysicsEntity(Entity):
    bomba_list = []
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
    global selected_weapon, shot_counter

    if key == '1':  # Select gun
        selected_weapon = 'gun'
        gun.visible = True
        bomba.visible = False

    if key == '2':  # Select bomb
        selected_weapon = 'bomba'
        bomba.visible = True
        gun.visible = False

    if key == 'left mouse down':  # Fire weapon
        if selected_weapon == 'gun':
            shoot()
            shot_counter += 1
            if shot_counter >= 3:
                for enemy in Enemy.enemy_list:
                    enemy.hit_enemy(34)  # Call hit_enemy function with appropriate damage
                shot_counter = 0

        elif selected_weapon == 'bomba':  # Throw bomb
            e = PhysicsEntity(model='bomba', velocity=Vec3(0), scale=1,
                              position=player.position + Vec3(0, 1.5, 0) + player.forward, collider='box')
            e.velocity = (camera.forward + Vec3(0, .5, 0)) * 15
            invoke(Particle.move, e, delay=2)
            invoke(generate_particle, e, delay=2)

def generate_particle(entity):
    p = Effects(parent=entity, position=entity.position, file=r'effects\dust.ptf')
    p.scale = 3
    a = Audio("sounds/cannon.wav", autoplay=False, auto_destroy=True)
    a.play()

def shoot():
    if not gun.on_cooldown:
        gun.on_cooldown = True
        gun.muzzle_flash.enabled = True
        ursfx([(0.0, 0.0), (0.1, 0.9), (0.15, 0.75), (0.3, 0.14), (0.6, 0.0)], volume=0.5, wave='noise',
              pitch=random.uniform(-13, -12), pitch_change=-12, speed=3.0)
        invoke(gun.muzzle_flash.disable, delay=.05)
        invoke(setattr, gun, 'on_cooldown', False, delay=.15)

        # Create and fire a bullet
        dir = camera.forward + Vec3(0, 0.01, 0)
        pos = player.position + player.forward + Vec3(0, 1.6, 0)
        ball = Mermi(pos=pos, speed=15, dir=dir, rot=player.rotation)
        ball.shader = bls

app = Ursina(borderless=False)

gun = Entity(model='gun3', parent=camera, position=(.5, -.25, .25), scale=(.3, .2, 1), origin_z=-.5,
             on_cooldown=False, visible=False)
gun.muzzle_flash = Entity(parent=gun, z=8, y=1, x=5, world_scale=.5, model='quad', color=color.yellow,
                          enabled=False)

bomba = Entity(model='bomba', parent=camera, position=(.5, -.25, .25), scale=(.3, .2, 1), origin_z=-.5,
               visible=False)

sky = CustomSky()

arena = Entity(model="map8", scale=350, y=-34.5)

bg = Entity(model="quad", parent=camera.ui, texture="Fps_game_bg", scale=(1.5, 1))

ground = Entity(model="plane", scale=300, y=0, texture="grass", color=color.lime)
ground_box = Entity(model="plane", scale=300, y=-1.5, collider="box")

player = FirstPersonController(x=-10, origin_y=-.5, speed=13)

selected_weapon = None
shot_counter = 0  # Initialize shot counter

enemies = [Enemy(x=x * 20, anim_speed=0.5, move_speed=0.1, collider_speed=0.05) for x in range(6)]

setup_scene("assets\colliders.json", 350)

app.enableParticles()
app.run()