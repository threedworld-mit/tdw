# Drive

`from robot_data.drive import Drive`

Static data for a joint drive.


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

# Get each joint.
for joint_id in robot.static.joints:
    # Get each drive.
    for drive_axis in robot.static.joints[joint_id].drives:
        drive = robot.static.joints[joint_id].drives[drive_axis]
        print(drive_axis, drive.force_limit, drive.damping, drive.stiffness)
c.communicate({"$type": "terminate"})
```

***

## Fields

- `axis` The axis of rotation. Can be `"x"`, `"y"`, or `"z"`.

- `limits` Tuple: The lower and upper limits of the drive rotation in degrees.

- `force_limit` The limit of how much force can be applied to the drive.

- `damping` The damping value.

- `stiffness` The stiffness value.

***

## Functions

#### \_\_init\_\_

**`Drive(sr, joint_index, drive_index)`**


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| sr |  StaticRobot |  | The StaticRobot output data. |
| joint_index |  int |  | The index of the joint in the output data that this drive belongs to. |
| drive_index |  int |  | The index of this drive in the joint data. |

