# JointDynamic

`from tdw.robot_data.joint_dynamic import JointDynamic`

Dynamic info for a joint that can change per-frame, such as its current position.

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

