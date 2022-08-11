##### Physics

# Overview

TDW supports four types of physics simulations:

## 1. PhysX

**[PhysX](physx.md)** is the Unity Engine's built-in physics engine. Because it is the default option, most controllers in TDW use PhysX. If **you are create a rigidbody-only simulation, PhysX is almost always the best option.**

Advantages:

- By certain metrics, PhysX is extremely stable. While it may at times exhibit strange behavior, it will rarely crash or otherwise wholly fail.
- PhysX is very fast. It has been optimized for video games with hundreds or thousands of moving entities.
- PhysX has the best support for physics-driven [agents](../agents/overview.md). All of TDW's physics-driven agents such as robots use PhysX and can interface with the other physics engines only to a limited extent.

Disadvantages:

- PhysX is a rigidbody-only physics engine. It doesn't support deformable bodies, fluids, cloth, etc.
- PhysX is non-deterministic. Simulation behavior often varies between different computers.
- PhysX is known to have strange glitches, especially when two objects accidentally overlap with each other.

## 2. Obi

**[Obi](../obi/obi.md)** is a physics engine that runs on top of PhysX. It supports rigidbodies, softbodies, cloth, and fluids using particles.

Advantages:

- Obi can simulate physical behavior such as fluids that PhysX can't.
- Obi can be combined seamlessly with PhysX.
- Obi is very stable, comparable to PhysX.

Disadvantages:

- Obi is the newest physics engine to be added in TDW and as such hasn't been fully implemented. Right now, it is possible to simulate Obi fluids in TDW but not cloth, softbodies, etc.
- Obi is much slower than either PhysX or Flex.

## 3. Flex

**[Flex](../flex/flex.md)** is a physics engine that supports rigidbodies, softbodies, cloth, and fluids using particles.

Flex is similar to Obi. It was added to TDW years before Obi was added. When possible, we recommend using Obi instead of Flex.

Advantages:

- Flex can simulate physical behavior such as fluids that PhysX can't.
- Flex is much faster than Obi because it utilizes the GPU while Obi is CPU-only.

Disadvantages:

- Flex doesn't work on OS X.
- Flex fluids don't work on OS X or Linux.
- Flex is a discontinued product and has many known bugs that can't be resolved in TDW.
- Only a subset of TDW [objects](../core_concepts/objects.md) can be used in Flex.

## 4. No physics

It is possible to totally disable physics in TDW, which can be useful if you just want to gather image data.

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