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

    def __init__(self, target: int, resp: List[bytes], arm: Arm, static: ReplicantStatic, dynamic: ReplicantDynamic, 
                 collision_detection: CollisionDetection, held_objects: Dict[Arm, List[int]], previous: Action = None):
        super().__init__(dynamic=dynamic, arm=arm, collision_detection=collision_detection, previous=previous)
        self._frame_count = 0
        self._target = target
        self._held_objects = held_objects
        self._initialized_drop = False
        #self.offset = AffordancePoints.AFFORDANCE_POINTS_BY_OBJECT_ID[self._target][self.static.primary_target_affordance_id]

    def get_initialization_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        commands = super().get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                       image_frequency=image_frequency)
        # Remember the image frequency for the action.
        self.__image_frequency: ImageFrequency = image_frequency
        return commands

    def get_ongoing_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
        if not self._initialized_drop:
            commands = []
            commands.extend(self._get_drop_commands(static=static,
                                                    object_id=self._target))
            self._initialized_drop = True
            return commands
        # We've completed the drop.
        if self._frame_count >= self._drop_length:
            self.status = ActionStatus.success
            # Remove the target object from the appropriate held objects list.
            self._held_objects[self._reach_arm].remove(self._target)
            # Reset the target object's affordance points to their original state.
            commands = []
            commands.extend(AffordancePoints.reset_affordance_points(self._target))
            return commands
        elif not self._is_valid_ongoing(dynamic=dynamic):
            return []
        else:
            while self._frame_count < self._drop_length:
                self._frame_count += 1 
                return []

    def _previous_was_same(self, previous: Action) -> bool:
        """
        if isinstance(previous, MoveBy):
            return (previous.distance > 0 and self.distance > 0) or (previous.distance < 0 and self.distance < 0)
        else:
            return False
        """
        return False
        
        
        