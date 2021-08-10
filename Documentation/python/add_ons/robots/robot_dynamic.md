# RobotDynamic

`from robots.robot_dynamic import RobotDynamic`

Dynamic data for a robot that can change per frame (such as the position of the robot, the angle of a joint, etc.)

***

## Fields

- `robot_id` The ID of this robot.

- `position` The current position of the robot as an `[x, y, z]` numpy array.

- `rotation` The current rotation of the robot as an `[x, y, z, w]` quaternion numpy array.

- `forward` The forward directional vector of the robot as an `[x, y, z]` numpy array.

- `joints` A dictionary of [dynamic joint data](joint_dynamic.md). Key = The ID of the joint.

***

## Functions

#### \_\_init\_\_

**`RobotDynamic(resp, robot_id)`**

**`RobotDynamic(resp, robot_id, previous=None, non_moving=0.001)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| resp |  List[bytes] |  | The response from the build, which we assume contains `StaticRobot` output data. |
| robot_id |  int |  | The ID of this robot. |
| previous |  | None | If not None, the previous RobotDynamic data. Use this to determine if the joints are moving. |
| non_moving |  float  | 0.001 | If the joint has moved by less than this angle or distance since the previous frame, it's considered to be non-moving. |

