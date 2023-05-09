from typing import Union, Dict, List
import numpy as np
from tdw.tdw_utils import TDWUtils
from tdw.drone.actions.action import Action
from tdw.drone.action_status import ActionStatus
from tdw.drone.drone_dynamic import droneDynamic
from tdw.drone.image_frequency import ImageFrequency


class TurnTo(Action):
    """
    Turn to a target object or position.

    This is a non-animated action, meaning that the drone will immediately snap to the angle.
    """

    def __init__(self, target: Union[int, Dict[str, float], np.ndarray]):
        """
        :param target: The target. If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array.
        """

        super().__init__()
        self._target: Union[int, Dict[str, float], np.ndarray] = target

    def get_initialization_commands(self, resp: List[bytes], dynamic: droneDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        commands = super().get_initialization_commands(resp=resp, dynamic=dynamic,
                                                       image_frequency=image_frequency)
        if isinstance(self._target, int):
            position = TDWUtils.array_to_vector3(self._get_object_position(object_id=self._target, resp=resp))
        elif isinstance(self._target, np.ndarray):
            position = TDWUtils.array_to_vector3(self._target)
        elif isinstance(self._target, dict):
            position = {k: v for k, v in self._target.items()}
        else:
            raise Exception(f"Invalid target: {self._target}")
        # Set the y value to match the drone's y value.
        position["y"] = float(dynamic.transform.position[1])
        commands.append({"$type": "object_look_at_position",
                         "position": position,
                         "id": dynamic.drone_id})
        commands.append({"$type": "drone_step",
                         "id": dynamic.drone_id})
        return commands

    def get_ongoing_commands(self, resp: List[bytes], dynamic: droneDynamic) -> List[dict]:
        self.status = ActionStatus.success
        return super().get_ongoing_commands(resp=resp, dynamic=dynamic)
