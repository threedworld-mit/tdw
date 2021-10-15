from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.robot import Robot
from tdw.add_ons.collision_manager import CollisionManager
from tdw.add_ons.object_manager import ObjectManager

"""
Enable collision detection for a UR5 robot.
"""

c = Controller()
robot = Robot(name="ur5",
              position={"x": 1, "y": 0, "z": -2},
              rotation={"x": 0, "y": 0, "z": 0},
              robot_id=c.get_unique_id())
c.add_ons.append(robot)
c.communicate(TDWUtils.create_empty_room(12, 12))

while robot.joints_are_moving():
    c.communicate([])

collision_manager = CollisionManager(enter=True, exit=False, stay=False)
object_manager = ObjectManager(transforms=True, rigidbodies=True)
c.add_ons.extend([collision_manager, object_manager])

object_id = c.get_unique_id()
c.communicate([c.get_add_object(model_name="iron_box",
                                position={"x": 1, "y": 10, "z": -2},
                                object_id=object_id)])

# Wait for the object to stop moving.
while not object_manager.rigidbodies[object_id].sleeping:
    c.communicate([])
    for collision in collision_manager.obj_collisions:
        if collision.int1 in robot.static.joints:
            print("Collision between iron_box and " + robot.static.joints[collision.int1].name)
        elif collision.int2 in robot.static.joints:
            print("Collision between iron_box and " + robot.static.joints[collision.int2].name)
c.communicate({"$type": "terminate"})