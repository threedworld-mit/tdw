# Replicant

`from tdw.add_ons.replicant import Replicant`

A Replicant is a human-like agent that can interact with the scene with pseudo-physics behavior.

When a Replicant collides with objects, it initiates a physics-driven collision. The Replicant's own movements are driven by non-physics animation.

A Replicant can walk, turn, reach for positions or objects, grasp and drop objects, and turn its head to look around.

***

## Class Variables

| Variable | Type | Description | Value |
| --- | --- | --- | --- |
| `LIBRARY_NAME` | str | The Replicants library file. You can override this to use a custom library (e.g. a local library). | `"replicants.json"` |

***

## Fields

- `initial_position` The initial position of the Replicant.

- `initial_rotation` The initial rotation of the Replicant.

- `static` The [`ReplicantStatic`](../replicant/replicant_static.md) data.

- `dynamic` The [`ReplicantDynamic`](../replicant/replicant_dynamic.md) data.

- `replicant_id` The ID of this replicant.

- `action` The Replicant's current [action](../replicant/actions/action.md). Can be None (no ongoing action).

- `image_frequency` An [`ImageFrequency`](../replicant/image_frequency.md) value that sets how often images are captured.

- `collision_detection` [The collision detection rules.](../replicant/collision_detection.md) This determines whether the Replicant will immediately stop moving or turning when it collides with something.

***

## Functions

#### \_\_init\_\_

**`Replicant(position, rotation)`**

**`Replicant(replicant_id=0, position, rotation, image_frequency=ImageFrequency.once, name="replicant_0", target_framerate=100)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| replicant_id |  int  | 0 | The ID of the Replicant. |
| position |  Union[Dict[str, float] |  | The position of the Replicant as an x, y, z dictionary or numpy array. If None, defaults to `{"x": 0, "y": 0, "z": 0}`. |
| rotation |  Union[Dict[str, float] |  | The rotation of the Replicant in Euler angles (degrees) as an x, y, z dictionary or numpy array. If None, defaults to `{"x": 0, "y": 0, "z": 0}`. |
| image_frequency |  ImageFrequency  | ImageFrequency.once | An [`ImageFrequency`](../replicant/image_frequency.md) value that sets how often images are captured. |
| name |  str  | "replicant_0" | The name of the Replicant model. |
| target_framerate |  int  | 100 | The target framerate. It's possible to set a higher target framerate, but doing so can lead to a loss of precision in agent movement. |

***

### Movement

These actions move or turn the Replicant.

#### turn_by

**`self.turn_by(angle)`**

Turn the Replicant by an angle.

This is a non-animated action, meaning that the Replicant will immediately snap to the angle.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| angle |  float |  | The target angle in degrees. Positive value = clockwise turn. |

#### turn_to

**`self.turn_to(target)`**

Turn the Replicant to face a target object or position.

This is a non-animated action, meaning that the Replicant will immediately snap to the angle.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| target |  Union[int, Dict[str, float] |  | The target. If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array. |

#### move_by

**`self.move_by(distance)`**

**`self.move_by(distance, reset_arms=True, reset_arms_duration=0.25, scale_reset_arms_duration=True, arrived_at=0.1, max_walk_cycles=100)`**

Walk a given distance.

The Replicant will continuously play a walk cycle animation until the action ends.

The action can end for several reasons depending on the collision detection rules (see [`self.collision_detection`](../replicant/collision_detection.md).

- If the Replicant walks the target distance, the action succeeds.
- If `collision_detection.previous_was_same == True`, and the previous action was `move_by()` or `move_to()`, and it was in the same direction (forwards/backwards), and the previous action ended in failure, this action ends immediately.
- If `self.collision_detection.avoid_obstacles == True` and the Replicant encounters a wall or object in its path:
- If the object is in `self.collision_detection.exclude_objects`, the Replicant ignores it.
- Otherwise, the action ends in failure.
- If the Replicant collides with an object or a wall and `self.collision_detection.objects == True` and/or `self.collision_detection.walls == True` respectively:
- If the object is in `self.collision_detection.exclude_objects`, the Replicant ignores it.
- Otherwise, the action ends in failure.
- If the Replicant takes too long to reach the target distance, the action ends in failure (see `self.max_walk_cycles`).

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| distance |  float |  | The target distance. If less than 0, the Replicant will walk backwards. |
| reset_arms |  bool  | True | If True, reset the arms to their neutral positions while beginning the walk cycle. |
| reset_arms_duration |  float  | 0.25 | The speed at which the arms are reset in seconds. |
| scale_reset_arms_duration |  bool  | True | If True, `reset_arms_duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds. |
| arrived_at |  float  | 0.1 | If at any point during the action the difference between the target distance and distance traversed is less than this, then the action is successful. |
| max_walk_cycles |  int  | 100 | The walk animation will loop this many times maximum. If by that point the Replicant hasn't reached its destination, the action fails. |

#### move_to

**`self.move_to(target)`**

**`self.move_to(target, reset_arms=True, reset_arms_duration=0.25, scale_reset_arms_duration=True, arrived_at=0.1, max_walk_cycles=100, bounds_position="center")`**

Turn the Replicant to a target position or object and then walk to it.

While walking, the Replicant will continuously play a walk cycle animation until the action ends.

The action can end for several reasons depending on the collision detection rules (see [`self.collision_detection`](../replicant/collision_detection.md).

- If the Replicant walks the target distance, the action succeeds.
- If `collision_detection.previous_was_same == True`, and the previous action was `move_by()` or `move_to()`, and it was in the same direction (forwards/backwards), and the previous action ended in failure, this action ends immediately.
- If `self.collision_detection.avoid_obstacles == True` and the Replicant encounters a wall or object in its path:
- If the object is in `self.collision_detection.exclude_objects`, the Replicant ignores it.
- Otherwise, the action ends in failure.
- If the Replicant collides with an object or a wall and `self.collision_detection.objects == True` and/or `self.collision_detection.walls == True` respectively:
- If the object is in `self.collision_detection.exclude_objects`, the Replicant ignores it.
- Otherwise, the action ends in failure.
- If the Replicant takes too long to reach the target distance, the action ends in failure (see `self.max_walk_cycles`).

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| target |  Union[int, Dict[str, float] |  | The target. If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array. |
| reset_arms |  bool  | True | If True, reset the arms to their neutral positions while beginning the walk cycle. |
| reset_arms_duration |  float  | 0.25 | The speed at which the arms are reset in seconds. |
| scale_reset_arms_duration |  bool  | True | If True, `reset_arms_duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds. |
| arrived_at |  float  | 0.1 | If at any point during the action the difference between the target distance and distance traversed is less than this, then the action is successful. |
| max_walk_cycles |  int  | 100 | The walk animation will loop this many times maximum. If by that point the Replicant hasn't reached its destination, the action fails. |
| bounds_position |  str  | "center" | If `target` is an integer object ID, move towards this bounds point of the object. Options: `"center"`, `"top`", `"bottom"`, `"left"`, `"right"`, `"front"`, `"back"`. |

***

### Arm Articulation

These actions move and bend the joints of the Replicant's arms.

#### reach_for

**`self.reach_for(target, arm)`**

**`self.reach_for(target, arm, absolute=True, offhand_follows=False, arrived_at=0.09, max_distance=1.5, duration=0.25, scale_duration=True)`**

Reach for a target object or position. One or both hands can reach for the target at the same time.

If target is an object, the target position is a point on the object.
If the object has affordance points, the target position is the affordance point closest to the hand.
Otherwise, the target position is the bounds position closest to the hand.

The Replicant's arm(s) will continuously over multiple `communicate()` calls move until either the motion is complete or the arm collides with something (see `self.collision_detection`).

- If the hand is near the target at the end of the action, the action succeeds.
- If the target is too far away at the start of the action, the action fails.
- The collision detection will respond normally to walls, objects, obstacle avoidance, etc.
- If `self.collision_detection.previous_was_same == True`, and if the previous action was a subclass of `ArmMotion`, and it ended in a collision, this action ends immediately.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| target |  Union[int, Dict[str, float] |  | The target. If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array. |
| arm |  Union[Arm, List[Arm] |  | The [`Arm`](../replicant/arm.md) value(s) that will reach for the `target` as a single value or a list. Example: `Arm.left` or `[Arm.left, Arm.right]`. |
| absolute |  bool  | True | If True, the target position is in world space coordinates. If False, the target position is relative to the Replicant. Ignored if `target` is an int. |
| offhand_follows |  bool  | False | If True, the offhand will follow the primary hand, meaning that it will maintain the same relative position. Ignored if `arm` is a list or `target` is an int. |
| arrived_at |  float  | 0.09 | If at the end of the action the hand(s) is this distance or less from the target position, the action succeeds. |
| max_distance |  float  | 1.5 | The maximum distance from the hand to the target position. |
| duration |  float  | 0.25 | The duration of the motion in seconds. |
| scale_duration |  bool  | True | If True, `duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds. |

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

***

### Object Interaction

These actions involve interaction with other objects, e.g. grasping or dropping.

#### grasp

**`self.grasp(target, arm)`**

**`self.grasp(target, arm, angle=90, axis="pitch")`**

Grasp a target object.

The action fails if the hand is already holding an object. Otherwise, the action succeeds.

When an object is grasped, it is made kinematic. Any objects contained by the object are parented to it and also made kinematic. For more information regarding containment in TDW, [read this](../../lessons/semantic_states/containment.md).

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| target |  int |  | The target object ID. |
| arm |  Arm |  | The [`Arm`](../replicant/arm.md) value for the hand that will grasp the target object. |
| angle |  Optional[float] | 90 | Continuously (per `communicate()` call, including after this action ends), rotate the the grasped object by this many degrees relative to the hand. If None, the grasped object will maintain its initial rotation. |
| axis |  Optional[str] | "pitch" | Continuously (per `communicate()` call, including after this action ends) rotate the grasped object around this axis relative to the hand. Options: `"pitch"`, `"yaw"`, `"roll"`. If None, the grasped object will maintain its initial rotation. |

#### drop

**`self.drop(arm)`**

**`self.drop(arm, max_num_frames=100)`**

Drop a held target object.

The action ends when the object stops moving or the number of consecutive `communicate()` calls since dropping the object exceeds `self.max_num_frames`.

When an object is dropped, it is made non-kinematic. Any objects contained by the object are parented to it and also made non-kinematic. For more information regarding containment in TDW, [read this](../../lessons/semantic_states/containment.md).

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| arm |  Arm |  | The [`Arm`](../replicant/arm.md) holding the object. |
| max_num_frames |  int  | 100 | Wait this number of `communicate()` calls maximum for the object to stop moving before ending the action. |

***

### Head

These actions rotate the Replicant's head.

#### look_at

**`self.look_at()`**

**`self.look_at(target=target, duration=0.1, scale_duration=True)`**

Look at a target object or position.

The head will continuously move over multiple `communicate()` calls until it is looking at the target.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| target |  Union[int, np.ndarray, Dict[str, float] | target | The target. If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array. |
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

***

### Animation

These actions play arbitrary humanoid animations.

#### animate

**`self.animate(animation)`**

**`self.animate(animation, library="humanoid_animations.json")`**

Play an animation.

The animation will end either when the animation clip is finished or if the Replicant collides with something (see [`self.collision_detection`](../replicant/collision_detection.md)).

- The collision detection will respond normally to walls, objects, obstacle avoidance, etc.
- If `self.collision_detection.previous_was_same == True`, and it was the same animation, and it ended in a collision, this action ends immediately.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| animation |  str |  | The name of the animation. |
| library |  str  | "humanoid_animations.json" | The animation library. |

***

### Misc.

Misc. non-action functions.

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

#### reset

**`self.reset(position, rotation)`**

Reset the Replicant. Call this when you reset the scene.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| position |  Union[Dict[str, float] |  | The position of the Replicant as an x, y, z dictionary or numpy array. If None, defaults to `{"x": 0, "y": 0, "z": 0}`. |
| rotation |  Union[Dict[str, float] |  | The rotation of the Replicant in Euler angles (degrees) as an x, y, z dictionary or numpy array. If None, defaults to `{"x": 0, "y": 0, "z": 0}`. |

***

