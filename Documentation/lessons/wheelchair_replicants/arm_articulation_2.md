##### Wheelchair Replicants

# Arm articulation, pt. 2: Grasp and drop objects

*Replicant arm articulation is a complex topic. [Part 1](arm_articulation_1.md) covers basic arm articulation actions. This document covers grasping and dropping. [Part 3](arm_articulation_3.md) covers more advanced examples that use some additional optional parameters.*

The Wheelchair Replicant can grasp and drop objects. Each hand can grasp exactly one object at a time.

## The `grasp(target, arm)` action

`grasp(target, arm)` will tell the Wheelchair Replicant to grasp an object. **This is a non-physics, non-motion action. The Wheelchair Replicant WILL NOT bend its arm towards the target.** To properly grasp, first call [`reach_for(target, arm)`](arm_articulation_1.md), *then* `grasp(target, arm)`.

When a Wheelchair Replicant grasps an object, the object becomes kinematic and continuously tracks the Wheelchair Replicant's hand. If the object [contains other objects](../semantic_states/containment.md), those objects will also become kinematic and will be parented to the root grasped object.

### The target position

The Wheelchair Replicant will grasp the target at a position defined by the build using affordance points and bounds positions. This is identical to the system used for `reach_for(target, arm)`, which you can read about [here](arm_articulation_1.md).

### Low-level description

`replicant.grasp(target, arm)` sets `replicant.action` to a [`Grasp`](../../python/replicant/actions/grasp.md) action. 

In addition to [the usual `Action` initialization commands](actions.md), `Grasp` sends [`replicant_grasp_object`](../../api/command_api.md#replicant_grasp_object). An object can be grasped only if it has a non-kinematic Rigidbody that isn't held by another Wheelchair Replicant or Replicant. If grasped, the object will become kinematic. The action additionally reads [`Containment`](../../api/output_data.md#Containment) for any objects [contained by the target object](../semantic_states/containment.md). Every contained object is parented to the grasped object via [`parent_object_to_object`](../../api/command_api.md#parent_object_to_object) and made kinematic via [`set_kinematic_state`](../../api/command_api.md#set_kinematic_state). To prevent collisions between the grasped object(s) and the agent, the action also sends [`ignore_collisions`](../../api/command_api.md#ignore_collisions).

If `angle` is not None and `axis` is not None, the action initializes object rotation via [`replicant_set_grasped_object_rotation`](../../api/command_api.md#replicant_set_grasped_object_rotation).

Assuming that the object can be grasped, the `Grasp` action always succeeds (i.e. there is no physics-related failure state).

A grasped object is *not* parented to its hand or connected to the object in any way. This is due to how the underlying FinalIK system updates per frame vs. how TDW updates per frame. Instead, the grasped object moves and rotates itself to the Replicant's hand per `communicate()` call.

## The `drop(arm)` action

`drop(arm)` will drop any object held by the hand corresponding to `arm`. The action ends in success when the dropped object stops moving or if `communicate()` has been called too many times (see below). The action ends in failure if the Wheelchair Replicant isn't grasping the object.

### The `max_num_frames` parameter

Certain objects such as spheres tend to roll for a long time after being dropped. To prevent the `drop(arm)` action from continuing indefinitely, the action includes a `max_num_frames` parameter. The action will always end after this many `communicate()` calls.

### Low-level description

`replicant.drop(arm)` sets `replicant.action` to a [`Drop`](../../python/replicant/actions/drop.md) action. 

In addition to [the usual `Action` initialization commands](actions.md), `Drop` sends [`replicant_drop_object`](../../api/command_api.md#replicant_drop_object). To enable collisions between the grasped object(s) and the agent, the action also sends [`ignore_collisions`](../../api/command_api.md#ignore_collisions).

Per `communicate()` call, the `Drop` action checks if the object has stopped moving using [`Transforms`](../../api/output_data.md#Transforms) output data. If so, the action succeeds.

## Wheelchair Replicants and Replicants

The Wheelchair Replicant and the Replicant have the exact same `drop(arm)` and `grasp(target, arm)` actions. They use the exact same code and action classes.

The transform marking the position of the Wheelchair Replicant's hand is in a different position and local rotation than the Replicant's. Because of this, objects will move relative to a point closer to the Wheelchair Replicant's wrist than its palm. You can handle this by setting optional parameters in the `grasp(target, arm)` action, as described in the next document.

***

**Next: [Arm articulation, pt. 3: Advanced topics](arm_articulation_3.md)**

[Return to the README](../../../README.md)

***

Command API:

- [`replicant_grasp_object`](../../api/command_api.md#replicant_grasp_object)
- [`parent_object_to_object`](../../api/command_api.md#parent_object_to_object)
- [`set_kinematic_state`](../../api/command_api.md#set_kinematic_state)
- [`replicant_set_grasped_object_rotation`](../../api/command_api.md#replicant_set_grasped_object_rotation)
- [`replicant_drop_object`](../../api/command_api.md#replicant_drop_object)
- [`ignore_collisions`](../../api/command_api.md#ignore_collisions)

Output Data API:

- [`Containment`](../../api/output_data.md#Containment)
- [`Transforms`](../../api/output_data.md#Transforms)

Python API:

- [`WheelchairReplicant`](../../python/add_ons/wheelchair_replicant.md)
- [`Grasp`](../../python/replicant/actions/grasp.md)
- [`Drop`](../../python/replicant/actions/drop.md)