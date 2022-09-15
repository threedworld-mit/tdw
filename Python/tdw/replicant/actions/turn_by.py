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


        super().__init__(aligned_at=aligned_at, dynamic=dynamic, collision_detection=collision_detection,
                         previous=previous)


    def _get_turn_command(self, replicant_id: int) -> dict:
            # Turn to face position.     
            return({"$type": "replicant_look_at_position", 
                                  "position": self.object_position, 
                                  "id": replicant_id})
