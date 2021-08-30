# NonMoving

`from robot_data.non_moving import NonMoving`

Static data for a non-moving object attached to a robot (i.e. a sub-object mesh of a limb).

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
# Print the ID and segmentation color of each non-moving body part.
for body_part_id in robot.static.non_moving:
    print(body_part_id, robot.static.non_moving[body_part_id].segmentation_color)
c.communicate({"$type": "terminate"})
```

***

## Fields

- `object_id` The ID of this object.

- `name` The name of this object.

- `segmentation_color` The segmentation color of this joint as an `[r, g, b]` numpy array.

***

## Functions

#### \_\_init\_\_

**`NonMoving(static_robot, index)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| static_robot |  StaticRobot |  | Static robot output data from the build. |
| index |  int |  | The index of this object in the list of non-moving objects. |

