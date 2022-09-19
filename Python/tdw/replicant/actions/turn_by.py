from typing import Union, Dict, List
import numpy as np
from tdw.tdw_utils import TDWUtils
from tdw.output_data import Transforms
from tdw.replicant.replicant_utils import ReplicantUtils
from tdw.replicant.actions.action import Action
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.collision_detection import CollisionDetection
from tdw.replicant.image_frequency import ImageFrequency

class TurnBy(Action):
    """
    Turn by a specified angle.
    """

    def __init__(self, angle: float, resp: List[bytes], dynamic: ReplicantDynamic,
                 collision_detection: CollisionDetection, aligned_at: float = 1, previous: Action = None):
        """
        :param target: The target. If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array.
        :param resp: The response from the build.
        :param aligned_at: If the difference between the current angle and the target angle is less than this value, then the action is successful.
        :param dynamic: [The dynamic Magnebot data.](../magnebot_dynamic.md)
        :param collision_detection: [The collision detection rules.](../collision_detection.md)
        :param previous: The previous action, if any.
        """

        super().__init__()
        self.turned = False
        self.angle = angle


    def get_initialization_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        commands = super().get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                       image_frequency=image_frequency)
        # Remember the image frequency for the move action.
        self.__image_frequency: ImageFrequency = image_frequency
        return commands

    def get_ongoing_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
        if self.turned:
            self.status = ActionStatus.success
            return []
        else:
            commands = []
            commands.extend(self._get_turn_command(dynamic=dynamic))
            self.turned = True
            return commands

    def _get_turn_command(self, dynamic: ReplicantDynamic) -> dict:
        # Turn by a given angle.
        commands = []     
        pos = TDWUtils.array_to_vector3(dynamic.position)
        pos["z"] = pos["z"] + 0.1
        pos["y"] = pos["y"] + 1.0
        dest = TDWUtils.array_to_vector3(dynamic.position + dynamic.forward * 1.0)
        commands.extend([{"$type": "rotate_object_by", 
                         "angle": self.angle, "id": dynamic.replicant_id, 
                         "axis": "yaw",
                         "is_world": True,
                         "use_centroid": False},
                         {"$type": "send_boxcast",
                          "half_extents": {"x": 0.1, "y": 0.1, "z": 0.25},
                          "origin": pos,
                          "destination": dest,
                          "id": 99999}])
        return commands
