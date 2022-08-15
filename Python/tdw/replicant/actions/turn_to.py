from typing import Union, Dict, List
import numpy as np
from tdw.tdw_utils import TDWUtils
from tdw.output_data import Transforms
from tdw.quaternion_utils import QuaternionUtils
from tdw.replicant.replicant_utils import ReplicantUtils
from tdw.replicant.actions.action import Action
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.collision_detection import CollisionDetection
from tdw.replicant.image_frequency import ImageFrequency

class TurnTo(Action):
    """
    Turn to a target position or object.
    """

    def __init__(self, target: Union[int, Dict[str, float]], resp: List[bytes], dynamic: ReplicantDynamic,
                 collision_detection: CollisionDetection, previous: Action = None):
        """
        :param target: The target. If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array.
        :param resp: The response from the build.
        :param aligned_at: If the difference between the current angle and the target angle is less than this value, then the action is successful.
        :param dynamic: [The dynamic Replicant data.](../magnebot_dynamic.md)
        :param collision_detection: [The collision detection rules.](../collision_detection.md)
        :param previous: The previous action, if any.
        """
        self.target_position = {"x": 0,"y": 0,"z": 0}
        # Set the target position.
        if isinstance(target, int):
            # Get the position of the object.
            self.target_position = ReplicantUtils.get_object_position(resp=resp, object_id=target)
        elif isinstance(target, dict):
            self.target_position = target
        else:
            raise Exception(f"Invalid target: {target}")
        self._initial_rotation = dynamic.rotation
        self.target_arr = TDWUtils.vector3_to_array(self.target_position)
        self._angle = self._get_angle(dynamic=dynamic)
        self.turned = False
        super().__init__()

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
        # Turn to face position. 
        commands = []    
        commands.append({"$type": "humanoid_look_at_position", 
                         "position": self.target_position, 
                         "id": dynamic.replicant_id})
        return commands

    def _get_angle(self, dynamic: ReplicantDynamic) -> float:
        return TDWUtils.get_angle_between(v1=dynamic.forward,
                                          v2=self.target_arr - dynamic.position)

