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
from tdw.replicant.replicant_body_part import ReplicantBodyPart, BODY_PARTS



"""
Reach for a target object or position, using one or both arms.
"""


class ReachFor(ArmMotion):
    """
    Reach for a target object or position.
    """

    def __init__(self, target: Union[int, np.ndarray, Dict[str,  float]], resp: List[bytes], arm: Arm, static: ReplicantStatic, 
                 dynamic: ReplicantDynamic, collision_detection: CollisionDetection, held_objects: Dict[Arm, List[int]], 
                 previous: Action = None, use_other_arm: bool = False):
        super().__init__(dynamic=dynamic, arm=arm, collision_detection=collision_detection, previous=previous)
        self.static = static
        self.dynamic = dynamic
        self.held_objects = held_objects
        self.use_other_arm = use_other_arm
        self.affordance_id = -1
        self.frame_count = 0
        self.target = target
        self.primary_target_position = {"x": 0,"y": 0,"z": 0}
        self.secondary_target_position = None
        self.initialized_reach = False
        self.initialized_affordances = False
        # Convert from a numpy array to a dictionary.
        if isinstance(target, np.ndarray):
            self.primary_target_position = TDWUtils.array_to_vector3(target)
        # The target is a vector3 position.
        elif isinstance(target, dict):
            self.primary_target_position = target
        self._reach_body_part: ReplicantBodyPart = ReplicantBodyPart.hand_l
      

    def get_initialization_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        commands = super().get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                       image_frequency=image_frequency)
        # Remember the image frequency for the action.
        self.__image_frequency: ImageFrequency = image_frequency
        # Is Replicant already holding an object in the reach arm?
        if len(self.held_objects[self.reach_arm]) > 0:
            # Use the other arm to reach with.
            if self.use_other_arm and self.reach_arm != Arm.both:
                if self.reach_arm == Arm.left:
                    self.reach_arm = Arm.right
                else:
                    self.reach_arm = Arm.left
            else:
                # Flag that we are already holding with that arm, and let the user decide what to do.
                self.status = ActionStatus.already_holding
        return commands


    def get_ongoing_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
        # Test we have initialized for when the target is an object ID.
        # We need to do this AFTER get_initialization_commands() has run, 
        #  as we need the empty objects and bounds output data.
        if isinstance(self.target, int):
            if not self.initialized_affordances:
                if self.reach_arm == Arm.left:
                   static.primary_target_affordance_id, self.primary_target_position = self._initialize_affordances(reach_body_part=ReplicantBodyPart.hand_l, resp=resp)
                elif self.reach_arm == Arm.right:
                    static.primary_target_affordance_id, self.primary_target_position = self._initialize_affordances(reach_body_part=ReplicantBodyPart.hand_r, resp=resp)
                elif self.reach_arm == Arm.both:
                    static.primary_target_affordance_id, self.primary_target_position = self._initialize_affordances(reach_body_part=ReplicantBodyPart.hand_l, resp=resp)
                    static.secondary_target_affordance_id, self.secondary_target_position = self._initialize_affordances(reach_body_part=ReplicantBodyPart.hand_r, resp=resp)
                self.initialized_affordances = True
                # If the target is too far away, fail immediately.
                target_pos_arr = TDWUtils.vector3_to_array(self.primary_target_position)
                distance = np.linalg.norm(target_pos_arr - dynamic.position)
                if distance > 0.99:
                    self.status = ActionStatus.cannot_reach
                    static.primary_target_affordance_id = -1
                    return []
        if not self.initialized_reach:
            commands = []
            commands.extend(self._get_reach_commands(dynamic=dynamic, 
                                                     primary_target_position=self.primary_target_position,
                                                     secondary_target_position=self.secondary_target_position))
            self.initialized_reach = True
            return commands
        # We've arrived at the target.
        if self.frame_count >= self.reach_action_length:
            self.status = ActionStatus.success
            return []
        elif not self._is_valid_ongoing(dynamic=dynamic):
            return []
        else:
            while self.frame_count < self.reach_action_length:
                self.frame_count += 1 
                return []

    def _initialize_affordances(self, resp: List[bytes], reach_body_part: ReplicantBodyPart):
        # Get the nearest affordance position.
        nearest_distance = np.inf
        nearest_position = np.array([0, 0, 0])
        self.affordance_id = 0
        got_affordance_position = False
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "empt":
                empt = EmptyObjects(resp[i])
                for j in range(empt.get_num()):
                    # Get the ID of the affordance point.
                    empty_object_id = empt.get_id(j)
                    # Get the parent object ID.
                    object_id = AffordancePoints.EMPTY_OBJECT_IDS[empty_object_id]["object_id"]
                    # Found the target object.
                    if object_id == self.target:
                        got_affordance_position = True
                        # Get the position of the empty object.
                        empty_object_position = empt.get_position(j)
                        # Get the nearest affordance position.
                        distance = np.linalg.norm(self.dynamic.body_part_transforms[self.static.body_parts[reach_body_part]].position - empty_object_position)
                        if distance < nearest_distance:
                            nearest_distance = distance
                            nearest_position = empty_object_position
                            self.affordance_id = empty_object_id
        # The target position is the nearest affordance point.
        if got_affordance_position:
            return self.affordance_id, TDWUtils.array_to_vector3(nearest_position)
        else:
            return -1, self.find_object_center(resp=resp)

    def find_object_center(self, resp: List[bytes]) -> Dict[str, float]:
        # If the object doesn't have empty game objects, aim for the center and hope for the best.
        got_center = False
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "boun":
                bounds = Bounds(resp[i])
                for j in range(bounds.get_num()):
                    if bounds.get_id(j) == self.target:
                        got_center = True
                        return TDWUtils.array_to_vector3(bounds.get_center(j))
        if not got_center:
            raise Exception("Couldn't get the centroid of the target object.")

    def _previous_was_same(self, previous: Action) -> bool:
        """
        if isinstance(previous, MoveBy):
            return (previous.distance > 0 and self.distance > 0) or (previous.distance < 0 and self.distance < 0)
        else:
            return False
        """
        return False


 