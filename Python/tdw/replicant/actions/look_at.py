from typing import List
import numpy as np
from tdw.tdw_utils import TDWUtils
from tdw.type_aliases import TARGET
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.actions.head_motion import HeadMotion
from tdw.replicant.image_frequency import ImageFrequency


class LookAt(HeadMotion):
    """
    Look at a target object or position.

    The head will continuously move over multiple `communicate()` calls until it is looking at the target.
    """

    def __init__(self, target: TARGET, duration: float, scale_duration: bool):
        """
        :param target: The target. If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array.
        :param duration: The duration of the motion in seconds.
        :param scale_duration: If True, `duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds.
        """

        super().__init__(duration=duration, scale_duration=scale_duration)
        """:field
        The target. If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array.
        """
        self.target: TARGET = target

    def get_initialization_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        commands = super().get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                       image_frequency=image_frequency)
        # Look at a target position.
        if isinstance(self.target, np.ndarray):
            commands.append({"$type": "replicant_look_at_position",
                             "id": static.replicant_id,
                             "position": TDWUtils.array_to_vector3(self.target),
                             "duration": self.duration})
        # Reach for a target position.
        elif isinstance(self.target, dict):
            commands.append({"$type": "replicant_look_at_position",
                             "id": static.replicant_id,
                             "position": self.target,
                             "duration": self.duration})
        # Reach for a target object.
        elif isinstance(self.target, int):
            commands.append({"$type": "replicant_look_at_object",
                             "id": static.replicant_id,
                             "object_id": self.target,
                             "use_centroid": True,
                             "duration": self.duration})
        else:
            raise Exception(f"Invalid target: {self.target}")
        return commands
