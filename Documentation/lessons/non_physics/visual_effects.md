##### Non-physics objects

# Visual Effects

A **visual effect** in TDW is a specialized object that can be visually rendered but is not physically embodied. Visual effects don't have colliders and won't respond to physics events. Visual effects are "objects" in that they have a position, rotation, and scale, but they aren't standard physically embodied TDW objects, which means that commands such as `add_object` or `teleport_object` won't work for a visual effect.

## How to add a visual effect to a scene

Visual effects are stored as asset bundles, just like [standard TDW objects](../core_concepts/objects.md). 

You can add a visual effect via the [`add_visual_effect`](../../api/command_api.md#add_visual_effect) command, or via the wrapper function `Controller.get_add_visual_effect(name, effect_id, position, rotation, library)`:

**TODO**

## The `VisualEffectLibrarian`

Metadata for visual effects is stored in a [`VisualEffectLibrarian`](../../python/librarian/visual_effect_librarian.md). Each `VisualEffectRecord` stores the effect's name and asset bundle URLs:

**TODO**

## How to adjust a visual effect

In TDW's backend C# code, visual effects share some common code with [line renderers](line_renderers.md), [position markers](position_markers.md), and [textured quads](textured_quads.md). However, you can only use visual effect commands:

- [`destroy_visual_effect`](../../api/command_api.md#destroy_visual_effect)
- [`scale_visual_effect`](../../api/command_api.md#scale_visual_effect)
- [`parent_visual_effect_to_object`](../../api/command_api.md#parent_visual_effect_to_object)
- [`unparent_visual_effect`](../../api/command_api.md#unparent_visual_effect)
- [`teleport_visual_effect`](../../api/command_api.md#teleport_visual_effect)
- [`rotate_visual_effect_by`](../../api/command_api.md#rotate_visual_effect_by)
- [`rotate_visual_effect_to`](../../api/command_api.md#rotate_visual_effect_to)

**TODO**

***

**This is the last document in the "Non-physics objects" tutorial.**

[Return to the README](../../../README.md)

***

Example controllers:

- **TODO**

Python API:

- [`VisualEffectLibrarian`](../../python/librarian/visual_effect_librarian.md)

Command API:

- [`add_visual_effect`](../../api/command_api.md#add_visual_effect)
- [`destroy_visual_effect`](../../api/command_api.md#destroy_visual_effect)
- [`scale_visual_effect`](../../api/command_api.md#scale_visual_effect)
- [`parent_visual_effect_to_object`](../../api/command_api.md#parent_visual_effect_to_object)
- [`unparent_visual_effect`](../../api/command_api.md#unparent_visual_effect)
- [`teleport_visual_effect`](../../api/command_api.md#teleport_visual_effect)
- [`rotate_visual_effect_by`](../../api/command_api.md#rotate_visual_effect_by)
- [`rotate_visual_effect_to`](../../api/command_api.md#rotate_visual_effect_to)