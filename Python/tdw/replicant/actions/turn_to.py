from typing import Union, Dict, List
import numpy as np
from tdw.tdw_utils import TDWUtils
from tdw.output_data import Transforms
from tdw.replicant.replicant_utils import ReplicantUtils
from tdw.replicant.action import Action

class TurnTo(Action):
    """
    Turn to a target position or object.
    """

    def __init__(self, target: Union[int, Dict[str, float], np.array], resp: List[bytes], dynamic: MagnebotDynamic,
                 collision_detection: CollisionDetection, aligned_at: float = 1, previous: Action = None):
        """
        :param target: The target. If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array.
        :param resp: The response from the build.
        :param aligned_at: If the difference between the current angle and the target angle is less than this value, then the action is successful.
        :param dynamic: [The dynamic Magnebot data.](../magnebot_dynamic.md)
        :param collision_detection: [The collision detection rules.](../collision_detection.md)
        :param previous: The previous action, if any.
        """

        self.object_position = {"x": 0,"y": 0,"z": 0}
        # Set the target position.
        if isinstance(target, int):
            # Get the position of the object.
            self.object_position = ReplicantUtils.get_object_position(target)
        elif isinstance(target, dict):
            self.object_position = target
        else:
            raise Exception(f"Invalid target: {target}")
        super().__init__(aligned_at=aligned_at, dynamic=dynamic, collision_detection=collision_detection,
                         previous=previous)


    def _get_turn_command(self, replicant_id: int) -> dict:
            # Turn to face position.     
            return({"$type": "humanoid_look_at_position", 
                                  "position": self.object_position, 
                                  "id": replicant_id})
