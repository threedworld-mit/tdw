from tdw.librarian import HumanoidAnimationLibrarian, HumanoidLibrarian
from tdw.container_data.container_tag import ContainerTag
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
        # First include any objects contained by the target object.
        for container_shape_id in self.static.container_manager.events:
            event = self.static.container_manager.events[container_shape_id]
            object_id = self.static.container_manager.container_shapes[container_shape_id]
            tag = self.static.container_manager.tags[container_shape_id]
            if object_id == self._target and tag == ContainerTag.inside:
                for ob_id in event.object_ids:
                    commands.extend([{"$type": "parent_object_to_object", 
                                      "parent_id": self._target, 
                                      "id": int(ob_id)},
                                     {"$type": "set_kinematic_state", 
                                      "id": int(ob_id), 
                                      "is_kinematic": True, 
                                      "use_gravity": False}])
        return commands

    def get_ongoing_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
        if not self.initialized_grasp:
            commands = []
            commands.append({"$type": "humanoid_grasp_object", 
                            "target": self._target, 
                            "primary_affordance_id": static.primary_target_affordance_id,
                            "secondary_affordance_id": static.secondary_target_affordance_id,  
                            "id": dynamic.replicant_id, 
                            "arm": self.reach_arm})
            commands.extend(self._get_hold_object_commands(static=static,
                                                           dynamic=dynamic, 
                                                           object_id=self._target))
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
