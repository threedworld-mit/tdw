# WheelchairMotion

`from tdw.wheelchair_replicant.actions.wheelchair_motion import WheelchairMotion`

Abstract base class for actions involving wheelchair motion (motor torques, brake torques, etc.)

***

## Fields

- `wheel_values` The [`WheelValues`](../wheel_values.md) that will be applied to the wheelchair's wheels.

- `reset_arms` If True, reset the arms to their neutral positions while beginning to move.

- `reset_arms_duration` The speed at which the arms are reset in seconds.

- `scale_reset_arms_duration` If True, `reset_arms_duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds.

- `arrived_at` A distance or time determines whether the WheelchairReplicant arrived at the target.

- `collision_detection` The [`CollisionDetection`](../../replicant/collision_detection.md) rules.

- `collision_avoidance_distance` If `collision_detection.avoid == True`, an overlap will be cast at this distance from the Wheelchair Replicant to detect obstacles.

- `collision_avoidance_half_extents` If `collision_detection.avoid == True`, an overlap will be cast with these half extents to detect obstacles.

- `status` [The current status of the action.](../../replicant/action_status.md) By default, this is `ongoing` (the action isn't done).

- `initialized` If True, the action has initialized. If False, the action will try to send `get_initialization_commands(resp)` on this frame.

- `done` If True, this action is done and won't send any more commands.

***

## Functions

#### \_\_init\_\_

**`WheelchairMotion(wheel_values, dynamic, collision_detection, previous, reset_arms, reset_arms_duration, scale_reset_arms_duration, arrived_at, collision_avoidance_distance, collision_avoidance_half_extents)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| wheel_values |  WheelValues |  | The [`WheelValues`](../wheel_values.md) that will be applied to the wheelchair's wheels. |
| dynamic |  ReplicantDynamic |  | The [`ReplicantDynamic`](../../replicant/replicant_dynamic.md) data that changes per `communicate()` call. |
| collision_detection |  CollisionDetection |  | The [`CollisionDetection`](../../replicant/collision_detection.md) rules. |
| previous |  Optional[Action] |  | The previous action, if any. |
| reset_arms |  bool |  | If True, reset the arms to their neutral positions while beginning to move. |
| reset_arms_duration |  float |  | The speed at which the arms are reset in seconds. |
| scale_reset_arms_duration |  bool |  | If True, `reset_arms_duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds. |
| arrived_at |  float |  | A distance or time determines whether the WheelchairReplicant arrived at the target. |
| collision_avoidance_distance |  float |  | If `collision_detection.avoid == True`, an overlap will be cast at this distance from the Wheelchair Replicant to detect obstacles. |
| collision_avoidance_half_extents |  Dict[str, float] |  | If `collision_detection.avoid == True`, an overlap will be cast with these half extents to detect obstacles. |

#### get_initialization_commands

**`self.get_initialization_commands(resp, static, dynamic, image_frequency)`**


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| resp |  List[bytes] |  | The response from the build. |
| static |  ReplicantStatic |  | The [`ReplicantStatic`](../../replicant/replicant_static.md) data that doesn't change after the Replicant is initialized. |
| dynamic |  ReplicantDynamic |  | The [`ReplicantDynamic`](../../replicant/replicant_dynamic.md) data that changes per `communicate()` call. |
| image_frequency |  ImageFrequency |  | An [`ImageFrequency`](../../replicant/image_frequency.md) value describing how often image data will be captured. |

_Returns:_  A list of commands to initialize this action.

#### get_ongoing_commands

**`self.get_ongoing_commands(resp, static, dynamic)`**

Evaluate an action per-frame to determine whether it's done.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| resp |  List[bytes] |  | The response from the build. |
| static |  ReplicantStatic |  | The [`ReplicantStatic`](../../replicant/replicant_static.md) data that doesn't change after the Replicant is initialized. |
| dynamic |  ReplicantDynamic |  | The [`ReplicantDynamic`](../../replicant/replicant_dynamic.md) data that changes per `communicate()` call. |

_Returns:_  A list of commands to send to the build to continue the action.

#### get_end_commands

**`self.get_end_commands(resp, static, dynamic, image_frequency)`**


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| resp |  List[bytes] |  | The response from the build. |
| static |  ReplicantStatic |  | The [`ReplicantStatic`](../../replicant/replicant_static.md) data that doesn't change after the Replicant is initialized. |
| dynamic |  ReplicantDynamic |  | The [`ReplicantDynamic`](../../replicant/replicant_dynamic.md) data that changes per `communicate()` call. |
| image_frequency |  ImageFrequency |  | An [`ImageFrequency`](../../replicant/image_frequency.md) value describing how often image data will be captured. |

_Returns:_  A list of commands that must be sent to end any action.