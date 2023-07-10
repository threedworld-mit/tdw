##### Replicants

# Collision Detection

The Replicant will stop a motion if it detects a collision with an obstacle. It can also physically interact with objects in the scene.

## How Replicant physics works

If a Replicant collides with an object, by default its [action](actions.md) will end. This behavior can be overridden (see below). Assuming that the Replicant is *allowed* to collide with an object, it will physically interact with an object.

In most respects, the Replicant will interact within the [physics engine](../physx/physx.md) like any other object. There is a significant difference, however: The Replicant is non-kinematic.

The Replicant won't interact with other kinematic objects or environment objects, which means that, barring additional collision detection rules, the Replicant can move through kinematic objects and walls.

The Replicant can induce forces (by pushing an object, throwing an object, etc.) but won't respond to forces. If an object is thrown at a Replicant, the object will bounce off the Replicant but the Replicant's position, speed, etc. won't be affected.

## `replicant.collision_detection`

The Replicant has a set of collision detection rules stored in `replicant.collision_detection`, which is a [`CollisionDetection`](../../python/replicant/collision_detection.md) data object.

These are *rules* that don't actually affect the physics behavior. They are just booleans that are referenced in the Python code to decide how to respond to physics events. For example, if `replicant.collision_detection.objects == True`, the Replicant will stop an action if it collides with an object. This *doesn't* affect whether a Replicant *can* collide with objects; it always can collide with objects.

Exactly how this works, and how to adjust the Replicant's behavior, differs between actions; see [Movement](movement.md), [Animation](animations.md), and [Arm articulation](arm_articulation_1.md) for more information.

## Enabling and disabling collision detection rules

`replicant.collision_detection` is designed to be adjusted during a simulation. You can, for example, tell the Replicant to ignore objects while walking and, once it is at its destination,  you can start an animation but tell the Replicant to stop the animation on object collisions.

## Low-level description

Replicant collision data isn't actually [the standard collision data](../physx/collisions.md). Instead, collision data is sent within [`Replicants`](../../api/output_data.md#Replicants), stored in [replicant_dynamic.collisions](../../python/replicant/replicant_dynamic.md). This data includes the body part ID and a list of object IDs that that body part collided with.

Within the build, the Replicant will [cast overlaps](https://docs.unity3d.com/ScriptReference/Physics.OverlapCapsule.html) rather than rely on standard collision detection.  This allows it to detect collisions with kinematic objects and objects without Rigidbodies and it also allows the Replicant to differentiate between body parts. The tradeoff is that there is no data for relative velocity, contact points, etc. (which in this case aren't actually needed).

***

**Next: [Movement](movement.md)**

[Return to the README](../../../README.md)

***

Output Data API:

- [`Replicants`](../../api/output_data.md#Replicants)

Python API:

- [`Replicant`](../../python/add_ons/replicant.md)
- [`CollisionDetection`](../../python/replicant/collision_detection.md)
- [`ReplicantDynamic`](../../python/replicant/replicant_dynamic.md)
