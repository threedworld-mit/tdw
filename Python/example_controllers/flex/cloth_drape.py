from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

"""
Using NVIDIA Flex, drape a cloth over an object.
"""

c = Controller()
solid_id = c.get_unique_id()
cloth_id = c.get_unique_id()
# Load a nice-looking room. Create the Flex container.
# Add a solid object. Add a cloth object.
commands = [c.get_add_scene(scene_name="tdw_room"),
            {"$type": "create_flex_container",
             "collision_distance": 0.001,
             "static_friction": 1.0,
             "dynamic_friction": 1.0,
             "iteration_count": 5,
             "substep_count": 8,
             "radius": 0.1875,
             "damping": 0,
             "drag": 0},
            c.get_add_object(model_name="linbrazil_diz_armchair",
                             object_id=solid_id,
                             position={"x": -1.2, "y": 0, "z": 0},
                             rotation={"x": 0.0, "y": 90, "z": 0.0},
                             library="models_core.json"),
            {"$type": "set_flex_solid_actor",
             "id": solid_id,
             "mass_scale": 100.0,
             "particle_spacing": 0.035},
            {"$type": "assign_flex_container",
             "id": solid_id,
             "container_id": 0},
            c.get_add_object(model_name="cloth_square",
                             object_id=cloth_id,
                             position={"x": -1.2, "y": 1.0, "z": 0},
                             library="models_special.json"),
            {"$type": "set_flex_cloth_actor",
             "id": cloth_id,
             "mass_scale": 1,
             "mesh_tesselation": 1,
             "tether_stiffness": 0.5,
             "bend_stiffness": 1.0,
             "self_collide": False,
             "stretch_stiffness": 1.0},
            {"$type": "assign_flex_container",
             "id": cloth_id,
             "container_id": 0}]
# Add an avatar.
commands.extend(TDWUtils.create_avatar(position={"x": 2.0, "y": 1, "z": 1},
                                       look_at={"x": -1.2, "y": 0.5, "z": 0}))
# Send the commands.
c.communicate(commands)
# Let the cloth fall.
for i in range(300):
    c.communicate([])
c.communicate({"$type": "terminate"})
