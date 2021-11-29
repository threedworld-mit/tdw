from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils


"""
Minimal example of a Flex scene.
"""

c = Controller()
object_id = c.get_unique_id()
c.communicate([TDWUtils.create_empty_room(12, 12),
               {"$type": "convexify_proc_gen_room"},
               {"$type": "create_flex_container"},
               c.get_add_object(model_name="rh10",
                                object_id=object_id,
                                position={"x": 0, "y": 1, "z": 0}),
               {"$type": "set_flex_solid_actor",
                "id": object_id,
                "mass_scale": 5,
                "particle_spacing": 0.05},
               {"$type": "assign_flex_container",
                "id": object_id,
                "container_id": 0}])
c.communicate({"$type": "terminate"})
