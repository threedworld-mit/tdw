from tdw.librarian import HumanoidAnimationLibrarian, HumanoidLibrarian
from typing import List, Dict, Union
from tdw.output_data import OutputData, Transforms, LocalTransforms, EmptyObjects, Bounds
import numpy as np
from tdw.tdw_utils import TDWUtils
from tdw.quaternion_utils import QuaternionUtils
from tdw.replicant.replicant_utils import ReplicantUtils
from tdw.replicant.actions.action import Action
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.collision_detection import CollisionDetection
from tdw.replicant.image_frequency import ImageFrequency
from tdw.replicant.affordance_points import AffordancePoints
from tdw.replicant.actions.arm_motion import ArmMotion
from tdw.replicant.arm import Arm


class Drop(ArmMotion):
    """
    Drop a grasped target object.
    """

    def __init__(self, target: Union[int, np.ndarray, Dict[str,  float]], resp: List[bytes], arm: Arm, hand_position: np.ndarray, 
                 dynamic: ReplicantDynamic, collision_detection: CollisionDetection, previous: Action = None):
        super().__init__(dynamic=dynamic, arm=arm, collision_detection=collision_detection, previous=previous)
        self.affordance_id = 0
        self.hand_position = hand_position
        self.frame_count = 0
        self.target = target
        self.target_position = {"x": 0,"y": 0,"z": 0}
        self.initialized_reach = False
        self.initialized_affordances = False
        # Convert from a numpy array to a dictionary.
        if isinstance(target, np.ndarray):
            self.target_position = TDWUtils.array_to_vector3(target)
        # The target is a vector3 position.
        elif isinstance(target, dict):
            self.target_position = target
        self.offset = AffordancePoints.AFFORDANCE_POINTS_BY_OBJECT_ID[object_id][empty_object_id]



    def get_initialization_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        commands = super().get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                       image_frequency=image_frequency)
        # Remember the image frequency for the action.
        self.__image_frequency: ImageFrequency = image_frequency
        return commands

    def get_ongoing_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
        # We've completed the drop.
        if self.frame_count >= self.reset_action_length:
            self.status = ActionStatus.success
            return []
        elif not self._is_valid_ongoing(dynamic=dynamic):
            return []
        else:
            while self.frame_count < self.reset_action_length:
                self.frame_count += 1 
                return []

        
        
        commands.extend(ReachForAffordancePoint._reset_affordance_points(self.t_id))