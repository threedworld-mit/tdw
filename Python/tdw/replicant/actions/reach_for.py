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



"""
Create a humanoid that walks across the room, knocks over a chair and reaches for 
a randomly-positioned object multiple times.
"""


class ReachFor(ArmMotion):
    """
    Reach for a target object or position.
    """

    def __init__(self, target: Union[int, np.ndarray, Dict[str,  float]], resp: List[bytes], arm: Arm, hand_position: np.ndarray, 
                 dynamic: ReplicantDynamic, collision_detection: CollisionDetection, previous: Action = None):
        super().__init__(dynamic=dynamic, collision_detection=collision_detection, previous=previous)
        self.reach_action_length=30
        self.reset_action_length=20
        self.affordance_id = 0
        self.reach_arm = "left"
        self.frame_count = 0
        self.target_position = {"x": 0,"y": 0,"z": 0}

        AffordancePoints.EMPTY_OBJECT_IDS.clear()
        # Convert from a numpy array to a dictionary.
        if isinstance(target, np.ndarray):
            self.target_position = TDWUtils.array_to_vector3(target)
        # The target is a vector3 position.
        elif isinstance(target, dict):
            self.target_position = target
        # The target is an object ID.
        elif isinstance(target, int):
            # Get the nearest affordance position.
            nearest_distance = np.inf
            nearest_position = np.array([0, 0, 0])
            got_affordance_position = False
            for i in range(len(resp) - 1):
                r_id = OutputData.get_data_type_id(resp[i])
                if r_id == "empt":
                    empt = EmptyObjects(resp[i])
                    for j in range(empt.get_num()):
                        # Get the ID of the affordance point.
                        empty_object_id = empt.get_id(j)
                        self.affordance_id = empty_object_id
                        # Get the parent object ID.
                        object_id = AffordancePoints.EMPTY_OBJECT_IDS[empty_object_id]["object_id"]
                        # Found the target object.
                        if object_id == target:
                            got_affordance_position = True
                            # Get the position of the empty object.
                            empty_object_position = empt.get_position(j)
                            # Get the nearest affordance position.
                            distance = np.linalg.norm(hand_position - empty_object_position)
                            if distance < nearest_distance:
                                nearest_distance = distance
                                nearest_position = empty_object_position
            # The target position is the nearest affordance point.
            if got_affordance_position:
                self.target_position = TDWUtils.array_to_vector3(nearest_position)
            # If the object doesn't have empty game objects, aim for the center and hope for the best.
            else:
                got_center = False
                for i in range(len(resp) - 1):
                    r_id = OutputData.get_data_type_id(resp[i])
                    if r_id == "boun":
                        bounds = Bounds(resp[i])
                        for j in range(bounds.get_num()):
                            if bounds.get_id(j) == target:
                                self.target_position = TDWUtils.array_to_vector3(bounds.get_center(j))
                                got_center = True
                                break
                if not got_center:
                    raise Exception("Couldn't get the centroid of the target object.")
        else:
            raise Exception(f"Invalid target: {target}")

    def get_initialization_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        commands = super().get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                       image_frequency=image_frequency)
        # Remember the image frequency for the action.
        self.__image_frequency: ImageFrequency = image_frequency
        # Reach for IK target, at affordance position. 
        # Request EmptyObjects and Bounds data.
        commands.extend([{"$type": "humanoid_reach_for_position", 
                          "position": self.target_position, 
                          "id": dynamic.replicant_id, 
                          "length": self.reach_action_length, 
                          "arm": self.reach_arm},
                         {"$type": "send_empty_objects",
                         "frequency": "always"},
                         {"$type": "send_bounds",
                          "frequency": "always"}])
        return commands


    def get_ongoing_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
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

    def _previous_was_same(self, previous: Action) -> bool:
        if isinstance(previous, MoveBy):
            return (previous.distance > 0 and self.distance > 0) or (previous.distance < 0 and self.distance < 0)
        else:
            return False




 