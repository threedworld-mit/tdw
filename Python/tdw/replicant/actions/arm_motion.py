from typing import Dict, List, Tuple
from abc import ABC, abstractmethod
from overrides import final
from tdw.tdw_utils import TDWUtils
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.actions.action import Action
from tdw.replicant.image_frequency import ImageFrequency
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.collision_detection import CollisionDetection
from tdw.output_data import OutputData, Collision, EnvironmentCollision
from tdw.replicant.replicant_body_part import ReplicantBodyPart, BODY_PARTS
from tdw.replicant.arm import Arm
import numpy as np


class ArmMotion(Action, ABC):
    """
    Abstract base class for actions related to Replicant arm motion.
    """

    def __init__(self, dynamic: ReplicantDynamic, arm: Arm, collision_detection: CollisionDetection, previous: Action = None):
        """
        :param dynamic: [The dynamic Replicant data.](../magnebot_dynamic.md)
        :param Arm. The arm performing the action.
        :param collision_detection: [The collision detection rules.](../collision_detection.md)
        :param previous: The previous action, if any.
        """

        super().__init__()
        self.reverse_reach: bool
        # My collision detection rules.
        self._collision_detection: CollisionDetection = collision_detection
        self._resetting: bool = False
        self._reach_action_length = 30
        self._reset_action_length = 20
        self._drop_length = 5
        self._reach_arm = arm

        # Immediately end the action if the previous action was the same motion and it ended with a collision.
        if self._collision_detection.previous_was_same and previous is not None and \
                previous.status != ActionStatus.success and previous.status != ActionStatus.ongoing and \
                self._previous_was_same(previous=previous):
            if previous.status == ActionStatus.collision:
                self.status = ActionStatus.collision

    def get_initialization_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        """
        :param resp: The response from the build.
        :param dynamic: [The dynamic Replicant data.](../magnebot_dynamic.md)
        :param image_frequency: [How image data will be captured during the image.](../image_frequency.md)

        :return: A list of commands to initialize this action.
        """

        commands: List[dict] = super().get_initialization_commands(resp=resp, static=static, dynamic=dynamic, image_frequency=image_frequency)
        # Request EmptyObjects and Bounds data.
        commands.extend([{"$type": "send_empty_objects",
                         "frequency": "always"},
                         {"$type": "send_bounds",
                          "frequency": "always"}])
        return commands

    def _get_reach_commands(self, dynamic: ReplicantDynamic, primary_target_position: Dict[str, float],
                            secondary_target_position: Dict[str, float]) -> List[dict]:
        commands=[]
        # Reach for IK target, at affordance position.
        if secondary_target_position != None:
            commands.append({"$type": "replicant_reach_for_position", 
                          "primary_target_position": primary_target_position, 
                          "secondary_target_position": secondary_target_position, 
                          "id": dynamic.replicant_id, 
                          "length": self._reach_action_length, 
                          "arm": self._reach_arm.name})
        else:
            commands.append({"$type": "replicant_reach_for_position", 
                          "primary_target_position": primary_target_position, 
                          "id": dynamic.replicant_id, 
                          "length": self._reach_action_length, 
                          "arm": self._reach_arm.name})
        return commands


    def _get_hold_object_commands(self,  static: ReplicantStatic, dynamic: ReplicantDynamic, object_id: int) -> List[dict]:
        commands=[]
        # Move the arm holding the object to a reasonable carrying position. 
        pos = TDWUtils.array_to_vector3(dynamic.position)
        l_hand_pos = TDWUtils.array_to_vector3(dynamic.body_part_transforms[static.body_parts[ReplicantBodyPart.hand_l]].position)
        r_hand_pos = TDWUtils.array_to_vector3(dynamic.body_part_transforms[static.body_parts[ReplicantBodyPart.hand_r]].position)
        # Handle the case where the replicant carries an object that is behind it (i.e. carrying one end of a sofa).
        if self.reverse_reach:
            fwd = TDWUtils.array_to_vector3(-dynamic.forward) 
            hold_dist = np.linalg.norm(dynamic.position + -dynamic.forward) * 0.1
        else:
            fwd = TDWUtils.array_to_vector3(dynamic.forward)
            hold_dist = np.linalg.norm(dynamic.position + dynamic.forward) * 0.1
        commands.extend([{"$type": "replicant_reach_for_position", 
                                   "primary_target_position": {"x": l_hand_pos["x"] + (fwd["x"] * 0.5), "y": l_hand_pos["y"] + 0.25, "z": l_hand_pos["z"] + (fwd["z"] * 0.5)},
                                   "secondary_target_position": {"x": r_hand_pos["x"] + (fwd["x"] * 0.5), "y": r_hand_pos["y"] + 0.25, "z": r_hand_pos["z"]  + (fwd["z"] * 0.5)},   
                                   "primary_affordance_id": static.primary_target_affordance_id,
                                   "secondary_affordance_id": static.secondary_target_affordance_id,  
                                   "id": dynamic.replicant_id,
                                   "length": self._reset_action_length, 
                                   "arm": self._reach_arm.name},
                          {"$type": "replicant_reset_held_object_rotation", 
                               "target": object_id, 
                               "primary_affordance_id": static.primary_target_affordance_id,
                               "secondary_affordance_id": static.secondary_target_affordance_id,   
                               "id": dynamic.replicant_id,
                               "length": self._reset_action_length, 
                               "arm": self._reach_arm.name}
                        ])
        return commands
   
    def _get_drop_commands(self, dynamic: ReplicantDynamic, object_id: int) -> List[dict]:
        commands=[]
        commands.append({"$type": "replicant_drop_object",
                          "target": object_id,
                          "id": dynamic.replicant_id,
                          "arm": self._reach_arm.name})
        return commands

    def _get_reset_arm_commands(self, dynamic: ReplicantDynamic) -> List[dict]:
        commands=[]
        commands.append({"$type": "replicant_reset_arm",
                          "id": dynamic.replicant_id,
                          "arm": self._reach_arm.name})
        return commands

    @final
    def _is_valid_ongoing(self, dynamic: ReplicantDynamic) -> bool:
        """
        :param replicant_id: The ID of this Replicant

        :return: True if the Replicant didn't collide with something that should make it stop.
        """

        # Stop if the Replicant is colliding with something.
        if self._is_collision(dynamic=dynamic):
            self.status = ActionStatus.collision
            return False
        else:
            return True
       
        return True

    @final
    def _is_collision(self, dynamic: ReplicantDynamic) -> bool:
        """
        :param replicant_id: The ID of this Replicant

        :return: True if there was a collision that according to the current detection rules means that the Replicant needs to stop moving.
        """
        
        # Check environment collisions.
        if self._collision_detection.floor or self._collision_detection.walls:
            enters: List[int] = list()
            exits: List[int] = list()
            for body_part_id in dynamic.collisions:
                for collision in dynamic.collisions[body_part_id]:
                    if isinstance(collision, EnvironmentCollision):
                        collider_id = collision.get_object_id()
                        state = collision.get_state()
                        if (self._collision_detection.floor and collision.get_floor()) or \
                                (self._collision_detection.walls and not collision.get_floor()):
                            if collision.get_state() == "enter":
                                enters.append(body_part_id)
                            elif collision.get_state() == "exit":
                                exits.append(body_part_id)
            # Ignore exit events.
            enters = [e for e in enters if e not in exits]
            if len(enters) > 0:
                return True
        # Check object collisions.
        if self._collision_detection.objects or len(self._collision_detection.include_objects) > 0:
            enters: List[Tuple[int, int]] = list()
            exits: List[Tuple[int, int]] = list()
            for body_part_id in dynamic.collisions:
                for collision in dynamic.collisions[body_part_id]:
                    if isinstance(collision, Collision):
                        collider_id = collision.get_collider_id()
                        collidee_id = collision.get_collidee_id()
                        state = collision.get_state()
                        # Accept the collision if the object is in the includes list or if it's not in the excludes list.
                        if collider_id in self._collision_detection.include_objects or \
                                (self._collision_detection.objects and collider_id not in
                                 self._collision_detection.exclude_objects):
                            if collision.get_state() == "enter":
                                enters.append(collider_id)
                            elif collision.get_state() == "exit":
                                exits.append(collider_id)
            # Ignore exit events.
            enters: List[Tuple[int, int]] = [e for e in enters if e not in exits]
            if len(enters) > 0:
                return True
        return False

    @abstractmethod
    def _previous_was_same(self, previous: Action) -> bool:
        """
        :param previous: The previous action.

        :return: True if the previous action was the "same" as this action for the purposes of collision detection.
        """

        raise Exception()

    
