from typing import Union, Dict, List
import numpy as np
from tdw.tdw_utils import TDWUtils
from tdw.replicant.actions.action import Action
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.agents.image_frequency import ImageFrequency


class TurnTo(Action):
    """
    Turn to a target object or position.
    """

    def __init__(self, target: Union[int, Dict[str, float], np.ndarray]):
        """
        :param target: The target. If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array.
        """

        super().__init__()
        self._target: Union[int, Dict[str, float], np.ndarray] = target

    def get_initialization_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        commands = super().get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                       image_frequency=image_frequency)
        if isinstance(self._target, int):
            commands.append({"$type": "object_look_at",
                             "other_object_id": int(self._target),
                             "id": static.replicant_id})
        elif isinstance(self._target, np.ndarray):
            commands.append({"$type": "object_look_at_position",
                             "position": TDWUtils.array_to_vector3(self._target),
                             "id": static.replicant_id})
        elif isinstance(self._target, dict):
            commands.append({"$type": "object_look_at_position",
                             "position": self._target,
                             "id": static.replicant_id})
        else:
            raise Exception(f"Invalid target: {self._target}")
        return commands

    def get_ongoing_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
        self.status = ActionStatus.success
        return []