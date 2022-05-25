##### Troubleshooting

# Performance optimizations

By default, TDW is optimized to strike a balance between simulation speed and realistic imagery and physics. This document explains how to optimize TDW for speed.

## 1. Compare your speed to TDW's performance benchmarks

**Before troubleshooting why your simulation is running slowly, we recommend comparing it to [TDW's performance benchmarks](../../benchmark/benchmark.md).** 

If your controller is running significantly slower than our benchmark controllers, your code might not be optimized.

## 2. Run TDW on a computer with a GPU

You should run TDW on a high-end machine. **A powerful GPU is the single most decisive factor in overall performance.**

## 3. Reduce image output data

[Image capture](../core_concepts/images.md) is by far the slowest process in TDW.

### 3A. Only request image data when you need it

If you don't need image data, don't request it! For example, requesting image data on every frame is *much* slower than requesting image data every 10 frames. Likewise, never request [capture passes](../visual_perception/overview.md) that you don't actually need. For example, if you're only using the `_id` pass, don't request `_id` *and* `_img`.

### 3B. Capture .jpg instead of .png

If you're capturing the `_img` pass, consider encoding images as .jpg rather than lossless .png; the .jpg data is much smaller and can significantly improve simulation speed.

- By default, TDW encodes images as lossless .png
- By default, the [`ImageCapture`](../../python/add_ons/image_capture.md) encodes images as lossy .jpg
- To set image encoding, send [`set_img_pass_encoding`](../../api/command_api.md#set_img_pass_encoding)

Note that all other passes are *always* encoded as lossless .png, even if the `_img` pass is .jpg.

### 3C. Reduce image size

Reducing the image size with [`set_screen_size`](../../api/command_api.md#set_screen_size) will greatly reduce how much data the build needs to send to the controller.

### 3D. Disable the image sensor

If you don't need image data at all, consider not adding an [avatar](../core_concepts/avatars.md) to the scene. Or, disable the avatar's camera by sending [`enable_image_sensor`](../../api/command_api.md#enable_image_sensor).

### 3E. Use alternative output data

- [`IdPassSegmentationColors` can be can be faster than the `_id` image pass.](../visual_perception/id.md) 
- [`Occlusion` can be faster than two `_mask` passes](../visual_perception/occlusion.md)
- You can use other output data such as [`Bounds`](../scene_setup_low_level/bounds.md) to infer much of the same information you'd get from image capture.

## 4. Reduce other output data

**Don't request output data that you don't need.** Examples:

- If you only need [`Transforms`](../../api/output_data.md#Transforms) data on the first frame, send `{"$type": "send_transforms", "frequency": "once"}`
- If you need `Transforms` data on every frame but only for certain objects, send `{"$type": "send_transforms", "frequency": "always", "ids": [object_id_0, object_id_1, ...]}`
- If you need `Transforms` data for every object on every frame for a span of time, send `{"$type": "send_transforms", "frequency": "always"}` and then when you no longer need the data, send  `{"$type": "send_transforms", "frequency": "never"}` 
- [`send_collisions`](../../api/command_api.md#send_collisions) can be slow if `"stay"` is `True` because there are *many* "stay" events per frame.
- Only request static data such as [`SegmentationColors`](../../api/output_data.md#SegmentationColors) once, when the objects are initially created, and then cache that data.

## 5. Reduce the complexity of the scene

In general, the more photorealistic the [scene](../core_concepts/scenes.md), the slower the simulation will be.

Avoid filling the scene with many complex objects. To determine how complex an object is, check [`record.asset_bundle_sizes`](../../python/librarian/model_librarian.md):

```python
from platform import system
from tdw.librarian import ModelLibrarian

librarian = ModelLibrarian()
for record in librarian.records:
    print(record.name, record.asset_bundle_sizes[system()])
```

Using copies of the same model is always faster than using multiple models. TDW must download each model and load it into memory. Once a model has been downloaded and loaded into memory, adding subsequent copies of the model is a near-instantaneous process.

However, it's possible to load too many models into the scene and run out of system memory. To unload models from memory, send [`unload_asset_bundles`](../../api/command_api.md#unload_asset_bundles). Be aware that the next time you want to add a model to the scene, TDW will need to download it and load it back into memory.

## 6. Reduce render quality

- Raise and lower the overall render quality by sending [`{"$type": "set_render_quality", "render_quality": value}`](../../api/command_api.md#set_render_quality) where `value` is an integer between 0 (lowest quality) and 5 (highest quality).
- [Post-processing](../photorealism/post_processing.md) can be an expensive process. Disable it by sending [`set_post_process`](../../api/command_api.md#set_post_process). This will lower image quality.
- Disable reflection probes by sending [`enable_reflection_probes`](../../api/command_api.md#enable_reflection_probes). Images will be flatter and less realistic.

## 7. Skip physics frames

[Read this for more information.](../physx/step_physics.md)

***

**Next: [Good coding practices](good_coding_practices.md)**

[Return to the README](../../../README.md)

***

Python API:

- [`ImageCapture`](../../python/add_ons/image_capture.md) 
- [`ModelLibrarian`](../../python/librarian/model_librarian.md) 

Command API:

- [`set_img_pass_encoding`](../../api/command_api.md#set_img_pass_encoding)
- [`set_screen_size`](../../api/command_api.md#set_screen_size)
- [`send_transforms`](../../api/command_api.md#send_transforms)
- [`send_collisions`](../../api/command_api.md#send_collisions)
- [`unload_asset_bundles`](../../api/command_api.md#unload_asset_bundles)
- [`set_render_quality`](../../api/command_api.md#set_render_quality)
- [`set_post_process`](../../api/command_api.md#set_post_process)
- [`enable_reflection_probes`](../../api/command_api.md#enable_reflection_probes)
- [`enable_image_sensor`](../../api/command_api.md#enable_image_sensor)

Output Data:

- [`Images`](../../api/output_data.md#Images)
- [`Transforms`](../../api/output_data.md#Transforms)
- [`SegmentationColors`](../../api/output_data.md#SegmentationColors)
- [`IdPassSegmentationColors`](../../api/output_data.md#IdPassSegmentationColors)
- [`Occlusion`](../../api/output_data.md#Occlusion)
- [`Bounds`](../../api/output_data.md#Bounds)