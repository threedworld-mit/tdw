# TurnTo

`from tdw.wheelchair_replicant.actions.turn_to import TurnTo`

Turn to a target object or position.

The wheelchair turns by applying motor torques to the rear wheels and a steer angle to the front wheels.

Therefore, the wheelchair is not guaranteed to turn in place.

The action can end for several reasons depending on the collision detection rules (see [`self.collision_detection`](../../replicant/collision_detection.md).

- If the Replicant turns by the target angle, the action succeeds.
- If `self.collision_detection.previous_was_same == True`, and the previous action was `MoveBy` or `MoveTo`, and it was in the same direction (forwards/backwards), and the previous action ended in failure, this action ends immediately.
- If `self.collision_detection.avoid_obstacles == True` and the Replicant encounters a wall or object in its path:
  - If the object is in `self.collision_detection.exclude_objects`, the Replicant ignores it.
  - Otherwise, the action ends in failure.
- If the Replicant collides with an object or a wall and `self.collision_detection.objects == True` and/or `self.collision_detection.walls == True` respectively:
  - If the object is in `self.collision_detection.exclude_objects`, the Replicant ignores it.
  - Otherwise, the action ends in failure.

***

## Fields

- `angle` The target angle in degrees.

- `wheel_values` The [`WheelValues`](../wheel_values.md) that will be applied to the wheelchair's wheels.

- `reset_arms` If True, reset the arms to their neutral positions while beginning to move.

- `reset_arms_duration` The speed at which the arms are reset in seconds.

- `scale_reset_arms_duration` If True, `reset_arms_duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds.

- `arrived_at` A distance or time determines whether the WheelchairReplicant arrived at the target.

- `collision_detection` The [`CollisionDetection`](../../replicant/collision_detection.md) rules.

- `collision_avoidance_distance` If `collision_detection.avoid == True`, an overlap will be cast at this distance from the Wheelchair Replicant to detect obstacles.

- `collision_avoidance_half_extents` If `collision_detection.avoid == True`, an overlap will be cast with these half extents to detect obstacles.

- `wheel_values` The [`WheelValues`](../wheel_values.md) that will be applied to the wheelchair's wheels.

- `reset_arms` If True, reset the arms to their neutral positions while beginning to move.

- `reset_arms_duration` The speed at which the arms are reset in seconds.

- `scale_reset_arms_duration` If True, `reset_arms_duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds.

- `arrived_at` A distance or time determines whether the WheelchairReplicant arrived at the target.

- `collision_detection` The [`CollisionDetection`](../../replicant/collision_detection.md) rules.

- `collision_avoidance_distance` If `collision_detection.avoid == True`, an overlap will be cast at this distance from the Wheelchair Replicant to detect obstacles.

- `collision_avoidance_half_extents` If `collision_detection.avoid == True`, an overlap will be cast with these half extents to detect obstacles.

***

## Functions

#### \_\_init\_\_

**`TurnTo(target, wheel_values, dynamic, collision_detection, previous, reset_arms, reset_arms_duration, scale_reset_arms_duration, arrived_at, collision_avoidance_distance, collision_avoidance_half_extents)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| target |  TARGET |  | The target. If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array. |
| wheel_values |  Optional[WheelValues] |  | The [`WheelValues`](../wheel_values.md) that will be applied to the wheelchair's wheels. If None, values will be derived from `angle`. |
| dynamic |  ReplicantDynamic |  | The [`ReplicantDynamic`](../../replicant/replicant_dynamic.md) data that changes per `communicate()` call. |
| collision_detection |  CollisionDetection |  | The [`CollisionDetection`](../../replicant/collision_detection.md) rules. |
| previous |  Optional[Action] |  | The previous action, if any. |
| reset_arms |  bool |  | If True, reset the arms to their neutral positions while beginning to move. |
| reset_arms_duration |  float |  | The speed at which the arms are reset in seconds. |
| scale_reset_arms_duration |  bool |  | If True, `reset_arms_duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds. |
| arrived_at |  float |  | If the angle between the traversed angle and the target angle is less than this threshold in degrees, the action succeeds. |
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