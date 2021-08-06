# Images

TDW makes a distinction between images rendered to the build's application window (render frames) and encoded image output data. By default, avatar cameras generate render frames but don't actually return output data; this is because serializing image output data is one of the slowest processes in TDW. Only request image data when you really need it!

Image data in TDW is divided into **capture passes**. By far the most commonly used capture pass is `_img`, which is a render of what the camera is currently viewing. Other capture passes will return more specialized data.

To capture an `_img` pass, we'll first create a scene, add an object, and add an avatar. Note that unlike previous examples using `ThirdPersonCamera`, we need to call `initialize_now()`. This is because we need to add image capture commands to the list. If we didn't do this, the controller would add the image capture commands *before* the camera initialization commands and there'd be an error in the build.

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.output_data import OutputData, Images

c = Controller()
c.start()
object_id = c.get_unique_id()
cam = ThirdPersonCamera(position={"x": 2, "y": 1.6, "z": -0.6},
                        look_at=object_id,
                        avatar_id="a")
c.add_ons.append(cam)
# We need to initialize the camera commands now so that they are in the correct order when setting up image capture.
# Typically, add-on initialization is handled automatically by the controller.
cam_commands = cam.initialize_now()

commands = [TDWUtils.create_empty_room(12, 12),
            c.get_add_object(model_name="iron_box",
                             position={"x": 1, "y": 0, "z": -0.5},
                             object_id=object_id)]
commands.extend(cam_commands)
```

Now we need to add two more commands:

- [`set_pass_masks`](../../api/command_api.md#set_pass_masks) to enable the `_img` pass.
- [`send_images`](../../api/command_api.md#send_images) to request image data per frame.

We'll send all of these commands and receive a response:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.output_data import OutputData, Images

c = Controller()
c.start()
object_id = c.get_unique_id()
cam = ThirdPersonCamera(position={"x": 2, "y": 1.6, "z": -0.6},
                        look_at=object_id,
                        avatar_id="a")
c.add_ons.append(cam)
# We need to initialize the camera commands now so that they are in the correct order when setting up image capture.
# Typically, add-on initialization is handled automatically by the controller.
cam_commands = cam.initialize_now()

commands = [TDWUtils.create_empty_room(12, 12),
            c.get_add_object(model_name="iron_box",
                             position={"x": 1, "y": 0, "z": -0.5},
                             object_id=object_id)]
commands.extend(cam_commands)
commands.extend([{"$type": "set_pass_masks",
                  "pass_masks": ["_img"],
                  "avatar_id": "a"},
                 {"$type": "send_images",
                  "frequency": "always",
                  "ids": ["a"]}])
```

We can then read the [`Images`](../../api/output_data.md#Images) output data, which contains metadata about the image plus the image itself. We can then choose what to do with the image: If we want to analyze it at runtime, we could convert it to a [PIL image](https://pillow.readthedocs.io/en/stable/reference/Image.html). Or, we could immediately save it to disk. The following example does both options:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.output_data import OutputData, Images

c = Controller()
c.start()
object_id = c.get_unique_id()
cam = ThirdPersonCamera(position={"x": 2, "y": 1.6, "z": -0.6},
                        look_at=object_id,
                        avatar_id="a")
c.add_ons.append(cam)
# We need to initialize the camera commands now so that they are in the correct order when setting up image capture.
# Typically, add-on initialization is handled automatically by the controller.
cam_commands = cam.initialize_now()

commands = [TDWUtils.create_empty_room(12, 12),
            c.get_add_object(model_name="iron_box",
                             position={"x": 1, "y": 0, "z": -0.5},
                             object_id=object_id)]
commands.extend(cam_commands)
commands.extend([{"$type": "set_pass_masks",
                  "pass_masks": ["_img"],
                  "avatar_id": "a"},
                 {"$type": "send_images",
                  "frequency": "always",
                  "ids": ["a"]}])

resp = c.communicate(commands)

for i in range(len(resp) - 1):
    r_id = OutputData.get_data_type_id(resp[i])
    # Get Images output data.
    if r_id == "imag":
        images = Images(resp[i])
        # Determine which avatar captured the image.
        if images.get_avatar_id() == "a":
            # Iterate throught each capture pass.
            for j in range(images.get_num_passes()):
                # This is the _img pass.
                if images.get_pass_mask(j) == "_img":
                    image_arr = images.get_image(j)
                    # Get a PIL image.
                    pil_image = TDWUtils.get_pil_image(images=images, index=j)
            # Save the image.
            TDWUtils.save_images(images=images, filename="0", output_directory="tmp")
c.communicate({"$type": "terminate"})
```

Result:

![](images/img_pass_box.png)

## Multiple capture passes

It is possible to capture multiple capture passes at the same time: simply add them to the `pass_masks` list:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera

c = Controller()
c.start()
object_id = c.get_unique_id()
cam = ThirdPersonCamera(position={"x": 2, "y": 1.6, "z": -0.6},
                        look_at=object_id,
                        avatar_id="a")
c.add_ons.append(cam)
cam_commands = cam.initialize_now()

commands = [TDWUtils.create_empty_room(12, 12),
            c.get_add_object(model_name="iron_box",
                             position={"x": 1, "y": 0, "z": -0.5},
                             object_id=object_id)]
commands.extend(cam_commands)
commands.extend([{"$type": "set_pass_masks",
                  "pass_masks": ["_img", "_id"],
                  "avatar_id": "a"},
                 {"$type": "send_images",
                  "frequency": "always",
                  "ids": ["a"]}])
```

## jpg vs. png encoding

The `_img` capture pass is standard rendering of the scene. It can be encoded as a lossless png or a lossy jpg. Generally, jpg encoding is significantly faster than png encoding and good enough for most use cases. To enable jpg encoding, send [`{"$type": "set_img_pass_encoding", "value": False}`](../../api/command_api.md#set_img_pass_encoding) or set `png=False` in the `ImageCapture` constructor.

| `_img` pass (png)        | `_img` pass (jpg)        |
| ------------------------ | ------------------------ |
| ![](images/img_0000.png) | ![](images/img_0000.jpg) |

## The `ImageCapture` add-on

You can add use an [`ImageCapture`](../../python/add_ons/ImageCapture.md) to save images per frame. Note that in this example, we don't need to manually initialize the camera, enable image capture, or parse output data; all of that is handled automatically by the `ImageCapture` add-on:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture

c = Controller()
c.start()
object_id = c.get_unique_id()
cam = ThirdPersonCamera(position={"x": 2, "y": 1.6, "z": -0.6},
                        look_at=object_id,
                        avatar_id="a")
c.add_ons.append(cam)

# Add the ImageCapture add-on.
cap = ImageCapture(path="tmp", avatar_ids=["a"], pass_masks=["_img", "_id"])
c.add_ons.append(cap)

# This will create the scene and the object.
# Then, the ThirdPersonCamera add-on will create an avatar.
# Then, the ImageCapture add-on will save an image to disk.
resp = c.communicate([TDWUtils.create_empty_room(12, 12),
                      c.get_add_object(model_name="iron_box",
                                       position={"x": 1, "y": 0, "z": -0.5},
                                       object_id=object_id)])
c.communicate({"$type": "terminate"})
```

***

Next: [Image capture passes](capture_passes.md)

Python API:

- [`ImageCapture`](../../python/add_ons/ImageCapture.md)  (add-on that saves images every frame)
- [`TDWUtils.save_images(images, filename, output_directory)`](../../python/tdw_utils.md)  (Save all capture passes)
- [`TDWUtils.get_pil_image(images, index)`](../../python/tdw_utils.md)  (Convert a capture pass to a PIL image)

Command API:

- [`set_pass_masks`](../../api/command_api.md#set_pass_masks)
- [`send_images`](../../api/command_api.md#send_images)
- [`set_img_pass_encoding`](../../api/command_api.md#set_img_pass_encoding)

Output Data API:

- [`Images`](../../api/output_data.md#Images) 

[Return to the README](../../README.md)