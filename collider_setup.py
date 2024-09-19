from ursina import *
import json
#from path import Path

# JSON dosyasının yolunu belirtin
json_file_path = 'assets/colliders.json'

colliders = []


def load_meshes_from_json(json_file):
    with open(json_file, 'r') as f:
        meshes_data = json.load(f)
    return meshes_data


def create_entity_from_data(mesh_data, custom_scale):
    position = Vec3(mesh_data["position"]["x"], mesh_data["position"]["z"], mesh_data["position"]["y"])
    rotation = Vec3(mesh_data["rotation"]["x"] * -60, mesh_data["rotation"]["z"] * -60, mesh_data["rotation"]["y"] * 60)
    scale = Vec3(mesh_data["scale"]["x"], mesh_data["scale"]["z"], mesh_data["scale"]["y"])

    entity = Entity(
        name=mesh_data["name"],
        position=position * custom_scale,
        y=1,
        rotation=rotation,
        scale=scale * custom_scale * 2,
        model="plane",  # Placeholder model; you can customize this based on your needs
        double_sided=True,
        color=color.clear
    )

    if "Cube" in entity.name:
        entity.model = "cube"
        entity.collider = 'box'

    elif "Plane" in entity.name:
        entity.model = "plane"
        entity.collider = 'box'



    colliders.append(entity)
    return entity


def setup_scene(json_file, custom_scale):
    meshes_data = load_meshes_from_json(json_file)
    print(meshes_data)
    # Sort the list of dictionaries by the 'name' key
    #sorted_data = sorted(meshes_data, key=lambda x: int(x['name'][5:]))
    #print(sorted_data)
    for mesh_data in meshes_data:
        create_entity_from_data(mesh_data, custom_scale)
