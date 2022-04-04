##### Objects and Scenes

# Overview

These lessons will cover the basics of how to populate a [scene](../core_concepts/scenes.md) with [objects](../core_concepts/objects.md). Broadly speaking, there are three ways to do this:

1. **Scripted object placement.** Objects are preselected and placed in predefined positions. These positions might be hardcoded into the controller, stored in a json file, etc. Most tutorials in the TDW documentation use scripted object placement.
2. **Procedural generation.** Objects are algorithmically selected and arranged in a scene.
2. **Hybrid.** Use a mix of scripted object placement and procedural generation.

## Procedural Generation

Procedural generation ("proc-gen") is a common technique in video game design to generate highly variable environments. In TDW, proc-gen usually refers to an algorithm for populating a scene with objects. It sometimes can refer to generating the scene itself. Proc-gen can also refer to more abstract randomness in the scene; for example, setting a random [HDRI skybox](../photorealism/lighting.md) could be considered procedural generation. There is no single canonical way to do proc-gen, although TDW includes some code to do common proc-gen tasks for you.

**Advantages to proc-gen:**

- It is trivial to create *large* quantities of unique environments (scenes populated by objects).

**Disadvantages to proc-gen:**

- Proc-gen programming is notoriously complex involves *a lot* of human effort. Whether that effort is worthwhile depends on how many environments you need. If you only need a few environments, you should consider using scripted object placement instead.
- Procedural generation, regardless of whether you're creating scenes in TDW, generating poetry, and so on, often has the ["10,000 Bowls of Oatmeal Problem"](https://galaxykate0.tumblr.com/post/139774965871/so-you-want-to-build-a-generator). It is easy to create infinite variations on a theme but much harder to make any of them interesting. Procedurally generated scenes tend have less interesting or unexpected elements than scenes created via scripted object placement.

## Hybrid

You can, of course, mix scripted object placement with procedural generation. For example, you could procedurally generate a group of objects and explicitly place that group of objects somewhere in the scene. The main difficult in this approach is that your scripted object placement system needs to be spatially aware of what your proc-gen system is doing, and vice versa. In other words, if you procedurally generate a group of objects, you'll need *either* a way to determine the group's width and length so that it can be placed at a good location, *or* you need to design the algorithm such that this doesn't matter. A good example of this is the [`KitchenTable`](../../python/proc_gen/arrangements/kitchen_table.md), which is procedurally generated, in part based on what is already in the scene (see the `used_walls` parameter).

In this tutorial, you'll first learn about "floorplan layouts", which use scripted object placement to generate interior environments. Then, you'll learn how to procedurally add objects to a scene.

***

**Next: [Scripted object placement (floorplan layouts)](floorplans.md)**

[Return to the README](../../../README.md)