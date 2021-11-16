##### Physics (Flex)

# Flex - Overview

## Drawbacks

Unfortunately, there are many drawbacks to using Flex in your simulation. In general, if you only need rigidbody physics, you should almost always opt for the default [PhysX](../physx/physx.md) physics engine rather than Flex.

- **Flex is no longer supported by NVIDIA.** There are bugs in the Unity Flex plugin that unfortunately we can't fix. Flex and PhysX have been merged as of PhysX 5. However, Unity uses a much older version of PhysX and it's not known when, or if, it will ever be upgraded.

## Known bugs

- **Flex leaks memory when objects are destroyed.** This is a bug in the Unity Flex plugin that we can't fix. If you destroy objects with the command [`destroy_flex_object`](../../api/command_api.md#destroy_flex_object) instead of [`destroy_object`](../../api/command_api.md#destroy_object), *less* memory will be leaked.
- If you teleport an object with `teleport_flex_object` or `teleport_and_rotate_flex_object`, the build must step through 4 phyiscs frames before the objects starts to move.
- Adding a Flex Source Actor with the `set_flex_source_actor` command disables all particle data for all Flex objects in the scene.

