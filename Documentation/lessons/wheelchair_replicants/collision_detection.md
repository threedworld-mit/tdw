##### Wheelchair Replicants

# Collision Detection

The Wheelchair Replicant will stop a motion if it detects a collision with an obstacle. It can also physically interact with objects in the scene.

## How Wheelchair Replicant physics works

If a Wheelchair Replicant collides with an object, by default its [action](actions.md) will end. This behavior can be overridden (see below). Assuming that the Wheelchair Replicant is *allowed* to collide with an object, it will physically interact with an object.

The Wheelchair Replicant can induce forces (by pushing an object, throwing an object, etc.) and, unlike the Replicant *will* respond to forces. That said, the WheelchairReplicant's position and rotation are constrained such that it can't tip over.

## `WheelchairReplicant.collision_detection`

The Wheelchair Replicant has a set of collision detection rules stored in `WheelchairReplicant.collision_detection`, which is a [`CollisionDetection`](../../python/Wheelchair Replicant/collision_detection.md) data object.

These are *rules* that don't actually affect the physics behavior. They are just booleans that are referenced in the Python code to decide how to respond to physics events. For example, if `WheelchairReplicant.collision_detection.objects == True`, the Wheelchair Replicant will stop an action if it collides with an object. This *doesn't* affect whether a Wheelchair Replicant *can* collide with objects; it always can collide with objects.

Exactly how this works, and how to adjust the Wheelchair Replicant's behavior, differs between actions; see [Movement](movement.md), [Animation](animations.md), and [Arm articulation](arm_articulation_1.md) for more information.

`WheelchairReplicant` and `Replicant` share the same `CollisionDetection` class. The *rules* governing each agent type's basic collision avoidance plans are the same and internally are handled identically, but the collision *behavior*, i.e. what physically happens once a collision occurs, is different.

## Enabling and disabling collision detection rules

`WheelchairReplicant.collision_detection` is designed to be adjusted during a simulation. You can, for example, tell the Wheelchair Replicant to ignore objects while walking and, once it is at its destination,  you can start an animation but tell the Wheelchair Replicant to stop the animation on object collisions.

## Low-level description

Wheelchair Replicant collision data isn't actually [the standard collision data](../physx/collisions.md). Instead, collision data is sent within [`Replicants`](../../api/output_data.md#Replicants), stored in [Wheelchair Replicant_dynamic.collisions](../../python/wheelchair_replicant/wheelchair_replicant_dynamic.md). This data includes the body part ID and a list of object IDs that that body part collided with.

Within the build, the Wheelchair Replicant will [cast overlaps](https://docs.unity3d.com/ScriptReference/Physics.OverlapCapsule.html) rather than rely on standard collision detection.  This allows it to detect collisions with kinematic objects and objects without Rigidbodies and it also allows the Wheelchair Replicant to differentiate between body parts. The tradeoff is that there is no data for relative velocity, contact points, etc. (which in this case aren't actually needed).

***

**Next: [Movement](movement.md)**

[Return to the README](../../../README.md)

***

Output Data API:

- [`Replicants`](../../api/output_data.md#Replicants)

Python API:

- [`WheelchairReplicant`](../../python/add_ons/WheelchairReplicant.md)
- [`CollisionDetection`](../../python/replicant/collision_detection.md)
- [`WheelchairReplicantDynamic`](../../python/wheelchair_replicant/wheelchair_replicant_dynamic.md)
