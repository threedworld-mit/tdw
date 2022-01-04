##### Visual Perception

# Overview

The [Core Concepts guide](../core_concepts/images.md) explained how to initialize image capture for the the `_img` pass. There are many other image passes available in TDW. It is possible to receive multiple capture passes on the same frame by setting the `pass_masks` parameter of the `set_pass_mask` command. In this example, the controller will receive and `_img` pass and an `_id` pass:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, Images
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

c = Controller()
object_id = c.get_unique_id()

commands = [TDWUtils.create_empty_room(12, 12),
            c.get_add_object(model_name="iron_box",
                             position={"x": 0, "y": 0, "z": 0},
                             object_id=object_id)]
commands.extend(TDWUtils.create_avatar(position={"x": 2, "y": 1.6, "z": -0.6},
                                       avatar_id="a",
                                       look_at={"x": 0, "y": 0, "z": 0}))
commands.extend([{"$type": "set_pass_masks",
                  "pass_masks": ["_img", "_id"],
                  "avatar_id": "a"},
                 {"$type": "send_images",
                  "frequency": "always",
                  "ids": ["a"]}])

resp = c.communicate(commands)
output_directory = str(EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("send_images_2").resolve())
print(f"Images will be saved to: {output_directory}")

for i in range(len(resp) - 1):
    r_id = OutputData.get_data_type_id(resp[i])
    # Get Images output data.
    if r_id == "imag":
        images = Images(resp[i])
        # Determine which avatar captured the image.
        if images.get_avatar_id() == "a":
            TDWUtils.save_images(images=images, filename="0", output_directory=output_directory)
c.communicate({"$type": "terminate"})
```

Or, with the `ImageCapture` add-on:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

c = Controller()
object_id = c.get_unique_id()
commands = [TDWUtils.create_empty_room(12, 12),
            c.get_add_object(model_name="iron_box",
                             position={"x": 0, "y": 0, "z": 0},
                             object_id=object_id)]
commands.extend(TDWUtils.create_avatar(position={"x": 2, "y": 1.6, "z": -0.6},
                                       avatar_id="a",
                                       look_at={"x": 0, "y": 0, "z": 0}))
c.add_ons.append(cam)
output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("send_images_2")
print(f"Images will be saved to: {output_directory}")

# Add the ImageCapture add-on.
cap = ImageCapture(path=output_directory, avatar_ids=["a"], pass_masks=["_img", "_id"])
c.add_ons.append(cap)

c.communicate(commands)
c.communicate({"$type": "terminate"})
```

## Capture passes and output data

Some visual perception data is image data such as the segmentation color passes and the depth passes. Some visual perception data is *not* image data; in some cases, it is faster and more convenient to return only a small amount of relevant information. This tutorial will cover examples of both image and non-image visual perception data.

***

**Next: [Instance ID segmentation colors (`_id` pass)](id.md)**

[Return to the README](../../../README.md)

***

Example controllers:

- [send_images.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/core_concepts/send_images.py) Capture an image and save it to disk.
- [image_capture.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/core_concepts/image_capture.py) Example implementation of the ImageCapture add-on.

Python API:

- [`ImageCapture`](../../python/add_ons/image_capture.md)  (add-on that saves images every frame)
- [`TDWUtils.save_images(images, filename, output_directory)`](../../python/tdw_utils.md)  (Save all capture passes)

Command API:

- [`set_pass_masks`](../../api/command_api.md#set_pass_masks)
- [`send_images`](../../api/command_api.md#send_images)

Output Data API:

- [`Images`](../../api/output_data.md#Images) 
