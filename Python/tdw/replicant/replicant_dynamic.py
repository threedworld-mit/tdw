from typing import List, Dict, Optional, Tuple, Union
import numpy as np
from pathlib import Path
from tdw.tdw_utils import TDWUtils
from PIL import Image
from tdw.output_data import OutputData, Transforms, Collision, EnvironmentCollision, Images, CameraMatrices, Replicants
from tdw.object_data.transform import Transform
from tdw.collision_data.collision_obj_obj import CollisionObjObj
from tdw.collision_data.collision_obj_env import CollisionObjEnv
from tdw.replicant.arm import Arm
from tdw.replicant.replicant_body_part import ReplicantBodyPart, BODY_PARTS


class ReplicantDynamic:
    """
    Dynamic data for a replicant that can change per frame (such as the position of the replicant)

    """

    def __init__(self, resp: List[bytes], replicant_id: int, body_parts: List[int], frame_count: int, previous=None):
        """
        :param resp: The response from the build, which we assume contains `replicant` output data.
        :param replicant_id: The ID of this replicant.
        :param body_parts: The IDs of all body parts belonging to this replicant.
        :param previous: If not None, the previous replicantDynamic data. Use this to determine if the joints are moving.
        """
        """:field
        The ID of the replicant.
        """
        self.replicant_id = replicant_id
        """:field
        The current position of this replicant.
        """
        self.position: np.array = [0, 0, 0]
        """:field
        The current orientation of this replicant.
        """
        self.rotation: np.array = [0, 0, 0]
        """:field
        The current forward direction vector of this replicant.
        """
        self.forward: np.array = [0, 0, 0]
        """:field
        A dictionary of collisions between one of this replicant's [body parts (joints or non-moving)](replicant_static.md) and another object.
        Key = A tuple where the first element is the body part ID and the second element is the object ID.
        Value = A list of [collision data.](../../object_data/collision_obj_obj.md)
        """
        self.collisions_with_objects: Dict[Tuple[int, int], List[CollisionObjObj]] = dict()
        """:field
        A dictionary of collisions between two of this replicant's [body parts](replicant_static.md).
        Key = An unordered tuple of two body part IDs.
        Value = A list of [collision data.](../../object_data/collision_obj_obj.md)
        """
        self.collisions_with_self: Dict[Tuple[int, int], List[CollisionObjObj]] = dict()
        """:field
        A dictionary of collisions between one of this replicant's [body parts](replicant_static.md) and the environment (floors, walls, etc.).
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

        """
        self.images: Dict[str, np.array] = dict()
        """:field
        The [camera projection matrix](https://github.com/threedworld-mit/tdw/blob/master/Documentation/api/output_data.md#cameramatrices) of the Magnebot's camera as a numpy array.
        """
        self.projection_matrix: Optional[np.array] = None
        """:field
        The [camera matrix](https://github.com/threedworld-mit/tdw/blob/master/Documentation/api/output_data.md#cameramatrices) of the Magnebot's camera as a numpy array.
        """
        self.camera_matrix: Optional[np.array] = None
        """:field
        The current frame count. This is used for image filenames.
        """
        self.frame_count: int = frame_count
        # File extensions per pass.
        self.__image_extensions: Dict[str, str] = dict()
        got_replicant_images = False
        avatar_id = str(replicant_id)
        # Transform data for each body part.
        self.body_part_transforms: Dict[int, Transform] = dict()
        # A dictionary of collisions. Key = Body part ID. Value = Collision data.
        self.collisions: Dict[int, List[Union[Collision, EnvironmentCollision]]] = dict()
        got_data = False
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            # Get replicant's data.
            if r_id == "repl":
                replicants = Replicants(resp[i])
                for j in range(replicants.get_num()):
                    object_id = replicants.get_id(j)
                    # We found the ID of this replicant.
                    if object_id == replicant_id:
                        # The order of the data is always:
                        # [replicant_0, replicant_0_hand_l, replicant_0_hand_r, ... ,replicant_1, replicant_1_hand_l, ... ]
                        # So, having found the ID of this replicant, we know that the next IDs are those of its body parts.
                        for k in range(len(BODY_PARTS)):
                            body_part_index = j + k + 1
                            body_part_transform = Transform(position=replicants.get_position(body_part_index),
                                                            forward=replicants.get_forward(body_part_index),
                                                            rotation=replicants.get_rotation(body_part_index))
                            # Cache the transform.
                            self.body_part_transforms[replicants.get_id(body_part_index)] = body_part_transform
                        # Stop reading output data. We have what we need.
                        self.position=replicants.get_position(0)
                        self.forward=replicants.get_forward(0)
                        self.rotation=replicants.get_rotation(0)
                        got_data = True
                        break
            if got_data:
                break
        # Now that we have the body part IDs, iterate through the output data a second time to get collisions.
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            # This is a collision.
            if r_id == "coll":
                collision = Collision(resp[i])
                collider_id = collision.get_collider_id()
                collidee_id = collision.get_collidee_id()
                # This collision included body parts.
                if collider_id in self.body_part_transforms:
                    body_part_id = collider_id
                elif collidee_id in self.body_part_transforms:
                    body_part_id = collidee_id
                else:
                    body_part_id = None
                if body_part_id is not None:
                    if body_part_id not in self.collisions:
                        self.collisions[body_part_id] = list()
                    # Record the collision.
                    self.collisions[body_part_id].append(collision)
                #print("registered object collision: " + str(collider_id) + " with " + str(collidee_id))
            # This is an environment collision.
            elif r_id == "enco":
                collision = EnvironmentCollision(resp[i])
                collider_id = collision.get_object_id()
                if collider_id not in self.collisions:
                    self.collisions[collider_id] = list()
                # Record the collision.
                self.collisions[collider_id].append(collision)
                #print("registered environment collision with " + str(collider_id))
            # Get the images captured by the avatar's camera.
            elif r_id == "imag":
                images = Images(resp[i])
                # Get this robot's avatar and save the images.
                if images.get_avatar_id() == avatar_id:
                    got_replicant_images = True
                    for j in range(images.get_num_passes()):
                        image_data = images.get_image(j)
                        pass_mask = images.get_pass_mask(j)
                        if pass_mask == "_depth":
                            image_data = TDWUtils.get_shaped_depth_pass(images=images, index=j)
                        # Remove the underscore from the pass mask such as: _img -> img
                        pass_name = pass_mask[1:]
                        # Save the image data.
                        self.images[pass_name] = image_data
                        # Record the file extension.
                        self.__image_extensions[pass_name] = images.get_extension(j)
                        self.save_images("D://TDW_Strategic_Plan_2021//HumanoidAgent//replicant_pov_images//")
            # Get the camera matrices for the avatar's camera.
            elif r_id == "cama":
                camera_matrices = CameraMatrices(resp[i])
                if camera_matrices.get_avatar_id() == avatar_id:
                    self.projection_matrix = camera_matrices.get_projection_matrix()
                    self.camera_matrix = camera_matrices.get_camera_matrix()
        # Update the frame count.
        if got_replicant_images:
            self.frame_count += 1


    def save_images(self, output_directory: Union[str, Path]) -> None:
        """
        Save the ID pass (segmentation colors) and the depth pass to disk.
        Images will be named: `[frame_number]_[pass_name].[extension]`
        For example, the depth pass on the first frame will be named: `00000000_depth.png`

        The `img` pass is either a .jpg. The `id` and `depth` passes are .png files.

        :param output_directory: The directory that the images will be saved to.
        """

        if isinstance(output_directory, str):
            output_directory = Path(output_directory)
        if not output_directory.exists():
            output_directory.mkdir(parents=True)
        # The prefix is a zero-padded integer to ensure sequential images.
        prefix = TDWUtils.zero_padding(self.frame_count, 8)
        # Save each image.
        for pass_name in self.images:
            if self.images[pass_name] is None:
                continue
            # Get the filename, such as: `00000000_img.png`
            p = output_directory.joinpath(f"{prefix}_{pass_name}.{self.__image_extensions[pass_name]}")
            if pass_name == "depth":
                Image.fromarray(self.images[pass_name]).save(str(p.resolve()))
            else:
                with p.open("wb") as f:
                    f.write(self.images[pass_name])

    def get_pil_images(self) -> Dict[str, Image.Image]:
        """
        Convert each image pass from the robot camera to PIL images.

        :return: A dictionary of PIL images. Key = the pass name (img, id, depth); Value = The PIL image (can be None)
        """

        images = dict()
        for pass_name in self.images:
            if pass_name == "depth":
                images[pass_name] = Image.fromarray(self.images[pass_name])
            else:
                images[pass_name] = Image.open(BytesIO(self.images[pass_name]))
        return images

    def get_depth_values(self) -> np.array:
        """
        Convert the depth pass to depth values. Can be None if there is no depth image data.

        :return: A decoded depth pass as a numpy array of floats.
        """

        if "depth" in self.images:
            return TDWUtils.get_depth_values(self.images["depth"])
        else:
            return None

    def get_point_cloud(self) -> np.array:
        """
        Returns a point cloud from the depth pass. Can be None if there is no depth image data.

        :return: A decoded depth pass as a numpy array of floats.
        """

        if "depth" in self.images:
            return TDWUtils.get_point_cloud(depth=TDWUtils.get_depth_values(self.images["depth"]),
                                            camera_matrix=self.camera_matrix, far_plane=100, near_plane=1)
        else:
            return None
