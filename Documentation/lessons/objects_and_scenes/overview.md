##### Objects and Scenes

# Overview

This tutorial will cover the basics of how to populate a [scene](../core_concepts/scenes.md) with [objects](../core_concepts/objects.md). Broadly speaking, there are two ways to do this:

1. **Scripted object placement.** Objects are preselected and placed in predefined positions. These positions might be hardcoded into the controller, stored in a json file, etc.
2. **Procedural generation.** Objects are algorithmically selected and arranged in a scene.

Procedural generation ("proc-gen") is a common technique in video game design to generate highly variable environments. However, there are many caveats to this approach:

- There isn't a "canonical" way to do proc-gen because the specifics of what is needed in any given scene vary too much. Accordingly, TDW doesn't include any procedural generators; you are expected to write your own. This tutorial includes some simple proc-gen examples.
- At a certain degree of complexity, procedural generation won't save you time. If you only need several good-looking scenes, then you're probably better off just using scripted object placement.
- It can be difficult to account for edge cases in procedural generation, i.e. unusual situations caused by rare interactions between objects. 

That said, procedural generation is very useful and is implemented in many of TDW's high-level APIs.

In this tutorial, you'll first learn about TDW's scripted object placement system (the floorplan layouts) and then how to procedurally add objects to a scene.

***

**Next: [Scripted object placement (floorplan layouts)](floorplans.md)**

[Return to the README](../../README.md)