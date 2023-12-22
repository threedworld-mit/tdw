# VehicleDynamic

`from tdw.vehicle.vehicle_dynamic import VehicleDynamic`

Dynamic data for a vehicle that can change per `communicate()` call (such as the position of the vehicle).

***

## Fields

- `rigidbody` The [`Rigidbody`](../object_data/rigidbody.md) (velocity and angular velocity) of the vehicle.

- `transform` The [`Transform`](../object_data/transform.md) of the agent.

- `images` The images rendered by the agent as dictionary. Key = the name of the pass. Value = the pass as a numpy array.

- `projection_matrix` The [camera projection matrix](../../api/output_data.md#cameramatrices) of the agent's camera as a numpy array.

- `camera_matrix` The [camera matrix](../../api/output_data.md#cameramatrices) of the agent's camera as a numpy array.

- `got_images` If True, we got images from the output data.

- `avatar_id` The ID of the avatar.

***

## Functions

#### \_\_init\_\_

**`VehicleDynamic()`**

The [`Rigidbody`](../object_data/rigidbody.md) (velocity and angular velocity) of the vehicle.

#### save_images

**`self.save_images(output_directory)`**

Save the ID pass (segmentation colors) and the depth pass to disk.
Images will be named: `[frame_number]_[pass_name].[extension]`
For example, the depth pass on the first frame will be named: `00000000_depth.png`

The `img` pass is either a .jpg. The `id` and `depth` passes are .png files.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| output_directory |  PATH |  | The directory that the images will be saved to. |

#### get_pil_image

**`self.get_pil_image()`**

**`self.get_pil_image(pass_mask="img")`**

Convert raw image data to a PIL image.
Use this function to read and analyze an image in memory.
Do NOT use this function to save image data to disk; `save_image` is much faster.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| pass_mask |  str  | "img" | The pass mask. Options: `"img"`, `"id"`, `"depth"`. |

_Returns:_  A PIL image.