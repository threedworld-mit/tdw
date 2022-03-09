# RobotDynamic

`from tdw.robot_data.robot_dynamic import RobotDynamic`

Dynamic data for a robot that can change per frame (such as the position of the robot, the angle of a joint, etc.)

***

## Class Variables

| Variable | Type | Description | Value |
| --- | --- | --- | --- |
| `NON_MOVING` | float | If the joint moved by less than this angle or distance since the previous frame, it's considered to be non-moving. | `0.001` |

***

## Fields

- `transform` The Transform data for this robot.

- `joints` A dictionary of [dynamic joint data](joint_dynamic.md). Key = The ID of the joint.

- `immovable` If True, this robot is immovable.

- `collisions_with_objects` A dictionary of collisions between one of this robot's [body parts (joints or non-moving)](robot_static.md) and another object.
Key = A tuple where the first element is the body part ID and the second element is the object ID.
Value = A list of [collision data.](../collision_data/collision_obj_obj.md)

- `collisions_with_self` A dictionary of collisions between two of this robot's [body parts](robot_static.md).
Key = An unordered tuple of two body part IDs.
Value = A list of [collision data.](../collision_data/collision_obj_obj.md)

- `collisions_with_environment` A dictionary of collisions between one of this robot's [body parts](robot_static.md) and the environment (floors, walls, etc.).
Key = The ID of the body part.
Value = A list of [environment collision data.](../collision_data/collision_obj_env.md)

***

## Functions

#### \_\_init\_\_

**`RobotDynamic(resp, robot_id, body_parts)`**

**`RobotDynamic(resp, robot_id, body_parts, previous=None)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| resp |  List[bytes] |  | The response from the build, which we assume contains `Robot` output data. |
| robot_id |  int |  | The ID of this robot. |
| body_parts |  List[int] |  | The IDs of all body parts belonging to this robot. |
| previous |  | None | If not None, the previous RobotDynamic data. Use this to determine if the joints are moving. |

