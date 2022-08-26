from typing import List, Tuple
from abc import ABC, abstractmethod
from overrides import final
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.actions.action import Action
from tdw.replicant.image_frequency import ImageFrequency
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.collision_detection import CollisionDetection


class WalkMotion(Action, ABC):
    """
    Abstract base class for a Replicant walking action.
    """

    def __init__(self, dynamic: ReplicantDynamic, collision_detection: CollisionDetection, previous: Action = None):
        """
        :param dynamic: [The dynamic Magnebot data.](../magnebot_dynamic.md)
        :param collision_detection: [The collision detection rules.](../collision_detection.md)
        :param previous: The previous action, if any.
        """

        super().__init__()
        # My collision detection rules.
        self._collision_detection: CollisionDetection = collision_detection
        self._resetting: bool = False
        self.meters_per_frame = 0.04911
        self.walk_cycle_num_frames = 68
        self.playing = False

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
        :param dynamic: [The dynamic Magnebot data.](../magnebot_dynamic.md)
        :param image_frequency: [How image data will be captured during the image.](../image_frequency.md)

        :return: A list of commands to initialize this action.
        """
        commands: List[dict] = super().get_initialization_commands(resp=resp, static=static, dynamic=dynamic, image_frequency=image_frequency)
        commands.extend(self._get_walk_commands(dynamic=dynamic))
        return commands


    def _get_walk_commands(self, dynamic: ReplicantDynamic) -> List[dict]:
        commands = []
        #print("Starting play")
        commands.extend([{"$type": "set_target_framerate", 
                          "framerate": self.walk_record.framerate},
                         {"$type": "play_humanoid_animation",
                          "name": "walking_2",
                          "id": dynamic.replicant_id}])
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
        :param static: [The static Magnebot data.](../magnebot_static.md)
        :param dynamic: [The dynamic Magnebot data.](../magnebot_dynamic.md)
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
            print("Collided")
            self.status = ActionStatus.collision
            return False
        else:
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
            for object_id in dynamic.collisions_with_environment:
                for collision in dynamic.collisions_with_environment[object_id]:
                    if (self._collision_detection.floor and collision.floor) or \
                            (self._collision_detection.walls and not collision.floor):
                        if collision.state == "enter":
                            enters.append(object_id)
                        elif collision.state == "exit":
                            exits.append(object_id)
            # Ignore exit events.
            enters = [e for e in enters if e not in exits]
            if len(enters) > 0:
                return True
        # Check object collisions.
        if self._collision_detection.objects or len(self._collision_detection.include_objects) > 0:
            enters: List[Tuple[int, int]] = list()
            exits: List[Tuple[int, int]] = list()
            for object_ids in dynamic.collisions_with_objects:
                for collision in dynamic.collisions_with_objects[object_ids]:
                    object_id = object_ids[1]
                    # Accept the collision if the object is in the includes list or if it's not in the excludes list.
                    if object_id in self._collision_detection.include_objects or \
                            (self._collision_detection.objects and object_id not in
                             self._collision_detection.exclude_objects):
                        if collision.state == "enter":
                            enters.append(object_ids)
                        elif collision.state == "exit":
                            exits.append(object_ids)
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

    
