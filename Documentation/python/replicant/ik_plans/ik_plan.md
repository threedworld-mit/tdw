# IkPlan

`from tdw.replicant.ik_plans.ik_plan import IkPlan`

A data class that stores a list of [`ReachFor`](../actions/reach_for.md) actions.

An `IkPlan` takes the reach-for parameters and converts them into a list of [`ReachFor`](../actions/reach_for.md) actions.

The parameters of `IkPlan` are similar to that of a `ReachFor` action, but an `IkPlan` is *not* an action.

This is an abstract class. Subclasses of `IkPlan` define how the list of `ReachFor` actions is set.

An `IkPlan` is used by the [`ReachForWithPlan`](../actions/reach_for_with_plan.md) action. (From the Replicant API, this is combined with the `reach_for(target, arm)` function).

***

## Fields

- `duration` The total duration of the motion in seconds. Each [`ReachFor`](../actions/reach_for.md) action is a fraction of this. For example, if there are 2 [`ReachFor`](../actions/reach_for.md) actions, then the duration of each of them is `duration / 2`.

- `scale_duration` If True, `duration` will be multiplied by `framerate / 60`, ensuring smoother motions at faster-than-life simulation speeds.

- `arms` The [`Arm`](../arm.md)(s) that will reach for each target.

- `collision_detection` The [`CollisionDetection`](../collision_detection.md) rules.

- `previous` The previous action. Can be None.

- `targets` The targets per arm. If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array.

- `absolute` If True, the target position is in world space coordinates. If False, the target position is relative to the Replicant. Ignored if `target` is an int.

- `arrived_at` If the final [`ReachFor`](../actions/reach_for.md) action ends and the hand is this distance or less from the target, the motion succeeds.

- `max_distance` If at the start of the first [`ReachFor`](../actions/reach_for.md) action the target is further away than this distance from the hand, the action fails.

- `from_held` If False, the Replicant will try to move its hand to the `target`. If True, the Replicant will try to move its held object to the `target`.

- `held_point` The bounds point of the held object from which the offset will be calculated. Can be `"bottom"`, `"top"`, etc. For example, if this is `"bottom"`, the Replicant will move the bottom point of its held object to the `target`. This is ignored if `from_held == False` or ths hand isn't holding an object.

***

## Functions

#### \_\_init\_\_

**`IkPlan(targets, absolute, arrived_at, max_distance, arms, dynamic, collision_detection, previous, duration, scale_duration, from_held, held_point)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| targets |  List[TARGET] |  | The targets per arm. If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array. |
| absolute |  bool |  | If True, the target position is in world space coordinates. If False, the target position is relative to the Replicant. Ignored if `target` is an int. |
| arrived_at |  float |  | If the final [`ReachFor`](../actions/reach_for.md) action ends and the hand is this distance or less from the target, the motion succeeds. |
| max_distance |  float |  | If at the start of the first [`ReachFor`](../actions/reach_for.md) action the target is further away than this distance from the hand, the action fails. |
| arms |  List[Arm] |  | The [`Arm`](../arm.md)(s) that will reach for each target. |
| dynamic |  ReplicantDynamic |  | The [`ReplicantDynamic`](../replicant_dynamic.md) data that changes per `communicate()` call. |
| collision_detection |  CollisionDetection |  | The [`CollisionDetection`](../collision_detection.md) rules. |
| previous |  Optional[Action] |  | The previous action. Can be None. |
| duration |  float |  | The total duration of the motion in seconds. Each [`ReachFor`](../actions/reach_for.md) action is a fraction of this. For example, if there are 2 [`ReachFor`](../actions/reach_for.md) actions, then the duration of each of them is `duration / 2`. |
| scale_duration |  bool |  | If True, `duration` will be multiplied by `framerate / 60`, ensuring smoother motions at faster-than-life simulation speeds. |
| from_held |  bool |  | If False, the Replicant will try to move its hand to the `target`. If True, the Replicant will try to move its held object to the `target`. This is ignored if the hand isn't holding an object. |
| held_point |  str |  | The bounds point of the held object from which the offset will be calculated. Can be `"bottom"`, `"top"`, etc. For example, if this is `"bottom"`, the Replicant will move the bottom point of its held object to the `target`. This is ignored if `from_held == False` or ths hand isn't holding an object. |

#### get_actions

**`self.get_actions(resp, static, dynamic)`**


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| resp |  List[bytes] |  | The response from the build. |
| static |  ReplicantStatic |  | The [`ReplicantStatic`](../replicant_static.md) data that doesn't change after the Replicant is initialized. |
| dynamic |  ReplicantDynamic |  | The [`ReplicantDynamic`](../replicant_dynamic.md) data that changes per `communicate()` call. |

_Returns:_  A list of [`ReachFor`](../actions/reach_for.md) actions.