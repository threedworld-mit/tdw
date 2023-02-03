from io import BytesIO
from typing import List, Dict, Optional, Union
import numpy as np
from pathlib import Path
from tdw.tdw_utils import TDWUtils
from PIL import Image
from tdw.output_data import OutputData, Images, CameraMatrices, Replicants
from tdw.object_data.transform import Transform
from tdw.replicant.replicant_body_part import BODY_PARTS
from tdw.replicant.collision_detection import CollisionDetection
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.arm import Arm


class ReplicantDynamic:
    """
    Dynamic data for a replicant that can change per `communicate()` call (such as the position of the Replicant).
    """

    def __init__(self, resp: List[bytes], replicant_id: int, frame_count: int):
        """
        :param resp: The response from the build, which we assume contains `replicant` output data.
        :param replicant_id: The ID of this replicant.
        :param frame_count: The current frame count.
        """

        """:field
        The [`Transform`](../object_data/transform.md) of the Replicant.
        """
        self.transform: Transform = Transform(np.zeros(shape=3), np.zeros(shape=4), np.zeros(shape=3))
        """:field
        A dictionary of objects held in each hand. Key = [`Arm`](arm.md). Value = Object ID.
        """
        self.held_objects: Dict[Arm, int] = dict()
        """:field
        The images rendered by the robot as dictionary. Key = the name of the pass. Value = the pass as a numpy array.
        """
        self.images: Dict[str, np.array] = dict()
        """:field
        The [camera projection matrix](../../api/output_data.md#cameramatrices) of the Replicant's camera as a numpy array.
        """
        self.projection_matrix: Optional[np.array] = None
        """:field
        The [camera matrix](../../api/output_data.md#cameramatrices) of the Replicant's camera as a numpy array.
        """
        self.camera_matrix: Optional[np.array] = None
        # File extensions per pass.
        self.__image_extensions: Dict[str, str] = dict()
        """:field
        If True, we got images from the output data.
        """
        self.got_images: bool = False
        """:field
        Transform data for each body part. Key = Body part ID. Value = [`Transform`](../object_data/transform.md).
        """
        self.body_parts: Dict[int, Transform] = dict()
        """:field
        Collision data per body part. Key = Body part ID. Value = A list of object IDs that the body part collided with.
        """
        self.collisions: Dict[int, List[int]] = dict()
        """:field
        This is meant for internal use only. For certain actions, the build will update the Replicant's `ActionStatus`. *Do not use this field to check the Replicant's status.* Always check `replicant.action.status` instead. 
        """
        self.output_data_status: ActionStatus = ActionStatus.ongoing
        self._frame_count: int = frame_count
        self._replicant_id: int = replicant_id
        avatar_id = str(replicant_id)
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
                        # Get the held objects.
                        if replicants.get_is_holding_left(j):
                            self.held_objects[Arm.left] = replicants.get_held_left(j)
                        if replicants.get_is_holding_right(j):
                            self.held_objects[Arm.right] = replicants.get_held_right(j)
                        # Get the body part transforms.
                        for k in range(len(BODY_PARTS)):
                            # Cache the transform.
                            body_part_id = replicants.get_body_part_id(j, k)
                            self.body_parts[body_part_id] = Transform(position=replicants.get_body_part_position(j, k),
                                                                      forward=replicants.get_body_part_forward(j, k),
                                                                      rotation=replicants.get_body_part_rotation(j, k))
                            # Get collisions.
                            self.collisions[body_part_id] = list()
                            for m in range(10):
                                if replicants.get_is_collision(j, k, m):
                                    self.collisions[body_part_id].append(replicants.get_collision_id(j, k, m))
                        self.transform = Transform(position=replicants.get_position(j),
                                                   rotation=replicants.get_rotation(j),
                                                   forward=replicants.get_forward(j))
                        self.output_data_status = replicants.get_status(j)
                        # Get collision data.
                        got_data = True
                        break
            if got_data:
                break
        # Now that we have the body part IDs, iterate through the output data a second time to get collisions.
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            # Get the images captured by the avatar's camera.
            if r_id == "imag":
                images = Images(resp[i])
                # Get this robot's avatar and save the images.
                if images.get_avatar_id() == avatar_id:
                    self.got_images = True
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
            # Get the camera matrices for the avatar's camera.
            elif r_id == "cama":
                camera_matrices = CameraMatrices(resp[i])
                if camera_matrices.get_avatar_id() == avatar_id:
                    self.projection_matrix = camera_matrices.get_projection_matrix()
                    self.camera_matrix = camera_matrices.get_camera_matrix()

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
        prefix = TDWUtils.zero_padding(self._frame_count, 8)
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

    def get_pil_image(self, pass_mask: str = "img") -> Image.Image:
        """
        Convert raw image data to a PIL image.
        Use this function to read and analyze an image in memory.
        Do NOT use this function to save image data to disk; `save_image` is much faster.

        :param pass_mask: The pass mask. Options: `"img"`, `"id"`, `"depth"`.

        :return A PIL image.
        """

        if pass_mask == "depth":
            return Image.fromarray(self.images[pass_mask])
        else:
            return Image.open(BytesIO(self.images[pass_mask]))

    def get_collision_enters(self, collision_detection: CollisionDetection) -> List[int]:
        """
        :param collision_detection: The [`CollisionDetection`](collision_detection.md) rules.

        :return: A list of body IDs that entered a collision on this frame, filtered by the collision detection rules.
        """

        if not collision_detection.objects:
            return []
        enters: List[int] = list()
        for body_part_id in self.collisions:
            if body_part_id not in self.body_parts:
                continue
            for object_id in self.collisions[body_part_id]:
                if object_id in collision_detection.exclude_objects or object_id in self.body_parts:
                    continue
                # Ignore held objects.
                if collision_detection.held and (
                        (Arm.left in self.held_objects and self.held_objects[Arm.left] == object_id) or
                        (Arm.right in self.held_objects and self.held_objects[Arm.right] == object_id)):
                    continue
                enters.append(object_id)
        return enters

