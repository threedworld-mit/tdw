from typing import List, Dict, Union
import numpy as np
from tdw.tdw_utils import TDWUtils
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.actions.head_motion import HeadMotion
from tdw.replicant.image_frequency import ImageFrequency


class LookAt(HeadMotion):
    """
    Look at a target object or position.
    """

    def __init__(self, target: Union[int, np.ndarray, Dict[str,  float]], duration: float = 0.1):
        """
        :param target: The target. If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array.
        :param duration: The duration of the motion in seconds.
        """

        super().__init__(duration=duration)
        self._target: Union[int, np.ndarray, Dict[str,  float]] = target

    def get_initialization_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        commands = super().get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                       image_frequency=image_frequency)
        # Look at a target position.
        if isinstance(self._target, np.ndarray):
            commands.append({"$type": "replicant_look_at_position",
                             "id": static.replicant_id,
                             "position": TDWUtils.array_to_vector3(self._target),
                             "duration": self._duration})
        # Reach for a target position.
        elif isinstance(self._target, dict):
            commands.append({"$type": "replicant_look_at_position",
                             "id": static.replicant_id,
                             "position": self._target,
                             "duration": self._duration})
        # Reach for a target object.
        elif isinstance(self._target, int):
            commands.append({"$type": "replicant_look_at_object",
                             "id": static.replicant_id,
                             "object_id": self._target,
                             "use_centroid": True,
                             "duration": self._duration})
        else:
            raise Exception(f"Invalid target: {self._target}")
        return commands
