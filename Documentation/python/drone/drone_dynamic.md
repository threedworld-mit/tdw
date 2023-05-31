# DroneDynamic

`from tdw.drone.drone_dynamic import DroneDynamic`

Dynamic data for a drone that can change per `communicate()` call (such as the position of the drone).

***

## Fields

- `raycast_hit` If True, the ray that was cast down from the drone hit something.

- `raycast_point` The point that the ray that was cast down from the drone hit. Ignore this if `self.raycast_hit == False`.

- `motor_on` If True, the drone's motor is on.

- `transform` The [`Transform`](../object_data/transform.md) of the agent.

- `images` The images rendered by the agent as dictionary. Key = the name of the pass. Value = the pass as a numpy array.

- `projection_matrix` The [camera projection matrix](../../api/output_data.md#cameramatrices) of the agent's camera as a numpy array.

- `camera_matrix` The [camera matrix](../../api/output_data.md#cameramatrices) of the agent's camera as a numpy array.

- `got_images` If True, we got images from the output data.

- `avatar_id` The ID of the avatar.

***

## Functions

#### \_\_init\_\_

**`DroneDynamic(resp, drone_id, frame_count)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| resp |  List[bytes] |  | The response from the build, which we assume contains `drone` output data. |
| drone_id |  int |  | The ID of this drone. |
| frame_count |  int |  | The current frame count. |

#### save_images

**`self.save_images(output_directory)`**

Save the ID pass (segmentation colors) and the depth pass to disk.
Images will be named: `[frame_number]_[pass_name].[extension]`
For example, the depth pass on the first frame will be named: `00000000_depth.png`

The `img` pass is either a .jpg. The `id` and `depth` passes are .png files.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| output_directory |  Union[str, Path] |  | The directory that the images will be saved to. |

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