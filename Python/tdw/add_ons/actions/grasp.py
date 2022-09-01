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


class Grasp(ArmMotion):
    """
    Grasp a target object.
    """

    def __init__(self, target: int, resp: List[bytes], arm: Arm, static: ReplicantStatic, dynamic: ReplicantDynamic, 
                 collision_detection: CollisionDetection, previous: Action = None):
        super().__init__(dynamic=dynamic, arm=arm, collision_detection=collision_detection, previous=previous)
        self.static=static
        self.affordance_id = -1
        self.frame_count = 0
        self._target = target
        self.initialized_grasp = False

    def get_initialization_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        # This Replicant is already holding the object.
        if self._target in dynamic.held[Arm.left] or self._target in dynamic.held[Arm.right]:
            self.status = ActionStatus.success
            return []
        commands = super().get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                       image_frequency=image_frequency)
        # Remember the image frequency for the action.
        self.__image_frequency: ImageFrequency = image_frequency
        commands.append({"$type": "humanoid_grasp_object", 
                          "target": self._target, 
                          "affordance_id": self.static.target_affordance_id, 
                          "id": dynamic.replicant_id, 
                          "arm": self.reach_arm})
        return commands

    def get_ongoing_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
        if not self.initialized_grasp:
            commands = []
            commands.extend(self._get_hold_object_commands(dynamic=dynamic,
                                                           target_position = ReplicantUtils.get_object_position(resp=resp, object_id=self._target), 
                                                           object_id=self._target, 
                                                           affordance_id=self.static.target_affordance_id))
            self.initialized_grasp = True
            return commands
        # We've completed the grasping sequence.
        if self.frame_count >= self.reset_action_length:
            self.status = ActionStatus.success
            # Add this object to the held objects for the grasping arm.
            if self.reach_arm == "left":
                dynamic.held[Arm.left].append(self._target)
            else:
                dynamic.held[Arm.right].append(self._target)
            return []
        elif not self._is_valid_ongoing(dynamic=dynamic):
            return []
        else:
            while self.frame_count < self.reset_action_length:
                self.frame_count += 1 
                return []

    def _is_success(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> bool:
        return self._target in dynamic.held[self.reach_arm]

    def _previous_was_same(self, previous: Action) -> bool:
        if isinstance(previous, MoveBy):
            return (previous.distance > 0 and self.distance > 0) or (previous.distance < 0 and self.distance < 0)
        else:
            return False
