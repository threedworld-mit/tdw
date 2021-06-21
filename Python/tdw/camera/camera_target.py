from abc import ABC, abstractmethod
from typing import List, Dict, Union, Optional
import numpy as np
from tdw.output_data import OutputData, Transforms, Bounds, AvatarKinematic
from tdw.transform import Transform
from tdw.tdw_utils import TDWUtils


class CameraTarget(ABC):
    """
    A target for a third-person camera.
    """

    def __init__(self, avatar_id: str, target: Union[int, Dict[str, float]] = None, speed: float = None,
                 centroid: bool = True):
        """
        :param avatar_id: The ID of the avatar (the camera).
        :param target: The target of the camera.
        :param speed: If None, the camera will instantly move/rotate/etc. the target. Otherwise, the camera will move/rotate/etc. towards the target per frame at this speed.
        :param centroid: If True and `target` is an `int`, use the centroid of the target object as the target. If False and `target` is an `int`, use the bottom-center of the object as the target.
        """

        self.avatar_id: str = avatar_id
        self.target: Optional[Union[int, Dict[str, float]]] = target
        self.speed: float = speed
        self.centroid: bool = centroid

    def get_commands(self, resp: List[bytes]) -> List[dict]:
        """
        :param resp: The most recent response from the build.

        :return: A list of commands for the next frame.
        """

        if self.speed is None:
            return self._get_instant_commands(resp=resp)
        else:
            return self._get_lerp_commands(resp=resp)

    @abstractmethod
    def _get_instant_commands(self, resp: List[bytes]) -> List[dict]:
        """
        :param resp: The most recent response from the build.

        :return: A list of commands to instantly move or rotate the camera.
        """

        raise Exception()

    @abstractmethod
    def _get_lerp_commands(self, resp: List[bytes]) -> List[dict]:
        """
        :param resp: The most recent response from the build.

        :return: A list of commands to move or rotate the camera towards the target.
        """

        raise Exception()

    def _get_transforms(self, resp: List[bytes]) -> Transform:
        """
        :param resp: The most recent response from the build.

        :return: The Transform data for the target object.
        """

        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "tran":
                tr = Transforms(resp[i])
                for j in range(tr.get_num()):
                    if tr.get_id(j) == self.target:
                        return Transform(position=np.array(tr.get_position(j)),
                                         rotation=np.array(tr.get_rotation(j)),
                                         forward=np.array(tr.get_forward(j)))
        raise Exception("Transform output data for target object not found in the response from the build.")

    def _get_bounds(self, resp: List[bytes]) -> Dict[str, np.array]:
        """
        :param resp: The most recent response from the build.

        :return: The bounds dictionary for the target object.
        """

        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "boun":
                b = Bounds(resp[i])
                for j in range(b.get_num()):
                    if b.get_id(j) == self.target:
                        return TDWUtils.get_bounds_dict(b, j)
        raise Exception("Bounds output data for target object not found in the response from the build.")

    def _get_target_position(self, resp: List[bytes]) -> Dict[str, float]:
        """
        :param resp: The most recent response from the build.

        :return: The target expressed as a spatial position.
        """

        if isinstance(self.target, int):
            # Target the centroid of the object.
            if self.centroid:
                return TDWUtils.array_to_vector3(self._get_bounds(resp=resp)["center"])
            # Target the bottom-center of the object.
            else:
                return TDWUtils.array_to_vector3(self._get_transforms(resp=resp).position)
        # Target a position.
        else:
            return self.target

    def _get_avatar(self, resp: List[bytes]) -> AvatarKinematic:
        """
        :param resp: The most recent response from the build.

        :return: Output data for this avatar.
        """

        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "avki":
                a = AvatarKinematic(resp[i])
                # Make sure this is the correct avatar.
                if a.get_avatar_id() == self.avatar_id:
                    return a
        raise Exception("Avatar output data not found in the response from the build.")
