##### Replicants

# Collision Detection

The Replicant will stop a [walk motion](movement.md), [arm motion](arm_articulation.md), or [animation](animation.md) if it detects a collision with an obstacle.

## How Replicant collision detection works

Collision detection works very differently for Replicants than for other objects in TDW, for three reasons:

1. The Replicant has a kinematic Rigidbody, meaning that it wouldn't normally interact with other kinematic Rigidbodies such as kitchen counters.
2. The Replicant's body parts don't have Rigidbodies, meaning that ordinarily it wouldn't be possible to distinguish them. For example, a collision between the left upper arm and an object would look the same in the output data as a collision between the right lower arm and an object.
3. We only need a small amount of collision metadata to control the Replicant; it is faster for the build to send only this information rather than generic TDW collision output data.

