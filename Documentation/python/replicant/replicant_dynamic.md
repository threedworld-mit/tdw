# ReplicantDynamic

`from tdw.replicant.replicant_dynamic import ReplicantDynamic`

Dynamic data for a replicant that can change per frame (such as the position of the replicant)

***

## Fields

- `transform` The [`Transform`](../object_data/transform.md) of the Replicant.

- `held_objects` A dictionary of objects held in each hand. Key = [`Arm`](../agents/arm.md). Value = Object ID.

- `images` A dictionary of collisions between one of this replicant's [body parts](replicant_static.md) and the environment (floors, walls, etc.).
Key = The ID of the body part.
Value = A list of [environment collision data.](../../object_data/collision_obj_env.md)
"""
""":field
The images rendered by the robot as dictionary. Key = the name of the pass. Value = the pass as a numpy array.

| Pass | Image | Description |
| --- | --- | --- |
| `"img"` | ![](images/pass_masks/img_0.jpg) | The rendered image. |
| `"id"` | ![](images/pass_masks/id_0.png) | The object color segmentation pass. See `Magnebot.segmentation_color_to_id` and `Magnebot.objects_static` to map segmentation colors to object IDs. |
| `"depth"` | ![](images/pass_masks/depth_0.png) | The depth values per pixel as a numpy array. Depth values are encoded into the RGB image; see `SceneState.get_depth_values()`. Use the camera matrices to interpret this data. |

- `projection_matrix` The [camera projection matrix](../../api/output_data.md#cameramatrices) of the Replicant's camera as a numpy array.

- `camera_matrix` The [camera matrix](../../api/output_data.md#cameramatrices) of the Replicant's camera as a numpy array.

- `got_images` If True, we got images from the output data.

- `body_parts` Transform data for each body part. Key = Body part ID. Value = [`Transform`](../object_data/transform.md).

***

## Functions

#### \_\_init\_\_

**`ReplicantDynamic(resp, replicant_id, frame_count)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| resp |  List[bytes] |  | The response from the build, which we assume contains `replicant` output data. |
| replicant_id |  int |  | The ID of this replicant. |
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

#### get_pil_images

**`self.get_pil_images()`**

Convert each image pass from the robot camera to PIL images.

_Returns:_  A dictionary of PIL images. Key = the pass name (img, id, depth); Value = The PIL image (can be None)

#### get_depth_values

**`self.get_depth_values()`**

Convert the depth pass to depth values. Can be None if there is no depth image data.

_Returns:_  A decoded depth pass as a numpy array of floats.

#### get_point_cloud

**`self.get_point_cloud()`**

Returns a point cloud from the depth pass. Can be None if there is no depth image data.

_Returns:_  A decoded depth pass as a numpy array of floats.

#### get_collision_enters

**`self.get_collision_enters(collision_detection)`**


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| collision_detection |  CollisionDetection |  | The [`CollisionDetection`](collision_detection.md) rules. |

_Returns:_  A list of body IDs that entered a collision on this frame and *didn't* exit a collision on this frame, filtered by the collision detection rules.

