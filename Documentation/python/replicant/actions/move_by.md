# MoveBy

`from tdw.replicant.actions.move_by import MoveBy`

Walk a given distance.

The Replicant will continuously play a walk cycle animation until the action ends.

The action can end for several reasons depending on the collision detection rules (see [`self.collision_detection`](../collision_detection.md).

- If the Replicant walks the target distance, the action succeeds.
- If `self.collision_detection.previous_was_same == True`, and the previous action was `MoveBy` or `MoveTo`, and it was in the same direction (forwards/backwards), and the previous action ended in failure, this action ends immediately.
- If `self.collision_detection.avoid_obstacles == True` and the Replicant encounters a wall or object in its path:
  - If the object is in `self.collision_detection.exclude_objects`, the Replicant ignores it.
  - Otherwise, the action ends in failure.
- If the Replicant collides with an object or a wall and `self.collision_detection.objects == True` and/or `self.collision_detection.walls == True` respectively:
  - If the object is in `self.collision_detection.exclude_objects`, the Replicant ignores it.
  - Otherwise, the action ends in failure.

***

## Fields

- `distance` The target distance. If less than 0, the Replicant will walk backwards.

- `reset_arms` If True, reset the arms to their neutral positions while beginning the walk cycle.

- `reset_arms_duration` The speed at which the arms are reset in seconds.

- `scale_reset_arms_duration` If True, `reset_arms_duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds.

- `arrived_at` If at any point during the action the difference between the target distance and distance traversed is less than this, then the action is successful.

- `collision_avoidance_distance` If `collision_detection.avoid == True`, an overlap will be cast at this distance from the Wheelchair Replicant to detect obstacles.

- `collision_avoidance_half_extents` If `collision_detection.avoid == True`, an overlap will be cast with these half extents to detect obstacles.

- `record` The `HumanoidAnimationRecord` of the animation.

- `collision_detection` The [`CollisionDetection`](../collision_detection.md) rules.

- `forward` If True, play the animation forwards. If False, play the animation backwards.

- `loop` If True, the animation will continuously loop and the action will continue until interrupted.

- `status` [The current status of the action.](../action_status.md) By default, this is `ongoing` (the action isn't done).

- `initialized` If True, the action has initialized. If False, the action will try to send `get_initialization_commands(resp)` on this frame.

- `done` If True, this action is done and won't send any more commands.

- `status` [The current status of the action.](../action_status.md) By default, this is `ongoing` (the action isn't done).

- `initialized` If True, the action has initialized. If False, the action will try to send `get_initialization_commands(resp)` on this frame.

- `done` If True, this action is done and won't send any more commands.

***

## Functions

#### \_\_init\_\_

**`MoveBy(distance, dynamic, collision_detection, previous, reset_arms, reset_arms_duration, scale_reset_arms_duration, arrived_at, collision_avoidance_distance, collision_avoidance_half_extents)`**

**`MoveBy(distance, dynamic, collision_detection, previous, reset_arms, reset_arms_duration, scale_reset_arms_duration, arrived_at, collision_avoidance_distance, collision_avoidance_half_extents, animation="walking_2", library="humanoid_animations.json")`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| distance |  float |  | The target distance. If less than 0, the Replicant will walk backwards. |
| dynamic |  ReplicantDynamic |  | The [`ReplicantDynamic`](../replicant_dynamic.md) data that changes per `communicate()` call. |
| collision_detection |  CollisionDetection |  | The [`CollisionDetection`](../collision_detection.md) rules. |
| previous |  Optional[Action] |  | The previous action, if any. |
| reset_arms |  bool |  | If True, reset the arms to their neutral positions while beginning the walk cycle. |
| reset_arms_duration |  float |  | The speed at which the arms are reset in seconds. |
| scale_reset_arms_duration |  bool |  | If True, `reset_arms_duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds. |
| arrived_at |  float |  | If at any point during the action the difference between the target distance and distance traversed is less than this, then the action is successful. |
| collision_avoidance_distance |  float |  | If `collision_detection.avoid == True`, an overlap will be cast at this distance from the Wheelchair Replicant to detect obstacles. |
| collision_avoidance_half_extents |  Dict[str, float] |  | If `collision_detection.avoid == True`, an overlap will be cast with these half extents to detect obstacles. |
| animation |  str  | "walking_2" | The name of the walk animation. |
| library |  str  | "humanoid_animations.json" | The name of the walk animation's library. |

#### get_initialization_commands

**`self.get_initialization_commands(resp, static, dynamic, image_frequency)`**


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| resp |  List[bytes] |  | The response from the build. |
| static |  ReplicantStatic |  | The [`ReplicantStatic`](../replicant_static.md) data that doesn't change after the Replicant is initialized. |
| dynamic |  ReplicantDynamic |  | The [`ReplicantDynamic`](../replicant_dynamic.md) data that changes per `communicate()` call. |
| image_frequency |  ImageFrequency |  | An [`ImageFrequency`](../image_frequency.md) value describing how often image data will be captured. |

_Returns:_  A list of commands to initialize this action.

#### get_ongoing_commands

**`self.get_ongoing_commands(resp, static, dynamic)`**

Evaluate an action per-frame to determine whether it's done.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| resp |  List[bytes] |  | The response from the build. |
| static |  ReplicantStatic |  | The [`ReplicantStatic`](../replicant_static.md) data that doesn't change after the Replicant is initialized. |
| dynamic |  ReplicantDynamic |  | The [`ReplicantDynamic`](../replicant_dynamic.md) data that changes per `communicate()` call. |

_Returns:_  A list of commands to send to the build to continue the action.

#### get_end_commands

**`self.get_end_commands(resp, static, dynamic, image_frequency)`**


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| resp |  List[bytes] |  | The response from the build. |
| static |  ReplicantStatic |  | The [`ReplicantStatic`](../replicant_static.md) data that doesn't change after the Replicant is initialized. |
| dynamic |  ReplicantDynamic |  | The [`ReplicantDynamic`](../replicant_dynamic.md) data that changes per `communicate()` call. |
| image_frequency |  ImageFrequency |  | An [`ImageFrequency`](../image_frequency.md) value describing how often image data will be captured. |

_Returns:_  A list of commands that must be sent to end any action.