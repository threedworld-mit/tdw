# NonMoving

`from tdw.robot_data.non_moving import NonMoving`

Static data for a non-moving object attached to a robot (i.e. a sub-object mesh of a limb).

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

