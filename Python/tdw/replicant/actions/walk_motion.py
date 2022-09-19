from typing import List, Dict, Tuple
from abc import ABC, abstractmethod
from overrides import final
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.actions.action import Action
from tdw.replicant.image_frequency import ImageFrequency
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.collision_detection import CollisionDetection
from tdw.librarian import HumanoidAnimationLibrarian, HumanoidLibrarian
from tdw.output_data import OutputData, Collision, EnvironmentCollision, Raycast
from tdw.tdw_utils import TDWUtils
from tdw.replicant.arm import Arm


class WalkMotion(Action, ABC):
    """
    Abstract base class for a Replicant walking action.
    """

    def __init__(self, dynamic: ReplicantDynamic, collision_detection: CollisionDetection,  held_objects: Dict[Arm, List[int]], 
                 avoid_objects: bool = False, previous: Action = None):
        """
        :param dynamic: [The dynamic Replicant data.](../Replicant_dynamic.md)
        :param collision_detection: [The collision detection rules.](../collision_detection.md)
        :param previous: The previous action, if any.
        """

        super().__init__()
        # My collision detection rules.
        self._collision_detection: CollisionDetection = collision_detection
        self.held_objects = held_objects
        self.avoid_objects = avoid_objects
        self._resetting: bool = False
        self.meters_per_frame = 0.04911
        self.walk_cycle_num_frames = 68
        self.playing = False
        self.walk_record = HumanoidAnimationLibrarian().get_record("walking_2")

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
        :param dynamic: [The dynamic Replicant data.](../Replicant_dynamic.md)
        :param image_frequency: [How image data will be captured during the image.](../image_frequency.md)

        :return: A list of commands to initialize this action.
        """
        commands: List[dict] = super().get_initialization_commands(resp=resp, static=static, dynamic=dynamic, image_frequency=image_frequency)
        url = self.walk_record.get_url()
        commands.append({"$type": "add_humanoid_animation", 
                         "name": self.walk_record.name, 
                         "url": url})
        commands.extend(self._get_walk_commands(dynamic=dynamic))
        return commands


    def _get_walk_commands(self, dynamic: ReplicantDynamic) -> List[dict]:
        commands = []
        commands.append({"$type": "set_target_framerate", 
                          "framerate": self.walk_record.framerate})
        left_id = -1
        right_id = -1
        if len(self.held_objects[Arm.left]) > 0:
            left_id = self.held_objects[Arm.left][0]
        if len(self.held_objects[Arm.right]) > 0:
            right_id = self.held_objects[Arm.right][0] 
        if len(self.held_objects[Arm.both]) > 0:
            left_id = self.held_objects[Arm.both][0] 
        pos = TDWUtils.array_to_vector3(dynamic.position)
        pos["z"] = pos["z"] + 0.1
        pos["y"] = pos["y"] + 1.0
        dest = TDWUtils.array_to_vector3(dynamic.position + dynamic.forward * 1.75)
        commands.extend([{"$type": "replicant_walk",
                         "left_arm_object_id": left_id,
                         "right_arm_object_id": right_id,
                          "id": dynamic.replicant_id},
                         {"$type": "send_boxcast",
                          "half_extents": {"x": 0.1, "y": 0.1, "z": 0.25},
                          "origin": pos,
                          "destination": dest,
                          "id": 99999}])
        self.playing = True
        return commands

    def _get_stop_commands(self, dynamic: ReplicantDynamic) -> List[dict]:
        commands = []
        #print("Stopping play")
        self.playing = False
        commands.append({"$type": "stop_humanoid_animation",
                         "id": dynamic.replicant_id})
        return commands

    def get_end_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                         image_frequency: ImageFrequency) -> List[dict]:
        """
        :param resp: The response from the build.
        :param static: [The static Replicant data.](../Replicant_static.md)
        :param dynamic: [The dynamic Replicant data.](../Replicant_dynamic.md)
        :param image_frequency: [How image data will be captured during the image.](../image_frequency.md)

        :return: A list of commands that must be sent to end any action.
        """
        #print("Ending")
        commands = []
        commands.extend(self._get_stop_commands(dynamic=dynamic))
        commands.extend(super().get_end_commands(resp=resp, static=static, dynamic=dynamic,
                                                 image_frequency=image_frequency))
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

    
