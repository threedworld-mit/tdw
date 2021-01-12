# Depth Maps

Depth passes are image that encode depth information into pixel colors. To receive a depth pass, you need to add an avatar to the scene, set the pass masks to include `_depth`, and then request images:

```python
import numpy as np
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, Images, CameraMatrices

c = Controller()
c.start()
# Create an empty room.
commands = [TDWUtils.create_empty_room(12, 12)]
# Add the avatar.
commands.extend(TDWUtils.create_avatar(position={"x": 1.57, "y": 3, "z": 3.56}, 
                                       look_at=TDWUtils.VECTOR3_ZERO))
# Add an object. Request image data that includes the depth pass.
commands.extend([c.get_add_object("trunck", object_id=0),
                 {"$type": "set_pass_masks",
                  "pass_masks": ["_depth"]},
                 {"$type": "send_images"}])
resp = c.communicate(commands)
images = None
depth_image = None
for i in range(len(resp) - 1):
    r_id = OutputData.get_data_type_id(resp[i])
    # Get the image.
    if r_id == "imag":
        images = Images(resp[i])
        for j in range(images.get_num_passes()):
            if images.get_pass_mask(j) == "_depth":
                depth_image = images.get_image(j)
```

## Types of depth passes

- `_depth_simple` is a grayscale depth map.
- `_depth` is a more accurate pass that encodes depth values to a 24-bit RGB value.

## How to get depth values

Decode a depth pass into an array of depth floats with `TDWUtils.get_depth_values()`.

```python
# Get the depth values of each pixel.
depth = TDWUtils.get_depth_values(image=depth_image, width=images.get_width(), height=images.get_height(), far_plane=far_plane, near_plane=near_plane)
```

The default values of `width`, `height`, `far_plane`, and `near_plane` all correspond to default camera values in TDW. To adjust them, see the commands `set_screen_size` and `set_camera_clipping_planes`.

## How to create a point cloud

Use the decoded depth values to create a point cloud with `TDWUtils.get_point_cloud()`. You will also need camera matrix data.

```python
commands.extend([c.get_add_object("trunck", object_id=0),
                 {"$type": "set_pass_masks",
                  "pass_masks": ["_depth"]},
                 {"$type": "send_images"},
                 {"$type": "send_camera_matrices"}])
resp = c.communicate(commands)

depth_image = None
camera_matrix = None
images = None
for i in range(len(resp) - 1):
    r_id = OutputData.get_data_type_id(resp[i])
    # Get the image.
    if r_id == "imag":
        images = Images(resp[i])
        for j in range(images.get_num_passes()):
            if images.get_pass_mask(j) == depth_pass:
                depth_image = images.get_image(j)
    # Get the camera matrix.
    elif r_id == "cama":
        camera_matrix = CameraMatrices(resp[i]).get_camera_matrix()

depth = TDWUtils.get_depth_values(image=depth_image, width=images.get_width(), height=images.get_height())
point_cloud = TDWUtils.get_point_cloud(depth=depth, camera_matrix=camera_matrix)
```

## Example

For a controller that combines all of the code snippets in this document, see: `tdw/Python/example_controllers/depth_shader.py`

