# RobotStatic

`from robot_data.robot_static import RobotStatic`

Static data for a robot that won't change due to physics (such as the joint IDs, segmentation colors, etc.)

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
# Initialize the scene.
c.communicate([{"$type": "load_scene",
                "scene_name": "ProcGenScene"},
               TDWUtils.create_empty_room(12, 12)])

# Print the ID, name, and mass of each joint.
for joint_id in robot.static.joints:
    print(joint_id, robot.static.joints[joint_id].name, robot.static.joints[joint_id].mass)
c.communicate({"$type": "terminate"})
```

***

## Fields

- `robot_id` The ID of the robot.

- `joints` A dictionary of [Static robot joint data](joint_static.md) for each joint. Key = The ID of the joint.

- `joint_ids_by_name` A dictionary of joint names. Key = The name of the joint. Value = The joint ID.

- `non_moving` A dictionary of [Static data for non-moving parts](non_moving.md) for each non-moving part. Key = The ID of the part.

- `body_parts` A list of joint IDs and non-moving body part IDs.

- `immovable` If True, the robot is immovable.

***

## Functions

#### \_\_init\_\_

**`RobotStatic(resp, robot_id)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| resp |  List[bytes] |  | The response from the build, which we assume contains `Robot` output data. |
| robot_id |  int |  | The ID of this robot. |

