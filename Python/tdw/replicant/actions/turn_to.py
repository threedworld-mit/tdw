from typing import List
import numpy as np
from tdw.type_aliases import TARGET
from tdw.tdw_utils import TDWUtils
from tdw.replicant.actions.action import Action
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.image_frequency import ImageFrequency


class TurnTo(Action):
    """
    Turn to a target object or position.

    This is a non-animated action, meaning that the Replicant will immediately snap to the angle.
    """

    def __init__(self, target: TARGET):
        """
        :param target: The target. If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array.
        """

        super().__init__()
        self._target: TARGET = target

    def get_initialization_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        commands = super().get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                       image_frequency=image_frequency)
        if isinstance(self._target, int):
            position = TDWUtils.array_to_vector3(self._get_object_position(object_id=self._target, resp=resp))
        elif isinstance(self._target, np.ndarray):
            position = TDWUtils.array_to_vector3(self._target)
        elif isinstance(self._target, dict):
            position = {k: v for k, v in self._target.items()}
        else:
            raise Exception(f"Invalid target: {self._target}")
        # Set the y value to match the Replicant's y value.
        position["y"] = float(dynamic.transform.position[1])
        commands.append({"$type": "object_look_at_position",
                         "position": position,
                         "id": static.replicant_id})
        commands.append({"$type": "replicant_step",
                         "id": static.replicant_id})
        return commands

    def get_ongoing_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
        self.status = ActionStatus.success
        return super().get_ongoing_commands(resp=resp, static=static, dynamic=dynamic)
