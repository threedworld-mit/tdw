# RobotStatic

`from tdw.robot_data.robot_static import RobotStatic`

Static data for a robot that won't change due to physics (such as the joint IDs, segmentation colors, etc.)

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

