##### Semantic states

# Overview

The **semantic state** of an object refers to a discrete descriptor of the object at runtime. For example, an oven with a door can be open and closed.

Because TDW is primarily a [physics-based simulation](../physx/overview.md), semantic states are for the most *not* built-in. In the above example, the oven door isn't actually ever open or closed; rather, it is at an angle between 0 and its maximum limit. In this case, you would need to define an angle past which the door is considered "open" vs. closed.