from ursina import *
from ursina.shaders import basic_lighting_shader as bls
import json

Entity.default_shader = bls


class Path(Entity):
    def __init__(self, colliders):
        super().__init__()
        self.points = [Point(pos=i) for i in self.load_path()]
        self.lines = Entity(model=Mesh(vertices=[i for i in self.load_path()], mode='line', thickness=5))

    def input(self, key):
        if key == "space":
            self.lines.model.vertices = [p.position for p in Point.list]
            # rotayı güncelle
            self.lines.model.generate()

        if key == "c":
            self.visible = not self.visible
            self.lines.visible = not self.lines.visible

        if key == "p up":
            self.save()

    def save(self):
        path_dict = {}
        for index, point in enumerate(Point.list):
            path_dict[index] = tuple(point.position)

        with open("assets/path.json", 'w') as f:
            json.dump(path_dict, f, indent=4)

    def load_path(self):
        with open("assets/path.json", 'r') as f:
            data = json.load(f)
        liste = []
        for key in data:
            liste.append(tuple(data[key]))
        return liste


class Point(Draggable):
    list = []

    def __init__(self, pos):
        super().__init__()
        self.parent = scene  # !!!!!!!! 3 BOYUTA TAŞIYORUZ
        self.model = "sphere"
        self.position = pos
        self.color = color.red
        self.collider = "sphere"
        self.on_click = self.select

        Point.list.append(self)

    def select(self):
        for p in Point.list:
            p.color = color.red
        self.color = color.lime

    def input(self, key):  # orjinali değiştiriyoruz
        if key == "x":
            self.lock = (0, 1, 1)
            self.plane_direction = (0, 1, 1)
        elif key == "y":
            self.lock = (1, 0, 1)
            self.plane_direction = (1, 0, 1)
        elif key == "z":
            self.lock = (1, 1, 0)
            self.plane_direction = (1, 1, 0)

        elif key == "delete":
            if self.color == color.lime:
                Point.list.remove(self)
                destroy(self)

        elif key == "c":
            self.visible = not self.visible

        super().input(key)  # !!! mutlaka yazmalıyız