##### Non-physics objects

# Overview

There are various types of objects in TDW that are *non-physics objects*, meaning that they won't interact with [PhysX](../physx/physx.md) or [Flex](../flex/flex.md). Usually, these objects are used in purely visual simulations or for debugging.

Non-physics objects have been added into TDW in a relatively piecemeal fashion. Some are are technically [objects](../core_concepts/objects.md) in the TDW sense, meaning that they will respond to non-physics object commands. For example, `teleport_object` will work with [non-physics humanoids](humanoids.md) but `set_mass` will not. Other non-physics objects use entirely different backend code. For example, [position markers](position_markers.md) are *not* objects in the TDW sense and will only respond to position marker commands. 

***

**Next: [Position markers](position_markers.md)**

[Return to the README](../../../README.md)

