##### Photorealism

# Post-processing

**Post-processing** refers to a multitude of effects that can be applied to an image immediately after it is rendered. In 3D graphics, post-processing is most often used to make images look more realistic. For example, the renderer might blur background objects to simulate how a camera lens focuses.

In TDW, post-processing is enabled in all scenes by default. You can disable post-processing with the command [`set_post_process`](../../api/command_api.md#set_post_process). This will result in images that appear "flatter". It also sometimes improves simulation speed.

If post-processing is enabled but images appear flat, make sure that you're running TDW with a GPU.

## Post-processing commands

Post-processing commands affect *all* cameras in the scene. If you load a new scene or reloading the current scene, you must re-send the post-processing commands.

These commands adjust global post-processing values in a scene. In nearly all cases, they should be sent only when a scene is first initialized. 

| Command                                                      | Description                                                  | Default value |
| ------------------------------------------------------------ | ------------------------------------------------------------ | ------------- |
| [`set_ambient_occlusion_intensity`](../../api/command_api.md#set_ambient_occlusion_intensity) | Set the intensity (darkness) of the Ambient Occlusion effect. | 0.25          |
| [`set_ambient_occlusion_thickness_modifier`](../../api/command_api.md#set_ambient_occlusion_thickness_modifier) | Set the Thickness Modifier for the Ambient Occlusion effect controls "spread" of the effect out from corners. | 1.25          |
| [`set_contrast`](../../api/command_api.md#set_contrast)      | Set the contrast value of the post-processing color grading. | 20            |
| [`set_post_exposure`](../../api/command_api.md#set_post_exposure) | Set the post-exposure value of the post-processing. A higher value will  create a brighter image. We don't recommend values less than 0, or  greater than 2. | 0             |
| [`set_saturation`](../../api/command_api.md#set_saturation)  | Set the saturation value of the post-processing color grading. | -20           |
| [`set_screen_space_reflections`](../../api/command_api.md#set_screen_space_reflections) | Toggle screen space reflections. This is used to create reflections off of visual materials in the scene. | True          |
| [`set_vignette`](../../api/command_api.md#set_vignette)      | Enable or disable the vignette, which darkens the image at the edges. | False         |

There are additional post-processing commands that are meant to be set *dynamically* while a simulation is running. The commands affect each [camera](../core_concepts/avatars.md) that are currently in the scene and will be covered in [the next document](depth_of_field.md).

***

**Next: [Interior lighting (the `InteriorSceneLighting` add-on)](interior_lighting.md)**

[Return to the README](../../../README.md)

***

Example controllers:

- [photoreal.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/photorealism/photoreal.py) Create a photorealistic scene, focusing on post-processing and other effects.
- [rotate_hdri_skybox.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/photorealism/rotate_hdri_skybox.py) Add an HDRI skybox to the scene and rotate it. This controller includes post-processing commands.

Command API:

- [`set_post_process`](../../api/command_api.md#set_post_process)
- [`set_ambient_occlusion_intensity`](../../api/command_api.md#set_ambient_occlusion_intensity)
- [`set_ambient_occlusion_thickness_modifier`](../../api/command_api.md#set_ambient_occlusion_thickness_modifier)
- [`set_contrast`](../../api/command_api.md#set_contrast)
- [`set_post_exposure`](../../api/command_api.md#set_post_exposure)
- [`set_saturation`](../../api/command_api.md#set_saturation)
- [`set_screen_space_reflections`](../../api/command_api.md#set_screen_space_reflections)
- [`set_vignette`](../../api/command_api.md#set_vignette)
