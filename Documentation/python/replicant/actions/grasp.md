# Grasp

`from tdw.replicant.actions.grasp import Grasp`

Grasp a target object.

The action fails if the hand is already holding an object. Otherwise, the action succeeds.

When an object is grasped, it is made kinematic. Any objects contained by the object are parented to it and also made kinematic. For more information regarding containment in TDW, [read this](../../../lessons/semantic_states/containment.md).

***

## Fields

- `target` The target object ID.

- `arm` The [`Arm`](../arm.md) value for the hand that will grasp the target object.

- `angle` Continuously (per `communicate()` call, including after this action ends), rotate the grasped object by this many degrees. If None, the grasped object will maintain its initial rotation.

- `axis` Continuously (per `communicate()` call, including after this action ends), rotate the grasped object around this axis. Options: `"pitch"`, `"yaw"`, `"roll"`. If None, the grasped object will maintain its initial rotation.

- `relative_to_hand` If True, the object rotates relative to the hand holding it. If False, the object rotates relative to the Replicant. Ignored if `angle` or `axis` is None.

- `offset` Offset the object's position from the Replicant's hand by this distance. If None, a default offset is used: `distance(left_bound_of_object, right_bound_of_object) / 3`.

- `status` [The current status of the action.](../action_status.md) By default, this is `ongoing` (the action isn't done).

- `initialized` If True, the action has initialized. If False, the action will try to send `get_initialization_commands(resp)` on this frame.

- `done` If True, this action is done and won't send any more commands.

***

## Functions

#### \_\_init\_\_

**`Grasp(target, arm, dynamic, angle, axis, relative_to_hand, offset)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| target |  int |  | The target object ID. |
| arm |  Arm |  | The [`Arm`](../arm.md) value for the hand that will grasp the target object. |
| dynamic |  ReplicantDynamic |  | The [`ReplicantDynamic`](../replicant_dynamic.md) data that changes per `communicate()` call. |
| angle |  Optional[float] |  | Continuously (per `communicate()` call, including after this action ends), rotate the the grasped object by this many degrees relative to the hand. If None, the grasped object will maintain its initial rotation. |
| axis |  Optional[str] |  | Continuously (per `communicate()` call, including after this action ends) rotate the grasped object around this axis relative to the hand. Options: `"pitch"`, `"yaw"`, `"roll"`. If None, the grasped object will maintain its initial rotation. |
| relative_to_hand |  bool |  | If True, the object rotates relative to the hand holding it. If False, the object rotates relative to the Replicant. Ignored if `angle` or `axis` is None. |
| offset |  Optional[float] |  | Offset the object's position from the Replicant's hand by this distance. If None, a default offset is used: `distance(left_bound_of_object, right_bound_of_object) / 3`. |

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