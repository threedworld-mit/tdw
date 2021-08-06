# 1.2.7 Images

TDW makes a distinction between images rendered to the build's application window (render frames) and encoded image output data. By default, avatar cameras generate render frames but don't actually return output data; this is because serializing image output data is one of the slowest processes in TDW. Only request image data when you really need it!

Image data in TDW is divided into **capture passes**. By far the most commonly used capture pass is `_img`, which is a render of what the camera is currently viewing. Other capture passes will return more specialized data.

To capture an `_img` pass, we'll first create a scene, add an object, and add an avatar:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera

c = Controller()
c.start()
object_id = c.get_unique_id()
cam = ThirdPersonCamera(position={"x": 2, "y": 1.6, "z": -0.6},
                        look_at=object_id)
c.add_ons.append(cam)
commands = [TDWUtils.create_empty_room(12, 12),
            c.get_add_object(model_name="iron_box",
                             position={"x": 1, "y": 0, "z": -0.5},
                             object_id=object_id)]

# Note that we haven't actually sent these commands yet!
```

We then need to add two more commands:

- [`set_pass_masks`](../../api/command_api.md#set_pass_masks) to enable the `_img` pass.
- [`send_images`](../../api/command_api.md#send_images) to request image data per frame.

We'll send all of these commands and receive a response:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera

c = Controller()
c.start()
object_id = c.get_unique_id()
cam = ThirdPersonCamera(position={"x": 2, "y": 1.6, "z": -0.6},
                        look_at=object_id)
c.add_ons.append(cam)
commands = [TDWUtils.create_empty_room(12, 12),
            c.get_add_object(model_name="iron_box",
                             position={"x": 1, "y": 0, "z": -0.5},
                             object_id=object_id),
            {"$type": "set_pass_masks",
             "pass_masks": ["_img"],
             "avatar_id": "a"},
            {"$type": "send_images",
             "frequency": "always",
             "ids": ["a"]}]

resp = c.communicate(commands)
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
                        look_at=object_id)
c.add_ons.append(cam)
commands = [TDWUtils.create_empty_room(12, 12),
            c.get_add_object(model_name="iron_box",
                             position={"x": 1, "y": 0, "z": -0.5},
                             object_id=object_id),
            {"$type": "set_pass_masks",
             "pass_masks": ["_img"],
             "avatar_id": "a"},
            {"$type": "send_images",
             "frequency": "always",
             "ids": ["a"]}]

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
            TDWUtils.save_images(images=images, filename="0", output_directory="/tmp")
c.communicate({"$type": "terminate"})
```



***

Next: [Images](1.2.7_images.md)

Python API:

- [`TDWUtils.save_images(images, filename, output_directory)`](../../python/tdw_utils.md)  (Save all capture passes)
- [`TDWUtils.get_pil_image(images, index)`](../../python/tdw_utils.md)  (Convert a capture pass to a PIL image)

Command API:

- [`set_pass_masks`](../../api/command_api.md#set_pass_masks)
- [`send_images`](../../api/command_api.md#send_images)

Output Data API:

- [`Images`](../../api/output_data.md#Images) 

[Return to the README](../../README.md)