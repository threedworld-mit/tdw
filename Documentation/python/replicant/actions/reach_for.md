# ReachFor

`from tdw.replicant.actions.reach_for import ReachFor`

Reach for a target object or position. One or both hands can reach for the target at the same time.

If target is an object, the target position is a point on the object.
If the object has affordance points, the target position is the affordance point closest to the hand.
Otherwise, the target position is the bounds position closest to the hand.

The Replicant's arm(s) will continuously over multiple `communicate()` calls move until either the motion is complete or the arm collides with something (see `self.collision_detection`).

- If the hand is near the target at the end of the action, the action succeeds.
- If the target is too far away at the start of the action, the action fails.
- The collision detection will respond normally to walls, objects, obstacle avoidance, etc.
- If `self.collision_detection.previous_was_same == True`, and if the previous action was a subclass of `ArmMotion`, and it ended in a collision, this action ends immediately.

***

## Fields

- `target` The target. If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array.

- `arrived_at` If the motion ends and the hand is this distance or less from the target, the action succeeds.

- `max_distance` If the target is further away from this distance at the start of the action, the action fails.

- `offhand_follows` If True, the offhand will follow the primary hand, meaning that it will maintain the same relative position. Ignored if `len(arms) > 1` or if `target` is an object ID.

- `from_held` If False, the Replicant will try to move its hand to the `target`. If True, the Replicant will try to move its held object to the `target`.

- `held_point` The bounds point of the held object from which the offset will be calculated. Can be `"bottom"`, `"top"`, etc. For example, if this is `"bottom"`, the Replicant will move the bottom point of its held object to the `target`. This is ignored if `from_held == False` or ths hand isn't holding an object.

- `arms` A list of [`Arm`](../arm.md) values that will reach for the `target`. Example: `[Arm.left, Arm.right]`.

- `collision_detection` The [`CollisionDetection`](../collision_detection.md) rules.

- `collisions` If the action fails in a collision, this is a list of arms that collided with something.

- `duration` The duration of the motion in seconds.

- `scale_duration` If True, `duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds.

- `status` [The current status of the action.](../action_status.md) By default, this is `ongoing` (the action isn't done).

- `initialized` If True, the action has initialized. If False, the action will try to send `get_initialization_commands(resp)` on this frame.

- `done` If True, this action is done and won't send any more commands.

- `duration` The duration of the motion in seconds.

- `scale_duration` If True, `duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds.

- `status` [The current status of the action.](../action_status.md) By default, this is `ongoing` (the action isn't done).

- `initialized` If True, the action has initialized. If False, the action will try to send `get_initialization_commands(resp)` on this frame.

- `done` If True, this action is done and won't send any more commands.

- `status` [The current status of the action.](../action_status.md) By default, this is `ongoing` (the action isn't done).

- `initialized` If True, the action has initialized. If False, the action will try to send `get_initialization_commands(resp)` on this frame.

- `done` If True, this action is done and won't send any more commands.

***

## Functions

#### \_\_init\_\_

**`ReachFor(target, offhand_follows, arrived_at, max_distance, arms, dynamic, collision_detection, previous, duration, scale_duration, from_held, held_point)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| target |  Union[int, np.ndarray, Dict[str, float] |  | The target. If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array. |
| offhand_follows |  bool |  | If True, the offhand will follow the primary hand, meaning that it will maintain the same relative position. Ignored if `len(arms) > 1` or if `target` is an object ID. |
| arrived_at |  float |  | If the motion ends and the hand is this distance or less from the target, the action succeeds. |
| max_distance |  float |  | If the target is further away from this distance at the start of the action, the action fails. |
| arms |  List[Arm] |  | A list of [`Arm`](../arm.md) values that will reach for the `target`. Example: `[Arm.left, Arm.right]`. |
| dynamic |  ReplicantDynamic |  | The [`ReplicantDynamic`](../replicant_dynamic.md) data that changes per `communicate()` call. |
| collision_detection |  CollisionDetection |  | The [`CollisionDetection`](../collision_detection.md) rules. |
| previous |  Optional[Action] |  | The previous action. Can be None. |
| duration |  float |  | The duration of the motion in seconds. |
| scale_duration |  bool |  | If True, `duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds. |
| from_held |  bool |  | If False, the Replicant will try to move its hand to the `target`. If True, the Replicant will try to move its held object to the `target`. This is ignored if the hand isn't holding an object. |
| held_point |  str |  | The bounds point of the held object from which the offset will be calculated. Can be `"bottom"`, `"top"`, etc. For example, if this is `"bottom"`, the Replicant will move the bottom point of its held object to the `target`. This is ignored if `from_held == False` or ths hand isn't holding an object. |

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