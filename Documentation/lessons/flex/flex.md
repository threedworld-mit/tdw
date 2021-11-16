##### Physics (Flex)

# Flex - Overview

NVIDIA Flex is a physics engine in TDW that supports particle-based soft body, cloth, and fluid dynamics.

![](images/flex_demo.gif)

## Core concepts of Flex

By default, simulations in TDW use [PhysX](../physx/physx.md). To create a Flex simulation, you must manually enable Flex.

Flex objects exist in a "Flex Container" and have "Flex Actors" (Solid Actor, Cloth Actor, etc.). Physics is simulated by modifying the actor's *particles*, calculated using a GPU.

## System requirements

- Linux
  - High-end NVIDIA GPU (e.g. Titan X) and drivers
  - CUDA 8
  - Ubuntu 16
- Windows
  - High-end NVIDIA GPU (e.g. Titan X) and drivers
  - _Windows Unity Editor only:_ Make sure that the Windows build settings are enabled.
- OS X
  - Flex is not supported on OS X

## Drawbacks

Unfortunately, there are many drawbacks to using Flex in your simulation. In general, if you only need rigidbody physics, you should almost always opt for the default [PhysX](../physx/physx.md) physics engine rather than Flex.

- **Flex is no longer supported by NVIDIA.** There are bugs in the Unity Flex plugin that unfortunately we can't fix. Flex and PhysX have been merged as of PhysX 5. However, Unity uses a much older version of PhysX and it's not known when, or if, it will ever be upgraded.
- Flex collision callbacks are very limited. Collision detection is supported *internally* but there is no direct way to [serialize collision "events" into output data.](../physx/collisions.md) In most Flex simulations, we use PhysX colliders, which will align with solid actors but won't perfectly align with cloth, soft, fluid, or source actors.

## Known bugs

- **Flex leaks memory when objects are destroyed.** This is a bug in the Unity Flex plugin that we can't fix. If you destroy objects with the command [`destroy_flex_object`](../../api/command_api.md#destroy_flex_object) instead of [`destroy_object`](../../api/command_api.md#destroy_object), *less* memory will be leaked.
- **Fluid simulations are supported only on Windows.** If you try loading fluids in Ubuntu 16, the screen will flip upside-down and the fluid will be invisible.
- Adding a Flex Source Actor with the `set_flex_source_actor` command disables all particle data for all Flex objects in the scene.
- If you teleport an object with `teleport_flex_object` or `teleport_and_rotate_flex_object`, the build must step through 4 phyiscs frames before the objects starts to move.

