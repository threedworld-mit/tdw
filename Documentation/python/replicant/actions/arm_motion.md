# ArmMotion

`from tdw.replicant.actions.arm_motion import ArmMotion`

Abstract base class for actions related to Replicant arm motion.

Duration an arm motion, the Replicant's arm(s) will continuously over multiple `communicate()` calls move until either the motion is complete or the arm collides with something (see `self.collision_detection`).

- The collision detection will respond normally to walls, objects, obstacle avoidance, etc.
- If `self.collision_detection.previous_was_same == True`, and if the previous action was a subclass of `ArmMotion`, and it ended in a collision, this action ends immediately.

***

## Fields

- `arms` A list of [`Arm`](../arm.md) values that will reach for the `target`. Example: `[Arm.left, Arm.right]`.

- `collision_detection` The [`CollisionDetection`](../collision_detection.md) rules.

- `collisions` If the action fails in a collision, this is a list of arms that collided with something.

- `duration` The duration of the motion in seconds.

- `scale_duration` If True, `duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds.

- `status` [The current status of the action.](../action_status.md) By default, this is `ongoing` (the action isn't done).

- `initialized` If True, the action has initialized. If False, the action will try to send `get_initialization_commands(resp)` on this frame.

- `done` If True, this action is done and won't send any more commands.

***

## Functions

#### \_\_init\_\_

**`ArmMotion(arms, dynamic, collision_detection, previous, duration, scale_duration)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| arms |  List[Arm] |  | A list of [`Arm`](../arm.md) values that will reach for the `target`. Example: `[Arm.left, Arm.right]`. |
| dynamic |  ReplicantDynamic |  | The [`ReplicantDynamic`](../replicant_dynamic.md) data that changes per `communicate()` call. |
| collision_detection |  CollisionDetection |  | The [`CollisionDetection`](../collision_detection.md) rules. |
| previous |  Optional[Action] |  | The previous action. Can be None. |
| duration |  float |  | The duration of the motion in seconds. |
| scale_duration |  bool |  | If True, `duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds. |

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