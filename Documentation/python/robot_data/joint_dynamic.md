# JointDynamic

`from robot_data.joint_dynamic import JointDynamic`

Dynamic info for a joint that can change per-frame, such as its current position.


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

# Get the current position of each joint.
for joint_id in robot.dynamic.joints:
    print(joint_id, robot.dynamic.joints[joint_id].position)
c.communicate({"$type": "terminate"})
```

***

## Fields

- `joint_id` The ID of this joint.

- `position` The worldspace position of this joint as an `[x, y, z]` numpy array.

- `angles` The angles of each axis of the joint in degrees. For prismatic joints, you need to convert this from degrees to radians in order to get the correct distance in meters.

- `moving` If True, this joint is currently moving.

***

## Functions

#### \_\_init\_\_

**`JointDynamic(robot, joint_index)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| robot |  Robot |  | The `Robot` output data from the build. |
| joint_index |  int |  | The index of the data for this joint. |

