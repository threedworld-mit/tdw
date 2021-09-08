# JointStatic

`from robot_data.joint_static import JointStatic`

Static robot joint data.


```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.robot import Robot

c = Controller()
# Add a robot.
robot = Robot(name="ur5",
              position={"x": -1, "y": 0, "z": 0.5},
              robot_id=0)
c.add_ons.append(robot)
# Initialize the scene_data.
c.communicate([{"$type": "load_scene",
                "scene_name": "ProcGenScene"},
               TDWUtils.create_empty_room(12, 12)])
# Print the ID and segmentation color of each joint.
for joint_id in robot.static.joints:
    print(joint_id, robot.static.joints[joint_id].segmentation_color)
c.communicate({"$type": "terminate"})
```

***

## Fields

- `joint_id` The ID of this joint.

- `name` The name of the joint.

- `joint_type` [The type of joint.](joint_type.md)

- `segmentation_color` The segmentation color of this joint as an `[r, g, b]` numpy array.

- `mass` The mass of this joint.

- `immovable` If True, this joint is immovable.

- `root` If True, this is the root joint.

- `parent_id` The ID of this joint's parent joint. Ignore if `self.root == True`.

- `drives` A dictionary of [Drive data](drive.md) for each of the robot's joints. Key = The drive axis (`"x"`, `"y"`, or `"z"`).

***

## Functions

#### \_\_init\_\_

**`JointStatic(static_robot, joint_index)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| static_robot |  StaticRobot |  | Static robot output data from the build. |
| joint_index |  int |  | The index of this joint in the list of joints. |

