##### Scene Setup (High-Level APIs)

# Overview

This sub-section of the "scene setup" guide covers TDW's high-level scene setup APIs.

Broadly speaking, all scene setup processes can be described as being in one of three categories:

1. **Procedural generation**
2. **Scripted object placement** 
3. **Hybrid**

## Procedural Generation

Procedural generation ("proc-gen") is a common technique in video game and digital art design to algorithmically generate content. Proc-gen is used not just for scene generation but also for poetry, music, and so on.

In TDW, proc-gen usually refers to an algorithm for populating a scene with objects. It sometimes can refer to generating the scene itself. Proc-gen can also refer to more abstract randomness in the scene; for example, setting a random [HDRI skybox](../photorealism/lighting.md) could be considered procedural generation. There is no single canonical way to do proc-gen, although TDW includes some code to do common proc-gen tasks for you.

**Advantages:**

- It is trivial to create *large* quantities of unique environments (scenes populated by objects).

**Disadvantages:**

- Proc-gen programming is notoriously complex involves *a lot* of human effort. Whether that effort is worthwhile depends on how many environments you need. If you only need a few environments, you should consider using scripted object placement instead.
- Procedural generation, regardless of whether its being used in TDW or elsewhere, often has the ["10,000 Bowls of Oatmeal Problem"](https://galaxykate0.tumblr.com/post/139774965871/so-you-want-to-build-a-generator). It is easy to create infinite variations on a theme but much harder to make any of them interesting. Procedurally generated scenes tend have less interesting or unexpected elements than scenes created via scripted object placement.

## Scripted Object Placement

Scripted object placement is a technique wherein objects are preselected and added to the scene at predetermined positions, rotations, etc. These positions might be hardcoded into the controller, stored in a json file, etc. Most tutorials in the TDW documentation use scripted object placement.

**Advantages:**

- It's relatively easy (compared to procedural generation) to create "interesting" scenes. If you only need a few good-looking scenes, scripted object placement is almost always the better option.

**Disadvantages:**

- If you need to create *many* scenes, explicitly defining each of these scenes can be very time-consuming.

## Hybrid

You can, of course, mix scripted object placement with procedural generation. For example, you could procedurally generate a group of objects and explicitly place that group of objects somewhere in the scene.

To some extent, the difference between scripted object placement and conceptual object placement is merely semantic. For example, if you use the 3D bounds of Object A to place Object B on top of it, this could be considered both scripted and procedural object placement. Both strategies ultimately use most of the same tools and API calls.

***

**[Next: Procedural Generation (the `ProcGenKitchen` add-on)](proc_gen_kitchen.md)**

[Return to the README](../../../README.md)