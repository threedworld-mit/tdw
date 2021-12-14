from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.collision_manager import CollisionManager


"""
Listen for collision output data with a CollisionManager.
"""

c = Controller()

# Add a collision manager
collision_manager = CollisionManager(enter=True, stay=False, exit=False, objects=True, environment=True)
c.add_ons.append(collision_manager)

commands = [TDWUtils.create_empty_room(12, 12)]
dropped_object_id = c.get_unique_id()
ground_object_id = c.get_unique_id()
# Add two objects.
commands.extend(c.get_add_physics_object(model_name="iron_box",
                                         object_id=dropped_object_id,
                                         position={"x": 0, "y": 3, "z": 0}))
commands.extend(c.get_add_physics_object(model_name="rh10",
                                         object_id=ground_object_id,
                                         position={"x": 0, "y": 0, "z": 0}))
c.communicate(commands)
for i in range(100):
    for object_ids in collision_manager.obj_collisions:
        print(i, object_ids.int1, object_ids.int2, collision_manager.obj_collisions[object_ids].state,
              collision_manager.obj_collisions[object_ids].relative_velocity)
        for normal, point in zip(collision_manager.obj_collisions[object_ids].normals,
                                 collision_manager.obj_collisions[object_ids].points):
            print("\t", normal, point)
    for object_id in collision_manager.env_collisions:
        print(i, object_id, collision_manager.env_collisions[object_id].state,
              collision_manager.env_collisions[object_id].floor)
        for normal, point in zip(collision_manager.env_collisions[object_id].normals,
                                 collision_manager.env_collisions[object_id].points):
            print("\t", normal, point)
    resp = c.communicate([])
c.communicate({"$type": "terminate"})
