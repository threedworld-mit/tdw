# Materials, Textures, and Colors

Unity differentiates between _materials_ and _textures_ and _colors_; these three terms are _not_ interchangeable.

This document will give an overview of some of the fundamental differences.

## Material

A _material_ is a binary file containing an initialized _shader_. A shader is a tiny program that is used to render a 3D object. The material shader might contain info such as:

- To what extent the material is transparent
- To what extent the material is "bumpy"
- The _texture_ and _color_ of the material

Each of these properties is a _channel_.

Every mesh in Unity _must_ have at least 1 material (or it will appear as horrible pink). It is possible for a mesh to have more than 1 material, and those materials can interact in myriad ways. Just a few examples of possibilities:
-  Decals on a racecar; the car's paint and the decal could be handled as separate materials.)
-  A puddle in the dirt might be handled as two materials on a flat surface that are blended together.

Every model in the TDW model library is comprised of _n_ meshes, each of which have _m_ materials. You can switch any material of any mesh of any object by sending [`set_visual_material`](../api/command_api.md#set_visual_material).

## Texture

A _texture_ is a .jpg or .png file. It is one of many aspects of a material. In computer graphics, the term _texture_ is often used interchangeably with _map_.

Intuition would suggest that the texture is the "visual" (_albedo_) channel of the material. This is not always the case, though:

- Some materials don't have textures, and instead have just a solid _color_.
- Some textures are actually meant to control specialized aspects of the material. For example, the "normal map" will modify the "bumpiness" of a material. Conversely, if you change the albedo texture of a material, the normal mapping and other channels of the material will remain unmodified.
- A material can sometimes have multiple albedo textures layered on top of each other, such as puddles on the ground, or decals on a racecar. Whether you'd want to handle multiple visual components of an object as textures or materials depends a lot on how they're being used in the simulation.

_Textures_ will "tile" across a material, repeating in a grid pattern. While they tile _effectively_ depends on whether the texture is "seamless". Many textures are not meant to tile, and the "grid" is effectively 1x1.

## Color

A _color_ is an RGBA color. The albedo channel of a material usually has a color property. The material with/without a texture can be tinted with a color.

# Ask yourself: "What do I want?"

If you want to control how an object/wall/floor/avatar "looks" in TDW, you need to decide what you're actually trying to accomplish.

| "I want to be able to change the..." | Pro | Con | Can I do it? |
| ---------- | --- | --- | --- |
| **Material** | It is likely that it will look "good" by default. For example, a "metallic" material will have a metallic texture and will reflect light in a metallic manner. | You are limited to the materials in our material library. (The library will continuously expand.) | Yes<br><br>Models: [`set_visual_material`](../api/command_api.md#set_visual_material)<br>Proc-gen floors: [`set_proc_gen_floor_material`](../api/command_api.md#set_proc_gen_floor_material)<br>Proc-gen walls:  [`set_proc_gen_walls_material`](../api/command_api.md#set_proc_gen_walls_material) |
| **Texture** | You can in principle set the texture of an existing material by just sending in the image as a byte array. This effectively means inifinite variability. | You still won't have control over the "normal maps", the "emissive" controls, or any other channel in the shader. For example, switching to a "metallic" _texture_ won't necessarily allow the object to "shine" like a metal. | No |
| **Color** | Switching colors is computationally fast at runtime. | This "tints" existing textures rather than replacing them. | Yes<br><br>Models: [`set_color`](../api/command_api.md#set_color)<br>Avatars: [`set_avatar_color`](../api/command_api.md#set_avatar_color) |

