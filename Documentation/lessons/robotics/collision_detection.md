##### Robotics

# Robot collision detection

Collision detection works exactly the same for robots as it does for [objects](../physx/collisions.md). The only significant difference is in how robots are initialized.

When collision detection is enabled (either by sending [`send_collisions`](../../api/command_api.md#send_collisions) or by initializing a [`CollisionManager`](../../python/add_ons/collision_manager.md)), **a robot must not be intersecting any objects or environment meshes such as the floor.** If there are any intersections, the robot will severely glitch, or the build will crash, or both.

Some of the robots in TDW initially intersect with the floor. 

Robot joints are handled via [ArticulationBodies](https://docs.unity3d.com/2020.1/Documentation/ScriptReference/ArticulationBody.html). ArticulationBodies are very stable when used correctly but brittle when used incorrectly. 

In Unity, if two objects with rigidbodies intersect each other, Unity will try to resolve the issue, sometimes with glitchy behavior. If an object with an ArticulationBody intersects with an object with a Rigibody, the build will likely *crash*. Be careful where you position your robots!

Some robots, such as `ur5` and `ur10`, intersect with the floor when they are first added to the scene. To resolve this, they have *initial joint targets* that are automatically set by the `Robot` add-on.

To ensure that collision detection can be enabled, wait for the robot to reach its initial targets. Once this is done, you can initialize collision detection.

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.robot import Robot
from tdw.add_ons.collision_manager import CollisionManager

c = Controller()
robot = Robot(name="ur5",
              position={"x": 1, "y": 0, "z": -2},
              rotation={"x": 0, "y": 0, "z": 0},
              robot_id=c.get_unique_id())
c.add_ons.append(robot)
c.communicate(TDWUtils.create_empty_room(12, 12))

while robot.joints_are_moving():
    c.communicate([])

# The robot has moved to its initial pose. Enable collision detection.
collision_manager = CollisionManager()
c.add_ons.append(collision_manager)
c.communicate([])

c.communicate({"$type": "terminate"})
```

In the below example, we've added an [`ObjectManager`](../../python/add_ons/object_manager.md). Individual robot joints won't appear as separate objects in the `ObjectManager` data. However, they *will* appear as objects in the `CollisionManager` data:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.robot import Robot
from tdw.add_ons.collision_manager import CollisionManager
from tdw.add_ons.object_manager import ObjectManager

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
```

Output:

```
Collision between iron_box and shoulder_link
Collision between iron_box and upper_arm_link
Collision between iron_box and ur5(Clone)
```

***

**Next: [Select a robot](select_robot.md)**

[Return to the README](../../../README.md)

***

Example controllers:

- [collision_detection.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/robotics/set_joint_targets.py) Enable collision detection for a UR5 robot.

Python API:

- [`Robot`](../../python/add_ons/robot.md)
- [`CollisionManager`](../../python/add_ons/collision_manager.md)
- [`ObjectManager`](../../python/add_ons/object_manager.md)

Command API:

- [`send_collisions`](../../api/command_api.md#send_collisions)