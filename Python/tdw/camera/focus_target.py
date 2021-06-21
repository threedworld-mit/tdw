from typing import Union, Dict, List
import numpy as np
from tdw.tdw_utils import TDWUtils
from tdw.camera.camera_target import CameraTarget


class FocusTarget(CameraTarget):
    """
    A target object, position, or distance to focus to or towards.
    """

    def __init__(self, avatar_id: str, target: Union[int, float, Dict[str, float]] = None, speed: float = None,
                 centroid: bool = True, is_object: bool = True):
        """
        :param avatar_id: The ID of the avatar (the camera).
        :param target: The target object ID, position, or distance.
        :param speed: If None, the camera will instantly focus on the target. Otherwise, the camera will focus on the target at this speed per frame.
        :param centroid: If True and `target` is an `int` and `is_object` is True, use the centroid of the target object as the target. If False and `target` is an `int`, use the bottom-center of the object as the target.
        :param is_object: If True, `target` is parsed as an object ID integer. If False, `target` is parsed as a distance in meters.
        """

        super().__init__(avatar_id=avatar_id, target=target, speed=speed, centroid=centroid)
        self.is_object: bool = is_object

    def _get_instant_commands(self, resp: List[bytes]) -> List[dict]:
        if self.target is None:
            return []
        elif self.is_object and isinstance(self.target, int):
            return [{"$type": "focus_on_object",
                     "object_id": self.target,
                     "use_centroid": self.centroid,
                     "avatar_id": self.avatar_id}]
        elif isinstance(self.target, float) or isinstance(self.target, int):
            return [{"$type": "set_focus_distance",
                     "focus_distance": self.target}]
        elif isinstance(self.target, dict):
            return [{"$type": "set_focus_distance",
                     "focus_distance": float(np.linalg.norm(np.array(self._get_avatar(resp=resp).get_position()) -
                                                            np.array(self.target)))}]
        else:
            raise TypeError(f"Bad target type: {self.target}")

    def _get_lerp_commands(self, resp: List[bytes]) -> List[dict]:
        if self.target is None:
            return []
        else:
            if self.is_object and isinstance(self.target, int):
                d = np.linalg.norm(np.array(self._get_avatar(resp=resp).get_position()) -
                                   TDWUtils.vector3_to_array(self._get_target_position(resp=resp)))
            elif isinstance(self.target, float) or isinstance(self.target, int):
                d = self.target
            elif isinstance(self.target, dict):
                d = np.linalg.norm(np.array(self._get_avatar(resp=resp).get_position()) -
                                   TDWUtils.vector3_to_array(self.target))
            else:
                raise TypeError(f"Bad target type: {self.target}")
            return [{"$type": "focus_towards",
                     "focus_distance": float(d)}]
