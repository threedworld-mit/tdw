# Depth Maps

Depth passes are image that include depth information into pixel colors. To receive a depth pass, you need to add an avatar to the scene, set the pass masks to include `_depth`, and then request images:

```python
import numpy as np
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, Images, Raycast, CameraMatrices, AvatarKinematic

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

- `_depth_simple` is a grayscale depth map with values normalized between 0  (the closest position in the image) and 1 (the furthest position in the image).
- `_depth` is a more accurate pass that encodes depth values to a 24-bit RGB value. The values of the `_depth` pass are normalized between 0 (the position of the camera eye) and 1 (the furthest position in the image).

## How to decode a depth pass

See: `TDWUtils.get_depth_values()`.

```python
# Get the depth values of each pixel.
depth = TDWUtils.get_depth_values(image=depth_image, width=images.get_width(), height=images.get_height())
```

## How to un-normalize a depth pass

To un-normalize the `_depth` pass, you will need the true distance of at least one pixel. This can be determined with the `send_viewport_raycast` command, which will cast a ray along the camera's forward vector until it hits an object.  You'll also need the position of the avatar. You can then use the distance between the avatar and the raycast point to un-normalize the depth map.

```python
# Add an object. Request images, a raycast, and avatar data.
commands.extend([c.get_add_object("trunck", object_id=0),
                 {"$type": "set_pass_masks",
                  "pass_masks": ["_depth"]},
                 {"$type": "send_images"},
                 {"$type": "send_viewport_raycast"},
                 {"$type": "send_avatars"}])
resp = c.communicate(commands)
images = None
depth_image = None
raycast = None
avatar = None
for i in range(len(resp) - 1):
    r_id = OutputData.get_data_type_id(resp[i])
    # Get the image.
    if r_id == "imag":
        images = Images(resp[i])
        for j in range(images.get_num_passes()):
            if images.get_pass_mask(j) == "_depth":
                depth_image = images.get_image(j)
    # Get the raycast.
    elif r_id == "rayc":
        raycast = Raycast(resp[i])
    elif r_id == "avki":
        avatar = AvatarKinematic(resp[i])
# Get the depth values of each pixel.
depth = TDWUtils.get_depth_values(image=depth_image, width=images.get_width(), height=images.get_height())

# Un-normalize the depth values by getting the distance from the avatar to the raycast point.
avatar_position = np.array(avatar.get_position())
raycast_point = np.array(raycast.get_point())
distance_to_raycast_point = np.linalg.norm(avatar_position - raycast_point)
unnormalized = distance_to_raycast_point / depth[int(images.get_height() / 2)][int(images.get_width() / 2)]
depth *= unnormalized
```

## How to create a point cloud

Use the decoded depth values to create a point cloud with `TDWUtils.get_point_cloud()`. You will also need camera matrix data.

```python
# Add an object. Request images, a raycast, avatar data, and camera matrix data.
commands.extend([c.get_add_object("trunck", object_id=0),
                 {"$type": "set_pass_masks",
                  "pass_masks": ["_depth"]},
                 {"$type": "send_images"},
                 {"$type": "send_viewport_raycast"},
                 {"$type": "send_avatars"},
                 {"$type": "send_camera_matrices"}])
resp = c.communicate(commands)

images = None
depth_image = None
raycast = None
avatar = None
camera_matrix = None
for i in range(len(resp) - 1):
    r_id = OutputData.get_data_type_id(resp[i])
    if r_id == "cama":
        camera_matrix = CameraMatrices(resp[i]).get_camera_matrix()
        
    # Get the rest of the output data here.
    
# Get the depth values here.

point_cloud = TDWUtils.get_point_cloud(depth=depth, camera_matrix=camera_matrix)
```

## Example

For a controller that combines all of the code snippets in this document, see: `tdw/Python/example_controllers/depth_shader.py`

