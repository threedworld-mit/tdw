##### Wheelchair Replicants

# Collision Detection

The Wheelchair Replicant will stop a motion if it detects a collision with an obstacle. It can also physically interact with objects in the scene.

## How Wheelchair Replicant physics works

If a Wheelchair Replicant collides with an object, by default its [action](actions.md) will end. This behavior can be overridden (see below). Assuming that the Wheelchair Replicant is *allowed* to collide with an object, it will physically interact with an object.

The Wheelchair Replicant can induce forces (by pushing an object, throwing an object, etc.) and *will* respond to forces to some extent. A fast-moving object can, for example, push the wheelchair to some extent. That said, the Wheelchair Replicant's position and rotation are constrained such that it can't tip over. The Wheelchair Replicant's arms aren't physics-driven, meaning that a Wheelchair Replicant's arms can push objects but can't be pushed by objects, and can effortlessly pick up any object regardless of its mass.

## `WheelchairReplicant.collision_detection`

The Wheelchair Replicant has a set of collision detection rules stored in `replicant.collision_detection`, which is a [`CollisionDetection`](../../python/replicant/collision_detection.md) data object.

These are *rules* that don't actually affect the physics behavior. They are just booleans that are referenced in the Python code to decide how to respond to physics events. For example, if `replicant.collision_detection.objects == True`, the Wheelchair Replicant will stop an action if it collides with an object. This *doesn't* affect whether a Replicant *can* collide with objects; it always can collide with objects.

Exactly how this works, and how to adjust the Wheelchair Replicant's behavior, differs between actions; see [Movement](movement.md) and [Arm articulation](arm_articulation_1.md) for more information.

## Enabling and disabling collision detection rules

`WheelchairReplicant.collision_detection` is designed to be adjusted during a simulation. You can, for example, tell the Wheelchair Replicant to ignore objects while walking and, once it is at its destination,  you can start an animation but tell the Wheelchair Replicant to stop the animation on object collisions.

## Low-level description

Wheelchair Replicants have colliders that act similarly to standard TDW object colliders. If the wheelchair collides with an object, it will can push the object out of the way. Its arms, however, work differently, and therefore its collision data needs to be handled differently than [the standard collision data](../physx/collisions.md). Instead, collision data is sent within [`Replicants` output data](../../api/output_data.md#Replicants), stored in [replicant.dynamic.collisions](../../python/replicant/replicant_dynamic.md). This data includes the body part ID and a list of object IDs that that body part collided with.

Within the build, the Wheelchair Replicant will [cast overlaps](https://docs.unity3d.com/ScriptReference/Physics.OverlapCapsule.html) rather than rely on standard collision detection.  This allows it to detect collisions with kinematic objects and objects without Rigidbodies and it also allows the Wheelchair Replicant to differentiate between body parts. The tradeoff is that there is no data for relative velocity, contact points, etc. (which in this case aren't actually needed).

## Wheelchair Replicants and Replicants

`WheelchairReplicant` and `Replicant` use the same `CollisionDetection` class and the same collision avoidance logic. There are significant differences between what happens when a collision is *not* avoided and actually occurs. A `WheelchairReplicant` can respond to collision forces while a `Replicant` cannot. A `WheelchairReplicant` can't move through kinematic objects, but a `Replicant` can.

***

**Next: [Movement](movement.md)**

[Return to the README](../../../README.md)

***

Output Data API:

- [`Replicants`](../../api/output_data.md#Replicants)

Python API:

- [`WheelchairReplicant`](../../python/add_ons/WheelchairReplicant.md)
- [`CollisionDetection`](../../python/replicant/collision_detection.md)
- [`ReplicantDynamic`](../../python/replicant/replicant_dynamic.md)
