# RobotStatic

`from robots.robot_static import RobotStatic`

Static data for a robot that won't change due to physics (such as the joint IDs, segmentation colors, etc.)

***

## Fields

- `joints` A dictionary of [Static robot joint data](joint_static.md) for each joint. Key = The ID of the joint.

- `non_moving` A dictionary of [Static data for non-moving parts](non_moving.md) for each non-moving part. Key = The ID of the part.

- `robot_id` The ID of this robot.

***

## Functions

#### \_\_init\_\_

**`RobotStatic(resp, robot_id)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| resp |  List[bytes] |  | The response from the build, which we assume contains `StaticRobot` output data. |
| robot_id |  int |  | The ID of this robot. |

