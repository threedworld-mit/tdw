##### Robots

# Robotics API (low-level)

So far, this tutorial has utilized the [`Robot` add-on](../../Python/add_ons/robot.md) for robotics simulations. Like all other add-ons in TDW, the `Robot` add-on is nothing more than a convenient wrapper class for lower-level commands. It is possible to control a robot using low-level commands, and there are a few commands that aren't implemented in the `Robot` add on.

## Add a robot to the scene

Add a robot to the scene with the [`add_robot` command](../../api/command_api.md#add_robot) or the wrapper function [`Controller.get_add_robot()`](../../python/controller.md):

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

c = Controller()
c.communicate([TDWUtils.create_empty_room(12, 12),
               c.get_add_robot(name="ur5",
                               robot_id=c.get_unique_id())])
```

The  example below does the exact same thing as the example above:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

c = Controller()
c.communicate([TDWUtils.create_empty_room(12, 12),
               {"$type": "add_robot",
                "id": c.get_unique_id(),
                "position": {"x": 0, "y": 0, "z": 0},
                "rotation": {"x": 0, "y": 0, "z": 0},
                "name": "ur5",
                "url": "https://tdw-public.s3.amazonaws.com/robots/windows/2020.2/ur5"}])
```

## Get static robot data

Send [`send_static_robots`](../../api/command_api.md#send_static_robots) to receive [`StaticRobot`](../../api/output_data.md#StaticRobot) output data per robot. This data includes the ID, name, mass, segmentation color, and drive information of each joint. In this example we're only going to read the joint names and IDs but you can check the  [`StaticRobot`](../../api/output_data.md#StaticRobot) API for how to get more static data.

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, StaticRobot

c = Controller()
resp = c.communicate([TDWUtils.create_empty_room(12, 12),
                      c.get_add_robot(name="ur5",
                                      robot_id=c.get_unique_id()),
                      {"$type": "send_static_robots"}])
joint_names_and_ids = dict()
for i in range(len(resp) - 1):
    r_id = OutputData.get_data_type_id(resp[i])
    if r_id == "srob":
        srob = StaticRobot(resp[i])
        for j in range(srob.get_num_joints()):
            joint_id = srob.get_joint_id(j)
            joint_name = srob.get_joint_name(j)
            joint_names_and_ids[joint_name] = joint_id
```

## Set joint targets or add joint forces

Once you have the names and IDs of each joint you can set target angles and positions, or target torques and forces. These commands will *start* the joint moving towards a target but won't wait for them to finish moving.

| Joint type    | Target command                                               | Force command                                                |
| ------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| `"revolute"`  | [`set_revolute_target`](../../api/command_api.md#set_revolute_target) | [`add_torque_to_revolute`](../../api/command_api.md#add_torque_to_revolute) |
| `"prismatic"` | [`set_prismatic_target`](../../api/command_api.md#set_prismatic_target) | [`add_force_to_prismatic`](../../api/command_api.md#add_force_to_prismatic) |
| `"spherical"` | [`set_spherical_target`](../../api/command_api.md#set_spherical_target) | [`add_torque_to_spherical`](../../api/command_api.md#`add_torque_to_spherical`) |
| `"fixed"`     |                                                              |                                                              |

In this example, we happen to know that all of the joints in a UR5 robot are revolute.

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, StaticRobot

c = Controller()
robot_id = c.get_unique_id()
resp = c.communicate([TDWUtils.create_empty_room(12, 12),
                      c.get_add_robot(name="ur5",
                                      robot_id=robot_id),
                      {"$type": "send_static_robots"}])
joint_names_and_ids = dict()
for i in range(len(resp) - 1):
    r_id = OutputData.get_data_type_id(resp[i])
    if r_id == "srob":
        srob = StaticRobot(resp[i])
        for j in range(srob.get_num_joints()):
            joint_id = srob.get_joint_id(j)
            joint_name = srob.get_joint_name(j)
            joint_names_and_ids[joint_name] = joint_id

c.communicate([{"$type": "set_revolute_target",
                "id": robot_id,
                "joint_id": joint_names_and_ids["shoulder_link"],
                "target": 70},
               {"$type": "set_revolute_target",
                "id": robot_id,
                "joint_id": joint_names_and_ids["forearm_link"],
                "target": -60}])
```

## Get dynamic robot data and check if the joints are still moving

To determine whether the robot's joints are still moving, you'll need to send [`send_robots`](../../api/command_api.md#send_robots) which will return [`Robot`](../../api/output_data.md#Robot) output data. In this example, we'll get the starting position of the joints. Per frame, we'll then parse `Robot` output data and compare it to the previous positions. If all of the joints have stopped moving or nearly stopped moving, the controller ends:

```python
import numpy as np
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, StaticRobot, Robot

c = Controller()
robot_id = c.get_unique_id()
resp = c.communicate([TDWUtils.create_empty_room(12, 12),
                      c.get_add_robot(name="ur5",
                                      robot_id=robot_id),
                      {"$type": "send_static_robots"},
                      {"$type": "send_robots",
                       "frequency": "always"}])
joint_names_and_ids = dict()
joint_positions_0 = dict()
for i in range(len(resp) - 1):
    r_id = OutputData.get_data_type_id(resp[i])
    if r_id == "srob":
        srob = StaticRobot(resp[i])
        for j in range(srob.get_num_joints()):
            joint_id = srob.get_joint_id(j)
            joint_name = srob.get_joint_name(j)
            joint_names_and_ids[joint_name] = joint_id
    elif r_id == "robo":
        robo = Robot(resp[i])
        for j in range(robo.get_num_joints()):
            joint_id = robo.get_joint_id(j)
            joint_position = robo.get_joint_position(j)
            joint_positions_0[joint_id] = np.array(joint_position)

resp = c.communicate([{"$type": "set_revolute_target",
                       "id": robot_id,
                       "joint_id": joint_names_and_ids["shoulder_link"],
                       "target": 70},
                      {"$type": "set_revolute_target",
                       "id": robot_id,
                       "joint_id": joint_names_and_ids["forearm_link"],
                       "target": -60}])
done = False
while not done:
    done = True
    # Get the current joint positions.
    joint_positions_1 = dict()
    for i in range(len(resp) - 1):
        r_id = OutputData.get_data_type_id(resp[i])
        if r_id == "robo":
            robo = Robot(resp[i])
            for j in range(robo.get_num_joints()):
                joint_id = robo.get_joint_id(j)
                joint_position = robo.get_joint_position(j)
                joint_positions_1[joint_id] = np.array(joint_position)
    # Check if any of the joints are still moving.
    for j0, j1 in zip(joint_positions_0, joint_positions_1):
        if np.linalg.norm(joint_positions_0[j0] - joint_positions_1[j1]) > 0.001:
            done = False
            break
    joint_positions_0 = joint_positions_1
    resp = c.communicate([])
c.communicate({"$type": "terminate"})
```

## Robots and immovability

Some robots are initially *immovable* meaning that their root object won't move or rotate regardless of the forces applied to it. To determine whether a robot is immovable, check the `immovable` field in the record:

```python
from tdw.librarian import RobotLibrarian

lib = RobotLibrarian()
record = lib.get_record("ur5")
print(record.immovable)  # True
```

You can toggle whether a robot is immovable with the command [`set_immovable`](../../api/command_api.md#set_immovable).

*Regardless* of immovability, it is possible to instantly move and rotate a robot without applying forces by sending [`teleport_robot`](../../api/command_api.md#teleport_robot).

## Set static robot parameters

It is possible to adjust many static robot parameters:

- [`set_robot_drive`](../../api/command_api.md#set_robot_drive) sets drive parameters for a given joint.
- [`set_robot_joint_friction`](../../api/command_api.md#set_robot_joint_friction) sets the friction coefficient of a given joint.
- [`set_robot_joint_mass`](../../api/command_api.md#set_robot_joint_mass) sets the mass of a given joint.
- [`set_robot_joint_physic_material`](../../api/command_api.md#set_robot_joint_physic_material) sets the [physic material](../physx/physics_objects.md) of a given joint.

```python
import numpy as np
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, StaticRobot

c = Controller()
robot_id = c.get_unique_id()
resp = c.communicate([TDWUtils.create_empty_room(12, 12),
                      c.get_add_robot(name="ur5",
                                      robot_id=robot_id),
                      {"$type": "send_static_robots"}])
commands = []
for i in range(len(resp) - 1):
    r_id = OutputData.get_data_type_id(resp[i])
    if r_id == "srob":
        srob = StaticRobot(resp[i])
        for j in range(srob.get_num_joints()):
            joint_id = srob.get_joint_id(j)
            joint_name = srob.get_joint_name(j)
            # Adjust the shoulder link.
            if joint_name == "shoulder_link":
                # Adjust the mass.
                mass = srob.get_joint_mass(j)
                commands.append({"$type": "set_robot_joint_mass",
                                 "mass": mass + 2,
                                 "joint_id": joint_id,
                                 "id": robot_id})
                # Adjust the friction coefficient.
                commands.append({"$type": "set_robot_joint_friction",
                                 "joint_id": joint_id,
                                 "friction": 0.3,
                                 "id": robot_id})
                # Set the physic material.
                commands.append({"$type": "set_robot_joint_physic_material",
                                 "dynamic_friction": 0.3, 
                                 "static_friction": 0.3, 
                                 "bounciness": 0.7,
                                 "joint_id": joint_id,
                                 "id": robot_id})
                # Adjust the joint drives.
                for k in range(srob.get_num_joint_drives(j)):
                    lower_limit = srob.get_joint_drive_lower_limit(j, k)
                    upper_limit = srob.get_joint_drive_upper_limit(j, k)
                    force_limit = srob.get_joint_drive_force_limit(j, k)
                    stiffness = srob.get_joint_drive_stiffness(j, k)
                    damping = srob.get_joint_drive_damping(j, k)
                    axis = srob.get_joint_drive_axis(j, k)
                    commands.append({"$type": "set_robot_joint_drive",
                                     "joint_id": joint_id,
                                     "axis": axis,
                                     "lower_limit": lower_limit - 15,
                                     "upper_limit": upper_limit + 15,
                                     "force_limit": force_limit * 1.5,
                                     "stiffness": stiffness * 1.3,
                                     "damping": damping * 0.8,
                                     "id": robot_id})
c.communicate(commands)
```

You can of course use any low-level API commands with any higher-level add-on, and the `Robot` add-on is no exception. However, the cached static data won't automatically update if you adjust static parameters.

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.robot import Robot

c = Controller()
robot_id = c.get_unique_id()
robot = Robot(name="ur5", robot_id=robot_id)
c.add_ons.append(robot)
c.communicate(TDWUtils.create_empty_room(12, 12))
commands = []
for joint_id in robot.static.joints:
    joint = robot.static.joints[joint_id]
    commands.extend([{"$type": "set_robot_joint_mass",
                      "mass": joint.mass + 2,
                      "joint_id": joint_id,
                      "id": robot_id},
                     {"$type": "set_robot_joint_friction",
                      "joint_id": joint_id,
                      "friction": 0.3,
                      "id": robot_id},
                     {"$type": "set_robot_joint_physic_material",
                      "dynamic_friction": 0.3,
                      "static_friction": 0.3,
                      "bounciness": 0.7,
                      "joint_id": joint_id,
                      "id": robot_id}])
    for axis in joint.drives:
        commands.append({"$type": "set_robot_joint_drive",
                         "joint_id": joint_id,
                         "axis": axis,
                         "lower_limit": joint.drives[axis].limits[0] - 15,
                         "upper_limit": joint.drives[axis].limits[1] + 15,
                         "force_limit": joint.drives[axis].force_limit * 1.5,
                         "stiffness": joint.drives[axis].stiffness * 1.3,
                         "damping": joint.drives[axis].damping * 0.8,
                         "id": robot_id})
c.communicate(commands)
```

***

**Next: [Add a camera to a robot](add_camera.md)**

[Return to the README](../../../README.md)

***

Example controllers:

- [robot_arm.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/robots/robot_arm.py) Control a UR5 robot with low-level commands.

Python API:

- [`Robot`](../../python/add_ons/robot.md)
- [`Controller.get_add_robot()`](../../python/controller.md)
- [`RobotLibrarian`](../../python/librarian/robot_librarian.md)

Command API:

- [`add_robot`](../../api/command_api.md#add_robot)
- [`send_static_robots`](../../api/command_api.md#send_static_robots)
- [`send_robots`](../../api/command_api.md#send_robots)
- [`set_revolute_target`](../../api/command_api.md#set_revolute_target)
- [`set_prismatic_target`](../../api/command_api.md#set_prismatic_target)
- [`set_spherical_target`](../../api/command_api.md#set_spherical_target)
- [`add_torque_to_revolute`](../../api/command_api.md#add_torque_to_revolute)
- [`add_force_to_prismatic`](../../api/command_api.md#add_force_to_prismatic)
- [`add_torque_to_spherical`](../../api/command_api.md#add_torque_to_spherical)
- [`set_immovable`](../../api/command_api.md#set_immovable)
- [`teleport_robot`](../../api/command_api.md#teleport_robot)
- [`set_robot_drive`](../../api/command_api.md#set_robot_drive)
- [`set_robot_joint_friction`](../../api/command_api.md#set_robot_joint_friction)
- [`set_robot_joint_mass`](../../api/command_api.md#set_robot_joint_mass)
- [`set_robot_joint_physic_material`](../../api/command_api.md#set_robot_joint_physic_material)

Output Data API:

- [`StaticRobot`](../../api/output_data.md#StaticRobot)
- [`Robot`](../../api/output_data.md#Robot)