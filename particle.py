from ursina import *
from random import uniform
from ursina.shaders import basic_lighting_shader as bls

class Particle(Entity):
    def __init__(self, position, velocity, color, texture):
        super().__init__(
            model = "cube",
            color = color,
            texture = texture,
            collider = "box",
            position = position,
            scale = uniform(0.05, 0.2),
            rotation = Vec3(uniform(0,360),uniform(0,360),uniform(0,360))
        )
        self.velocity = velocity
        self.lifetime = uniform(1, 7)
        self.shader=bls
    
        
    
    def update(self):
        self.position += self.velocity * time.dt
        self.lifetime -= time.dt
        if self.lifetime <= 0:
            destroy(self)

    @staticmethod
    def move(entity): 
        # entity.animate_scale(Vec3(0,0,0), duration=.1)
        entity.visible = False

        for i in range(50):
            pos = entity.position
            vel = Vec3(random.uniform(-2,2), random.uniform(-2,2), random.uniform(-2,2))
            clr = color.dark_gray
            txr = "white_cube"

            Particle(pos,vel,clr,txr)

    @staticmethod
    def explode_enemy(enemy_list,bomb_pos):
        near_enemies = []
        for e in enemy_list:
            if distance_xz(e,bomb_pos) < 8:
                near_enemies.append(e)






if __name__ == "__main__":

    from ursina.prefabs.first_person_controller import FirstPersonController

    app = Ursina(borderless=False)

    player = FirstPersonController()

    ground = Entity(model='plane', scale=32, texture='white_cube', texture_scale=Vec2(32), collider='box')

    def input(key):
        if key == 'left mouse down':
            e = Entity(model='cube', scale =1 ,position=player.position + Vec3(0,1.5,0) + player.camera_pivot.forward*10, collider='box')
            Particle.move(e)

    Sky()

    app.run()
    