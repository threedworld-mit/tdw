from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.object_manager import ObjectManager

"""
Bounce a ball on a table.
"""

c = Controller()
camera = ThirdPersonCamera(position={"x": -4.5, "y": 2.1, "z": 0.5},
                           look_at={"x": 0, "y": 0, "z": 0})
object_manager = ObjectManager(transforms=False, bounds=True, rigidbodies=True)
c.add_ons.extend([camera, object_manager])
table_id = c.get_unique_id()
commands = [TDWUtils.create_empty_room(12, 12)]
commands.extend(c.get_add_physics_object(model_name="small_table_green_marble",
                                         object_id=table_id))
c.communicate(commands)

# Get the top of the table.
table_top = object_manager.bounds[table_id].top

ball_id = c.get_unique_id()
# Add a ball. Note that this is from the models_special.json model library.
commands = c.get_add_physics_object(model_name="prim_sphere",
                                    library="models_special.json",
                                    position={"x": 0.5, "y": 4, "z": -1.3},
                                    scale_factor={"x": 0.2, "y": 0.2, "z": 0.2},
                                    default_physics_values=False,
                                    scale_mass=False,
                                    mass=10,
                                    dynamic_friction=0.3,
                                    static_friction=0.3,
                                    bounciness=0.7,
                                    object_id=ball_id)
# Orient the ball to look at the top of the table. Apply a force.
commands.extend([{"$type": "object_look_at_position",
                 "position": TDWUtils.array_to_vector3(table_top),
                 "id": ball_id},
                 {"$type": "apply_force_magnitude_to_object",
                  "magnitude": 60,
                  "id": ball_id}])
# Re-initialize the object manager.
object_manager.initialized = False
c.communicate(commands)

# Wait until the ball stops moving.
while not object_manager.rigidbodies[ball_id].sleeping:
    c.communicate([])
c.communicate({"$type": "terminate"})