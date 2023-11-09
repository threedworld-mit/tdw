# ReplicantBase

`from tdw.add_ons.replicant_base import ReplicantBase`

Abstract base class for Replicants.

***

## Fields

- `initial_position` The initial position of the Replicant.

- `initial_rotation` The initial rotation of the Replicant.

- `replicant_id` The ID of this replicant.

- `action` The Replicant's current [action](../replicant/actions/action.md). Can be None (no ongoing action).

- `image_frequency` An [`ImageFrequency`](../replicant/image_frequency.md) value that sets how often images are captured.

- `collision_detection` [The collision detection rules.](../replicant/collision_detection.md) This determines whether the Replicant will immediately stop moving or turning when it collides with something.

- `static` The [`ReplicantStatic`](../replicant/replicant_static.md) data.

- `dynamic` The [`ReplicantDynamic`](../replicant/replicant_dynamic.md) data.

- `commands` These commands will be appended to the commands of the next `communicate()` call.

- `initialized` If True, this module has been initialized.

***

## Functions

#### \_\_init\_\_

**`ReplicantBase()`**

**`ReplicantBase(replicant_id=0, position=None, rotation=None, image_frequency=ImageFrequency.once, name="replicant_0", target_framerate=100)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| replicant_id |  int  | 0 | The ID of the Replicant. |
| position |  POSITION  | None | The position of the Replicant as an x, y, z dictionary or numpy array. If None, defaults to `{"x": 0, "y": 0, "z": 0}`. |
| rotation |  ROTATION  | None | The rotation of the Replicant in Euler angles (degrees) as an x, y, z dictionary or numpy array. If None, defaults to `{"x": 0, "y": 0, "z": 0}`. |
| image_frequency |  ImageFrequency  | ImageFrequency.once | An [`ImageFrequency`](../replicant/image_frequency.md) value that sets how often images are captured. |
| name |  str  | "replicant_0" | The name of the Replicant model. |
| target_framerate |  int  | 100 | The target framerate. It's possible to set a higher target framerate, but doing so can lead to a loss of precision in agent movement. |

#### get_initialization_commands

**`self.get_initialization_commands()`**

This function gets called exactly once per add-on. To re-initialize, set `self.initialized = False`.

_Returns:_  A list of commands that will initialize this add-on.

#### on_send

**`self.on_send(resp)`**

This is called within `Controller.communicate(commands)` after commands are sent to the build and a response is received.

Use this function to send commands to the build on the next `Controller.communicate(commands)` call, given the `resp` response.
Any commands in the `self.commands` list will be sent on the *next* `Controller.communicate(commands)` call.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| resp |  List[bytes] |  | The response from the build. |

#### before_send

**`self.before_send(commands)`**

This is called within `Controller.communicate(commands)` before sending commands to the build. By default, this function doesn't do anything.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| commands |  List[dict] |  | The commands that are about to be sent to the build. |

#### get_early_initialization_commands

**`self.get_early_initialization_commands()`**

This function gets called exactly once per add-on. To re-initialize, set `self.initialized = False`.

These commands are added to the list being sent on `communicate()` *before* any other commands, including those added by the user and by other add-ons.

Usually, you shouldn't override this function. It is useful for a small number of add-ons, such as loading screens, which should initialize before anything else.

_Returns:_  A list of commands that will initialize this add-on.

#### reach_for

**`self.reach_for(target, arm)`**

**`self.reach_for(target, arm, absolute=True, offhand_follows=False, arrived_at=0.09, max_distance=1.5, duration=0.25, scale_duration=True, from_held=False, held_point="bottom")`**

Reach for a target object or position. One or both hands can reach for the same or separate targets.

If target is an object, the target position is a point on the object.
If the object has affordance points, the target position is the affordance point closest to the hand.
Otherwise, the target position is the bounds position closest to the hand.

The Replicant's arm(s) will continuously over multiple `communicate()` calls move until either the motion is complete or the arm collides with something (see `self.collision_detection`).

- If the hand is near the target at the end of the action, the action succeeds.
- If the target is too far away at the start of the action, the action fails.
- The collision detection will respond normally to walls, objects, obstacle avoidance, etc.
- If `self.collision_detection.previous_was_same == True`, and if the previous action was a subclass of `ArmMotion`, and it ended in a collision, this action ends immediately.

Unlike [`Replicant`](replicant.md), this action doesn't support [IK plans](../replicant/ik_plans/ik_plan_type.md).

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| target |  Union[TARGET, List[TARGET] |  | The target(s). This can be a list (one target per hand) or a single value (the hand's target). If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array. |
| arm |  Union[Arm, List[Arm] |  | The [`Arm`](../replicant/arm.md) value(s) that will reach for each target as a single value or a list. Example: `Arm.left` or `[Arm.left, Arm.right]`. |
| absolute |  bool  | True | If True, the target position is in world space coordinates. If False, the target position is relative to the Replicant. Ignored if `target` is an int. |
| offhand_follows |  bool  | False | If True, the offhand will follow the primary hand, meaning that it will maintain the same relative position. Ignored if `arm` is a list or `target` is an int. |
| arrived_at |  float  | 0.09 | If at the end of the action the hand(s) is this distance or less from the target position, the action succeeds. |
| max_distance |  float  | 1.5 | The maximum distance from the hand to the target position. |
| duration |  float  | 0.25 | The duration of the motion in seconds. |
| scale_duration |  bool  | True | If True, `duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds. |
| from_held |  bool  | False | If False, the Replicant will try to move its hand to the `target`. If True, the Replicant will try to move its held object to the `target`. This is ignored if the hand isn't holding an object. |
| held_point |  str  | "bottom" | The bounds point of the held object from which the offset will be calculated. Can be `"bottom"`, `"top"`, etc. For example, if this is `"bottom"`, the Replicant will move the bottom point of its held object to the `target`. This is ignored if `from_held == False` or ths hand isn't holding an object. |

#### grasp

**`self.grasp(target, arm)`**

**`self.grasp(target, arm, angle=90, axis="pitch", relative_to_hand=True, offset=0)`**

Grasp a target object.

The action fails if the hand is already holding an object. Otherwise, the action succeeds.

When an object is grasped, it is made kinematic. Any objects contained by the object are parented to it and also made kinematic. For more information regarding containment in TDW, [read this](../../lessons/semantic_states/containment.md).

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| target |  int |  | The target object ID. |
| arm |  Arm |  | The [`Arm`](../replicant/arm.md) value for the hand that will grasp the target object. |
| angle |  Optional[float] | 90 | Continuously (per `communicate()` call, including after this action ends), rotate the the grasped object by this many degrees relative to the hand. If None, the grasped object will maintain its initial rotation. |
| axis |  Optional[str] | "pitch" | Continuously (per `communicate()` call, including after this action ends) rotate the grasped object around this axis relative to the hand. Options: `"pitch"`, `"yaw"`, `"roll"`. If None, the grasped object will maintain its initial rotation. |
| relative_to_hand |  bool  | True | If True, the object rotates relative to the hand holding it. If False, the object rotates relative to the Replicant. Ignored if `angle` or `axis` is None. |
| offset |  float  | 0 | Offset the object's position from the Replicant's hand by this distance. |

#### reset_arm

**`self.reset_arm(arm)`**

**`self.reset_arm(arm, duration=0.25, scale_duration=True)`**

Move arm(s) back to rest position(s). One or both arms can be reset at the same time.

The Replicant's arm(s) will continuously over multiple `communicate()` calls move until either the motion is complete or the arm collides with something (see `self.collision_detection`).

- The collision detection will respond normally to walls, objects, obstacle avoidance, etc.
- If `self.collision_detection.previous_was_same == True`, and if the previous action was an arm motion, and it ended in a collision, this action ends immediately.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| arm |  Union[Arm, List[Arm] |  | The [`Arm`](../replicant/arm.md) value(s) that will reach for the `target` as a single value or a list. Example: `Arm.left` or `[Arm.left, Arm.right]`. |
| duration |  float  | 0.25 | The duration of the motion in seconds. |
| scale_duration |  bool  | True | If True, `duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds. |

#### drop

**`self.drop(arm, offset)`**

**`self.drop(arm, max_num_frames=100, offset)`**

Drop a held target object.

The action ends when the object stops moving or the number of consecutive `communicate()` calls since dropping the object exceeds `self.max_num_frames`.

When an object is dropped, it is made non-kinematic. Any objects contained by the object are parented to it and also made non-kinematic. For more information regarding containment in TDW, [read this](../../lessons/semantic_states/containment.md).

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| arm |  Arm |  | The [`Arm`](../replicant/arm.md) holding the object. |
| max_num_frames |  int  | 100 | Wait this number of `communicate()` calls maximum for the object to stop moving before ending the action. |
| offset |  Union[float, np.ndarray, Dict[str, float] |  | Prior to being dropped, set the object's positional offset. This can be a float (a distance along the object's forward directional vector). Or it can be a dictionary or numpy array (a world space position). |

#### look_at

**`self.look_at()`**

**`self.look_at(target=target, duration=0.1, scale_duration=True)`**

Look at a target object or position.

The head will continuously move over multiple `communicate()` calls until it is looking at the target.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| target |  TARGET | target | The target. If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array. |
| duration |  float  | 0.1 | The duration of the motion in seconds. |
| scale_duration |  bool  | True | If True, `duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds. |

#### rotate_head

**`self.rotate_head()`**

**`self.rotate_head(axis=axis, angle=angle, duration=0.1, scale_duration=True)`**

Rotate the head by an angle around an axis.

The head will continuously move over multiple `communicate()` calls until it is looking at the target.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| axis |  str | axis | The axis of rotation. Options: `"pitch"`, `"yaw"`, `"roll"`. |
| angle |  float | angle | The target angle in degrees. |
| duration |  float  | 0.1 | The duration of the motion in seconds. |
| scale_duration |  bool  | True | If True, `duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds. |

#### reset_head

**`self.reset_head()`**

**`self.reset_head(duration=0.1, scale_duration=True)`**

Reset the head to its neutral rotation.

The head will continuously move over multiple `communicate()` calls until it is at its neutral rotation.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| duration |  float  | 0.1 | The duration of the motion in seconds. |
| scale_duration |  bool  | True | If True, `duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds. |

#### reset

**`self.reset()`**

**`self.reset(position=None, rotation=None)`**

Reset the Replicant. Call this when you reset the scene.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| position |  POSITION  | None | The position of the Replicant as an x, y, z dictionary or numpy array. If None, defaults to `{"x": 0, "y": 0, "z": 0}`. |
| rotation |  ROTATION  | None | The rotation of the Replicant in Euler angles (degrees) as an x, y, z dictionary or numpy array. If None, defaults to `{"x": 0, "y": 0, "z": 0}`. |