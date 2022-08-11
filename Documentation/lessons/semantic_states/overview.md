##### Semantic states

# Overview

The **semantic state** of an object refers to a discrete descriptor of the object at runtime. For example, an oven with a door can be open and closed. Because TDW is primarily a [physics-based simulation](../physx/overview.md), semantic states aren't always predefined. In the case of the oven door, it isn't actually ever "open" or "closed"; rather, it is at an angle between 0 and its maximum limit. In this case, you would need to define an angle past which the door is considered "open" vs. closed. In other cases, the semantic state may be more concretely defined.

This section will cover some of the most commonly used semantic states in TDW and how to either define them or read them from existing API calls.

***

**Next: [Line of sight (`Raycast` output data)](raycast.md)**

[Return to the README](../../../README.md)