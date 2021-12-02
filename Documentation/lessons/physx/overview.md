##### Physics

# Overview

TDW supports three types of physics simulations:

1. [PhysX](https://docs.unity3d.com/2020.1/Documentation/Manual/PhysicsOverview.html) is the Unity Engine's built-in physics engine. It only supports rigidbody physics, which means  that behavior such as deformable bodies, fluids, cloth, etc. cannot be simulated. PhysX is relatively stable but not 100% deterministic. Because it is the default option, most controllers in TDW use PhysX.
2. [Flex](https://docs.nvidia.com/gameworks/content/gameworkslibrary/physx/flex/index.html) is a physics engine that can simulate rigidbodies, soft bodies, cloth, and fluids. It is less stable than PhysX. Only a subset of TDW [objects](../core_concepts/objects.md) can be used in Flex.
3. It is possible to totally disable physics in TDW, which can be useful if you just want to gather image data.

## Core concepts of physics engines

PhysX and Flex were both made for video game development, and therefore share a number of core concepts:

- In TDW, rendered frames, output data frames, and physics frames are identical. Every time you call `communicate()`, the build receives and executes commands, advances one physics frame, renders the scene (if applicable) and returns output data. There is an exception to this though, which will be covered later in this tutorial.
- You don't need to have an agent in the scene to apply a force. Forces can be applied directly to an object.
- The physics engine automatically updates the scene state in the background. You don't need to simulate physics from a controller. For example, if you want to roll a ball down a ramp, you only need to add the ball, add the ramp, and apply a small force. The physics engine will handle the rest of the motion.

## High-level API: `tdw_physics`

[`tdw_physics`](https://github.com/alters-mit/tdw_physics) is a high-level API for writing physics simulation controllers and outputting data to a standardized format. It includes PhysX and Flex scenarios.

`tdw_physics` can be very useful for quickly creating physics-enabled trials but it assumes that you know how the underlying system works. For this reason, we recommend that you read the rest of the tutorial and then try using `tdw_physics`.

***

**Next:**

- **[PhysX](physx.md)** (We recommend you read the PhysX tutorial regardless of whether or not you intend to only use Flex)
- **[Flex](../flex/flex.md)**

[Return to the README](../../../README.md)

***

High-level API:

- [`tdw_physics`](https://github.com/alters-mit/tdw_physics)