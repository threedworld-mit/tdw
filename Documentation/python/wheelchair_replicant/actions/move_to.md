# MoveTo

`from tdw.wheelchair_replicant.actions.move_to import MoveTo`

Turn the wheelchair to a target position or object and then move to it.

The action can end for several reasons depending on the collision detection rules (see [`self.collision_detection`](../../replicant/collision_detection.md).

- If the Replicant moves the target distance (i.e. it reaches its target), the action succeeds.
- If `self.collision_detection.previous_was_same == True`, and the previous action was `MoveBy` or `MoveTo`, and it was in the same direction (forwards/backwards), and the previous action ended in failure, this action ends immediately.
- If `self.collision_detection.avoid_obstacles == True` and the Replicant encounters a wall or object in its path:
  - If the object is in `self.collision_detection.exclude_objects`, the Replicant ignores it.
  - Otherwise, the action ends in failure.
- If the Replicant collides with an object or a wall and `self.collision_detection.objects == True` and/or `self.collision_detection.walls == True` respectively:
  - If the object is in `self.collision_detection.exclude_objects`, the Replicant ignores it.
  - Otherwise, the action ends in failure.

***

## Fields

- `turning` If True, the wheelchair is turning. If False, the wheelchair is moving.

- `action` The current sub-action. This is first a `TurnTo`, then a `MoveBy`.

- `arrived_at` If at any point during the action the difference between the target distance and distance traversed is less than this, then the action is successful.

- `status` [The current status of the action.](../../replicant/action_status.md) By default, this is `ongoing` (the action isn't done).

- `initialized` If True, the action has initialized. If False, the action will try to send `get_initialization_commands(resp)` on this frame.

- `done` If True, this action is done and won't send any more commands.

***

## Functions

#### \_\_init\_\_

**`MoveTo(target, turn_wheel_values, move_wheel_values, dynamic, collision_detection, previous, reset_arms, reset_arms_duration, scale_reset_arms_duration, aligned_at, arrived_at)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| target |  TARGET |  | The target. If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array. |
| turn_wheel_values |  Optional[WheelValues] |  | The [`WheelValues`](../wheel_values.md) that will be applied to the wheelchair's wheels while it's turning. If None, values will be derived from the angle. |
| move_wheel_values |  Optional[WheelValues] |  | The [`WheelValues`](../wheel_values.md) that will be applied to the wheelchair's wheels while it's moving. If None, values will be derived from the distance. |
| dynamic |  ReplicantDynamic |  | The [`ReplicantDynamic`](../../replicant/replicant_dynamic.md) data that changes per `communicate()` call. |
| collision_detection |  CollisionDetection |  | The [`CollisionDetection`](../../replicant/collision_detection.md) rules. |
| previous |  Optional[Action] |  | The previous action, if any. |
| reset_arms |  bool |  | If True, reset the arms to their neutral positions while beginning to move. |
| reset_arms_duration |  float |  | The speed at which the arms are reset in seconds. |
| scale_reset_arms_duration |  bool |  | If True, `reset_arms_duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds. |
| aligned_at |  float |  | If the angle between the traversed angle and the target angle is less than this threshold in degrees, the action succeeds. |
| arrived_at |  float |  | If at any point during the action the difference between the target distance and distance traversed is less than this, then the action is successful. |

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