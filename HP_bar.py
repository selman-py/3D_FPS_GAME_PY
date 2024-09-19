from ursina import *
import random
from ursina.shaders import basic_lighting_shader as bls, lit_with_shadows_shader as lit
from ursina import curve

Entity.default_shader = lit

airplanes = []

def update():
    global fuel, current_target_index

    if not plane : return

    # Hedef noktaya doğru uçağı hareket ettirin
    target_point = target_points[current_target_index]
    
    # plane.look_at_2d(Vec3(target_point), axis="y")
    
    if plane.fly : plane.position += plane.forward * 0.05  # Uçak hızı ayarlayın

    # Hedef noktaya ulaşıldığında bir sonraki hedefe geçin
    if distance(plane.position, target_point) < 0.1:
        current_target_index = (current_target_index + 1) % len(target_points)

    # Yakıtı azaltın
    fuel -= 0.1  # Örneğin, her güncelleme döngüsünde 0.1 birim yakıt azalıyor

    # Yakıt çubuğunu güncelleyin
    health_percentage = fuel / 100.0  # Sağlık çubuğunu yakıt miktarına göre güncelleyin
    if health_percentage < 0.002:
        health_percentage = 0.01

    health_bar.scale_x = health_percentage * 7  # Sağlık çubuğu negatif değer almasın

    # Yakıt tükendiğinde oyunu sonlandırın
    if fuel <= 0 and plane.fly:
        plane.animate('y', 0, duration=3, curve = curve.linear)
        invoke(destroy, plane, delay=5) # tetikle, ateşle, başlat
        plane.fly = False

    for airplane in airplanes:
        if airplane.y == 15 and airplane.fly:
            fly_on_air(airplane)


def on_mouse_click():
    if mouse.hovered_entity == plane and plane.fly:
        plane.fly = False
        time_counter = 0
        for key, value in pos_dict.items():
            invoke(land_on_airport, plane, value, delay = time_counter)
            time_counter += 3
                
    elif mouse.hovered_entity == airport:
        for airplane in airplanes:
            if airplane.fly:
                airplane.animate('y', 15, duration=3, curve=curve.linear)
                airplane.animate('z', airplane.z + 30, duration=3, curve=curve.linear)
                airplane.fly = True

def land_on_airport(airplane, position):
    airplane.look_at_2d(position, axis="y")

    # İki nokta arasındaki uzaklık hesaplanır
    distance_to_target = distance(airplane, Vec3(position))

    # Uçağın rotation_x değeri hesaplanır
    airplane.rotation_x = math.degrees(math.atan2(airplane.y-position[1], distance_to_target))
    airplane.animate('position', position, duration=3, curve=curve.linear)

def fly_on_air(plane):
    if plane.fly : plane.position += plane.forward * 0.1  # Uçak hızı ayarlayın


def toggle_fly(air_plane):
    air_plane.fly = not air_plane.fly
    if air_plane.fly:
        air_plane.color = color.lime
    else:
        air_plane.color = color.red

def input(key):
    if key == "left mouse down":
        # print_on_screen(getattr(mouse.hovered_entity, "model"))
        print_on_screen(mouse.hovered_entity.model)

        for airplane in airplanes:
            return
            print(distance(mouse.world_point, airplane.position))
            if distance(mouse.world_point, airplane.position) < 10:
                if airplane.y > 10 : return
                toggle_fly(airplane)


app = Ursina()

# Uçağınızı oluşturun veya içe aktarın
plane = Entity(model="Airplane", texture="Cube", y=15, fly=True, shader=bls, collider="box")
plane.on_click = on_mouse_click

# Sağlık çubuğunu oluşturun
health_bar = Entity(model='quad', scale=(7, .5), color=color.green, parent=plane, billboard = True)
health_bar.y = 1.5  # Sağlık çubuğunu uçağın üstüne yerleştirin

# Uçağın başlangıç yakıt miktarını ayarlayın
fuel = 100.0  # Örneğin, başlangıçta 100 birim yakıt

# Uçağın uçacağı 5 farklı hedef nokta belirleyin
target_points = [(3, 15, 3), (-3, 15, 3), (25, 15, -20), (-15, 15, -3), (0, 15, 0)]
# hedefin şu anki indeksi (sırası)
current_target_index = 0

ground = Entity(model="plane", texture="grass", scale=200, collider="box")

# Havaalanı oluşturun
airport = Entity(model='Airport_lowpoly', y=0.05, x=50, scale=3, collider="mesh", unlit=True)
airport.on_click = on_mouse_click

# Uçakları oluşturun ve havaalanına yerleştirin

for i in range(3):
    # GÖREV-1 3 tane uçak yapınız ve farklı noktalarda olsunlar
    airplane = Entity(model="Airplane.obj", texture="AirplaneBaked", position=airport.position+Vec3(0, 0.7, i*12), shader=bls, collider="box", fly=False)
    
    airplane.on_click = lambda x = airplane: toggle_fly(x) # Görev-2 fonksiyonun uçağın fly özelliğini True veya False

    airplanes.append(airplane) 



cursor0 = Entity(model="sphere", parent=airport, position = Vec3(-4.51541, 0.000631, -8.17821), scale=.5, color=color.red)

cursor1 = Entity(model="sphere", parent=airport, position = Vec3(-4.51541, 0.000631, -0.636948), scale=.5, color=color.red)

cursor2 = Entity(model="sphere", parent=airport, position = Vec3(-0.459872, 0.000631, -0.636948), scale=.5, color=color.red)

cursor3 = Entity(model="sphere", parent=airport, position = Vec3(-0.32745, 0.000265, 6.03683), scale=.5, color=color.lime)

cursor4 = Entity(model="sphere", parent=airport, position = Vec3(6.28977, 4.64072, 6.5397), scale=.5, color=color.lime)


pos_dict = {
    "0" : cursor0.world_position,
    "1" : cursor1.world_position,
    "2" : cursor2.world_position,
    "3" : cursor3.world_position,
    "4" : cursor4.world_position,
}

Sky()

EditorCamera(y=30)

sun = DirectionalLight() # yönlendirilmiş ışık 
sun.look_at((-1, -1, 1))

app.run()

# ödevimiz 



# liste[0]  listenşn 0. elemanı
# sozluk["model1"] sözlüğün model1 isimli elamanı
 