# ReplicantDynamic

`from tdw.replicant.replicant_dynamic import ReplicantDynamic`

Dynamic data for a replicant that can change per `communicate()` call (such as the position of the Replicant).

***

## Fields

- `transform` The [`Transform`](../object_data/transform.md) of the Replicant.

- `held_objects` A dictionary of objects held in each hand. Key = [`Arm`](arm.md). Value = Object ID.

- `images` The images rendered by the robot as dictionary. Key = the name of the pass. Value = the pass as a numpy array.

- `projection_matrix` The [camera projection matrix](../../api/output_data.md#cameramatrices) of the Replicant's camera as a numpy array.

- `camera_matrix` The [camera matrix](../../api/output_data.md#cameramatrices) of the Replicant's camera as a numpy array.

- `got_images` If True, we got images from the output data.

- `body_parts` Transform data for each body part. Key = Body part ID. Value = [`Transform`](../object_data/transform.md).

- `collisions` Collision data per body part. Key = Body part ID. Value = A list of object IDs that the body part collided with.

- `output_data_status` This is meant for internal use only. For certain actions, the build will update the Replicant's `ActionStatus`. *Do not use this field to check the Replicant's status.* Always check `replicant.action.status` instead.

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

#### get_collision_enters

**`self.get_collision_enters(collision_detection)`**


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| collision_detection |  CollisionDetection |  | The [`CollisionDetection`](collision_detection.md) rules. |

_Returns:_  A list of body IDs that entered a collision on this frame, filtered by the collision detection rules.

