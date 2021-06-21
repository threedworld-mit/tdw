from typing import List, Union, Dict
import numpy as np
from tdw.tdw_utils import TDWUtils
from tdw.camera.camera_target import CameraTarget


class MoveTarget(CameraTarget):
    """
    A target for the camera to move to or towards.
    """

    def __init__(self, avatar_id: str, target: Union[int, Dict[str, float]] = None, speed: float = None,
                 centroid: bool = True):
        """
        :param avatar_id: The ID of the avatar (the camera).
        :param target: If an `int`, move to or towards an object with a matching ID. If `Dict[str, float]`, move to a target position expressed as an XYZ dictionary.
        :param speed: If None, the camera will instantly move to the target. Otherwise, the camera will move the target this many meters per frame.
        :param centroid: If True and `target` is an `int`, use the centroid of the target object as the target. If False and `target` is an `int`, use the bottom-center of the object as the target.
        """

        super().__init__(avatar_id=avatar_id, target=target, speed=speed, centroid=centroid)

    def get_commands(self, resp: List[bytes]) -> List[dict]:
        if self.target is None:
            return []
        else:
            return super().get_commands(resp=resp)

    def _get_instant_commands(self, resp: List[bytes]) -> List[dict]:
        return [{"$type": "teleport_avatar_to",
                 "position": self._get_target_position(resp=resp),
                 "avatar_id": self.avatar_id}]

    def _get_lerp_commands(self, resp: List[bytes]) -> List[dict]:
        # Get the target position.
        destination = TDWUtils.vector3_to_array(self._get_target_position(resp=resp))
        # Get the current position of the avatar.
        origin = np.array(self._get_avatar(resp=resp).get_position())
        # Get the movement vector.
        v = destination - origin
        v = v / np.linalg.norm(v)
        v = origin + v * self.speed
        return [{"$type": "teleport_avatar_to",
                 "position": TDWUtils.array_to_vector3(v),
                 "avatar_id": self.avatar_id}]
