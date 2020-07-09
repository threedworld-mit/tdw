# Performance Optimizations

## 1. Known benchmarks

**Compare your simulation to [known benchmarks](benchmark.md).**

These benchmarks reflect speeds to expect TDW to run at when using a high-end machine with a powerful GPU.

The bottom of the benchmarks page has instructions for how to run your own benchmarks, as does each sub-page.

 - [Benchmarks](benchmark.md)

## 2. Your machine

- [Machine Performance](machine_performance.md)

You should run TDW on a high-end machine. **A powerful GPU is the single most decisive factor in overall performance.**

**TDW runs faster on Windows than on Linux servers.** We're not sure why.

## 3. Your build

### General

- **Use the latest release.** If you make a custom build and run into performance issues, it will be difficult for us to determine whether the issue was introduced by the build, by your hardware, etc. The releases on GitHub are (unless otherwise specified), stable and well-tested. Likewise, **always use the most recent Python scripts**, which are included in every release.
- **Use a compiled build.** Running the build directly in the Editor makes debugging very easy, but the Editor will always be slower than a compiled build.
- **Don't make a build with "Development Build" enabled.** This setting enables a more verbose log file. It's great for debugging, less so for performance.

### Models

- Avoid loading too many objects from the model library. Objects can consume more memory than you might expect. Check the record's `"asset_bundle_sizes"` field.
- If you send `destroy_object` and create a new copy of the same object, you won't need to re-download it; multiple copies of the same object are always faster than single instances of many objects.
- `unload_asset_bundles` will clear the download cache, freeing up memory. But, you'll need to re-download any asset bundles you wish to use.

## 4. Your controller

### Never request data that you don't need

This is by far the easiest way to optimize your controller.

#### Images

- [Image capture is one of the slowest processes in TDW.](image_capture.md) Only capture images you actually need.
- Compressed (.jpg) images are much faster to encode and send than uncompressed .png images. Toggle .jpg compression with `set_img_pass_encoding`.
- Smaller images are always faster to encode and send than larger images. Adjust the image size with `set_screen_size`.
- Cameras that aren't sending data can still be _enabled_ and rendering to the GPU.
	- Send `set_pass_masks` and set `"passes"` to `[]`.
	- Toggle off the sensor entirely with `toggle_sensor` if you aren't capturing images. 
- There are many ways to get "observation data" that are much faster than images. See [Observation Data](observation_data.md).

### Render Quality

_Even if there are no enabled cameras in the scene, render quality can still affect performance._

- `set_post_process` will disable post-processing, an expensive process that runs even when there are no cameras. If you are rendering, your images will be lower-quality.
- `set_render_quality` will lower the overall render quality, with 0 being the lowest and fastest option.
- The ProcGenScene (created with the `load_scene` command) runs faster than any streamed scene.

#### Object data

Object data is generally extremely fast. `Bounds` and `Collision` data are somewhat slow.

- [Objects Data](object_data.md)

##### `Bounds`

`Bounds` data can often be inferred. Try caching `Bounds` data as much as possible.

##### `Collision`

If you need collision data, consider requesting only `enter` and/or `exit` data, e.g.:

```python
{"$type": "send_collisions", "enter": True, "exit": True, "stay": False}
```

Collision `stay` events occur many times per frame per object, and will slow down your simulation.

##### `SegmentationColors`

Segmentation color data is slow. You should only request this data after adding new objects to the scene:

```python
{"$type": "send_segmentation_colors", "frequency": "once"}
```

### Avoid expensive commands

Any command in the [API](../api/command_api.md) labeled <font style="color:orange">**Expensive**</font> is computationally expensive; this usually only matters if the command is sent frequently. (e.g. sending `destroy_all_objects` once per minute is fine, but sending it per frame _will_ slow down the build.)

### Use the existing TDW scripts

- Extend the `Controller` class but don't modify it.
- The wrapper classes in `output_data.py` are optimized for general use cases. Because it's possible to read individual Flatbuffer fields without deserializing the entire object, you could feasibly write faster wrappers. However, we might not be able to help you do this.
